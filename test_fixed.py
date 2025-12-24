#!/usr/bin/env python3
"""
测试修复后的情绪识别服务
"""

import asyncio
import sys
import os

def test_emotion_service():
    """测试情绪识别服务"""
    print("🧪 测试修复后的情绪识别服务...")
    
    try:
        # 导入服务
        from app.services.emotion_service import EmotionService
        service = EmotionService()
        
        # 检查模型状态
        status = asyncio.run(service.check_model_status())
        
        if not status:
            print("❌ 情绪识别模型未加载")
            print("💡 请运行: python scripts/download_models.py")
            return False
        
        print("✅ 情绪识别模型已加载")
        
        # 创建测试音频数据（简单的正弦波）
        import numpy as np
        sample_rate = 16000
        duration = 3  # 3秒
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio_data = np.sin(2 * np.pi * 440 * t)  # 440Hz正弦波
        
        # 转换为WAV格式
        import io
        import wave
        
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            # 转换为16位PCM
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
        
        wav_data = wav_buffer.getvalue()
        
        print("🎵 生成测试音频完成")
        print(f"📊 音频大小: {len(wav_data)} bytes")
        
        # 测试情绪识别
        print("🔍 进行情绪识别...")
        result = asyncio.run(service.detect_emotion(wav_data))
        
        print("✅ 情绪识别成功!")
        print(f"🎭 主要情绪: {result.dominant_emotion}")
        print(f"📈 置信度: {result.confidence:.3f}")
        print(f"💪 强度: {result.intensity:.3f}")
        print(f"🌀 复杂度: {result.complexity:.3f}")
        print(f"⭐ 质量评分: {result.quality_score:.3f}")
        
        print("\n📊 情绪概率分布:")
        for emotion, prob in result.emotion_probabilities.items():
            print(f"   {emotion}: {prob:.3f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("💡 请检查依赖包是否正确安装")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🎯 修复后情绪识别服务测试")
    print("-" * 50)
    
    success = test_emotion_service()
    
    if success:
        print("\n✅ 测试完成!")
        print("💡 现在可以重新测试文件上传功能")
    else:
        print("\n❌ 测试失败!")
        print("💡 建议检查:")
        print("   1. 依赖包是否正确安装")
        print("   2. 模型文件是否下载")
        print("   3. 查看详细错误信息")

if __name__ == "__main__":
    main()