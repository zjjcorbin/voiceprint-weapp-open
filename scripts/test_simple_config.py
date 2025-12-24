#!/usr/bin/env python3
"""
测试简化配置
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simple_config():
    """测试简化配置"""
    print("测试简化配置")
    print("=" * 50)
    
    try:
        from app.core.config_simple import simple_settings
        print("✓ 简化配置导入成功")
        print()
        
        print("情绪识别配置:")
        print(f"  EMOTION_MODEL: {simple_settings.EMOTION_MODEL}")
        print(f"  SUPPORTED_EMOTIONS: {simple_settings.SUPPORTED_EMOTIONS}")
        print(f"  SUPPORTED_EMOTIONS_LIST: {simple_settings.SUPPORTED_EMOTIONS_LIST}")
        print(f"  EMOTION_ANALYSIS_ENABLED: {simple_settings.EMOTION_ANALYSIS_ENABLED}")
        print()
        
        print("日志配置:")
        print(f"  LOG_LEVEL: {simple_settings.LOG_LEVEL}")
        print(f"  LOG_FILE: {simple_settings.LOG_FILE}")
        print()
        
        print("列表操作测试:")
        emotions_list = simple_settings.SUPPORTED_EMOTIONS_LIST
        print(f"  类型: {type(emotions_list)}")
        print(f"  长度: {len(emotions_list)}")
        print(f"  包含'happy': {'happy' in emotions_list}")
        print(f"  包含'sad': {'sad' in emotions_list}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_config()
    print("=" * 50)
    if success:
        print("✓ 简化配置测试通过")
        print("可以尝试使用简化配置运行应用")
    else:
        print("✗ 简化配置测试失败")
    print("=" * 50)
    
    sys.exit(0 if success else 1)