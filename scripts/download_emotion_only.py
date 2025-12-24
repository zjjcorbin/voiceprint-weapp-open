#!/usr/bin/env python3
"""
精简模型下载脚本 - 只下载指定的情绪识别模型
"""

import os
import sys

def download_emotion_model_only():
    """只下载emotion-recognition-wav2vec2-IEMOCAP模型"""
    print("开始下载情绪识别模型...")
    print("=" * 50)
    
    model_name = "speechbrain/emotion-recognition-wav2vec2-IEMOCAP"
    save_dir = "emotion_recognition_wav2vec2"
    
    try:
        # 导入SpeechBrain
        try:
            from speechbrain.inference.classifiers import EncoderClassifier
        except ImportError:
            from speechbrain.pretrained import EncoderClassifier
        
        # 创建模型目录
        os.makedirs(f"pretrained_models/{save_dir}", exist_ok=True)
        
        print(f"正在下载模型: {model_name}")
        print(f"保存目录: pretrained_models/{save_dir}")
        
        # 下载模型
        model = EncoderClassifier.from_hparams(
            source=model_name,
            savedir=f"pretrained_models/{save_dir}"
        )
        
        print("=" * 50)
        print("✓ 情绪识别模型下载成功！")
        print(f"模型: {model_name}")
        print(f"目录: pretrained_models/{save_dir}")
        print("=" * 50)
        
        return True
        
    except ImportError as e:
        print(f"模块导入错误: {e}")
        print("请确保已安装SpeechBrain: pip install speechbrain")
        return False
        
    except Exception as e:
        print(f"模型下载失败: {e}")
        print("请检查网络连接或磁盘空间")
        return False

def main():
    """主函数"""
    print("精简模型下载脚本")
    print("只下载: emotion-recognition-wav2vec2-IEMOCAP")
    
    success = download_emotion_model_only()
    
    if success:
        print("\n下一步:")
        print("1. 运行测试脚本: python scripts/test_emotion_only.py")
        print("2. 启动应用: docker-compose up -d")
    else:
        print("\n请检查错误信息并重试")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)