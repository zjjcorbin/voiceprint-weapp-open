#!/usr/bin/env python3
"""
安装和配置依赖的简化脚本
"""

import subprocess
import sys

def run_command(cmd, description=""):
    """运行命令并处理错误"""
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 成功")
            return True
        else:
            print(f"✗ 失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def install_dependencies():
    """安装依赖的推荐顺序"""
    print("安装声纹识别系统依赖")
    print("=" * 50)
    
    # 1. 更新pip
    print("\n1. 更新pip...")
    run_command("python -m pip install --upgrade pip", "更新pip")
    
    # 2. 安装核心依赖
    print("\n2. 安装核心依赖...")
    
    # 按顺序安装，避免版本冲突
    deps = [
        ("numpy>=1.20.0", "NumPy（基础数值计算）"),
        ("torch>=2.0.0", "PyTorch（深度学习框架）"),
        ("torchaudio>=2.0.0", "PyTorch Audio（音频处理）"),
        ("transformers>=4.20.0", "Transformers（HuggingFace模型）"),
        ("huggingface_hub>=0.19.0", "HuggingFace Hub（模型下载）"),
        ("speechbrain>=1.0.0", "SpeechBrain（语音AI）"),
        ("librosa>=0.9.0", "Librosa（音频分析）"),
        ("soundfile>=0.12.0", "SoundFile（音频文件）"),
        ("scipy>=1.9.0", "SciPy（科学计算）"),
    ]
    
    for dep, desc in deps:
        print(f"\n  安装 {desc}")
        success = run_command(f"python -m pip install {dep}", f"安装 {dep}")
        if not success:
            print(f"  ⚠️ {dep} 安装失败，继续下一个...")
    
    # 3. 安装其他依赖
    print("\n3. 安装其他依赖...")
    
    other_deps = [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0", 
        "sqlalchemy>=2.0.0",
        "mysql-connector-python>=8.0.0",
        "databases[mysql]>=0.9.0",
        "python-jose[cryptography]>=3.0.0",
        "passlib[bcrypt]>=1.7.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
        "httpx>=0.25.0",
        "aiofiles>=23.0.0",
        "pillow>=10.0.0",
        "webrtcvad>=2.0.10",
        "pydub>=0.25.0",
    ]
    
    for dep in other_deps:
        success = run_command(f"python -m pip install {dep}", f"安装 {dep}")
        if not success:
            print(f"  ⚠️ {dep} 安装失败，继续...")
    
    print("\n" + "=" * 50)
    print("依赖安装完成！")

def test_installation():
    """测试安装"""
    print("\n测试安装...")
    print("=" * 30)
    
    tests = [
        ("import numpy", "NumPy"),
        ("import torch", "PyTorch"),
        ("import transformers", "Transformers"),
        ("import huggingface_hub", "HuggingFace Hub"),
        ("import speechbrain", "SpeechBrain"),
        ("import librosa", "Librosa"),
        ("import soundfile", "SoundFile"),
        ("import scipy", "SciPy"),
        ("import fastapi", "FastAPI"),
        ("import sqlalchemy", "SQLAlchemy"),
        ("import pydantic", "Pydantic"),
        ("import loguru", "Loguru"),
    ]
    
    failed = []
    
    for import_cmd, name in tests:
        try:
            exec(import_cmd)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")
            failed.append((name, str(e)))
    
    if failed:
        print(f"\n⚠️ {len(failed)} 个模块导入失败:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        return False
    else:
        print("\n🎉 所有模块导入成功！")
        return True

def main():
    """主函数"""
    print("声纹识别系统依赖安装工具")
    print("=" * 50)
    
    # 安装依赖
    install_dependencies()
    
    # 测试安装
    success = test_installation()
    
    if success:
        print("\n✅ 安装成功！现在可以：")
        print("  1. 下载模型: python scripts/download_models.py")
        print("  2. 启动应用: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ 安装失败，请检查错误信息并重试")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)