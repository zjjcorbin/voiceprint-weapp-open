#!/usr/bin/env python3
"""
启动服务并检查依赖
"""

import subprocess
import sys
import os

def check_dependencies():
    """检查关键依赖包"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        ("fastapi", "FastAPI框架"),
        ("uvicorn", "ASGI服务器"),
        ("torch", "PyTorch深度学习框架"),
        ("speechbrain", "语音处理库"),
        ("librosa", "音频处理库"),
        ("sqlalchemy", "数据库ORM"),
        ("minio", "对象存储客户端")
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {description} ({package})")
        except ImportError as e:
            print(f"❌ {description} ({package}) - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少以下包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包检查通过")
    return True

def start_service():
    """启动服务"""
    print("\n🚀 启动服务...")
    
    # 设置环境变量，跳过模型预加载以加快启动
    env = os.environ.copy()
    env.update({
        "PRELOAD_MODELS": "false",
        "SKIP_AUDIO_CHECK": "true",
        "CHECK_MODELS_IN_HEALTH": "false"
    })
    
    try:
        # 启动服务
        process = subprocess.Popen([
            sys.executable, "-m", "app.main"
        ], env=env)
        
        print("✅ 服务已启动")
        print(f"📡 访问地址: http://127.0.0.1:8000")
        print(f"📚 API文档: http://127.0.0.1:8000/docs")
        print(f"🆘 健康检查: http://127.0.0.1:8000/health")
        print("\n💡 按 Ctrl+C 停止服务")
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 停止服务")
        process.terminate()
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎯 声纹识别系统 - 服务启动器")
    print("-" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，无法启动服务")
        return
    
    # 启动服务
    start_service()

if __name__ == "__main__":
    main()