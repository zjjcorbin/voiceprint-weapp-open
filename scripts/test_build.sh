#!/bin/bash

# 测试Docker构建的脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 测试docker-compose语法
test_compose_syntax() {
    log_info "测试docker-compose语法..."
    
    if docker-compose config > /dev/null 2>&1; then
        log_info "✓ docker-compose语法正确"
    else
        log_error "✗ docker-compose语法错误"
        docker-compose config
        exit 1
    fi
}

# 测试构建参数
test_build_args() {
    log_info "测试构建参数..."
    
    # 检查args格式
    if grep -A 2 "args:" docker-compose.yml | grep -q "HF_ENDPOINT:"; then
        log_info "✓ 构建参数格式正确"
    else
        log_error "✗ 构建参数格式错误"
        grep -A 2 "args:" docker-compose.yml
        exit 1
    fi
}

# 测试Dockerfile语法
test_dockerfile() {
    log_info "测试Dockerfile语法..."
    
    if docker build --dry-run -f Dockerfile . > /dev/null 2>&1; then
        log_info "✓ Dockerfile语法正确"
    else
        log_error "✗ Dockerfile语法错误"
        exit 1
    fi
}

# 测试构建过程
test_build() {
    log_info "测试构建过程..."
    
    export DOCKER_BUILDKIT=1
    
    # 尝试构建（不下载完整模型，只测试语法）
    if docker-compose build --no-cache --pull voiceprint-api; then
        log_info "✓ 构建测试成功"
    else
        log_error "✗ 构建测试失败"
        exit 1
    fi
}

# 显示测试结果
show_results() {
    log_info "测试完成！"
    echo ""
    echo "如果所有测试都通过，可以运行："
    echo "  ./scripts/setup.sh init"
    echo ""
    echo "或直接构建："
    echo "  docker-compose build --no-cache voiceprint-api"
    echo "  docker-compose up -d"
}

# 主函数
main() {
    log_info "开始Docker构建测试..."
    echo ""
    
    test_compose_syntax
    test_build_args
    test_dockerfile
    test_build
    
    show_results
}

main "$@"