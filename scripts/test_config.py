#!/usr/bin/env python3
"""
测试配置文件解析
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_parsing():
    """测试配置文件解析"""
    print("测试配置文件解析...")
    print("=" * 50)
    
    try:
        from app.core.config import settings
        print("✓ 配置文件解析成功")
        print()
        
        print("情绪识别相关配置:")
        print(f"  EMOTION_MODEL: {settings.EMOTION_MODEL}")
        print(f"  EMOTION_CONFIDENCE_THRESHOLD: {settings.EMOTION_CONFIDENCE_THRESHOLD}")
        print(f"  SUPPORTED_EMOTIONS: {settings.SUPPORTED_EMOTIONS}")
        print(f"  SUPPORTED_EMOTIONS_LIST: {settings.SUPPORTED_EMOTIONS_LIST}")
        print(f"  EMOTION_ANALYSIS_ENABLED: {settings.EMOTION_ANALYSIS_ENABLED}")
        print()
        
        print("SUPPORTED_EMOTIONS_LIST类型检查:")
        print(f"  类型: {type(settings.SUPPORTED_EMOTIONS_LIST)}")
        print(f"  长度: {len(settings.SUPPORTED_EMOTIONS_LIST)}")
        print(f"  元素: {settings.SUPPORTED_EMOTIONS_LIST}")
        print()
        
        # 测试列表操作
        if "happy" in settings.SUPPORTED_EMOTIONS_LIST:
            print("✓ 列表操作测试通过")
        else:
            print("✗ 列表操作测试失败")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置文件解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_env_parsing():
    """测试环境变量解析"""
    print("测试环境变量解析...")
    print("=" * 50)
    
    # 模拟环境变量
    test_env = {
        "EMOTION_MODEL": "speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
        "SUPPORTED_EMOTIONS": "neutral,happy,sad,angry,fear,disgust,surprise",
        "EMOTION_CONFIDENCE_THRESHOLD": "0.6"
    }
    
    # 临时设置环境变量
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        # 重新导入配置
        import importlib
        if 'app.core.config' in sys.modules:
            importlib.reload(sys.modules['app.core.config'])
        
        from app.core.config import Settings
        test_settings = Settings()
        
        print("✓ 环境变量解析成功")
        print(f"  EMOTION_MODEL: {test_settings.EMOTION_MODEL}")
        print(f"  SUPPORTED_EMOTIONS: {test_settings.SUPPORTED_EMOTIONS}")
        print(f"  SUPPORTED_EMOTIONS_LIST: {test_settings.SUPPORTED_EMOTIONS_LIST}")
        print(f"  类型: {type(test_settings.SUPPORTED_EMOTIONS_LIST)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 环境变量解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

if __name__ == "__main__":
    print("配置解析测试")
    print("=" * 60)
    
    success1 = test_config_parsing()
    print()
    success2 = test_env_parsing()
    
    print("=" * 60)
    if success1 and success2:
        print("✓ 所有配置测试通过")
    else:
        print("✗ 配置测试失败")
    print("=" * 60)
    
    sys.exit(0 if (success1 and success2) else 1)