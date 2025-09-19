# 小雪宝 Docker 部署脚本 - PowerShell 版本
# 适用于 Windows 系统
# 使用方法: .\scripts\deploy.ps1

param(
    [string]$Environment = "development",
    [switch]$Clean = $false,
    [switch]$BuildOnly = $false
)

# 颜色输出函数
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info {
    param([string]$Message)
    Write-ColoredOutput "[INFO] $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColoredOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "[ERROR] $Message" "Red"
}

function Write-Step {
    param([string]$Message)
    Write-ColoredOutput "[STEP] $Message" "Magenta"
}

# 显示Logo
function Show-Logo {
    Write-ColoredOutput "┌─────────────────────────────────────────────┐" "Blue"
    Write-ColoredOutput "│  小雪宝 (LeukemiaPal) - Docker 部署脚本     │" "Blue"
    Write-ColoredOutput "│  🐳 白血病AI关爱助手 - 微服务架构           │" "Blue"
    Write-ColoredOutput "│  ❄️  让科技温暖生命，用AI点亮希望          │" "Blue"
    Write-ColoredOutput "└─────────────────────────────────────────────┘" "Blue"
    Write-Host ""
}

# 检查Docker环境
function Test-DockerEnvironment {
    Write-Step "检查Docker环境..."
    
    # 检查Docker是否安装
    try {
        $dockerVersion = docker --version
        Write-Info "Docker版本: $dockerVersion"
    }
    catch {
        Write-Error "Docker未安装，请先安装Docker Desktop for Windows"
        Write-Info "下载地址: https://www.docker.com/products/docker-desktop/"
        exit 1
    }
    
    # 检查Docker Compose是否安装
    try {
        $composeVersion = docker-compose --version
        Write-Info "Docker Compose版本: $composeVersion"
    }
    catch {
        Write-Error "Docker Compose未安装，请升级Docker Desktop"
        exit 1
    }
    
    # 检查Docker服务状态
    try {
        docker info | Out-Null
        Write-Success "Docker服务运行正常"
    }
    catch {
        Write-Error "Docker服务未运行，请启动Docker Desktop"
        exit 1
    }
}

# 检查系统资源
function Test-SystemResources {
    Write-Step "检查系统资源..."
    
    # 检查内存
    $memory = Get-WmiObject -Class Win32_ComputerSystem
    $totalMemoryGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
    Write-Info "系统总内存: ${totalMemoryGB}GB"
    
    if ($totalMemoryGB -lt 4) {
        Write-Warning "系统内存不足4GB，可能影响性能"
    }
    else {
        Write-Success "内存检查通过: ${totalMemoryGB}GB"
    }
    
    # 检查磁盘空间
    $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
    Write-Info "C盘可用空间: ${freeSpaceGB}GB"
    
    if ($freeSpaceGB -lt 20) {
        Write-Warning "C盘可用空间不足20GB"
    }
    else {
        Write-Success "磁盘空间检查通过: ${freeSpaceGB}GB"
    }
}

# 创建必要目录
function New-RequiredDirectories {
    Write-Step "创建必要目录..."
    
    $directories = @(
        "nginx\ssl",
        "database\init", 
        "database\migrations",
        "logs",
        "backups",
        "uploads"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Info "创建目录: $dir"
        }
    }
    
    Write-Success "目录创建完成"
}

# 设置环境变量
function Set-Environment {
    Write-Step "配置环境变量..."
    
    if (!(Test-Path ".env")) {
        if (Test-Path "env.example") {
            Copy-Item "env.example" ".env"
            Write-Info "已创建.env文件，请编辑配置"
        }
        else {
            Write-Error "未找到env.example文件"
            exit 1
        }
    }
    
    # 生成随机密钥 (PowerShell方式)
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "your_secret_key_change_in_production") {
        $secretKey = [System.Web.Security.Membership]::GeneratePassword(64, 0)
        $jwtSecret = [System.Web.Security.Membership]::GeneratePassword(64, 0)
        
        $envContent = $envContent -replace "your_secret_key_change_in_production", $secretKey
        $envContent = $envContent -replace "your_jwt_secret_change_in_production", $jwtSecret
        
        Set-Content ".env" $envContent
        Write-Info "已生成随机密钥"
    }
    
    Write-Success "环境变量配置完成"
}

# 构建镜像
function Build-Images {
    Write-Step "构建Docker镜像..."
    
    try {
        docker-compose build --parallel
        Write-Success "镜像构建完成"
    }
    catch {
        Write-Error "镜像构建失败"
        exit 1
    }
}

# 启动服务
function Start-Services {
    Write-Step "启动服务..."
    
    try {
        # 清理旧容器（如果指定了Clean参数）
        if ($Clean) {
            Write-Info "清理旧容器和数据..."
            docker-compose down -v
        }
        
        # 启动基础服务
        Write-Info "启动基础服务..."
        docker-compose up -d postgres redis elasticsearch
        
        # 等待基础服务就绪
        Write-Info "等待基础服务启动（30秒）..."
        Start-Sleep -Seconds 30
        
        # 启动应用服务
        Write-Info "启动应用服务..."
        docker-compose up -d
        
        Write-Success "服务启动完成"
    }
    catch {
        Write-Error "服务启动失败"
        exit 1
    }
}

# 检查服务状态
function Test-Services {
    Write-Step "检查服务状态..."
    
    # 等待服务完全启动
    Start-Sleep -Seconds 60
    
    # 检查容器状态
    $services = @("nginx", "web-app", "web-admin", "api-gateway", "knowledge-service")
    
    foreach ($service in $services) {
        $status = docker-compose ps $service 2>$null
        if ($status -match "Up") {
            Write-Success "$service 服务运行正常"
        }
        else {
            Write-Warning "$service 服务状态异常"
        }
    }
    
    # 检查API健康状态
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "API服务健康检查通过"
        }
    }
    catch {
        Write-Warning "API服务健康检查失败"
    }
}

# 显示部署信息
function Show-DeploymentInfo {
    Write-Success "部署完成！"
    Write-Host ""
    Write-ColoredOutput "🌐 访问地址：" "Blue"
    Write-Host "   用户前端: http://localhost:3000"
    Write-Host "   管理后台: http://localhost:3001"
    Write-Host "   API文档: http://localhost:8000/docs"
    Write-Host ""
    Write-ColoredOutput "📊 服务状态：" "Blue"
    docker-compose ps
    Write-Host ""
    Write-ColoredOutput "📝 常用命令：" "Blue"
    Write-Host "   查看日志: docker-compose logs -f [服务名]"
    Write-Host "   重启服务: docker-compose restart [服务名]"
    Write-Host "   停止服务: docker-compose down"
    Write-Host "   更新服务: docker-compose pull && docker-compose up -d"
    Write-Host ""
    Write-ColoredOutput "⚠️  重要提醒：" "Yellow"
    Write-Host "   1. 请及时修改.env文件中的默认密码"
    Write-Host "   2. 生产环境请配置SSL证书"
    Write-Host "   3. 定期备份数据库"
    Write-Host ""
}

# 主函数
function Main {
    Show-Logo
    
    Write-Info "开始部署小雪宝Docker化版本..."
    Write-Info "部署环境: $Environment"
    
    # 确保当前目录正确
    if (!(Test-Path "docker-compose.yml")) {
        Write-Error "请在项目根目录下运行此脚本"
        exit 1
    }
    
    # 执行部署步骤
    Test-DockerEnvironment
    Test-SystemResources
    New-RequiredDirectories
    Set-Environment
    
    if (!$BuildOnly) {
        Build-Images
        Start-Services
        Test-Services
        Show-DeploymentInfo
    }
    else {
        Build-Images
        Write-Success "仅构建完成！"
    }
}

# 错误处理
$ErrorActionPreference = "Stop"

# 开始执行
try {
    Main
}
catch {
    Write-Error "部署过程中发生错误: $($_.Exception.Message)"
    exit 1
}
