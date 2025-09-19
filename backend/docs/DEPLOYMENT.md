# 小雪宝部署文档

## 📋 概述

本文档详细说明如何部署小雪宝AI助手系统，包括开发环境、测试环境和生产环境的部署配置。

## 🚀 快速部署

### 环境要求

#### 最低配置
- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+)
- **Python**: 3.8+
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **网络**: 稳定的互联网连接

#### 推荐配置
- **操作系统**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **CPU**: 4核心

### 依赖服务
- **PostgreSQL**: 13+
- **Redis**: 6+
- **Elasticsearch**: 8+

## 🛠️ 开发环境部署

### 1. 克隆项目
```bash
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/backend
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

**环境变量配置:**
```bash
# 应用配置
APP_NAME=小雪宝
DEBUG=true
ENVIRONMENT=development

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./xiaoxuebao.db
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-secret-key-for-development
JWT_SECRET=your-jwt-secret-for-development

# 搜索配置
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=xiaoxuebao_wiki_dev
```

### 5. 初始化数据库
```bash
# 运行数据库迁移
alembic upgrade head

# 或直接创建表
python -c "from app.core.database import engine, Base; import asyncio; asyncio.run(engine.begin().run_sync(Base.metadata.create_all))"
```

### 6. 启动服务
```bash
# 开发模式启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 验证部署
```bash
# 检查健康状态
curl http://localhost:8000/health

# 查看API文档
# 访问: http://localhost:8000/docs
```

## 🐳 Docker部署

### 1. 使用Docker Compose

#### 开发环境
```bash
cd xiaoxuebao-docker
docker-compose up -d
```

#### 生产环境
```bash
cd xiaoxuebao-docker
docker-compose -f docker-compose.prod.yml up -d
```

### 2. 环境配置
```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置
nano .env
```

**生产环境配置示例:**
```bash
# 应用配置
APP_NAME=小雪宝
DEBUG=false
ENVIRONMENT=production

# 数据库配置
POSTGRES_DB=xiaoxuebao
POSTGRES_USER=xiaoxuebao
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Elasticsearch配置
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

# 安全配置
SECRET_KEY=your_production_secret_key
JWT_SECRET=your_production_jwt_secret

# AI模型配置
ZHIPU_API_KEY=your_zhipu_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 3. 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 服务访问
- **API服务**: http://localhost:8000
- **前端应用**: http://localhost:3000
- **管理后台**: http://localhost:3001
- **API文档**: http://localhost:8000/docs

## 🏭 生产环境部署

### 1. 服务器准备

#### 系统更新
```bash
sudo apt update && sudo apt upgrade -y
```

#### 安装Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 安装Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. SSL证书配置

#### 使用Let's Encrypt
```bash
# 安装certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown -R $USER:$USER nginx/ssl/
```

### 3. 生产环境配置

#### 更新环境变量
```bash
# 编辑生产环境配置
nano .env

# 重要配置项
SECRET_KEY=your_very_secure_secret_key
JWT_SECRET=your_very_secure_jwt_secret
POSTGRES_PASSWORD=your_very_secure_db_password
REDIS_PASSWORD=your_very_secure_redis_password
```

#### 启动生产服务
```bash
# 使用生产环境配置
docker-compose -f docker-compose.prod.yml up -d

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 4. 数据库备份配置

#### 创建备份脚本
```bash
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="xiaoxuebao_backup_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T postgres pg_dump -U xiaoxuebao xiaoxuebao > "$BACKUP_DIR/$BACKUP_FILE"

# 压缩备份文件
gzip "$BACKUP_DIR/$BACKUP_FILE"

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_FILE.gz"
EOF

chmod +x scripts/backup.sh
```

#### 设置定时备份
```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天凌晨2点备份）
0 2 * * * /path/to/xiaoxuebao-docker/scripts/backup.sh
```

## 📊 监控与维护

### 1. 服务监控

#### 检查服务状态
```bash
# 查看所有服务
docker-compose ps

# 查看特定服务日志
docker-compose logs -f api-gateway
docker-compose logs -f knowledge-service
```

#### 资源监控
```bash
# 查看资源使用情况
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

### 2. 日志管理

#### 查看应用日志
```bash
# 查看所有日志
docker-compose logs

# 查看错误日志
docker-compose logs | grep ERROR

# 实时查看日志
docker-compose logs -f
```

#### 日志轮转配置
```bash
# 配置logrotate
sudo nano /etc/logrotate.d/xiaoxuebao

# 添加配置
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

### 3. 性能优化

#### 数据库优化
```sql
-- 创建索引
CREATE INDEX CONCURRENTLY idx_medical_terms_search 
ON medical_terms USING gin(to_tsvector('chinese', term || ' ' || definition));

CREATE INDEX CONCURRENTLY idx_guidelines_categories 
ON medical_guidelines USING gin(categories);

-- 分析表统计信息
ANALYZE;
```

#### Redis优化
```bash
# 在docker-compose.yml中配置Redis
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

#### Elasticsearch优化
```yaml
# 在elasticsearch.yml中配置
indices.memory.index_buffer_size: 30%
indices.queries.cache.size: 10%
```

## 🔧 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 检查Docker状态
docker system df
docker system prune

# 重新构建镜像
docker-compose build --no-cache
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose exec postgres psql -U xiaoxuebao -d xiaoxuebao -c "SELECT 1;"

# 检查网络连接
docker network ls
docker network inspect xiaoxuebao-docker_xiaoxuebao-network
```

#### 3. 内存不足
```bash
# 检查内存使用
free -h
docker stats

# 调整服务资源限制
# 编辑 docker-compose.yml 中的 deploy.resources
```

#### 4. 磁盘空间不足
```bash
# 检查磁盘使用
df -h
docker system df

# 清理Docker资源
docker system prune -a
docker volume prune
```

### 日志分析

#### 查看错误日志
```bash
# 查看API错误
docker-compose logs api-gateway | grep ERROR

# 查看数据库错误
docker-compose logs postgres | grep ERROR

# 查看搜索服务错误
docker-compose logs elasticsearch | grep ERROR
```

#### 性能分析
```bash
# 查看慢查询
docker-compose exec postgres psql -U xiaoxuebao -d xiaoxuebao -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

## 🔐 安全配置

### 1. 防火墙配置
```bash
# 配置UFW防火墙
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. SSL/TLS配置
```nginx
# 在nginx.conf中配置SSL
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
}
```

### 3. 安全头配置
```nginx
# 添加安全头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## 📞 技术支持

### 获取帮助
1. **查看日志**: `docker-compose logs -f`
2. **检查状态**: `docker-compose ps`
3. **重启服务**: `docker-compose restart`
4. **重新部署**: `docker-compose down && docker-compose up -d`

### 联系支持
- **GitHub Issues**: [项目Issues页面]
- **文档**: 查看 `docs/` 目录
- **社区**: 加入开发者社区

---

*最后更新: 2025年9月19日*
