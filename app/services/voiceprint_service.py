import librosa
import numpy as np
import torch
import torchaudio
import webrtcvad
import soundfile as sf
from speechbrain.inference.speaker import SpeakerRecognition
from speechbrain.inference.encoders import MelSpectrogramEncoder
from scipy import signal
from scipy.stats import entropy
from typing import List, Dict, Tuple, Optional
import asyncio
import io
import tempfile
import os
from loguru import logger

from app.core.config import settings
from app.core.minio_client import minio_client
from app.schemas.voiceprint import VoiceprintFeature, VoiceprintMatch
from app.models.database import get_db
from app.models.voiceprint import VoiceprintModel
from app.models.employee import EmployeeModel


class VoiceprintService:
    """声纹识别服务"""
    
    _instance = None
    _model = None
    _encoder = None
    _vad = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def initialize_model(cls):
        """初始化声纹识别模型"""
        try:
            # 设置Hugging Face镜像（如果在中国大陆）
            if os.getenv("USE_HF_MIRROR", "false").lower() == "true":
                os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
                logger.info("Using Hugging Face mirror: https://hf-mirror.com")
            
            # 尝试导入不同版本的SpeechBrain
            try:
                from speechbrain.inference.speaker import SpeakerRecognition
            except ImportError:
                try:
                    from speechbrain.pretrained import SpeakerRecognition
                except ImportError as e:
                    logger.error(f"SpeechBrain import failed: {e}")
                    logger.warning("请安装SpeechBrain: pip install speechbrain")
                    cls._model = None
                    return False
            
            # 使用绝对路径，避免相对路径在不同工作目录下找不到模型
            base_dir = "/app/pretrained_models"
            model_dir = os.path.join(base_dir, settings.VOICEPRINT_MODEL.split("/")[-1])
            # 使用本地文件，不重新下载
            # 检查模型文件是否已存在，避免意外下载
            required_files = ["hyperparams.yaml"]
            missing_files = [f for f in required_files if not os.path.exists(os.path.join(model_dir, f))]
            if missing_files:
                logger.error(f"Model files missing in {model_dir}: {missing_files}")
                logger.warning("Please run the download script first: python scripts/download_models.py")
                cls._model = None
                return False

            cls._model = SpeakerRecognition.from_hparams(
                source=settings.VOICEPRINT_MODEL,
                savedir=model_dir,
                run_opts={"device": "cpu"}  # 初始化时使用CPU避免GPU内存问题
            )
            
            # 初始化VAD
            try:
                cls._vad = webrtcvad.Vad(3)  # 高敏感度
            except ImportError as e:
                logger.warning(f"VAD module not available: {e}")
                cls._vad = None
            
            logger.info(f"Voiceprint model loaded: {settings.VOICEPRINT_MODEL}")
            return True
        except ImportError as e:
            logger.error(f"SpeechBrain not properly installed for voiceprint recognition: {e}")
            logger.warning("Voiceprint recognition will be unavailable")
            cls._model = None
            return False
        except Exception as e:
            logger.error(f"Failed to initialize voiceprint model: {e}")
            logger.warning("Voiceprint recognition will be unavailable - run download script to get models")
            cls._model = None
            cls._vad = None
            return False
    
    async def check_model_status(self) -> bool:
        """检查模型状态"""
        return self._model is not None
    
    async def extract_voiceprint(self, audio_data: bytes, employee_id: int) -> VoiceprintFeature:
        """提取声纹特征"""
        if not self._model:
            raise RuntimeError("声纹识别模型未初始化，请先运行模型下载脚本: python scripts/download_models.py")
        
        try:
            # 1. 音频预处理
            audio_tensor, sr = await self._preprocess_audio(audio_data)
            
            # 2. 质量评估
            quality_score = await self._assess_audio_quality(audio_tensor, sr)
            
            if quality_score < settings.AUDIO_QUALITY_THRESHOLD:
                raise ValueError(f"音频质量过低 ({quality_score:.2f})，请重新录制")
            
            # 3. 提取声纹特征
            with torch.no_grad():
                embedding = self._model.encode_batch(audio_tensor.unsqueeze(0))
                embedding = embedding.squeeze().cpu().numpy()
            
            # 4. 归一化特征
            embedding = self._normalize_embedding(embedding)
            
            return VoiceprintFeature(
                embedding=embedding.tolist(),
                model_name=settings.VOICEPRINT_MODEL,
                sample_rate=sr,
                duration=len(audio_tensor) / sr,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Voiceprint extraction failed: {e}")
            raise
    
    async def register_voiceprint(self, employee_id: int, audio_data: bytes, sample_index: int) -> str:
        """注册声纹"""
        try:
            # 提取声纹特征
            feature = await self.extract_voiceprint(audio_data, employee_id)
            
            # 上传音频到MinIO
            audio_url = await self._upload_audio(audio_data, f"voiceprint_{employee_id}_{sample_index}.wav")
            
            # 保存到数据库
            voiceprint_id = await self._save_voiceprint(employee_id, feature, audio_url)
            
            logger.info(f"Voiceprint registered for employee {employee_id}, sample {sample_index}")
            return voiceprint_id
            
        except Exception as e:
            logger.error(f"Voiceprint registration failed: {e}")
            raise
    
    async def recognize_voiceprint(self, audio_data: bytes, meeting_id: Optional[int] = None) -> VoiceprintMatch:
        """声纹识别"""
        try:
            # 提取当前音频特征
            current_feature = await self.extract_voiceprint(audio_data, 0)
            
            # 获取所有活跃的声纹特征
            voiceprints = await self._get_active_voiceprints()
            
            if not voiceprints:
                raise ValueError("No active voiceprints found")
            
            # 计算相似度
            best_match = None
            best_similarity = 0
            all_matches = []
            
            for vp in voiceprints:
                # 计算余弦相似度
                similarity = self._calculate_similarity(
                    np.array(current_feature.embedding),
                    np.array(vp.feature_data)
                )
                
                match_info = {
                    "voiceprint_id": vp.voiceprint_id,
                    "employee_id": vp.employee_id,
                    "similarity": float(similarity)
                }
                all_matches.append(match_info)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = match_info
            
            # 上传音频
            import time
            audio_url = await self._upload_audio(audio_data, f"recognition_{int(time.time())}.wav")
            
            # 生成结果
            threshold = settings.VOICEPRINT_THRESHOLD
            is_identified = best_similarity >= threshold
            
            result = VoiceprintMatch(
                success=is_identified,
                voiceprint_id=best_match["voiceprint_id"] if is_identified else None,
                employee_id=best_match["employee_id"] if is_identified else None,
                confidence=best_similarity,
                threshold=threshold,
                audio_url=audio_url,
                all_matches=all_matches,
                processing_time=0  # 实际应该计算处理时间
            )
            
            # 记录识别日志
            await self._log_recognition(result, audio_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Voiceprint recognition failed: {e}")
            raise
    
    async def _preprocess_audio(self, audio_data: bytes) -> Tuple[torch.Tensor, int]:
        """音频预处理"""
        try:
            # 使用tempfile处理音频数据
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # 加载音频
                audio, sr = librosa.load(temp_file_path, sr=settings.SAMPLE_RATE, mono=True)
                
                # 重采样到目标采样率
                if sr != settings.SAMPLE_RATE:
                    audio = librosa.resample(audio, orig_sr=sr, target_sr=settings.SAMPLE_RATE)
                    sr = settings.SAMPLE_RATE
                
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
            logger.error(f"Audio preprocessing failed: {e}")
            raise
    
    def _enhance_audio(self, audio: np.ndarray) -> np.ndarray:
        """音频增强"""
        try:
            # 1. 降噪处理
            # 使用谱减法进行简单降噪
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            
            # 估计噪声（取前几帧的平均值）
            noise_frames = magnitude[:, :10]
            noise_profile = np.mean(noise_frames, axis=1, keepdims=True)
            
            # 谱减法
            alpha = 2.0  # 减法因子
            enhanced_magnitude = magnitude - alpha * noise_profile
            enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)  # 防止过度削减
            
            # 重构音频
            enhanced_stft = enhanced_magnitude * np.exp(1j * np.angle(stft))
            enhanced_audio = librosa.istft(enhanced_stft)
            
            # 2. 音量归一化
            if len(enhanced_audio) > 0:
                max_val = np.max(np.abs(enhanced_audio))
                if max_val > 0:
                    enhanced_audio = enhanced_audio / max_val * 0.9
            
            return enhanced_audio
            
        except Exception as e:
            logger.warning(f"Audio enhancement failed, using original: {e}")
            return audio
    
    async def _assess_audio_quality(self, audio_tensor: torch.Tensor, sr: int) -> float:
        """评估音频质量"""
        try:
            audio = audio_tensor.numpy()
            
            # 1. 计算信噪比
            snr = self._calculate_snr(audio)
            
            # 2. 计算过零率
            zcr = librosa.feature.zero_crossing_rate(audio)[0].mean()
            
            # 3. 计算频谱特征
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0].mean()
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0].mean()
            
            # 4. 计算MFCC特征
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            mfcc_std = np.std(mfcc, axis=1).mean()
            
            # 5. VAD活动度检测
            vad_activity = self._calculate_vad_activity(audio_tensor, sr)
            
            # 综合质量评分 (0-1)
            snr_score = min(snr / 20, 1.0)  # SNR评分，最高20dB给满分
            zcr_score = 1.0 - abs(zcr - 0.1)  # 过零率评分，语音通常在0.1左右
            vad_score = vad_activity  # VAD活动度评分
            mfcc_score = min(mfcc_std / 5.0, 1.0)  # MFCC标准差评分
            
            quality_score = (snr_score * 0.3 + zcr_score * 0.2 + 
                           vad_score * 0.3 + mfcc_score * 0.2)
            
            return float(quality_score)
            
        except Exception as e:
            logger.error(f"Audio quality assessment failed: {e}")
            return 0.5  # 默认中等质量
    
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """计算信噪比"""
        try:
            # 简单的信噪比计算方法
            signal_power = np.mean(audio ** 2)
            
            # 估计噪声功率（取信号幅度的最小值作为噪声估计）
            noise_power = np.min(audio ** 2) if len(audio) > 0 else 0
            
            if noise_power == 0:
                return 20.0  # 默认20dB
            
            snr_db = 10 * np.log10(signal_power / noise_power)
            return float(snr_db)
            
        except Exception as e:
            logger.error(f"SNR calculation failed: {e}")
            return 10.0  # 默认10dB
    
    def _calculate_vad_activity(self, audio_tensor: torch.Tensor, sr: int) -> float:
        """计算VAD活动度"""
        try:
            # 将音频转换为适合VAD的格式
            audio_bytes = (audio_tensor * 32767).short().numpy().tobytes()
            
            # 每帧10ms
            frame_duration = 10  # ms
            frame_size = int(sr * frame_duration / 1000)
            
            # 确保帧大小为30ms的倍数（WebRTC VAD要求）
            frame_size = (frame_size // 3) * 3
            
            active_frames = 0
            total_frames = 0
            
            for i in range(0, len(audio_bytes), frame_size * 2):  # 16-bit音频
                frame = audio_bytes[i:i + frame_size * 2]
                if len(frame) == frame_size * 2:
                    total_frames += 1
                    if self._vad.is_speech(frame, sample_rate=sr):
                        active_frames += 1
            
            if total_frames == 0:
                return 0.5
            
            return active_frames / total_frames
            
        except Exception as e:
            logger.error(f"VAD activity calculation failed: {e}")
            return 0.5
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """归一化嵌入向量"""
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """计算余弦相似度"""
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        return float(similarity)
    
    async def _upload_audio(self, audio_data: bytes, filename: str) -> str:
        """上传音频到MinIO"""
        try:
            import time
            timestamp = int(time.time())
            object_name = f"audio/{timestamp}_{filename}"
            
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
            logger.error(f"Failed to upload audio to MinIO: {e}")
            raise
    
    async def _save_voiceprint(self, employee_id: int, feature: VoiceprintFeature, audio_url: str) -> str:
        """保存声纹到数据库"""
        async with get_db() as db:
            voiceprint_model = VoiceprintModel(
                employee_id=employee_id,
                audio_sample_url=audio_url,
                feature_data=feature.embedding,
                feature_model=feature.model_name,
                sample_duration=feature.duration,
                sample_rate=feature.sample_rate,
                quality_score=feature.quality_score,
                embedding_version=feature.embedding_version or "v1.0"
            )
            
            db.add(voiceprint_model)
            await db.commit()
            await db.refresh(voiceprint_model)
            
            return voiceprint_model.voiceprint_id
    
    async def _get_active_voiceprints(self) -> List[VoiceprintModel]:
        """获取所有活跃的声纹"""
        async with get_db() as db:
            from sqlalchemy import select
            stmt = select(VoiceprintModel).where(VoiceprintModel.is_active == True)
            result = await db.execute(stmt)
            return result.scalars().all()
    
    async def _log_recognition(self, result: VoiceprintMatch, audio_data: bytes):
        """记录识别日志"""
        try:
            async with get_db() as db:
                from app.models.recognition_log import RecognitionLogModel
                
                log_model = RecognitionLogModel(
                    employee_id=result.employee_id,
                    audio_url=result.audio_url,
                    audio_duration=0,  # 需要计算
                    matched_voiceprint_id=result.voiceprint_id,
                    confidence_score=result.confidence,
                    threshold_used=result.threshold,
                    is_success=result.success,
                    processing_time=result.processing_time,
                    model_version=settings.VOICEPRINT_MODEL,
                    top_candidates=result.all_matches
                )
                
                db.add(log_model)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to log recognition: {e}")


# 创建全局服务实例
voiceprint_service = VoiceprintService()