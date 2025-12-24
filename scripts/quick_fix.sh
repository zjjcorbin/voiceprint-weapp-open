#!/bin/bash

# 快速修复脚本 - 解决常见的部署问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 修复服务名称错误
fix_service_name() {
    log_info "修复docker-compose服务名称问题..."
    
    # 检查docker-compose.yml中的服务名称
    if grep -q "voiceprint-api:" docker-compose.yml; then
        log_info "✓ 服务名称正确: voiceprint-api"
    else
        log_error "× 服务名称不正确，应为 voiceprint-api"
    fi
}

# 修复构建命令
fix_build_command() {
    log_info "修复构建命令..."
    
    # 直接使用docker build
    log_info "使用docker build构建镜像..."
    
    export DOCKER_BUILDKIT=1
    docker build \
        --build-arg HF_ENDPOINT=https://hf-mirror.com \
        -t voiceprint-api:latest \
        -f Dockerfile .
    
    log_info "镜像构建完成"
}

# 更新docker-compose使用本地镜像
update_compose_to_local() {
    log_info "更新docker-compose使用本地镜像..."
    
    # 备份原文件
    cp docker-compose.yml docker-compose.yml.backup
    
    # 修改为使用本地构建的镜像
    sed -i.tmp '/build:/,/args:/c\
    image: voiceprint-api:latest' docker-compose.yml
    sed -i.tmp '/context:/d; /dockerfile:/d' docker-compose.yml
    mv docker-compose.yml.tmp docker-compose.yml
    
    log_info "✓ docker-compose已更新为使用本地镜像"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动基础设施服务
    docker-compose up -d mysql minio redis
    
    # 等待基础设施就绪
    log_info "等待数据库启动..."
    sleep 20
    
    # 启动API服务
    docker-compose up -d voiceprint-api
    
    # 等待API服务就绪
    sleep 15
    
    # 检查健康状态
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_info "✓ 服务启动成功"
    else
        log_error "× 服务启动失败，请检查日志"
        docker-compose logs voiceprint-api
    fi
}

# 显示状态
show_status() {
    log_info "服务状态："
    docker-compose ps
}

# 主函数
main() {
    log_info "开始快速修复..."
    
    fix_service_name
    fix_build_command
    update_compose_to_local
    start_services
    show_status
    
    log_info "修复完成！"
    echo ""
    echo "访问地址："
    echo "API文档: http://localhost:8000/docs"
    echo "健康检查: http://localhost:8000/health"
}

main "$@"