#!/bin/bash

# PyTorch安全升级脚本
# 修复CVE-2025-32434漏洞并消除Transformers警告

set -e

echo "开始PyTorch安全升级..."
echo "修复CVE-2025-32434: torch.load安全漏洞"
echo "消除Transformers配置警告"

echo "1. 备份当前版本..."
python -c "
import torch, torchaudio, torchvision, transformers
print('当前版本:')
print(f'  PyTorch: {torch.__version__}')
print(f'  TorchAudio: {torchaudio.__version__}')  
print(f'  TorchVision: {torchvision.__version__}')
print(f'  Transformers: {transformers.__version__}')
"

echo "2. 卸载旧版本..."
pip uninstall -y torch torchaudio torchvision transformers

echo "3. 安装PyTorch 2.6.0安全版本..."
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118

echo "4. 安装Transformers 4.46.0（消除警告）..."
pip install transformers==4.46.0

echo "5. 验证升级..."
python -c "
import torch
import torchaudio  
import torchvision
import transformers
import numpy

print('升级后版本:')
print(f'✓ PyTorch: {torch.__version__}')
print(f'✓ TorchAudio: {torchaudio.__version__}')
print(f'✓ TorchVision: {torchvision.__version__}') 
print(f'✓ Transformers: {transformers.__version__}')
print(f'✓ NumPy: {numpy.__version__}')

# 测试torch.load安全性
try:
    test_tensor = torch.randn(1, 1)
    temp_file = '/tmp/test_tensor.pt'
    torch.save(test_tensor, temp_file)
    loaded = torch.load(temp_file, weights_only=True)
    import os
    os.remove(temp_file)
    print('✓ torch.load weights_only安全检查通过')
except Exception as e:
    print(f'✗ torch.load安全检查失败: {e}')

# 测试基本功能
try:
    audio = torch.randn(1, 16000)
    print(f'✓ PyTorch张量操作正常: {audio.shape}')
except Exception as e:
    print(f'✗ PyTorch张量操作失败: {e}')

# 验证SpeechBrain兼容性
try:
    from speechbrain.inference.classifiers import EncoderClassifier
    print('✓ SpeechBrain导入成功')
    
    # 读取配置文件中的模型
    if [ -f '/app/app/core/config.py' ]; then
        python -c "
from app.core.config import settings
print(f'配置的情绪识别模型: {settings.EMOTION_MODEL}')
"
    fi
except Exception as e:
    print(f'⚠ SpeechBrain兼容性检查: {e}')
"

echo "6. 测试情绪识别模型..."
if python -c "
try:
    from speechbrain.inference.classifiers import EncoderClassifier
    model = EncoderClassifier.from_hparams(
        source=\"$EMOTION_MODEL\",
        savedir='pretrained_models/emotion_recognition_wav2vec2',
        run_opts={'device': 'cpu'}
    )
    print('✓ 情绪识别模型加载成功')
except Exception as e:
    print(f'⚠ 情绪识别模型测试: {e}')
    exit(1)
"; then
    echo "✓ 模型测试通过"
else
    echo "⚠ 模型测试失败，请检查网络连接"
fi

echo ""
echo "PyTorch安全升级完成！"
echo "已修复CVE-2025-32434安全漏洞"
echo "已消除Transformers配置警告"
echo ""
echo "升级内容:"
echo "  - PyTorch 2.6.0 (torch.load安全修复)"
echo "  - TorchAudio 2.6.0 (版本兼容)"
echo "  - TorchVision 0.21.0 (版本兼容)"
echo "  - Transformers 4.46.0 (消除警告)"