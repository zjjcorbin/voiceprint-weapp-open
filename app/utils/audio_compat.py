"""
音频处理兼容性工具运行
处理SpeechBrain 1.0和torchaudio 2.1+版本的兼容性问题
"""

import torchaudio
import warnings
import sys
import os

def setup_torchaudio_compatibility():
    """
    设置torchaudio兼容性
    解决新版本torchaudio中移除的list_audio_backends方法
    SpeechBrain 1.0需要这个方法
    """
    
    # 检查是否存在list_audio_backends方法
    if not hasattr(torchaudio, 'list_audio_backends'):
        
        def list_audio_backends():
            """获取可用的音频后端列表 - SpeechBrain 1.0兼容实现"""
            # torchaudio 2.1+的实现
            try:
                # 尝试获取当前后端
                if hasattr(torchaudio, 'get_audio_backend'):
                    backend = torchaudio.get_audio_backend()
                    if backend:
                        return [backend]
                
                # 检查可用的后端
                available_backends = []
                
                # 检查soundfile后端
                try:
                    import soundfile
                    available_backends.append("soundfile")
                except ImportError:
                    pass
                
                # 检查sox后端
                try:
                    import sox
                    available_backends.append("sox")
                except ImportError:
                    pass
                
                # 检查ffmpeg后端
                try:
                    import ffmpeg
                    available_backends.append("ffmpeg")
                except ImportError:
                    pass
                
                if not available_backends:
                    # 如果都没有，返回默认
                    available_backends = ["soundfile"]
                
                return available_backends
                
            except Exception as e:
                warnings.warn(f"获取音频后端时出错: {e}", UserWarning)
                return ["soundfile"]
        
        # 动态添加方法
        torchaudio.list_audio_backends = list_audio_backends
        print("✓ 已为torchaudio添加list_audio_backends兼容性补丁 (SpeechBrain 1.0)")

def check_speechbrain_compatibility():
    """检查SpeechBrain 1.0.3兼容性"""
    try:
        import speechbrain
        print(f"✓ SpeechBrain版本: {speechbrain.__version__}")
        
        # 检查是否为1.0.3或更高版本
        version_parts = speechbrain.__version__.split('.')
        major, minor, patch = map(int, version_parts[:3]) if len(version_parts) >= 3 else (int(version_parts[0]), int(version_parts[1]), 0)
        
        if major > 1 or (major == 1 and minor > 0) or (major == 1 and minor == 0 and patch >= 3):
            print("✓ 使用SpeechBrain 1.0.3+最新版本")
            return True
        elif major == 1 and minor == 0:
            print(f"⚠ 使用SpeechBrain 1.0.{patch}，建议升级到1.0.3+")
            return True
        else:
            print("⚠ 建议使用SpeechBrain 1.0.3+版本")
            return False
            
    except ImportError as e:
        print(f"✗ SpeechBrain导入失败: {e}")
        return False

def check_audio_backend():
    """检查音频后端是否可用"""
    setup_torchaudio_compatibility()
    
    try:
        backends = torchaudio.list_audio_backends()
        if backends:
            print(f"✓ 可用的音频后端: {backends}")
            return True
        else:
            print("⚠ 警告: 没有找到可用的音频后端")
            return False
    except Exception as e:
        print(f"⚠ 检查音频后端时出错: {e}")
        return False

def get_audio_backend():
    """获取当前音频后端"""
    setup_torchaudio_compatibility()
    
    try:
        if hasattr(torchaudio, 'get_audio_backend'):
            return torchaudio.get_audio_backend()
        else:
            # 兼容旧版本
            return "soundfile"
    except Exception:
        return "soundfile"

def verify_audio_stack():
    """验证整个音频处理栈的兼容性"""
    print("验证音频处理栈兼容性...")
    
    # 检查torch版本
    import torch
    print(f"✓ PyTorch版本: {torch.__version__}")
    
    # 检查torch.load安全性
    try:
        # 检查是否支持weights_only参数
        test_tensor = torch.randn(1, 1)
        temp_file = "/tmp/test_tensor.pt"
        torch.save(test_tensor, temp_file)
        
        # 测试weights_only加载
        loaded = torch.load(temp_file, weights_only=True)
        os.remove(temp_file)
        print("✓ torch.load weights_only安全检查通过")
    except Exception as e:
        print(f"⚠ torch.load安全检查失败: {e}")
    
    # 检查torchaudio版本
    print(f"✓ TorchAudio版本: {torchaudio.__version__}")
    
    # 检查SpeechBrain版本
    check_speechbrain_compatibility()
    
    # 检查音频后端
    check_audio_backend()
    
    return True

# 在模块导入时自动设置兼容性
setup_torchaudio_compatibility()