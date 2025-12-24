#!/bin/bash

# 安装音频依赖的修复脚本
# 解决torchaudio版本兼容性问题

set -e

echo "开始修复音频依赖兼容性问题..."

# 方案1: 完全卸载并重新安装兼容版本
echo "1. 卸载现有音频相关包..."
pip uninstall -y torchaudio speechbrain torch

echo "2. 安装PyTorch 2.6.0安全修复版本..."
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu118

echo "3. 安装PyTorch 2.6.0兼容的torchaudio版本..."
pip install torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118

echo "4. 安装SpeechBrain 1.0.3最新版本..."
pip install speechbrain==1.0.3

echo "5. 安装Transformers 4.46.0版本（消除警告）..."
pip install transformers==4.46.0

echo "6. 安装NumPy兼容版本..."
pip install "numpy<2.0.0"

echo "5. 安装其他音频依赖..."
pip install --upgrade librosa soundfile scipy

echo "6. 验证安装..."
python -c "
import torch
import torchaudio
import speechbrain
import numpy
print(f'✓ PyTorch版本: {torch.__version__}')
print(f'✓ TorchAudio版本: {torchaudio.__version__}')
print(f'✓ SpeechBrain版本: {speechbrain.__version__}')
print(f'✓ NumPy版本: {numpy.__version__}')

# 检查NumPy兼容性
import warnings
if numpy.__version__.startswith('2.'):
    warnings.warn('NumPy 2.x可能存在兼容性问题，建议使用numpy<2.0.0')

# 导入兼容性工具进行验证
from app.utils.audio_compat import verify_audio_stack
verify_audio_stack()
"

echo "音频依赖修复完成！"
echo "请重启应用以使更改生效。"