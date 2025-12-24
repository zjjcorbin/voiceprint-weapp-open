#!/usr/bin/env python3
"""检查模型状态脚本"""

import os
import sys
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def check_models():
    """检查所有模型的状态"""
    print("检查模型状态...")
    print("=" * 50)
    
    try:
        # 导入服务
        from app.services.voiceprint_service import VoiceprintService
        from app.services.emotion_service import EmotionService
        
        # 检查声纹模型
        voiceprint_service = VoiceprintService()
        vp_status = await voiceprint_service.check_model_status()
        print(f"声纹识别模型: {'✓ 已加载' if vp_status else '✗ 未加载'}")
        
        # 检查情绪识别模型
        emotion_service = EmotionService()
        emo_status = await emotion_service.check_model_status()
        print(f"情绪识别模型: {'✓ 已加载' if emo_status else '✗ 未加载'}")
        
        print("=" * 50)
        
        if not vp_status or not emo_status:
            print("\n解决方案:")
            print("1. 运行模型下载脚本:")
            print("   python scripts/download_models.py")
            print("   # 或者单独下载:")
            print("   python scripts/download_emotion_only.py")
            print("\n2. 确保已安装 SpeechBrain:")
            print("   pip install speechbrain")
            print("\n3. 检查网络连接和磁盘空间")
        else:
            print("所有模型已成功加载！")
            
    except Exception as e:
        print(f"检查模型状态时出错: {e}")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(check_models())