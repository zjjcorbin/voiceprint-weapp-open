#!/bin/bash

# 声纹识别系统 - 镜像构建脚本（包含预训练模型）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_step "检查构建依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_info "依赖检查通过"
}

# 清理旧镜像
cleanup_old_images() {
    log_step "清理旧的镜像..."
    
    # 停止并删除容器
    docker-compose down --remove-orphans || true
    
    # 删除旧镜像
    docker images | grep voiceprint | awk '{print $3}' | xargs -r docker rmi -f || true
    
    log_info "清理完成"
}

# 构建包含模型的Docker镜像
build_with_models() {
    log_step "构建Docker镜像（包含预训练模型）..."
    
    # 设置构建参数
    export DOCKER_BUILDKIT=1
    export BUILDKIT_PROGRESS=plain
    
    # 构建镜像
    docker build \
        --build-arg HF_ENDPOINT=https://hf-mirror.com \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") \
        -t voiceprint-api:latest \
        -f Dockerfile .
    
    if [ $? -eq 0 ]; then
        log_info "镜像构建成功"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 验证镜像内容
verify_image() {
    log_step "验证镜像内容..."
    
    # 创建临时容器检查模型文件
    container_id=$(docker create voiceprint-api:latest)
    
    # 检查模型文件
    if docker exec $container_id ls -la /app/pretrained_models/ | grep -E "(spkrec-ecapa|emotion)" > /dev/null; then
        log_info "✓ 预训练模型已正确打包到镜像中"
    else
        log_warn "⚠ 模型文件可能未正确打包，请检查构建日志"
    fi
    
    # 清理临时容器
    docker rm $container_id
    
    log_info "镜像验证完成"
}

# 更新docker-compose使用本地镜像
update_compose_file() {
    log_step "更新docker-compose配置..."
    
    # 备份原文件
    cp docker-compose.yml docker-compose.yml.backup
    
    # 临时修改配置使用本地构建的镜像
    sed -i.bak 's/build:/context: \.\/dockerfile:/image: voiceprint-api:latest/' docker-compose.yml
    
    log_info "配置更新完成，将使用本地构建的镜像"
}

# 启动服务
start_services() {
    log_step "启动系统服务..."
    
    # 启动所有服务
    docker-compose up -d
    
    log_info "服务启动完成，等待就绪..."
    
    # 等待服务就绪
    sleep 30
    
    # 检查健康状态
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_info "✓ API服务健康检查通过"
    else
        log_warn "⚠ API服务可能仍在启动中，请稍后检查"
    fi
}

# 显示状态
show_status() {
    log_step "显示系统状态..."
    
    echo ""
    docker-compose ps
    echo ""
    
    echo "访问地址："
    echo "API文档: http://localhost:8000/docs"
    echo "健康检查: http://localhost:8000/health"
    echo "MinIO控制台: http://localhost:9001 (用户名: minioadmin, 密码: minioadmin)"
    echo ""
    echo "镜像信息："
    docker images | grep voiceprint
}

# 恢复原配置
restore_config() {
    log_step "恢复原配置..."
    
    if [ -f docker-compose.yml.backup ]; then
        mv docker-compose.yml.backup docker-compose.yml
        log_info "配置已恢复"
    fi
}

# 显示帮助
show_help() {
    echo "用法: $0 {build|start|stop|clean|help}"
    echo ""
    echo "命令:"
    echo "  build  - 构建包含预训练模型的Docker镜像"
    echo "  start  - 启动服务（使用已构建的镜像）"
    echo "  stop   - 停止服务"
    echo "  clean  - 清理镜像和容器"
    echo "  help   - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build  # 构建镜像（包含模型）"
    echo "  $0 start  # 启动服务"
}

# 主函数
main() {
    case "$1" in
        build)
            log_info "开始构建包含预训练模型的镜像..."
            check_dependencies
            cleanup_old_images
            build_with_models
            verify_image
            update_compose_file
            log_info "镜像构建完成！"
            echo ""
            echo "下一步："
            echo "  $0 start  # 启动服务"
            ;;
        start)
            log_info "启动系统服务..."
            start_services
            show_status
            ;;
        stop)
            log_info "停止系统服务..."
            docker-compose down
            log_info "服务已停止"
            ;;
        clean)
            log_info "清理镜像和容器..."
            docker-compose down --volumes --remove-orphans
            docker system prune -f
            docker volume prune -f
            log_info "清理完成"
            ;;
        restore)
            restore_config
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# 错误处理
trap 'log_error "构建过程中发生错误，正在清理..."; restore_config; exit 1' ERR

# 执行主函数
main "$@"