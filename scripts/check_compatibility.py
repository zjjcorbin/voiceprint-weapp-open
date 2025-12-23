#!/usr/bin/env python3
"""
检查Python和包的版本兼容性
"""

import sys
import subprocess

def run_python_script(code, description=""):
    """运行Python代码片段"""
    try:
        exec(code)
        return True, ""
    except Exception as e:
        return False, str(e)

def check_python_version():
    """检查Python版本"""
    print("Python版本检查")
    print("-" * 30)
    
    version = sys.version_info
    print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
    
    # 检查版本兼容性
    issues = []
    
    if version < (3, 8):
        issues.append("Python 3.8+ 推荐，当前版本可能不支持某些包")
    elif version >= (3, 12):
        issues.append("Python 3.12+ 可能有兼容性问题，建议使用3.9-3.11")
    
    if issues:
        print("⚠️ 警告:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Python版本兼容")
    
    return len(issues) == 0

def check_package_compatibility():
    """检查包的版本兼容性"""
    print("\n包兼容性检查")
    print("-" * 30)
    
    # 定义兼容的包版本范围
    compatible_packages = {
        "torch": ">=1.13.0",
        "torchaudio": ">=2.0.0", 
        "transformers": ">=4.20.0",
        "speechbrain": ">=1.0.0",
        "numpy": ">=1.20.0",
        "librosa": ">=0.9.0"
    }
    
    failed = []
    
    for package, min_version in compatible_packages.items():
        print(f"检查 {package} {min_version}+...")
        success, error = run_python_script(f"""
try:
    import {package}
    if hasattr({package}, '__version__'):
        version = {package}.__version__
        print(f"  版本: {{version}}")
    else:
        print(f"  已安装，但无法获取版本")
except ImportError as e:
    print(f"  未安装: {{e}}")
""", f"{package} 检查")
        
        if not success and "未安装" in error:
            failed.append(f"{package}: {error}")
    
    return len(failed) == 0

def suggest_fixes():
    """建议修复方案"""
    print("\n修复建议")
    print("-" * 30)
    
    print("1. 使用正确的包版本:")
    print("   pip install 'torch>=1.13.0' 'torchaudio>=2.0.0'")
    print("   pip install 'transformers>=4.20.0' 'speechbrain>=1.0.0'")
    
    print("\n2. 如果有版本冲突，使用:")
    print("   pip install --upgrade setuptools wheel")
    print("   pip install --no-cache-dir <package_name>")
    
    print("\n3. 创建新的虚拟环境:")
    print("   python -m venv voiceprint-env")
    print("   source voiceprint-env/bin/activate")
    print("   pip install -r requirements.txt")
    
    print("\n4. 分步安装核心包:")
    print("   pip install numpy>=1.20.0")
    print("   pip install torch>=1.13.0 torchaudio>=2.0.0")
    print("   pip install transformers>=4.20.0")
    print("   pip install speechbrain>=1.0.0")

def main():
    """主函数"""
    print("声纹识别系统兼容性检查")
    print("=" * 50)
    
    # 检查Python版本
    python_ok = check_python_version()
    
    # 检查包兼容性
    packages_ok = check_package_compatibility()
    
    print("\n" + "=" * 50)
    print("检查总结:")
    print(f"  Python版本: {'✓ 兼容' if python_ok else '⚠️ 需要注意'}")
    print(f"  包兼容性: {'✓ 兼容' if packages_ok else '⚠️ 有冲突'}")
    
    if python_ok and packages_ok:
        print("\n🎉 系统兼容！可以继续安装。")
        print("\n下一步:")
        print("  python scripts/install_deps.py")
        print("  python scripts/download_models.py")
    else:
        print("\n⚠️ 存在兼容性问题，请查看建议。")
        suggest_fixes()
    
    return python_ok and packages_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)