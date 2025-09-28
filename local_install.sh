#!/bin/bash

# 小雪宝 - 本地一键安装脚本
# 使用本地文件进行部署，避免GitHub连接问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 艺术字LOGO
print_logo() {
    echo -e "${BLUE}"
    echo "┌─────────────────────────────────────────────┐"
    echo "│  小雪宝 (LeukemiaPal) - 本地Docker部署       │"
    echo "│  🐳 白血病AI关爱助手 - 微服务架构           │"
    echo "│  ❄️  让科技温暖生命，用AI点亮希望          │"
    echo "└─────────────────────────────────────────────┘"
    echo -e "${NC}"
}

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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$NAME
            VER=$VERSION_ID
        else
            OS="Unknown Linux"
        fi
    else
        log_error "不支持的操作系统: $OSTYPE"
        log_info "目前仅支持 Linux 系统"
        exit 1
    fi
    
    log_info "检测到操作系统: $OS $VER"
}

# 检查Docker环境
check_docker() {
    log_step "检查 Docker 环境..."
    
    if ! command -v docker &> /dev/null; then
        log_warning "Docker 未安装，尝试自动安装..."
        install_docker
    else
        log_info "Docker 已安装: $(docker --version)"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose 未安装，尝试自动安装..."
        install_docker_compose
    else
        log_info "Docker Compose 已安装: $(docker-compose --version)"
    fi
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        log_warning "Docker 服务未运行，尝试启动..."
        sudo systemctl start docker
        sudo systemctl enable docker
    fi
    
    log_success "Docker 环境检查完成"
}

# 安装Docker
install_docker() {
    log_info "开始安装 Docker..."
    
    # 更新包索引
    sudo apt-get update -y
    
    # 安装必要的包
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # 添加Docker的官方GPG密钥
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # 设置Docker仓库
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker Engine
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin
    
    # 将用户添加到docker组
    sudo usermod -aG docker $USER
    
    log_success "Docker 安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "开始安装 Docker Compose..."
    
    # 下载最新版本的Docker Compose
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 赋予执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose 安装完成"
}

# 检查系统资源
check_resources() {
    log_step "检查系统资源..."
    
    # 检查内存
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    log_info "系统总内存: ${TOTAL_MEM}MB"
    
    if [ $TOTAL_MEM -lt 4096 ]; then
        log_warning "系统内存不足4GB，可能影响性能"
        log_info "建议内存: 4GB+，当前: ${TOTAL_MEM}MB"
    else
        log_success "内存检查通过: ${TOTAL_MEM}MB"
    fi
    
    # 检查磁盘空间
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    log_info "可用磁盘空间: ${AVAILABLE_SPACE}GB"
    
    if [ $AVAILABLE_SPACE -lt 20 ]; then
        log_warning "可用磁盘空间不足20GB"
        log_info "建议空间: 20GB+，当前: ${AVAILABLE_SPACE}GB"
    else
        log_success "磁盘空间检查通过: ${AVAILABLE_SPACE}GB"
    fi
}

# 使用本地项目进行部署
use_local_project() {
    log_step "使用本地项目进行部署..."
    
    # 检查是否在正确目录
    if [ ! -d "xiaoxuebao-docker" ]; then
        log_error "未找到 xiaoxuebao-docker 目录，请确保在项目根目录执行"
        exit 1
    fi
    
    cd xiaoxuebao-docker
    
    # 检查部署脚本是否存在
    if [ ! -f "scripts/deploy.sh" ]; then
        log_error "未找到部署脚本 scripts/deploy.sh"
        exit 1
    fi
    
    # 赋予执行权限
    chmod +x scripts/deploy.sh
    
    log_success "本地项目准备完成"
}

# 部署应用
deploy_application() {
    log_step "开始部署小雪宝应用..."
    
    # 执行本地部署脚本
    log_info "执行本地部署脚本..."
    ./scripts/deploy.sh
    
    log_success "应用部署完成!"
}

# 显示完成信息
show_completion() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}🎉 小雪宝本地部署成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}🌐 访问地址:${NC}"
    echo -e "   用户前端: ${YELLOW}http://localhost:3000${NC}"
    echo -e "   管理后台: ${YELLOW}http://localhost:3001${NC}"
    echo -e "   API文档:  ${YELLOW}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${BLUE}📊 系统管理:${NC}"
    echo -e "   查看状态: ${YELLOW}docker-compose ps${NC}"
    echo -e "   查看日志: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "   停止服务: ${YELLOW}docker-compose down${NC}"
    echo ""
    echo -e "${BLUE}📝 重要提醒:${NC}"
    echo -e "   1. 首次启动可能需要几分钟下载镜像"
    echo -e "   2. 如需配置AI功能，请编辑 .env 文件"
    echo -e "   3. 生产环境请配置SSL证书和域名"
    echo ""
    echo -e "${PURPLE}❄️ 感谢使用小雪宝！让科技温暖生命，用AI点亮希望！${NC}"
    echo ""
}

# 主函数
main() {
    print_logo
    
    log_info "开始小雪宝本地一键安装流程..."
    
    # 检查是否为root用户
    if [ "$EUID" -eq 0 ]; then
        log_warning "检测到root用户，建议使用普通用户执行"
        read -p "是否继续? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 执行安装步骤
    detect_os
    check_resources
    check_docker
    use_local_project
    deploy_application
    show_completion
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 开始执行
main "$@"