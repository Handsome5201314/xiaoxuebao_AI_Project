#!/bin/bash

# 小雪宝Docker化部署脚本
# 使用方法: ./scripts/deploy.sh [环境] [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查Docker版本
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    log_info "Docker版本: $DOCKER_VERSION"
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查系统资源
check_resources() {
    log_info "检查系统资源..."
    
    # 检查内存
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ $TOTAL_MEM -lt 4096 ]; then
        log_warning "系统内存不足4GB，可能影响性能"
    fi
    
    # 检查磁盘空间
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    if [ $AVAILABLE_SPACE -lt 20 ]; then
        log_warning "可用磁盘空间不足20GB"
    fi
    
    log_success "系统资源检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p nginx/ssl
    mkdir -p database/init
    mkdir -p database/migrations
    mkdir -p logs
    mkdir -p backups
    mkdir -p uploads
    
    log_success "目录创建完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            log_info "已创建.env文件，请编辑配置"
        else
            log_error "未找到env.example文件"
            exit 1
        fi
    fi
    
    # 生成随机密钥
    if grep -q "your_secret_key_change_in_production" .env; then
        SECRET_KEY=$(openssl rand -hex 32)
        JWT_SECRET=$(openssl rand -hex 32)
        
        sed -i "s/your_secret_key_change_in_production/$SECRET_KEY/g" .env
        sed -i "s/your_jwt_secret_change_in_production/$JWT_SECRET/g" .env
        
        log_info "已生成随机密钥"
    fi
    
    log_success "环境变量配置完成"
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建所有服务镜像
    docker-compose build --parallel
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动基础服务
    docker-compose up -d postgres redis elasticsearch
    
    # 等待基础服务就绪
    log_info "等待基础服务启动..."
    sleep 30
    
    # 启动应用服务
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 等待服务完全启动
    sleep 60
    
    # 检查服务健康状态
    SERVICES=("nginx" "web-app" "web-admin" "api-gateway" "knowledge-service" "search-service" "user-service")
    
    for service in "${SERVICES[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            log_success "$service 服务运行正常"
        else
            log_error "$service 服务启动失败"
        fi
    done
    
    # 检查API健康状态
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "API服务健康检查通过"
    else
        log_warning "API服务健康检查失败"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "部署完成！"
    echo ""
    echo "🌐 访问地址："
    echo "   用户前端: http://localhost:3000"
    echo "   管理后台: http://localhost:3001"
    echo "   API文档: http://localhost:8000/docs"
    echo ""
    echo "📊 服务状态："
    docker-compose ps
    echo ""
    echo "📝 常用命令："
    echo "   查看日志: docker-compose logs -f [服务名]"
    echo "   重启服务: docker-compose restart [服务名]"
    echo "   停止服务: docker-compose down"
    echo "   更新服务: docker-compose pull && docker-compose up -d"
    echo ""
    echo "⚠️  重要提醒："
    echo "   1. 请及时修改.env文件中的默认密码"
    echo "   2. 生产环境请配置SSL证书"
    echo "   3. 定期备份数据库"
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    # 这里可以添加清理逻辑
}

# 主函数
main() {
    local ENVIRONMENT=${1:-"development"}
    local OPTIONS=${2:-""}
    
    log_info "开始部署小雪宝Docker化版本..."
    log_info "部署环境: $ENVIRONMENT"
    
    # 设置错误处理
    trap cleanup EXIT
    
    # 执行部署步骤
    check_docker
    check_resources
    create_directories
    setup_environment
    build_images
    start_services
    check_services
    show_deployment_info
    
    log_success "部署完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
