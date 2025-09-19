# 小雪宝 (LeukemiaPal) - Docker化部署版本

[![Docker](https://img.shields.io/badge/Docker-20.x+-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub stars](https://img.shields.io/github/stars/Handsome5201314/xiaoxuebao_AI_Project.svg)](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/stargazers)

## 🎯 项目概述

**小雪宝Docker化版本**是基于原小雪宝项目，采用类似PandaWiki的微服务架构，支持一键部署的Docker化白血病AI关爱助手系统。

### 🌟 核心特性

- **🐳 一键部署**: 基于Docker Compose，支持Linux+Docker20+环境
- **🏗️ 微服务架构**: 分布式设计，高可用性和可扩展性
- **🤖 AI驱动**: 集成RAG技术，提供智能问答服务
- **👶 儿童关爱**: 专门的儿童白血病支持模块
- **🏥 医生工具**: 专业医疗知识检索和文献查询
- **🔒 隐私保护**: 零主动数据收集，严格隐私保护

## 🚀 快速开始

### ⚡ 极速部署（推荐）

#### 🐧 Linux/macOS 用户

对于初次使用者，我们推荐使用一键部署脚本：

```bash
# 复制粘贴执行即可，无需任何配置！
curl -fsSL https://raw.githubusercontent.com/Handsome5201314/xiaoxuebao_AI_Project/main/xiaoxuebao-docker/scripts/install.sh | bash
```

或者手动克隆并执行：

```bash
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/xiaoxuebao-docker
chmod +x scripts/deploy.sh && ./scripts/deploy.sh
```

#### 🪟 Windows 用户

请先安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)，然后：

```powershell
# 在 PowerShell 中执行
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/xiaoxuebao-docker
.\scripts\deploy.ps1
```

**部署完成后访问**: http://localhost:3000 🎉

### 环境要求

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+)
- **Docker**: 20.x 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **内存**: 最少 4GB RAM
- **存储**: 最少 20GB 可用空间

### 一键部署

#### 🎯 自动化部署脚本

我们提供了智能部署脚本，可以自动检查环境、配置服务并启动所有组件：

```bash
# 🚀 超级简单：真正的一键部署
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/xiaoxuebao-docker
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

#### 📋 部署脚本功能

部署脚本会自动执行以下操作：

- ✅ **环境检查**: 自动检测Docker版本和系统资源
- ✅ **依赖安装**: 确保所有必需的依赖已安装
- ✅ **配置生成**: 自动生成安全密钥和环境配置
- ✅ **服务构建**: 并行构建所有Docker镜像
- ✅ **有序启动**: 按依赖关系顺序启动服务
- ✅ **健康检查**: 验证所有服务运行正常
- ✅ **访问提示**: 显示所有访问地址和管理命令

#### 🛠️ 自定义部署选项

```bash
# 开发环境部署
./scripts/deploy.sh development

# 生产环境部署  
./scripts/deploy.sh production

# 仅构建镜像（不启动服务）
./scripts/deploy.sh development --build-only

# 重新部署（清理旧数据）
./scripts/deploy.sh production --clean
```

#### 📝 手动部署步骤

如果您需要更多控制，也可以手动执行：

```bash
# 1. 克隆项目
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/xiaoxuebao-docker

# 2. 环境检查
docker --version && docker-compose --version

# 3. 配置环境变量
cp env.example .env
# 编辑 .env 文件，配置AI API密钥等参数

# 4. 创建必要目录
mkdir -p nginx/ssl database/{init,migrations} logs backups uploads

# 5. 启动基础服务
docker-compose up -d postgres redis elasticsearch

# 6. 等待基础服务就绪（约30秒）
sleep 30

# 7. 启动应用服务
docker-compose up -d

# 8. 检查服务状态
docker-compose ps
curl -f http://localhost:8000/health
```

#### 🌍 访问地址

部署完成后，您可以访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🖥️ **用户前端** | http://localhost:3000 | 主要的用户界面，类似PandaWiki |
| 👑 **管理后台** | http://localhost:3001 | 管理员控制面板 |
| 📚 **API文档** | http://localhost:8000/docs | FastAPI自动生成的API文档 |
| 📊 **监控面板** | http://localhost:3000/monitoring | 系统监控和状态页面 |

#### ⚡ 快速验证

```bash
# 检查所有服务状态
docker-compose ps

# 验证前端是否正常
curl -I http://localhost:3000

# 验证API是否正常
curl http://localhost:8000/health

# 查看实时日志
docker-compose logs -f web-app api-gateway
```

#### 🔧 故障排除

```bash
# 如果部署失败，查看日志
docker-compose logs

# 重启特定服务
docker-compose restart [service-name]

# 完全重新部署
docker-compose down
docker-compose up -d

# 清理并重建
docker-compose down -v
docker system prune -f
./scripts/deploy.sh production --clean
```

## 🏗️ 架构设计

### 微服务组件

| 服务名称 | 端口 | 描述 | 技术栈 |
|---------|------|------|--------|
| nginx | 80, 443 | 反向代理和负载均衡 | Nginx |
| web-app | 3000 | 用户前端应用 | Next.js |
| web-admin | 3001 | 管理后台 | React |
| api-gateway | 8000 | API网关 | FastAPI |
| knowledge-service | 8001 | 知识库服务 | FastAPI |
| search-service | 8002 | 搜索服务 | FastAPI |
| user-service | 8003 | 用户服务 | FastAPI |
| postgres | 5432 | 主数据库 | PostgreSQL |
| redis | 6379 | 缓存服务 | Redis |
| elasticsearch | 9200 | 搜索引擎 | Elasticsearch |

### 数据流架构

```
用户请求 → Nginx → Web前端/管理后台
                ↓
            API Gateway → 微服务集群
                ↓
        数据库层 (PostgreSQL + Redis + Elasticsearch)
```

## 📁 项目结构

```
xiaoxuebao-docker/
├── docker-compose.yml          # Docker编排文件
├── docker-compose.prod.yml     # 生产环境配置
├── .env.example                # 环境变量示例
├── nginx/                      # Nginx配置
│   ├── nginx.conf
│   └── ssl/                    # SSL证书目录
├── services/                   # 微服务目录
│   ├── api-gateway/            # API网关
│   ├── knowledge-service/      # 知识库服务
│   ├── search-service/         # 搜索服务
│   └── user-service/           # 用户服务
├── frontend/                   # 前端应用
│   ├── web-app/               # 用户前端 (Next.js)
│   └── web-admin/             # 管理后台 (React)
├── database/                   # 数据库相关
│   ├── init/                  # 初始化脚本
│   └── migrations/            # 数据库迁移
├── scripts/                   # 部署脚本
│   ├── deploy.sh              # 部署脚本
│   ├── backup.sh              # 备份脚本
│   └── restore.sh             # 恢复脚本
└── docs/                      # 文档
    ├── deployment.md          # 部署文档
    ├── api.md                 # API文档
    └── troubleshooting.md     # 故障排除
```

## ⚙️ 配置说明

### 环境变量配置

```bash
# 应用配置
APP_NAME=小雪宝
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
POSTGRES_DB=xiaoxuebao
POSTGRES_USER=xiaoxuebao
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Elasticsearch配置
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

# AI模型配置
LLM_API_KEY=your_llm_api_key
EMBEDDING_MODEL=text-embedding-ada-002

# 安全配置
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret
```

## 🔧 开发指南

### 本地开发

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec [service_name] bash

# 重启服务
docker-compose restart [service_name]
```

### 生产部署

```bash
# 生产环境部署
docker-compose -f docker-compose.prod.yml up -d

# 配置SSL证书
cp your-ssl-cert.crt nginx/ssl/
cp your-ssl-key.key nginx/ssl/

# 设置定时备份
crontab -e
# 添加: 0 2 * * * /path/to/scripts/backup.sh
```

## 📊 监控和维护

### 健康检查

```bash
# 检查所有服务状态
docker-compose ps

# 检查服务健康状态
curl http://localhost:8000/health

# 查看资源使用情况
docker stats
```

### 日志管理

```bash
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs [service_name]

# 实时查看日志
docker-compose logs -f [service_name]
```

### 备份和恢复

```bash
# 备份数据库
./scripts/backup.sh

# 恢复数据库
./scripts/restore.sh backup_file.sql
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 开发环境设置

1. Fork 本仓库
2. 克隆到本地: `git clone [your-fork-url]`
3. 创建开发分支: `git checkout -b feature/your-feature`
4. 启动开发环境: `docker-compose -f docker-compose.dev.yml up -d`
5. 进行开发和测试
6. 提交更改: `git commit -m "Add your feature"`
7. 推送分支: `git push origin feature/your-feature`
8. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 (Python) 和 ESLint (JavaScript) 规范
- 编写清晰的注释和文档
- 添加适当的测试用例
- 确保Docker镜像构建成功

## 📞 技术支持

### 常见问题

1. **服务启动失败**: 检查端口占用和资源使用情况
2. **数据库连接失败**: 检查数据库配置和网络连接
3. **AI功能不可用**: 检查LLM API配置和网络连接

### 获取帮助

- **GitHub Issues**: [项目Issues页面]
- **文档**: 查看 `docs/` 目录下的详细文档
- **社区**: 加入我们的开发者社区

## ⚠️ 重要声明

**医疗免责声明**: 本项目提供的所有信息仅供参考和教育目的，不能替代专业医生的诊断和治疗建议。

**隐私保护**: 我们严格遵守"零主动数据收集"原则，所有用户数据都进行匿名化处理。

## 📄 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🚀 快速链接

### 📦 一键部署脚本

```bash
# 🐧 Linux/macOS 用户（推荐）
curl -fsSL https://raw.githubusercontent.com/Handsome5201314/xiaoxuebao_AI_Project/main/xiaoxuebao-docker/scripts/install.sh | bash

# 🐧 或者手动执行（Linux/macOS）
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/xiaoxuebao-docker
chmod +x scripts/deploy.sh && ./scripts/deploy.sh
```

```powershell
# 🪟 Windows 用户
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/xiaoxuebao-docker
.\scripts\deploy.ps1
```

### 🔗 重要命令速查

```bash
# 🚀 启动所有服务
docker-compose up -d

# 📊 查看服务状态  
docker-compose ps

# 📝 查看日志
docker-compose logs -f

# 🛑 停止所有服务
docker-compose down

# 🔄 重启服务
docker-compose restart

# 🗑️ 清理并重建
docker-compose down -v && docker-compose up -d

# 📱 访问应用
open http://localhost:3000  # 或在浏览器中打开
```

### 📞 获取帮助

| 场景 | 解决方案 |
|------|----------|
| 🐛 **遇到问题** | [提交Issue](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/issues) |
| 📖 **查看文档** | [部署文档](docs/deployment.md) \| [API文档](docs/api.md) |
| 💬 **功能建议** | [发起讨论](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/discussions) |
| 🤝 **参与贡献** | [贡献指南](#-贡献指南) |

### 🎯 项目亮点

- ✅ **真正的一键部署** - 3行命令即可运行
- ✅ **PandaWiki级别的UI** - 现代化可视界面  
- ✅ **微服务架构** - 高可用、易扩展
- ✅ **Docker原生支持** - 跨平台部署
- ✅ **完整的AI功能** - RAG智能问答
- ✅ **生产就绪** - 监控、日志、备份

---

*让科技温暖生命，用AI点亮希望* ✨

*最后更新: 2025年9月19日*
