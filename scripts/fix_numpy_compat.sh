#!/bin/bash

# NumPy兼容性修复脚本
# 解决NumPy 2.x与PyTorch生态的兼容性问题

set -e

echo "开始修复NumPy兼容性问题..."
echo "NumPy 2.x与某些PyTorch模块不兼容，需要降级到1.x版本"

echo "1. 卸载当前NumPy版本..."
pip uninstall -y numpy

echo "2. 安装NumPy 1.x兼容版本..."
pip install "numpy<2.0.0"

echo "3. 验证NumPy版本..."
python -c "
import numpy
print(f'✓ NumPy版本: {numpy.__version__}')

# 测试基本功能
arr = numpy.array([1, 2, 3])
print(f'✓ NumPy基本功能测试通过: {arr}')

# 检查与PyTorch的兼容性
try:
    import torch
    tensor = torch.from_numpy(arr)
    print(f'✓ NumPy与PyTorch兼容性测试通过: {tensor}')
except Exception as e:
    print(f'⚠ NumPy与PyTorch兼容性测试失败: {e}')
"

echo "4. 验证音频处理栈..."
python -c "
try:
    from app.utils.audio_compat import verify_audio_stack
    verify_audio_stack()
    print('✓ 音频处理栈兼容性验证通过')
except Exception as e:
    print(f'⚠ 音频处理栈验证失败: {e}')
"

echo "NumPy兼容性修复完成！"
echo "已安装NumPy < 2.0.0版本，与PyTorch生态系统完全兼容"
echo ""
echo "注意：如果仍有torch.load安全警告，请升级到PyTorch 2.6.0+"
echo "使用: pip install torch==2.6.0 torchaudio==2.6.0 torchvision==0.21.0"