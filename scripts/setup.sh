#!/bin/bash

# 声纹识别系统部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    
    log_info "依赖检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p logs
    mkdir -p uploads
    mkdir -p temp
    mkdir -p pretrained_models
    mkdir -p minio-data
    log_info "目录创建完成"
}

# 复制配置文件
setup_config() {
    if [ ! -f .env ]; then
        log_info "创建环境配置文件..."
        cp .env.example .env
        log_warn "请编辑 .env 文件配置您的环境变量"
    fi
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 启动数据库
    docker-compose up -d mysql
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 30
    
    # 检查数据库连接
    until docker-compose exec -T mysql mysqladmin ping -h"localhost" --silent; do
        log_info "等待MySQL启动..."
        sleep 5
    done
    
    # 创建数据库（如果不存在）
    docker-compose exec -T mysql mysql -uroot -proot123 -e "CREATE DATABASE IF NOT EXISTS voiceprint_system;"
    docker-compose exec -T mysql mysql -uroot -proot123 -e "CREATE USER IF NOT EXISTS 'voiceprint'@'%' IDENTIFIED BY 'password123';"
    docker-compose exec -T mysql mysql -uroot -proot123 -e "GRANT ALL PRIVILEGES ON voiceprint_system.* TO 'voiceprint'@'%';"
    docker-compose exec -T mysql mysql -uroot -proot123 -e "FLUSH PRIVILEGES;"
    
    log_info "数据库初始化完成"
}

# 启动MinIO
init_minio() {
    log_info "初始化MinIO..."
    
    # 启动MinIO
    docker-compose up -d minio
    
    # 等待MinIO启动
    sleep 10
    
    # 创建存储桶（如果不存在）
    if command -v mc &> /dev/null; then
        mc alias set minio http://localhost:9000 minioadmin minioadmin
        mc mb minio/voiceprint-audio --ignore-existing
        log_info "MinIO存储桶创建完成"
    else
        log_warn "MinIO客户端未安装，请手动创建存储桶"
    fi
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_info "Python依赖安装完成"
}

# 下载模型文件
download_models() {
    log_info "下载预训练模型..."
    
    source venv/bin/activate
    
    # 创建模型目录
    mkdir -p pretrained_models/voiceprint
    mkdir -p pretrained_models/emotion
    
    # Python脚本下载模型
    python3 - <<'EOF'
import os
from speechbrain.inference.speaker import SpeakerRecognition
from speechbrain.inference.classifiers import EncoderClassifier

try:
    print("下载声纹识别模型...")
    spk_model = SpeakerRecognition.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir="pretrained_models/spkrec-ecapa-voxceleb"
    )
    print("声纹识别模型下载完成")
    
    print("下载情绪识别模型...")
    emo_model = EncoderClassifier.from_hparams(
        source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
        savedir="pretrained_models/emotion-recognition-wav2vec2-IEMOCAP"
    )
    print("情绪识别模型下载完成")
    
except Exception as e:
    print(f"模型下载失败: {e}")
    print("系统将在首次运行时自动下载模型")
EOF
    
    log_info "模型下载完成"
}

# 启动服务
start_services() {
    log_info "启动系统服务..."
    
    # 启动所有服务
    docker-compose up -d
    
    log_info "服务启动完成"
    
    # 等待服务就绪
    sleep 30
    
    # 检查服务状态
    check_health
}

# 检查健康状态
check_health() {
    log_info "检查服务健康状态..."
    
    # 检查API服务
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_info "API服务运行正常"
    else
        log_error "API服务异常"
    fi
    
    # 检查MinIO
    if curl -f http://localhost:9001 &> /dev/null; then
        log_info "MinIO服务运行正常"
    else
        log_error "MinIO服务异常"
    fi
}

# 显示状态
show_status() {
    log_info "系统状态："
    docker-compose ps
    
    echo ""
    echo "访问地址："
    echo "API文档: http://localhost:8000/docs"
    echo "MinIO控制台: http://localhost:9001 (用户名: minioadmin, 密码: minioadmin)"
    echo "健康检查: http://localhost:8000/health"
}

# 显示帮助
show_help() {
    echo "用法: $0 {init|start|stop|restart|status|logs}"
    echo ""
    echo "命令:"
    echo "  init    - 初始化系统（首次部署使用）"
    echo "  start   - 启动服务"
    echo "  stop    - 停止服务"
    echo "  restart - 重启服务"
    echo "  status  - 查看状态"
    echo "  logs    - 查看日志"
    echo ""
    echo "示例:"
    echo "  $0 init    # 首次部署"
    echo "  $0 start   # 启动服务"
    echo "  $0 status  # 查看状态"
}

# 主函数
main() {
    case "$1" in
        init)
            log_info "初始化声纹识别系统..."
            check_dependencies
            create_directories
            setup_config
            install_dependencies
            init_database
            init_minio
            download_models
            start_services
            show_status
            ;;
        start)
            log_info "启动服务..."
            docker-compose up -d
            sleep 15
            show_status
            ;;
        stop)
            log_info "停止服务..."
            docker-compose down
            ;;
        restart)
            log_info "重启服务..."
            docker-compose down
            sleep 5
            docker-compose up -d
            sleep 15
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            docker-compose logs -f
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"