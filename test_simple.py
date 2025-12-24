#!/usr/bin/env python3
"""
测试简单情绪识别端点
"""

import requests
import sys
import os

def test_simple_emotion(audio_file_path):
    """测试简单情绪识别端点"""
    
    # 检查文件是否存在
    if not os.path.exists(audio_file_path):
        print(f"❌ 文件不存在: {audio_file_path}")
        return False
    
    file_size = os.path.getsize(audio_file_path)
    print(f"📁 测试文件: {audio_file_path}")
    print(f"📊 文件大小: {file_size} bytes")
    
    # 测试简单端点
    print("\n🎭 测试简单情绪识别端点...")
    try:
        url = "http://127.0.0.1:8000/simple/emotion"
        files = {"audio_file": open(audio_file_path, "rb")}
        
        response = requests.post(url, files=files)
        files["audio_file"].close()
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ 简单情绪识别成功!")
                print(f"📄 文件名: {result['filename']}")
                print(f"⏱️  处理时间: {result['processing_time']}秒")
                
                emotion_data = result["result"]
                print("\n🎭 检测结果:")
                print(f"   主要情绪: {emotion_data['dominant_emotion']}")
                print(f"   置信度: {emotion_data['confidence']:.3f}")
                print(f"   强度: {emotion_data['intensity']:.3f}")
                print(f"   复杂度: {emotion_data['complexity']:.3f}")
                print(f"   质量评分: {emotion_data['quality_score']:.3f}")
                print(f"   音频时长: {emotion_data['audio_duration']:.2f}秒")
                
                if emotion_data.get('emotion_probabilities'):
                    print("\n📊 情绪概率分布:")
                    for emotion, prob in emotion_data['emotion_probabilities'].items():
                        print(f"   {emotion}: {prob:.3f}")
                
                if emotion_data.get('analysis'):
                    print(f"\n📝 分析: {emotion_data['analysis']}")
                
                return True
            else:
                print("❌ 简单情绪识别失败")
                print(f"错误信息: {result['message']}")
                print(f"错误代码: {result.get('error_code', 'N/A')}")
                return False
                
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 简单端点异常: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python test_simple.py <音频文件路径>")
        print("示例: python test_simple.py /home/hnkz/201.wav")
        return
    
    audio_file_path = sys.argv[1]
    
    print("🎯 简单情绪识别测试")
    print("-" * 50)
    
    success = test_simple_emotion(audio_file_path)
    
    if success:
        print("\n✅ 测试完成!")
    else:
        print("\n❌ 测试失败!")

if __name__ == "__main__":
    main()