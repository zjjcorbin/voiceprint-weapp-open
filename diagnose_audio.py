#!/usr/bin/env python3
"""
诊断音频处理问题
"""

import asyncio
import sys
import os

def diagnose_audio_processing(audio_file_path):
    """诊断音频处理问题"""
    print("🔍 诊断音频处理问题...")
    
    # 检查文件
    if not os.path.exists(audio_file_path):
        print(f"❌ 文件不存在: {audio_file_path}")
        return False
    
    file_size = os.path.getsize(audio_file_path)
    print(f"📁 文件: {audio_file_path}")
    print(f"📊 大小: {file_size} bytes")
    
    try:
        # 读取文件内容
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
        
        print(f"✅ 文件读取成功: {len(audio_data)} bytes")
        
        # 测试librosa加载
        print("\n🎵 测试librosa加载...")
        import librosa
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            audio, sr = librosa.load(temp_path, sr=16000, mono=True)
            print(f"✅ Librosa加载成功")
            print(f"   采样率: {sr} Hz")
            print(f"   时长: {len(audio)/sr:.2f} 秒")
            print(f"   样本数: {len(audio)}")
            print(f"   最大值: {audio.max():.3f}")
            print(f"   最小值: {audio.min():.3f}")
            print(f"   平均值: {audio.mean():.3f}")
            
            # 检查音频质量
            if len(audio) < sr:
                print("⚠️  音频过短（小于1秒），可能影响识别效果")
            
            if abs(audio.max()) < 0.01:
                print("⚠️  音频信号过弱，可能无法识别")
                
        except Exception as e:
            print(f"❌ Librosa加载失败: {e}")
            
            # 尝试soundfile
            print("\n🔊 尝试soundfile加载...")
            import soundfile as sf
            
            try:
                audio, sr = sf.read(temp_path)
                print(f"✅ Soundfile加载成功")
                print(f"   采样率: {sr} Hz")
                print(f"   时长: {len(audio)/sr:.2f} 秒")
                print(f"   形状: {audio.shape}")
                
                # 如果是立体声，转换为单声道
                if len(audio.shape) > 1:
                    audio_mono = audio.mean(axis=1)
                    print(f"   单声道时长: {len(audio_mono)/sr:.2f} 秒")
                    
            except Exception as e2:
                print(f"❌ Soundfile加载失败: {e2}")
        
        finally:
            os.unlink(temp_path)
        
        # 测试情绪识别服务
        print("\n🤖 测试情绪识别服务...")
        from app.services.emotion_service import EmotionService
        service = EmotionService()
        
        # 检查模型状态
        status = asyncio.run(service.check_model_status())
        print(f"模型状态: {'已加载' if status else '未加载'}")
        
        if status:
            print("🔍 进行情绪识别测试...")
            try:
                result = asyncio.run(service.detect_emotion(audio_data))
                print("✅ 情绪识别成功!")
                print(f"主要情绪: {result.dominant_emotion}")
                print(f"置信度: {result.confidence:.3f}")
                return True
                
            except Exception as e:
                print(f"❌ 情绪识别失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("❌ 模型未加载，无法测试")
            return False
        
    except Exception as e:
        print(f"❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python diagnose_audio.py <音频文件路径>")
        print("示例: python diagnose_audio.py /home/hnkz/201.wav")
        return
    
    audio_file_path = sys.argv[1]
    
    print("🎯 音频处理诊断工具")
    print("-" * 50)
    
    success = diagnose_audio_processing(audio_file_path)
    
    if success:
        print("\n✅ 诊断完成!")
    else:
        print("\n❌ 诊断发现问题!")

if __name__ == "__main__":
    main()