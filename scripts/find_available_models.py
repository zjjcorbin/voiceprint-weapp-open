#!/usr/bin/env python3
"""
查找可用的SpeechBrain模型
"""

import sys
import os

def test_model_availability():
    """测试模型可用性"""
    
    # 常用的声纹识别模型
    speaker_models = [
        "speechbrain/spkrec-ecapa-voxceleb",
        "speechbrain/spkrec-resnet-voxceleb",
        "speechbrain/spkrec-xvector-voxceleb"
    ]
    
    # 常用的情绪识别模型
    emotion_models = [
        "speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
        "speechbrain/emotion-recognition-dair-emo",
        "speechbrain/emotion-identification-IEMOCAP",
        "speechbrain/emotion-raw-wav2vec2-IEMOCAP"
    ]
    
    try:
        try:
            from speechbrain.inference.speaker import SpeakerRecognition
            from speechbrain.inference.classifiers import EncoderClassifier
        except ImportError:
            from speechbrain.pretrained import SpeakerRecognition
            from speechbrain.pretrained import EncoderClassifier
        
        print("测试声纹识别模型...")
        for model in speaker_models:
            try:
                test_model = SpeakerRecognition.from_hparams(
                    source=model,
                    savedir=f"test_{model.split('/')[-1]}",
                    run_opts={"device": "cpu"}
                )
                print(f"✓ {model}")
            except Exception as e:
                print(f"✗ {model} - {str(e)[:100]}...")
        
        print("\n测试情绪识别模型...")
        for model in emotion_models:
            try:
                test_model = EncoderClassifier.from_hparams(
                    source=model,
                    savedir=f"test_{model.split('/')[-1]}",
                    run_opts={"device": "cpu"}
                )
                print(f"✓ {model}")
            except Exception as e:
                print(f"✗ {model} - {str(e)[:100]}...")
                
    except ImportError as e:
        print(f"SpeechBrain导入失败: {e}")

if __name__ == "__main__":
    test_model_availability()