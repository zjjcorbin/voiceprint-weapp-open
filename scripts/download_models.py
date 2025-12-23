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
        # 尝试导入SpeechBrain
        from speechbrain.inference.speaker import SpeakerRecognition
        from speechbrain.inference.classifiers import EncoderClassifier
        
        # 创建模型目录
        os.makedirs("pretrained_models/spkrec-ecapa-voxceleb", exist_ok=True)
        os.makedirs("pretrained_models/emotion-recognition-wav2vec2-IEMOCAP", exist_ok=True)
        
        print("下载声纹识别模型...")
        spk_model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb"
        )
        print("声纹识别模型下载完成")
        
        print("下载情绪识别模型...")
        emo_model = EncoderClassifier.from_hparams(
            source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            savedir="pretrained_models/emotion-recognition-wav2vec2-IEMOCAP"
        )
        print("情绪识别模型下载完成")
        
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