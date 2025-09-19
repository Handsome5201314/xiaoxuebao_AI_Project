# 小雪宝API文档

## 📋 概述

小雪宝API是一个基于FastAPI构建的RESTful API服务，为白血病知识库系统提供后端支持。

## 🚀 快速开始

### 基础URL
```
开发环境: http://localhost:8000
生产环境: https://api.xiaoxuebao.com
```

### 认证方式
API使用JWT Token进行认证，在请求头中包含：
```
Authorization: Bearer <your_token>
```

## 📚 API端点

### 健康检查

#### GET /health
检查API服务状态

**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-19T00:00:00Z"
}
```

### 知识库管理

#### GET /api/knowledge/categories
获取知识库分类列表

**查询参数:**
- `include_inactive` (boolean, optional): 是否包含未激活分类，默认false

**响应示例:**
```json
[
  {
    "id": 1,
    "name": "白血病指南",
    "slug": "leukemia-guidelines",
    "description": "白血病相关诊疗指南",
    "icon": "book",
    "color": "#ff6b6b",
    "is_active": true,
    "created_at": "2025-09-19T00:00:00Z"
  }
]
```

#### POST /api/knowledge/categories
创建新的知识库分类

**请求体:**
```json
{
  "name": "白血病指南",
  "slug": "leukemia-guidelines",
  "description": "白血病相关诊疗指南",
  "icon": "book",
  "color": "#ff6b6b"
}
```

**响应示例:**
```json
{
  "id": 1,
  "name": "白血病指南",
  "slug": "leukemia-guidelines",
  "description": "白血病相关诊疗指南",
  "icon": "book",
  "color": "#ff6b6b",
  "is_active": true,
  "created_at": "2025-09-19T00:00:00Z"
}
```

#### GET /api/knowledge/categories/{category_id}
获取指定分类详情

**路径参数:**
- `category_id` (integer): 分类ID

#### PUT /api/knowledge/categories/{category_id}
更新分类信息

#### DELETE /api/knowledge/categories/{category_id}
删除分类

### 医学术语管理

#### GET /api/knowledge/terms/search
搜索医学术语

**查询参数:**
- `query` (string, required): 搜索关键词
- `category_id` (integer, optional): 分类ID

**响应示例:**
```json
[
  {
    "id": 1,
    "term": "急性淋巴细胞白血病",
    "slug": "acute-lymphoblastic-leukemia",
    "definition": "一种起源于淋巴细胞的急性白血病",
    "explanation": "ALL是儿童最常见的恶性肿瘤之一",
    "category_id": 1,
    "synonyms": ["ALL", "急性淋巴性白血病"],
    "source": "NCCN指南",
    "created_at": "2025-09-19T00:00:00Z"
  }
]
```

#### POST /api/knowledge/terms
创建医学术语

**请求体:**
```json
{
  "term": "急性淋巴细胞白血病",
  "slug": "acute-lymphoblastic-leukemia",
  "definition": "一种起源于淋巴细胞的急性白血病",
  "explanation": "ALL是儿童最常见的恶性肿瘤之一",
  "category_id": 1,
  "synonyms": ["ALL", "急性淋巴性白血病"],
  "source": "NCCN指南"
}
```

### 知识搜索

#### POST /api/knowledge/search
知识库全文搜索

**请求体:**
```json
{
  "query": "急性淋巴细胞白血病",
  "category_id": 1,
  "limit": 10,
  "offset": 0
}
```

**响应示例:**
```json
{
  "results": [
    {
      "id": 1,
      "title": "急性淋巴细胞白血病诊断指南",
      "content": "ALL的诊断标准...",
      "category": "白血病指南",
      "relevance_score": 0.95,
      "source": "NCCN指南"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

#### POST /api/knowledge/related
获取相关内容推荐

**请求体:**
```json
{
  "content_id": 1,
  "content_type": "term",
  "limit": 5
}
```

### 搜索服务

#### GET /api/search/articles
搜索文章

**查询参数:**
- `query` (string, required): 搜索关键词
- `category` (string, optional): 分类过滤
- `limit` (integer, optional): 结果数量限制，默认20
- `offset` (integer, optional): 偏移量，默认0

**响应示例:**
```json
[
  {
    "id": 1,
    "title": "白血病基础知识",
    "slug": "leukemia-basics",
    "summary": "白血病是一种血液系统恶性肿瘤...",
    "category": "基础知识",
    "author": "张医生",
    "created_at": "2025-09-19T00:00:00Z",
    "relevance_score": 0.92
  }
]
```

### 用户管理

#### POST /api/users/register
用户注册

**请求体:**
```json
{
  "username": "test_user",
  "email": "test@example.com",
  "password": "secure_password",
  "full_name": "测试用户"
}
```

#### POST /api/auth/login
用户登录

**请求体:**
```json
{
  "username": "test_user",
  "password": "secure_password"
}
```

**响应示例:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

## 🔒 认证与授权

### JWT Token
API使用JWT Token进行用户认证，Token包含以下信息：
- `user_id`: 用户ID
- `username`: 用户名
- `role`: 用户角色
- `exp`: 过期时间

### 用户角色
- `admin`: 管理员，拥有所有权限
- `editor`: 编辑者，可以管理内容
- `user`: 普通用户，只能查看内容

### 权限要求
- 创建/更新/删除操作需要认证
- 管理员操作需要admin角色
- 内容管理需要editor或admin角色

## 📊 响应格式

### 成功响应
```json
{
  "data": {...},
  "message": "操作成功",
  "status": "success"
}
```

### 错误响应
```json
{
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "具体错误信息"
  }
}
```

### 分页响应
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## 🚨 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `VALIDATION_ERROR` | 422 | 数据验证失败 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `UNAUTHORIZED` | 401 | 未认证 |
| `FORBIDDEN` | 403 | 权限不足 |
| `INTERNAL_ERROR` | 500 | 内部服务器错误 |
| `CATEGORY_NOT_FOUND` | 404 | 分类不存在 |
| `TERM_NOT_FOUND` | 404 | 术语不存在 |
| `SEARCH_QUERY_INVALID` | 400 | 搜索查询无效 |

## 🔧 开发指南

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 环境变量
```bash
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./xiaoxuebao.db

# Redis配置
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# 搜索配置
ELASTICSEARCH_URL=http://localhost:9200
```

### 测试
```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app tests/
```

## 📈 性能优化

### 缓存策略
- 分类列表缓存：5分钟
- 搜索结果缓存：10分钟
- 用户信息缓存：30分钟

### 数据库优化
- 关键字段建立索引
- 使用连接池
- 查询优化

### 搜索优化
- Elasticsearch索引优化
- 搜索结果缓存
- 分页查询优化

## 🔐 安全考虑

### 数据保护
- 所有敏感数据加密存储
- 密码使用bcrypt哈希
- JWT Token安全配置

### 输入验证
- 所有输入数据验证
- SQL注入防护
- XSS攻击防护

### 访问控制
- API限流
- 用户权限验证
- 操作日志记录

## 📞 技术支持

如有问题，请联系：
- 邮箱: support@xiaoxuebao.com
- GitHub Issues: [项目Issues页面]
- 文档: [项目文档页面]

---

*最后更新: 2025年9月19日*
