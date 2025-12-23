#!/bin/bash
# 拉取所需镜像的脚本

echo "正在拉取 MySQL 8.0..."
docker pull mysql:8.0

echo "正在拉取 MinIO..."
docker pull minio/minio:latest

echo "正在拉取 Redis..."
docker pull redis:7-alpine

echo "正在拉取 Nginx..."
docker pull nginx:alpine

echo "所有镜像拉取完成！"