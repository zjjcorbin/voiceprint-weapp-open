# 模型下载脚本使用说明

本项目的模型下载脚本已配置为使用国内镜像 `https://hf-mirror.com` 来加速下载。

## 快速开始

### 1. 启用国内镜像（推荐在中国大陆使用）

创建 `.env` 文件并添加以下配置：

```bash
# 使用国内镜像加速模型下载
USE_HF_MIRROR=true
HF_ENDPOINT=https://hf-mirror.com
```

### 2. 下载模型

#### 方式一：使用管理脚本（推荐）
```bash
# 检查模型状态
python scripts/manage_models.py --check

# 下载所有缺失的模型
python scripts/manage_models.py --download

# 强制重新下载所有模型
python scripts/manage_models.py --download --force

# 清理已下载的模型
python scripts/manage_models.py --clean
```

#### 方式二：单独下载
```bash
# 下载情绪识别模型
python scripts/download_emotion_only.py

# 下载所有模型
python scripts/download_models.py
```

## 脚本功能说明

### `manage_models.py` - 综合管理脚本
- `--check`: 检查模型是否已下载
- `--download`: 下载缺失的模型
- `--force`: 强制重新下载所有模型
- `--clean`: 删除已下载的模型文件

### `download_models.py` - 批量下载脚本
- 自动检测已存在的模型文件
- 支持国内镜像加速
- 自动创建模型目录

### `download_emotion_only.py` - 情绪模型下载
- 只下载情绪识别模型
- 检查文件完整性
- 支持镜像加速

## 模型存储位置

模型文件下载到以下位置：
- 声纹识别模型: `pretrained_models/spkrec-ecapa-voxceleb/`
- 情绪识别模型: `pretrained_models/emotion_recognition_wav2vec2-IEMOCAP/`

## 故障排除

### 1. 下载速度慢
确保设置了环境变量：
```bash
export USE_HF_MIRROR=true
export HF_ENDPOINT=https://hf-mirror.com
```

### 2. 模型导入失败
检查 SpeechBrain 安装：
```bash
pip install speechbrain
```

### 3. 磁盘空间不足
清理现有模型：
```bash
python scripts/manage_models.py --clean
```

### 4. 网络连接问题
- 检查网络连接
- 尝试使用VPN或代理
- 验证镜像地址可访问性

## 自动化部署

在 Docker 环境中，可以在 `docker-compose.yml` 中设置环境变量：

```yaml
services:
  app:
    environment:
      - USE_HF_MIRROR=true
      - HF_ENDPOINT=https://hf-mirror.com
```

## 注意事项

1. 模型文件较大（总计约 2-3GB），请确保有足够的磁盘空间
2. 首次下载可能需要较长时间，请耐心等待
3. 如遇到下载中断，可以重新运行脚本，脚本会自动续传
4. 模型文件为预训练模型，包含版权信息，请遵循相关许可协议