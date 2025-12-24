#!/usr/bin/env python3
"""
修复torchaudio版本兼容性问题 - 支持SpeechBrain 1.0
"""

import subprocess
import sys
import os

def fix_speechbrain_103_compatibility():
    """修复SpeechBrain 1.0.3和torchaudio兼容性问题"""
    
    print("正在修复SpeechBrain 1.0.3 torchaudio兼容性问题...")
    
    # 检查当前版本
    try:
        import torchaudio
        import speechbrain
        print(f"当前torchaudio版本: {torchaudio.__version__}")
        print(f"当前speechbrain版本: {speechbrain.__version__}")
    except ImportError as e:
        print(f"库未安装: {e}")
        return False
    
    # 升级到PyTorch 2.6.0安全修复版本
    print("升级到PyTorch 2.6.0安全修复版本...")
    
    packages = [
        ("numpy<2.0.0", "NumPy 1.x 兼容版本"),
        ("torch==2.6.0", "PyTorch 2.6.0 (CVE-2025-32434安全修复)"),
        ("torchvision==0.21.0", "TorchVision 0.21.0 (PyTorch 2.6兼容版)"), 
        ("torchaudio==2.6.0", "TorchAudio 2.6.0 (PyTorch 2.6兼容版)"),
        ("speechbrain==1.0.3", "SpeechBrain 1.0.3"),
        ("transformers==4.46.0", "Transformers 4.46.0 (消除警告)")
    ]
    
    for package, name in packages:
        print(f"安装 {name}...")
        try:
            if "torch" in package.lower():
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    package, "--force-reinstall", "--index-url", 
                    "https://download.pytorch.org/whl/cu118"
                ])
            else:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    package, "--force-reinstall"
                ])
            print(f"✓ {name} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"✗ {name} 安装失败: {e}")
            return False
    
    # 创建兼容性补丁
    print("创建SpeechBrain 1.0.3兼容性补丁...")
    create_compatibility_patch()
    
    print("修复完成！请重启应用。")
    return True

def create_compatibility_patch():
    """创建兼容性补丁文件"""
    
    patch_content = '''
"""
torchaudio兼容性补丁
适用于新版本torchaudio中移除的list_audio_backends方法
"""

import torchaudio

def list_audio_backends():
    """获取可用的音频后端列表"""
    try:
        # 尝试新版本的方式
        return [torchaudio.get_audio_backend()] if torchaudio.get_audio_backend() else []
    except AttributeError:
        try:
            # 尝试旧版本的方式
            return torchaudio.list_audio_backends()
        except AttributeError:
            # 如果都不支持，返回默认后端
            return ["soundfile", "sox"]

# 如果不存在list_audio_backends方法，则添加一个
if not hasattr(torchaudio, 'list_audio_backends'):
    torchaudio.list_audio_backends = list_audio_backends
    print("已为torchaudio添加list_audio_backends兼容性补丁")
'''
    
    patch_file = "/app/torchaudio_compatibility_patch.py"
    with open(patch_file, "w") as f:
        f.write(patch_content)
    
    print(f"✓ 兼容性补丁已创建: {patch_file}")

if __name__ == "__main__":
    fix_speechbrain_103_compatibility()