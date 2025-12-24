#!/usr/bin/env python3
"""
测试模型可用性和基本功能
"""

import torch
import tempfile
import numpy as np
import soundfile as sf
import os
import sys
from loguru import logger
from app.core.config import settings

def create_test_audio():
    """创建测试音频文件"""
    # 生成简单的正弦波音频
    sample_rate = 16000
    duration = 3  # 3秒
    frequency = 440  # A4音符
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t) * 0.5  # 50%音量
    
    return audio, sample_rate

def test_speaker_recognition():
    """测试声纹识别模型"""
    print("测试声纹识别模型...")
    
    try:
        try:
            from speechbrain.inference.speaker import SpeakerRecognition
        except ImportError:
            from speechbrain.pretrained import SpeakerRecognition
        
        # 加载模型
        model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb"
        )
        
        # 创建测试音频
        audio, sr = create_test_audio()
        audio_tensor = torch.tensor(audio).unsqueeze(0).float()
        
        # 提取声纹特征
        with torch.no_grad():
            embedding = model.encode_batch(audio_tensor)
            
        print(f"✓ 声纹特征提取成功，特征维度: {embedding.shape}")
        return True
        
    except Exception as e:
        print(f"✗ 声纹识别模型测试失败: {e}")
        return False

def test_emotion_recognition():
    """测试情绪识别模型 - 使用 HuggingFace AutoFeatureExtractor + AutoModel"""
    print("测试情绪识别模型...")
    
    model_name = settings.EMOTION_MODEL
    
    print(f"  测试模型: {model_name}")
    try:
        from transformers import AutoFeatureExtractor, AutoModelForSequenceClassification
        import torch
        
        # 加载特征提取器和模型
        feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # 创建测试音频
        audio, sr = create_test_audio()
        
        # 预处理音频（使用 feature_extractor）
        inputs = feature_extractor(audio, sampling_rate=sr, return_tensors="pt", padding=True)
        
        # 推理
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            score, index = torch.max(probs, dim=-1)
            emotion_label = model.config.id2label[index.item()]
            confidence = score.item()
        
        print(f"  ✓ 情绪识别模型 {model_name} 加载成功")
        print(f"    预测情绪: {emotion_label}, 置信度: {confidence:.4f}")
        return True
        
    except Exception as e:
        print(f"  ✗ 模型 {model_name} 测试失败: {e}")
        return False

def test_audio_processing():
    """测试音频处理功能"""
    print("测试音频处理功能...")
    
    try:
        import librosa
        import soundfile as sf
        
        # 创建测试音频
        audio, sr = create_test_audio()
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sf.write(tmp_file.name, audio, sr)
            
            # 使用librosa加载
            y, sr_loaded = librosa.load(tmp_file.name, sr=16000)
            
            # 验证音频
            assert sr_loaded == 16000, "采样率不匹配"
            assert len(y) > 0, "音频数据为空"
            
            print(f"✓ 音频处理测试通过")
            print(f"  采样率: {sr_loaded}")
            print(f"  音频长度: {len(y)} 样本")
            
            # 清理临时文件
            os.unlink(tmp_file.name)
            return True
            
    except Exception as e:
        print(f"✗ 音频处理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("模型功能测试")
    print("=" * 50)
    
    # 检查PyTorch
    print(f"PyTorch版本: {torch.__version__}")
    print(f"CUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA设备: {torch.cuda.get_device_name()}")
    
    print("\n开始测试...")
    
    results = {}
    
    # 测试音频处理
    results['audio_processing'] = test_audio_processing()
    
    # 测试声纹识别
    results['speaker_recognition'] = test_speaker_recognition()
    
    # 测试情绪识别
    results['emotion_recognition'] = test_emotion_recognition()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结:")
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n总体结果: {success_count}/{total_count} 测试通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！系统可以正常运行。")
    else:
        print("⚠️  部分测试失败，系统功能可能受限。")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)