#!/usr/bin/env python3
"""
下载预训练模型脚本
"""

import os
import sys

def download_models():
    """下载声纹和情绪识别模型"""
    print("开始下载预训练模型...")
    
    try:
        # 导入SpeechBrain (使用新版inference模块)
        from speechbrain.inference.speaker import SpeakerRecognition
        from speechbrain.inference.classifiers import EncoderClassifier
        
        # 创建模型目录
        os.makedirs("pretrained_models/spkrec-ecapa-voxceleb", exist_ok=True)
        os.makedirs("pretrained_models/emotion-recognition-ecapa", exist_ok=True)
        
        print("下载声纹识别模型...")
        spk_model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb"
        )
        print("声纹识别模型下载完成")
        
        print("下载情绪识别模型...")
        # 尝试多个可用的情绪识别模型
        emotion_models = [
            "speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            "speechbrain/emotion-identification-IEMOCAP",
            "speechbrain/emotion-raw-wav2vec2-IEMOCAP"
        ]
        
        emotion_model_loaded = False
        for model_name in emotion_models:
            try:
                emo_model = EncoderClassifier.from_hparams(
                    source=model_name,
                    savedir=f"pretrained_models/{model_name.split('/')[-1]}"
                )
                print(f"情绪识别模型 {model_name} 下载完成")
                emotion_model_loaded = True
                break
            except Exception as e:
                print(f"模型 {model_name} 下载失败: {str(e)[:100]}")
                continue
        
        if not emotion_model_loaded:
            print("警告：所有情绪识别模型都下载失败，系统将跳过情绪识别功能")
            print("建议：系统将在首次运行时自动尝试下载模型")
        
        print("所有模型下载完成！")
        return True
        
    except ImportError as e:
        print(f"模块导入错误: {e}")
        print("请确保已安装SpeechBrain: pip install speechbrain")
        return False
        
    except Exception as e:
        print(f"模型下载失败: {e}")
        print("系统将在首次运行时自动下载模型")
        return False

if __name__ == "__main__":
    success = download_models()
    sys.exit(0 if success else 1)