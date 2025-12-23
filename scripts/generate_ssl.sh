#!/bin/bash

# SSL证书生成脚本
# 用于开发环境生成自签名SSL证书

set -e

SSL_DIR="nginx/ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"

echo "正在生成SSL证书..."

# 创建SSL目录（如果不存在）
mkdir -p "$SSL_DIR"

# 检查是否已存在证书文件
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "SSL证书文件已存在："
    echo "  - 证书: $CERT_FILE"
    echo "  - 私钥: $KEY_FILE"
    read -p "是否要重新生成？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "证书生成已取消"
        exit 0
    fi
fi

# 生成私钥
echo "生成私钥..."
openssl genrsa -out "$KEY_FILE" 2048

# 生成证书
echo "生成自签名证书..."
openssl req -new -x509 -key "$KEY_FILE" -out "$CERT_FILE" -days 365 \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=Voiceprint/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,DNS:voiceprint.local"

# 设置文件权限
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo "SSL证书生成完成："
echo "  - 证书: $CERT_FILE"
echo "  - 私钥: $KEY_FILE"
echo ""
echo "注意：这是自签名证书，仅用于开发环境"
echo "生产环境请使用有效的SSL证书"