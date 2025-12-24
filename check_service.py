#!/usr/bin/env python3
"""
检查服务状态脚本
"""

import requests
import sys

def check_service():
    """检查服务状态"""
    
    urls_to_check = [
        ("http://127.0.0.1:8000/health", "健康检查"),
        ("http://127.0.0.1:8000/", "根路径"),
        ("http://localhost:8000/health", "localhost健康检查"),
        ("http://localhost:8000/", "localhost根路径")
    ]
    
    print("🔍 检查服务状态...")
    print("-" * 50)
    
    for url, description in urls_to_check:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {description} ({url})")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   响应: {data}")
                except:
                    print(f"   响应: {response.text[:100]}...")
            else:
                print(f"   错误: {response.text[:200]}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {description} ({url}) - 连接失败")
            print("   请确保服务正在运行: python -m app.main")
        except requests.exceptions.Timeout:
            print(f"⏰ {description} ({url}) - 请求超时")
        except Exception as e:
            print(f"⚠️  {description} ({url}) - 错误: {str(e)}")
        print()

def main():
    """主函数"""
    check_service()
    
    print("💡 如果服务未运行，请执行以下命令启动:")
    print("   python -m app.main")
    print()
    print("📋 如果服务已运行但仍有问题，请检查:")
    print("   1. 端口8000是否被占用")
    print("   2. 依赖包是否正确安装")
    print("   3. 模型文件是否下载")

if __name__ == "__main__":
    main()