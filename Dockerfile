FROM fastcn-registry-changsha42.crs.ctyun.cn/hnkz/python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /root/.config/pip/ && \
    echo "[global]" > /root/.config/pip/pip.conf && \
    echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> /root/.config/pip/pip.conf && \
    echo "trusted-host = pypi.tuna.tsinghua.edu.cn" >> /root/.config/pip/pip.conf
# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖 - 使用PyTorch 2.6安全版本
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade setuptools wheel \
    && pip install --no-cache-dir "numpy<2.0.0" \
    && pip install --no-cache-dir torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu118 \
    && pip install --no-cache-dir torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118 \
    && pip install --no-cache-dir speechbrain==1.0.3 \
    && pip install --no-cache-dir transformers==4.46.0 \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade librosa soundfile scipy

# 复制应用代码
COPY app/ ./app/
COPY scripts/ ./scripts/

# 创建必要的目录
RUN mkdir -p logs uploads temp pretrained_models

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]