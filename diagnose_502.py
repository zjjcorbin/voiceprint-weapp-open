#!/usr/bin/env python3
"""
诊断502错误问题
"""

import socket
import requests
import subprocess
import sys
import os

def check_port(host='127.0.0.1', port=8000):
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")
        return False

def check_service_response():
    """检查服务响应"""
    print("🔍 检查服务响应...")
    
    test_urls = [
        ("http://127.0.0.1:8000/health", "健康检查"),
        ("http://127.0.0.1:8000/", "根路径"),
        ("http://localhost:8000/health", "localhost健康检查"),
        ("http://localhost:8000/", "localhost根路径")
    ]
    
    for url, description in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {description} - 状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"   响应正常")
            else:
                print(f"   响应内容: {response.text[:200]}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {description} - 连接被拒绝")
            print("   服务可能未启动")
        except requests.exceptions.Timeout:
            print(f"⏰ {description} - 请求超时")
        except Exception as e:
            print(f"⚠️  {description} - 错误: {str(e)}")

def check_model_status():
    """检查模型状态"""
    print("\n🤖 检查模型状态...")
    
    try:
        # 尝试导入情绪识别服务
        from app.services.emotion_service import EmotionService
        service = EmotionService()
        
        # 检查模型是否加载
        import asyncio
        status = asyncio.run(service.check_model_status())
        
        if status:
            print("✅ 情绪识别模型已加载")
        else:
            print("❌ 情绪识别模型未加载")
            print("💡 运行: python scripts/download_models.py")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"⚠️  模型检查错误: {e}")

def check_database():
    """检查数据库连接"""
    print("\n🗄️  检查数据库连接...")
    
    try:
        from app.core.config import settings
        print(f"📊 数据库URL: {settings.DATABASE_URL}")
        
        # 测试数据库连接
        from sqlalchemy import text
        from app.models.database import engine
        import asyncio
        
        async def test_db():
            try:
                async with engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                return True
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                return False
        
        result = asyncio.run(test_db())
        if result:
            print("✅ 数据库连接正常")
        
    except Exception as e:
        print(f"⚠️  数据库检查错误: {e}")

def main():
    """主函数"""
    print("🔧 502错误诊断工具")
    print("-" * 50)
    
    # 检查端口
    print("🔌 检查端口8000...")
    if check_port():
        print("✅ 端口8000已被占用（服务可能正在运行）")
        check_service_response()
    else:
        print("❌ 端口8000未被占用（服务未启动）")
        print("💡 请先启动服务: python -m app.main")
        return
    
    # 检查模型状态
    check_model_status()
    
    # 检查数据库
    check_database()
    
    print("\n📋 解决方案建议:")
    print("1. 确保服务正在运行: python -m app.main")
    print("2. 检查依赖包: pip install -r requirements.txt")
    print("3. 下载模型文件: python scripts/download_models.py")
    print("4. 检查防火墙设置")
    print("5. 查看服务日志获取详细错误信息")

if __name__ == "__main__":
    main()