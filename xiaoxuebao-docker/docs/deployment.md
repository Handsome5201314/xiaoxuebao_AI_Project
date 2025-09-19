# 小雪宝Docker化部署文档

## 📋 目录

- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [生产环境部署](#生产环境部署)
- [配置说明](#配置说明)
- [监控和维护](#监控和维护)
- [故障排除](#故障排除)

## 🔧 环境要求

### 最低配置
- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+)
- **Docker**: 20.x 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **CPU**: 2核心

### 推荐配置
- **操作系统**: Ubuntu 22.04 LTS
- **Docker**: 24.x
- **Docker Compose**: 2.20+
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **CPU**: 4核心

## 🚀 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/xiaoxuebao-docker
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置文件
nano .env
```

**重要配置项：**
```bash
# 数据库密码
POSTGRES_PASSWORD=your_secure_password_here
REDIS_PASSWORD=your_redis_password_here

# 安全密钥
SECRET_KEY=your_secret_key_change_in_production
JWT_SECRET=your_jwt_secret_change_in_production

# AI模型配置
ZHIPU_API_KEY=your_zhipu_api_key_here
```

### 3. 一键部署

```bash
# 运行部署脚本
./scripts/deploy.sh

# 或者手动部署
docker-compose up -d
```

### 4. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 健康检查
curl http://localhost:8000/health
```

### 5. 访问应用

- **用户前端**: http://localhost:3000
- **管理后台**: http://localhost:3001
- **API文档**: http://localhost:8000/docs

## 🏭 生产环境部署

### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 配置防火墙
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

### 2. SSL证书配置

```bash
# 使用Let's Encrypt获取免费SSL证书
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown -R $USER:$USER nginx/ssl/
```

### 3. 生产环境配置

```bash
# 使用生产环境配置
docker-compose -f docker-compose.prod.yml up -d

# 配置域名
# 编辑 .env 文件，更新域名配置
NEXT_PUBLIC_API_URL=https://your-domain.com
REACT_APP_API_URL=https://your-domain.com
```

### 4. 数据库备份配置

```bash
# 创建备份脚本
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="xiaoxuebao_backup_$DATE.sql"

docker-compose exec -T postgres pg_dump -U xiaoxuebao xiaoxuebao > "$BACKUP_DIR/$BACKUP_FILE"
gzip "$BACKUP_DIR/$BACKUP_FILE"

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_FILE.gz"
EOF

chmod +x scripts/backup.sh

# 设置定时备份
crontab -e
# 添加: 0 2 * * * /path/to/xiaoxuebao-docker/scripts/backup.sh
```

## ⚙️ 配置说明

### 环境变量详解

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `POSTGRES_PASSWORD` | 数据库密码 | - | ✅ |
| `REDIS_PASSWORD` | Redis密码 | - | ✅ |
| `SECRET_KEY` | 应用密钥 | - | ✅ |
| `JWT_SECRET` | JWT密钥 | - | ✅ |
| `ZHIPU_API_KEY` | 智谱AI密钥 | - | ✅ |
| `DEBUG` | 调试模式 | false | ❌ |
| `LOG_LEVEL` | 日志级别 | INFO | ❌ |

### 服务配置

#### Nginx配置
- 反向代理配置
- SSL证书配置
- 静态资源缓存
- 请求限流

#### 数据库配置
- PostgreSQL连接池
- Redis缓存策略
- Elasticsearch索引配置

#### 应用配置
- 微服务通信
- 负载均衡
- 健康检查

## 📊 监控和维护

### 1. 服务监控

```bash
# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]
```

### 2. 性能监控

```bash
# 启用Prometheus监控
docker-compose --profile monitoring up -d

# 访问监控面板
# http://your-domain.com:9090
```

### 3. 日志管理

```bash
# 查看应用日志
tail -f logs/xiaoxuebao.log

# 查看Nginx日志
tail -f logs/nginx/access.log
tail -f logs/nginx/error.log

# 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete
```

### 4. 数据库维护

```bash
# 数据库备份
./scripts/backup.sh

# 数据库恢复
./scripts/restore.sh backup_file.sql

# 数据库优化
docker-compose exec postgres psql -U xiaoxuebao -d xiaoxuebao -c "VACUUM ANALYZE;"
```

## 🔧 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 检查端口占用
netstat -tulpn | grep :80
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

```bash
# 查看错误日志
docker-compose logs | grep ERROR

# 查看特定服务日志
docker-compose logs api-gateway | tail -100

# 实时监控日志
docker-compose logs -f --tail=50
```

### 性能优化

#### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX CONCURRENTLY idx_articles_title ON articles(title);
CREATE INDEX CONCURRENTLY idx_knowledge_category ON knowledge(category);

-- 分析表统计信息
ANALYZE;
```

#### 2. Redis优化

```bash
# 配置Redis内存策略
# 在 docker-compose.yml 中添加:
# command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

#### 3. Elasticsearch优化

```yaml
# 在 elasticsearch.yml 中配置:
indices.memory.index_buffer_size: 30%
indices.queries.cache.size: 10%
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
