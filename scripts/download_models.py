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
        os.makedirs("pretrained_models/emotion_recognition_wav2vec2", exist_ok=True)
        
        print("下载声纹识别模型...")
        spk_model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb"
        )
        print("声纹识别模型下载完成")
        
        print("下载情绪识别模型...")
        # 使用配置文件中指定的情绪识别模型
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.core.config import settings
        emotion_model = settings.EMOTION_MODEL
        
        try:
            emo_model = EncoderClassifier.from_hparams(
                source=emotion_model,
                savedir="pretrained_models/emotion_recognition_wav2vec2"
            )
            print(f"情绪识别模型 {emotion_model} 下载完成")
        except Exception as e:
            print(f"情绪识别模型下载失败: {e}")
            print("系统将在首次运行时自动尝试下载模型")
            return False
        
        print("模型下载完成！")
        print("已下载模型:")
        print("  - 声纹识别: speechbrain/spkrec-ecapa-voxceleb")
        print(f"  - 情绪识别: {emotion_model}")
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