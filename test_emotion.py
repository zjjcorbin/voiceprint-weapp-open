#!/usr/bin/env python3
"""
情绪识别测试脚本
用于测试 /test/emotion 端点
"""

import requests
import sys
import os

def test_emotion_detection(audio_file_path):
    """测试情绪识别功能"""
    
    # 检查文件是否存在
    if not os.path.exists(audio_file_path):
        print(f"错误: 文件 '{audio_file_path}' 不存在")
        return False
    
    # 检查文件大小
    file_size = os.path.getsize(audio_file_path)
    if file_size > 50 * 1024 * 1024:
        print("错误: 文件过大，请上传小于50MB的文件")
        return False
    
    try:
        # 发送请求
        url = "http://localhost:8000/test/emotion"
        files = {"audio_file": open(audio_file_path, "rb")}
        
        print(f"正在测试情绪识别...")
        print(f"文件: {audio_file_path}")
        print(f"大小: {file_size / 1024:.2f} KB")
        print("-" * 50)
        
        response = requests.post(url, files=files)
        files["audio_file"].close()
        
        # 处理响应
        if response.status_code == 200:
            result = response.json()
            
            if result["success"]:
                print("✅ 情绪检测成功!")
                print(f"📄 文件名: {result['filename']}")
                print(f"⏱️  处理时间: {result['processing_time']}秒")
                print()
                
                emotion_data = result["result"]
                print("🎭 检测结果:")
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
                print("❌ 情绪检测失败")
                print(f"错误信息: {result['message']}")
                print(f"错误代码: {result.get('error_code', 'N/A')}")
                return False
                
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务正在运行")
        print("   运行命令: python -m app.main")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python test_emotion.py <音频文件路径>")
        print("示例: python test_emotion.py test_audio.wav")
        print("\n支持的音频格式: WAV, MP3, M4A, OGG")
        return
    
    audio_file_path = sys.argv[1]
    test_emotion_detection(audio_file_path)

if __name__ == "__main__":
    main()