#!/usr/bin/env python3
"""
测试文件上传功能
"""

import requests
import sys
import os

def test_upload(audio_file_path):
    """测试文件上传"""
    
    # 检查文件是否存在
    if not os.path.exists(audio_file_path):
        print(f"❌ 文件不存在: {audio_file_path}")
        return False
    
    file_size = os.path.getsize(audio_file_path)
    print(f"📁 测试文件: {audio_file_path}")
    print(f"📊 文件大小: {file_size} bytes")
    
    # 测试调试端点
    print("\n🔍 测试调试端点...")
    try:
        url = "http://127.0.0.1:8000/debug/upload"
        files = {"audio_file": open(audio_file_path, "rb")}
        
        response = requests.post(url, files=files)
        files["audio_file"].close()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 调试端点测试成功")
            print(f"响应: {result}")
            return True
        else:
            print(f"❌ 调试端点失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 调试端点异常: {e}")
        return False

def test_emotion_endpoint(audio_file_path):
    """测试情绪识别端点"""
    print("\n🎭 测试情绪识别端点...")
    
    try:
        url = "http://127.0.0.1:8000/test/emotion"
        files = {"audio_file": open(audio_file_path, "rb")}
        
        response = requests.post(url, files=files)
        files["audio_file"].close()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 情绪识别端点测试成功")
            print(f"响应: {result}")
            return True
        else:
            print(f"❌ 情绪识别端点失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 情绪识别端点异常: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python test_upload.py <音频文件路径>")
        print("示例: python test_upload.py /home/hnkz/201.wav")
        return
    
    audio_file_path = sys.argv[1]
    
    print("🎯 文件上传测试工具")
    print("-" * 50)
    
    # 先测试调试端点
    debug_success = test_upload(audio_file_path)
    
    if debug_success:
        # 再测试情绪识别端点
        emotion_success = test_emotion_endpoint(audio_file_path)
        
        if emotion_success:
            print("\n✅ 所有测试通过!")
        else:
            print("\n⚠️  情绪识别端点有问题，但文件上传正常")
    else:
        print("\n❌ 文件上传存在问题")

if __name__ == "__main__":
    main()