#!/usr/bin/env python3
"""简单模型状态测试 - 不依赖VAD等模块"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """测试关键模块导入"""
    print("测试关键模块导入...")
    print("=" * 50)
    
    try:
        # 测试基础导入
        from app.core.config import settings
        print("[OK] 配置模块导入成功")
        print(f"  EMOTION_MODEL: {settings.EMOTION_MODEL}")
        print(f"  VOICEPRINT_MODEL: {settings.VOICEPRINT_MODEL}")
        
        # 测试SpeechBrain导入
        try:
            import speechbrain
            print(f"[OK] SpeechBrain导入成功 - 版本: {getattr(speechbrain, '__version__', 'unknown')}")
            
            # 尝试不同的导入路径
            try:
                from speechbrain.inference.classifiers import EncoderClassifier
                from speechbrain.inference.speaker import SpeakerRecognition
                print("[OK] 新版SpeechBrain模块导入成功")
            except ImportError:
                try:
                    from speechbrain.pretrained import EncoderClassifier
                    from speechbrain.pretrained import SpeakerRecognition
                    print("[OK] 旧版SpeechBrain模块导入成功")
                except ImportError as e:
                    print(f"[FAIL] SpeechBrain子模块导入失败: {e}")
                    return False
        except ImportError as e:
            print(f"[FAIL] SpeechBrain模块导入失败: {e}")
            print("  请运行: pip install speechbrain")
            return False
        
        # 测试torch导入
        try:
            import torch
            print(f"[OK] PyTorch导入成功 - 版本: {torch.__version__}")
        except ImportError as e:
            print(f"[FAIL] PyTorch导入失败: {e}")
            return False
        
        # 测试模型是否存在（不实际加载）
        model_dirs = [
            f"pretrained_models/{settings.VOICEPRINT_MODEL.split('/')[-1]}",
            f"pretrained_models/emotion_recognition_{settings.EMOTION_MODEL.split('/')[-1]}"
        ]
        
        print("\n检查模型目录:")
        for model_dir in model_dirs:
            if os.path.exists(model_dir):
                print(f"[OK] {model_dir} 存在")
            else:
                print(f"[FAIL] {model_dir} 不存在")
        
        print("=" * 50)
        print("基础模块导入测试完成")
        return True
        
    except Exception as e:
        print(f"导入测试失败: {e}")
        return False


if __name__ == "__main__":
    success = test_imports()
    
    if not success:
        print("\n解决方案:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 下载模型: python scripts/download_models.py")
        print("3. 检查Python环境和网络连接")
    
    sys.exit(0 if success else 1)