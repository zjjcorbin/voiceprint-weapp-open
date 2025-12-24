#!/usr/bin/env python3
"""
创建测试音频文件
用于情绪识别测试
"""

import wave
import numpy as np
import struct
import os

def create_sine_wave(filename, frequency=440, duration=3, sample_rate=44100):
    """
    创建正弦波音频文件
    
    Args:
        filename: 输出文件名
        frequency: 频率 (Hz)
        duration: 时长 (秒)
        sample_rate: 采样率
    """
    # 生成音频数据
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # 转换为16位PCM格式
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # 创建WAV文件
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16位
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"✅ 已创建测试音频文件: {filename}")
    print(f"   频率: {frequency} Hz")
    print(f"   时长: {duration} 秒")
    print(f"   采样率: {sample_rate} Hz")
    print(f"   文件大小: {os.path.getsize(filename) / 1024:.2f} KB")

def main():
    """主函数"""
    # 创建不同情绪的测试音频
    test_files = [
        ("happy_audio.wav", 523.25),  # C5 - 高兴的声音
        ("sad_audio.wav", 261.63),    # C4 - 悲伤的声音  
        ("angry_audio.wav", 783.99),  # G5 - 愤怒的声音
        ("neutral_audio.wav", 440.00) # A4 - 中性的声音
    ]
    
    print("🎵 创建测试音频文件...")
    print("-" * 50)
    
    for filename, frequency in test_files:
        create_sine_wave(filename, frequency)
    
    print("-" * 50)
    print("\n📋 使用说明:")
    print("1. 启动服务: python -m app.main")
    print("2. 测试情绪识别: python test_emotion.py happy_audio.wav")
    print("3. 或使用curl命令测试")
    print("\n💡 提示: 您也可以使用自己的音频文件进行测试")

if __name__ == "__main__":
    main()