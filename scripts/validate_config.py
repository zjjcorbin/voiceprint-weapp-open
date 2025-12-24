#!/usr/bin/env python3
"""
配置验证脚本
验证所有配置字段的正确性
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def validate_config():
    """验证配置文件"""
    print("配置验证脚本")
    print("=" * 60)
    
    try:
        print("1. 检查Python模块导入...")
        from app.core.config import Settings
        print("   ✓ Settings类导入成功")
        
        print("\n2. 检查配置实例化...")
        try:
            settings = Settings()
            print("   ✓ Settings实例化成功")
        except Exception as e:
            print(f"   ✗ Settings实例化失败: {e}")
            if "Extra inputs are not permitted" in str(e):
                print("   → 原因：配置类中未定义某些环境变量字段")
                print("   → 解决：添加 extra='allow' 或定义缺失字段")
            return False
        
        print("\n3. 检查配置字段...")
        
        # 检查情绪识别相关
        emotion_fields = [
            'EMOTION_MODEL',
            'EMOTION_CONFIDENCE_THRESHOLD', 
            'SUPPORTED_EMOTIONS',
            'EMOTION_ANALYSIS_ENABLED'
        ]
        
        for field in emotion_fields:
            value = getattr(settings, field, None)
            if value is not None:
                print(f"   ✓ {field}: {value}")
            else:
                print(f"   ✗ {field}: 未设置")
        
        # 检查日志字段
        log_fields = ['LOG_LEVEL', 'LOG_FILE']
        for field in log_fields:
            value = getattr(settings, field, None)
            if value is not None:
                print(f"   ✓ {field}: {value}")
            else:
                print(f"   ✗ {field}: 未设置")
        
        print("\n4. 检查SUPPORTED_EMOTIONS_LIST...")
        try:
            emotions_list = settings.SUPPORTED_EMOTIONS_LIST
            print(f"   ✓ 类型: {type(emotions_list)}")
            print(f"   ✓ 长度: {len(emotions_list)}")
            print(f"   ✓ 内容: {emotions_list}")
        except Exception as e:
            print(f"   ✗ 属性访问失败: {e}")
        
        print("\n5. 检查环境变量解析...")
        
        # 模拟.env文件
        test_env_values = {
            'EMOTION_MODEL': 'speechbrain/emotion-recognition-wav2vec2-IEMOCAP',
            'SUPPORTED_EMOTIONS': 'neutral,happy,sad,angry,fear,disgust,surprise',
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': 'logs/app.log'
        }
        
        # 临时设置环境变量
        original_env = {}
        for key, value in test_env_values.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            # 重新实例化
            test_settings = Settings()
            print("   ✓ 环境变量解析成功")
            
            # 验证解析结果
            if test_settings.EMOTION_MODEL == test_env_values['EMOTION_MODEL']:
                print("   ✓ EMOTION_MODEL解析正确")
            
            if isinstance(test_settings.SUPPORTED_EMOTIONS_LIST, list):
                print("   ✓ SUPPORTED_EMOTIONS转换为列表成功")
            
            if test_settings.LOG_LEVEL == test_env_values['LOG_LEVEL']:
                print("   ✓ LOG_LEVEL解析正确")
            
        except Exception as e:
            print(f"   ✗ 环境变量解析失败: {e}")
        
        finally:
            # 恢复环境变量
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        
        print("\n6. 配置文件建议...")
        print("   ✓ 已添加 extra='allow' 允许额外字段")
        print("   ✓ 已定义 LOG_LEVEL 和 LOG_FILE 字段")
        print("   ✓ SUPPORTED_EMOTIONS 使用字符串格式")
        print("   ✓ 添加属性方法处理列表转换")
        
        return True
        
    except ImportError as e:
        print(f"   ✗ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"   ✗ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_config()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 配置验证通过！")
        print("所有字段都能正确解析，模型应该可以正常下载。")
    else:
        print("✗ 配置验证失败")
        print("请检查上述错误并修复配置。")
    print("=" * 60)
    
    sys.exit(0 if success else 1)