#!/usr/bin/env python3
"""
验证模型配置一致性脚本
检查所有相关文件中的模型名称是否与配置文件一致
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def check_config_consistency():
    """检查配置一致性"""
    print("=" * 60)
    print("模型配置一致性检查")
    print("=" * 60)
    
    config_model = settings.EMOTION_MODEL
    print(f"配置文件中的情绪识别模型: {config_model}")
    print()
    
    # 检查各个文件
    files_to_check = [
        ("app/core/config.py", "EMOTION_MODEL"),
        ("app/services/emotion_service.py", "settings.EMOTION_MODEL"),
        ("scripts/test_emotion_only.py", "settings.EMOTION_MODEL"),
        ("scripts/download_emotion_only.py", "settings.EMOTION_MODEL"),
        ("scripts/download_models.py", "settings.EMOTION_MODEL"),
    ]
    
    all_consistent = True
    
    for filepath, expected_usage in files_to_check:
        if os.path.exists(filepath):
            print(f"检查文件: {filepath}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if expected_usage in content and config_model in content:
                        print(f"  ✓ 使用配置文件设置")
                    elif "settings.EMOTION_MODEL" in content:
                        print(f"  ✓ 正确使用settings.EMOTION_MODEL")
                    elif config_model in content:
                        print(f"  ⚠ 硬编码模型名称，建议改为settings.EMOTION_MODEL")
                        all_consistent = False
                    else:
                        print(f"  - 未找到模型相关代码")
            except Exception as e:
                print(f"  ✗ 读取失败: {e}")
                all_consistent = False
        else:
            print(f"  - 文件不存在: {filepath}")
        print()
    
    print("=" * 60)
    if all_consistent:
        print("✓ 所有配置检查通过！")
        print("  所有文件都正确使用配置文件中的模型设置")
    else:
        print("⚠ 发现配置不一致！")
        print("  建议修改硬编码的模型名称为 settings.EMOTION_MODEL")
    
    print("=" * 60)
    
    # 显示当前配置
    print("当前配置:")
    print(f"  情绪识别模型: {config_model}")
    print(f"  模型保存目录: pretrained_models/emotion_recognition_{config_model.split('/')[-1]}")
    print()
    
    return all_consistent

if __name__ == "__main__":
    success = check_config_consistency()
    sys.exit(0 if success else 1)