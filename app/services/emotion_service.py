import librosa
import numpy as np
import torch
import torchaudio
import soundfile as sf
try:
    from speechbrain.inference.classifiers import EncoderClassifier
except ImportError:
    from speechbrain.pretrained import EncoderClassifier
from typing import List, Dict, Tuple, Optional
import asyncio
import io
import tempfile
import os
from loguru import logger

from app.core.config import settings
from app.core.minio_client import minio_client
from app.schemas.emotion import EmotionFeature, EmotionResult

# 支持的情绪标签
EMOTION_LABELS = {
    0: "neutral",      # 中性
    1: "happy",        # 开心
    2: "sad",          # 悲伤
    3: "angry",        # 愤怒
    4: "fear",         # 恐惧
    5: "disgust",      # 厌恶
    6: "surprise"      # 惊讶
}

# 情绪标签的中文映射
EMOTION_LABELS_CN = {
    "neutral": "中性",
    "happy": "开心", 
    "sad": "悲伤",
    "angry": "愤怒",
    "fear": "恐惧",
    "disgust": "厌恶",
    "surprise": "惊讶"
}


class EmotionService:
    """语音情绪识别服务"""
    
    _instance = None
    _model = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def initialize_model(cls):
        """初始化情绪识别模型"""
        try:
            # 检测设备
            cls._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Using device: {cls._device}")
            
            # 使用SpeechBrain的情绪识别模型
            # 使用ECAPA模型，更稳定可靠
            cls._model = EncoderClassifier.from_hparams(
                source=settings.EMOTION_MODEL,
                savedir="pretrained_models/emotion_recognition",
                run_opts={"device": str(cls._device)}
            )
            
            logger.info("Emotion recognition model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize emotion model: {e}")
            # 备用方案：尝试不同的模型
            backup_models = [
                "speechbrain/emotion-identification-IEMOCAP",
                "speechbrain/emotion-raw-wav2vec2-IEMOCAP",
                "speechbrain/emotion-recognition-cnn14-esc50"
            ]
            
            for backup_model in backup_models:
                try:
                    cls._model = EncoderClassifier.from_hparams(
                        source=backup_model,
                        savedir=f"pretrained_models/emotion_backup_{backup_model.split('/')[-1]}",
                        run_opts={"device": str(cls._device)}
                    )
                    logger.info(f"Backup emotion recognition model loaded: {backup_model}")
                    return True
                except Exception as backup_e:
                    logger.warning(f"Failed to load backup model {backup_model}: {backup_e}")
            
            raise Exception("All emotion recognition models failed to load")
    
    async def check_model_status(self) -> bool:
        """检查模型状态"""
        return self._model is not None
    
    async def detect_emotion(self, audio_data: bytes, employee_id: Optional[int] = None) -> EmotionResult:
        """检测语音情绪"""
        if not self._model:
            raise RuntimeError("Emotion recognition model not initialized")
        
        try:
            # 1. 音频预处理
            audio_tensor, sr = await self._preprocess_audio(audio_data)
            
            # 2. 音频质量评估
            quality_score = await self._assess_audio_quality(audio_tensor, sr)
            
            if quality_score < settings.AUDIO_QUALITY_THRESHOLD:
                raise ValueError(f"音频质量过低 ({quality_score:.2f})，无法准确识别情绪")
            
            # 3. 情绪识别
            with torch.no_grad():
                # 确保音频在正确的设备上
                audio_tensor = audio_tensor.to(self._device)
                
                # 添加批次维度
                if audio_tensor.dim() == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)
                
                # 进行情绪预测
                prediction = self._model.classify_batch(audio_tensor)
                
                # 获取概率分布
                if hasattr(prediction, 'logits'):
                    probs = torch.softmax(prediction.logits, dim=-1)
                elif isinstance(prediction, tuple):
                    probs = torch.softmax(prediction[0], dim=-1)
                else:
                    probs = torch.softmax(prediction, dim=-1)
                
                # 转换为numpy
                probs = probs.cpu().numpy()[0]
            
            # 4. 处理结果
            emotion_probabilities = {}
            for i, prob in enumerate(probs):
                if i < len(EMOTION_LABELS):
                    emotion_label = EMOTION_LABELS[i]
                    emotion_probabilities[emotion_label] = float(prob)
            
            # 5. 确定主要情绪
            dominant_emotion = max(emotion_probabilities, key=emotion_probabilities.get)
            confidence = emotion_probabilities[dominant_emotion]
            
            # 6. 计算情绪强度和复杂度
            intensity = await self._calculate_emotion_intensity(emotion_probabilities)
            complexity = await self._calculate_emotion_complexity(emotion_probabilities)
            
            # 7. 上传音频文件
            audio_url = await self._upload_audio(audio_data, f"emotion_{int(asyncio.get_event_loop().time())}.wav")
            
            # 8. 生成详细分析
            emotion_analysis = await self._generate_emotion_analysis(
                emotion_probabilities, 
                dominant_emotion, 
                confidence,
                intensity,
                complexity
            )
            
            result = EmotionResult(
                dominant_emotion=dominant_emotion,
                confidence=confidence,
                emotion_probabilities=emotion_probabilities,
                intensity=intensity,
                complexity=complexity,
                quality_score=quality_score,
                analysis=emotion_analysis,
                audio_url=audio_url,
                audio_duration=len(audio_tensor) / sr,
                model_name="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
                processing_time=0  # 实际应该计算处理时间
            )
            
            logger.info(f"Emotion detection completed: {dominant_emotion} ({confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            raise
    
    async def batch_detect_emotion(self, audio_files: List[bytes], employee_id: Optional[int] = None) -> List[EmotionResult]:
        """批量检测情绪"""
        results = []
        
        for i, audio_data in enumerate(audio_files):
            try:
                result = await self.detect_emotion(audio_data, employee_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to detect emotion for audio {i}: {e}")
                # 可以选择添加一个错误结果或者跳过
                continue
        
        return results
    
    async def _preprocess_audio(self, audio_data: bytes) -> Tuple[torch.Tensor, int]:
        """音频预处理"""
        try:
            # 使用tempfile处理音频数据
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # 加载音频 - 情绪识别模型通常需要16kHz采样率
                audio, sr = librosa.load(temp_file_path, sr=16000, mono=True)
                
                # 音频增强
                audio = self._enhance_audio(audio)
                
                # 转换为tensor
                audio_tensor = torch.from_numpy(audio).float()
                
                return audio_tensor, sr
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Audio preprocessing for emotion failed: {e}")
            raise
    
    def _enhance_audio(self, audio: np.ndarray) -> np.ndarray:
        """音频增强（针对情绪识别优化）"""
        try:
            # 1. 预加重滤波
            pre_emphasis = 0.97
            emphasized_audio = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])
            
            # 2. 归一化
            if len(emphasized_audio) > 0:
                max_val = np.max(np.abs(emphasized_audio))
                if max_val > 0:
                    emphasized_audio = emphasized_audio / max_val * 0.95
            
            return emphasized_audio
            
        except Exception as e:
            logger.warning(f"Audio enhancement for emotion failed, using original: {e}")
            return audio
    
    async def _assess_audio_quality(self, audio_tensor: torch.Tensor, sr: int) -> float:
        """评估音频质量（针对情绪识别）"""
        try:
            audio = audio_tensor.numpy()
            
            # 1. 计算信噪比
            snr = self._calculate_snr(audio)
            
            # 2. 计算过零率
            zcr = librosa.feature.zero_crossing_rate(audio)[0].mean()
            
            # 3. 计算能量
            energy = np.sum(audio ** 2) / len(audio)
            
            # 4. 计算频谱特征
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0].mean()
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0].mean()
            
            # 5. 情绪识别质量评分标准
            snr_score = min(snr / 15, 1.0)  # SNR评分
            zcr_score = 1.0 - min(abs(zcr - 0.1) * 5, 1.0)  # 过零率评分
            energy_score = min(energy * 1000, 1.0)  # 能量评分
            spectral_score = min(spectral_centroid / 4000, 1.0)  # 频谱重心评分
            
            # 综合质量评分
            quality_score = (snr_score * 0.3 + zcr_score * 0.2 + 
                           energy_score * 0.3 + spectral_score * 0.2)
            
            return float(quality_score)
            
        except Exception as e:
            logger.error(f"Audio quality assessment for emotion failed: {e}")
            return 0.5
    
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """计算信噪比"""
        try:
            signal_power = np.mean(audio ** 2)
            noise_power = np.var(audio) * 0.1  # 估计噪声功率
            
            if noise_power == 0:
                return 20.0
            
            snr_db = 10 * np.log10(signal_power / noise_power)
            return float(snr_db)
            
        except Exception as e:
            logger.error(f"SNR calculation for emotion failed: {e}")
            return 10.0
    
    async def _calculate_emotion_intensity(self, emotion_probabilities: Dict[str, float]) -> float:
        """计算情绪强度"""
        try:
            # 移除中性情绪的影响
            neutral_prob = emotion_probabilities.get("neutral", 0.0)
            
            # 计算其他情绪的平均概率
            non_neutral_probs = [p for k, p in emotion_probabilities.items() if k != "neutral"]
            if non_neutral_probs:
                intensity = np.mean(non_neutral_probs)
            else:
                intensity = 0.0
            
            return float(intensity)
            
        except Exception as e:
            logger.error(f"Emotion intensity calculation failed: {e}")
            return 0.5
    
    async def _calculate_emotion_complexity(self, emotion_probabilities: Dict[str, float]) -> float:
        """计算情绪复杂度"""
        try:
            # 使用熵来衡量情绪的复杂度
            probs = list(emotion_probabilities.values())
            probs = np.array(probs)
            probs = probs + 1e-8  # 避免log(0)
            probs = probs / np.sum(probs)
            
            # 计算香农熵
            entropy_value = -np.sum(probs * np.log2(probs))
            
            # 归一化到0-1范围
            max_entropy = np.log2(len(probs))
            complexity = entropy_value / max_entropy
            
            return float(complexity)
            
        except Exception as e:
            logger.error(f"Emotion complexity calculation failed: {e}")
            return 0.5
    
    async def _generate_emotion_analysis(
        self, 
        emotion_probabilities: Dict[str, float], 
        dominant_emotion: str,
        confidence: float,
        intensity: float,
        complexity: float
    ) -> Dict:
        """生成情绪分析报告"""
        try:
            analysis = {
                "dominant_emotion_cn": EMOTION_LABELS_CN.get(dominant_emotion, dominant_emotion),
                "confidence_level": self._get_confidence_level(confidence),
                "intensity_level": self._get_intensity_level(intensity),
                "complexity_level": self._get_complexity_level(complexity),
                "emotion_distribution": {},
                "suggestions": await self._generate_suggestions(dominant_emotion, confidence, intensity),
                "emotion_breakdown": {}
            }
            
            # 情绪分布分析
            for emotion, prob in emotion_probabilities.items():
                emotion_cn = EMOTION_LABELS_CN.get(emotion, emotion)
                analysis["emotion_distribution"][emotion_cn] = f"{prob:.2%}"
            
            # 情绪详细分解
            sorted_emotions = sorted(emotion_probabilities.items(), key=lambda x: x[1], reverse=True)
            analysis["emotion_breakdown"] = {
                "primary": {
                    "emotion": EMOTION_LABELS_CN.get(sorted_emotions[0][0], sorted_emotions[0][0]),
                    "probability": f"{sorted_emotions[0][1]:.2%}"
                },
                "secondary": {
                    "emotion": EMOTION_LABELS_CN.get(sorted_emotions[1][0], sorted_emotions[1][0]) if len(sorted_emotions) > 1 else None,
                    "probability": f"{sorted_emotions[1][1]:.2%}" if len(sorted_emotions) > 1 else "0%"
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Emotion analysis generation failed: {e}")
            return {}
    
    def _get_confidence_level(self, confidence: float) -> str:
        """获取置信度等级"""
        if confidence >= 0.8:
            return "非常高"
        elif confidence >= 0.6:
            return "较高"
        elif confidence >= 0.4:
            return "中等"
        elif confidence >= 0.2:
            return "较低"
        else:
            return "很低"
    
    def _get_intensity_level(self, intensity: float) -> str:
        """获取强度等级"""
        if intensity >= 0.7:
            return "强烈"
        elif intensity >= 0.5:
            return "中等"
        elif intensity >= 0.3:
            return "轻微"
        else:
            return "平淡"
    
    def _get_complexity_level(self, complexity: float) -> str:
        """获取复杂度等级"""
        if complexity >= 0.7:
            return "复杂"
        elif complexity >= 0.5:
            return "较复杂"
        elif complexity >= 0.3:
            return "简单"
        else:
            return "单一"
    
    async def _generate_suggestions(self, dominant_emotion: str, confidence: float, intensity: float) -> List[str]:
        """生成建议"""
        suggestions = []
        
        try:
            if dominant_emotion == "angry":
                suggestions.extend([
                    "建议进行深呼吸放松",
                    "可以尝试听一些舒缓的音乐",
                    "避免在情绪激动时做重要决定"
                ])
            elif dominant_emotion == "sad":
                suggestions.extend([
                    "建议与朋友或家人交流",
                    "可以适当进行户外活动",
                    "尝试做一些让自己开心的事情"
                ])
            elif dominant_emotion == "happy":
                suggestions.extend([
                    "保持积极的心态",
                    "可以分享这份快乐给他人",
                    "记录下这美好的时刻"
                ])
            elif dominant_emotion == "fear":
                suggestions.extend([
                    "尝试面对恐惧的来源",
                    "寻求他人的支持和帮助",
                    "通过正念练习来缓解焦虑"
                ])
            elif dominant_emotion == "surprise":
                suggestions.extend([
                    "保持开放的心态接受新事物",
                    "可以记录下这个意外的发现",
                    "与他人分享这个惊喜"
                ])
            elif dominant_emotion == "disgust":
                suggestions.extend([
                    "尝试理解产生这种情绪的原因",
                    "可以通过转移注意力来缓解",
                    "避免接触引起厌恶的事物"
                ])
            else:  # neutral
                suggestions.extend([
                    "保持平和的心态",
                    "可以尝试一些新的体验",
                    "适当增加一些有趣的活动"
                ])
            
            # 根据置信度和强度添加额外建议
            if confidence < 0.5:
                suggestions.append("情绪识别置信度较低，建议再次确认")
            
            if intensity > 0.7:
                suggestions.append("情绪强度较高，建议适当调节")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return ["建议保持良好的情绪状态"]
    
    async def _upload_audio(self, audio_data: bytes, filename: str) -> str:
        """上传音频到MinIO"""
        try:
            import time
            timestamp = int(time.time())
            object_name = f"emotion/{timestamp}_{filename}"
            
            minio_client.put_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=object_name,
                data=io.BytesIO(audio_data),
                length=len(audio_data),
                content_type="audio/wav"
            )
            
            audio_url = f"{settings.minio_url}/{settings.MINIO_BUCKET}/{object_name}"
            return audio_url
            
        except Exception as e:
            logger.error(f"Failed to upload emotion audio to MinIO: {e}")
            raise


# 创建全局服务实例
emotion_service = EmotionService()