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

### 环境要求

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+)
- **Docker**: 20.x 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **内存**: 最少 4GB RAM
- **存储**: 最少 20GB 可用空间

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/xiaoxuebao-docker

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的参数

# 3. 启动所有服务
docker-compose up -d

# 4. 等待服务启动完成
docker-compose logs -f

# 5. 访问应用
# 前端: http://localhost:3000
# 管理后台: http://localhost:3001
# API文档: http://localhost:8000/docs
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

---

*让科技温暖生命，用AI点亮希望* ✨

*最后更新: 2025年9月19日*
