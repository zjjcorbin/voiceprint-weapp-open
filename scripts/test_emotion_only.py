#!/usr/bin/env python3
"""
精简模型测试脚本 - 只测试指定的情绪识别模型
"""

import torch
import tempfile
import numpy as np
import soundfile as sf
import os
import sys
from loguru import logger

def create_test_audio():
    """创建测试音频文件"""
    # 生成简单的正弦波音频
    sample_rate = 16000
    duration = 3  # 3秒
    frequency = 440  # A4音符
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t) * 0.5  # 50%音量
    
    return audio, sample_rate

def test_emotion_recognition_only():
    """只测试emotion-recognition-wav2vec2-IEMOCAP模型"""
    print("测试情绪识别模型...")
    
    model_name = "speechbrain/emotion-recognition-wav2vec2-IEMOCAP"
    save_dir = "emotion_recognition_wav2vec2"
    
    try:
        try:
            from speechbrain.inference.classifiers import EncoderClassifier
        except ImportError:
            from speechbrain.pretrained import EncoderClassifier
        
        print(f"正在加载模型: {model_name}")
        
        # 加载模型
        model = EncoderClassifier.from_hparams(
            source=model_name,
            savedir=f"pretrained_models/{save_dir}",
            run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
        )
        
        # 创建测试音频
        audio, sr = create_test_audio()
        audio_tensor = torch.tensor(audio).unsqueeze(0).float()
        
        print("正在进行情绪识别测试...")
        
        # 情绪识别
        with torch.no_grad():
            prediction = model.classify_batch(audio_tensor)
            
            # 获取概率分布
            if hasattr(prediction, 'logits'):
                probs = torch.softmax(prediction.logits, dim=-1)
            elif isinstance(prediction, tuple):
                probs = torch.softmax(prediction[0], dim=-1)
            else:
                probs = torch.softmax(prediction, dim=-1)
            
            # 转换为numpy
            probs = probs.cpu().numpy()[0]
            
            # 情绪标签
            emotion_labels = ["neutral", "happy", "sad", "angry", "fear", "disgust", "surprise"]
            
            print(f"✓ 模型 {model_name} 测试成功")
            print(f"  预测概率分布:")
            for i, (label, prob) in enumerate(zip(emotion_labels, probs)):
                print(f"    {label}: {prob:.4f}")
            
            # 主导情绪
            dominant_idx = np.argmax(probs)
            dominant_emotion = emotion_labels[dominant_idx]
            confidence = probs[dominant_idx]
            
            print(f"  主导情绪: {dominant_emotion} (置信度: {confidence:.4f})")
            
        return True
        
    except Exception as e:
        print(f"✗ 模型 {model_name} 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("精简情绪识别模型测试")
    print("只测试: emotion-recognition-wav2vec2-IEMOCAP")
    print("=" * 50)
    
    success = test_emotion_recognition_only()
    
    print("=" * 50)
    if success:
        print("✓ 模型测试通过")
        print("系统可以正常进行情绪识别")
    else:
        print("✗ 模型测试失败")
        print("请检查网络连接或模型下载")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)