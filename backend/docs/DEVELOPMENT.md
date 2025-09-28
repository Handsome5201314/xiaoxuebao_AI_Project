# 小雪宝AI助手 开发指南

## 📋 概述

本文档为小雪宝AI助手项目的开发者提供详细的开发指南，包括项目结构、开发规范、最佳实践和贡献指南。

## 🏗️ 项目架构

### 技术栈

- **后端框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL 15+ (主数据库)
- **缓存**: Redis 7+ (缓存和会话存储)
- **搜索引擎**: Elasticsearch 8.11+ (全文搜索)
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据验证**: Pydantic 2.0
- **认证**: JWT (JSON Web Tokens)
- **任务队列**: Celery (可选)
- **容器化**: Docker & Docker Compose

### 项目结构

```
backend/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI应用入口
│   ├── api/                      # API路由
│   │   ├── __init__.py
│   │   └── v1/                   # API版本1
│   │       ├── __init__.py
│   │       ├── auth.py           # 认证相关API
│   │       ├── knowledge.py      # 知识库API
│   │       ├── search.py         # 搜索API
│   │       └── users.py          # 用户管理API
│   ├── core/                     # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── cache.py              # 缓存管理
│   │   ├── security.py           # 安全相关
│   │   ├── exceptions.py         # 异常处理
│   │   ├── logging.py            # 日志配置
│   │   ├── container.py          # 依赖注入
│   │   ├── performance_monitor.py # 性能监控
│   │   ├── query_optimizer.py    # 查询优化
│   │   ├── rate_limiter.py       # 限流器
│   │   └── security_enhanced.py  # 增强安全
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py               # 基础模型
│   │   ├── user.py               # 用户模型
│   │   ├── knowledge.py          # 知识库模型
│   │   └── article.py            # 文章模型
│   ├── schemas/                  # Pydantic模式
│   │   ├── __init__.py
│   │   ├── user.py               # 用户模式
│   │   ├── knowledge.py          # 知识库模式
│   │   ├── response.py           # 响应模式
│   │   └── auth.py               # 认证模式
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth.py               # 认证服务
│   │   ├── knowledge.py          # 知识库服务
│   │   ├── search.py             # 搜索服务
│   │   └── user.py               # 用户服务
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── helpers.py            # 辅助函数
│       ├── validators.py         # 验证器
│       └── formatters.py         # 格式化工具
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── conftest.py               # 测试配置
│   ├── test_api_*.py             # API测试
│   ├── test_services_*.py        # 服务测试
│   └── integration/              # 集成测试
├── alembic/                      # 数据库迁移
│   ├── versions/                 # 迁移版本
│   ├── env.py                    # 迁移环境
│   └── script.py.mako            # 迁移模板
├── docs/                         # 文档目录
│   ├── API.md                    # API文档
│   ├── DEPLOYMENT.md             # 部署文档
│   └── DEVELOPMENT.md            # 开发文档
├── scripts/                      # 脚本目录
│   ├── init_data.py              # 初始化数据
│   ├── create_admin.py           # 创建管理员
│   └── backup.sh                 # 备份脚本
├── requirements.txt              # Python依赖
├── Dockerfile                    # Docker配置
├── docker-compose.yml            # Docker Compose配置
├── .env.example                  # 环境变量模板
├── alembic.ini                   # Alembic配置
├── pytest.ini                   # 测试配置
└── run_tests.py                  # 测试运行器
```

## 🚀 开发环境设置

### 1. 环境准备

```bash
# 安装Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 安装Redis
sudo apt install redis-server

# 安装Elasticsearch (可选，用于全文搜索)
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt update && sudo apt install elasticsearch
```

### 2. 项目设置

```bash
# 克隆项目
git clone https://github.com/xiaoxuebao/xiaoxuebao-ai.git
cd xiaoxuebao-ai/backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 3. 数据库设置

```bash
# 创建数据库用户和数据库
sudo -u postgres psql
CREATE USER xiaoxuebao WITH PASSWORD 'your_password';
CREATE DATABASE xiaoxuebao OWNER xiaoxuebao;
GRANT ALL PRIVILEGES ON DATABASE xiaoxuebao TO xiaoxuebao;
\q

# 配置环境变量
cp .env.example .env
# 编辑.env文件，设置数据库连接信息
```

### 4. 运行迁移

```bash
# 初始化Alembic
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 运行迁移
alembic upgrade head
```

### 5. 启动开发服务器

```bash
# 启动API服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用开发脚本
python scripts/run_dev.py
```

## 📝 开发规范

### 代码风格

项目使用以下工具确保代码质量：

- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查
- **bandit**: 安全检查

```bash
# 安装开发工具
pip install black isort flake8 mypy bandit

# 格式化代码
black app/
isort app/

# 检查代码风格
flake8 app/

# 类型检查
mypy app/

# 安全检查
bandit -r app/
```

### 命名规范

1. **文件和目录**: 使用小写字母和下划线 (`snake_case`)
2. **类名**: 使用大驼峰命名 (`PascalCase`)
3. **函数和变量**: 使用小写字母和下划线 (`snake_case`)
4. **常量**: 使用大写字母和下划线 (`UPPER_CASE`)
5. **私有成员**: 以单下划线开头 (`_private`)

### 注释和文档

```python
"""
模块级文档字符串
描述模块的功能和用途
"""

class UserService:
    """
    用户服务类
    
    提供用户相关的业务逻辑处理
    """
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            UserExistsException: 用户已存在时抛出
        """
        # 实现逻辑
        pass
```

### 错误处理

```python
from app.core.exceptions import XiaoxuebaoException

class UserService:
    async def get_user(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise XiaoxuebaoException(
                message="用户不存在",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        return user
```

### 日志记录

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

class UserService:
    async def create_user(self, user_data: UserCreate) -> User:
        logger.info(f"创建用户: {user_data.username}")
        
        try:
            user = await self._create_user_in_db(user_data)
            logger.info(f"用户创建成功: {user.id}")
            return user
        except Exception as e:
            logger.error(f"用户创建失败: {str(e)}")
            raise
```

## 🧪 测试指南

### 测试结构

```
tests/
├── conftest.py                   # 测试配置和fixtures
├── test_api_auth.py              # 认证API测试
├── test_api_knowledge.py         # 知识库API测试
├── test_services_user.py         # 用户服务测试
├── test_services_knowledge.py    # 知识库服务测试
└── integration/                  # 集成测试
    ├── test_user_flow.py         # 用户流程测试
    └── test_knowledge_flow.py    # 知识库流程测试
```

### 编写测试

```python
import pytest
from httpx import AsyncClient
from app.main import app

class TestUserAPI:
    """用户API测试"""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, async_client: AsyncClient):
        """测试成功创建用户"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        response = await async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "password" not in data
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, async_client: AsyncClient):
        """测试创建重复用户名的用户"""
        # 先创建一个用户
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "testpass123"
        }
        await async_client.post("/api/v1/users/", json=user_data)
        
        # 尝试创建相同用户名的用户
        duplicate_data = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpass456"
        }
        
        response = await async_client.post("/api/v1/users/", json=duplicate_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "已存在" in data["message"]
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api_auth.py

# 运行特定测试方法
pytest tests/test_api_auth.py::TestAuthAPI::test_login_success

# 生成覆盖率报告
pytest --cov=app tests/

# 生成HTML覆盖率报告
pytest --cov=app --cov-report=html tests/

# 使用测试运行器
python run_tests.py --type unit --coverage --verbose
```

## 🔧 开发工具

### IDE配置

推荐使用VS Code，配置文件 `.vscode/settings.json`：

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### Git Hooks

设置pre-commit钩子：

```bash
# 安装pre-commit
pip install pre-commit

# 创建.pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
EOF

# 安装钩子
pre-commit install
```

### 调试配置

VS Code调试配置 `.vscode/launch.json`：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/venv/bin/uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

## 📚 最佳实践

### 1. 异步编程

```python
# 正确的异步服务方法
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

### 2. 依赖注入

```python
from app.core.container import container, inject

@injectable(ServiceLifetime.SCOPED)
class UserService:
    def __init__(self, db: AsyncSession, cache: CacheManager):
        self.db = db
        self.cache = cache

# 在API中使用
@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(create_dependency(UserService))
):
    return await user_service.get_user(user_id)
```

### 3. 缓存策略

```python
from app.core.cache import cached

class KnowledgeService:
    @cached(ttl=3600, key_prefix="categories")
    async def get_categories(self) -> List[KnowledgeCategory]:
        result = await self.db.execute(select(KnowledgeCategory))
        return result.scalars().all()
```

### 4. 性能监控

```python
from app.core.performance_monitor import monitor_performance

class KnowledgeService:
    @monitor_performance
    async def search_terms(self, query: str) -> List[MedicalTerm]:
        # 搜索逻辑
        pass
```

## 🤝 贡献指南

### 提交代码

1. **Fork项目**到你的GitHub账户
2. **创建功能分支**: `git checkout -b feature/new-feature`
3. **提交更改**: `git commit -am 'Add new feature'`
4. **推送分支**: `git push origin feature/new-feature`
5. **创建Pull Request**

### 提交信息规范

使用约定式提交格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(auth): add JWT token refresh functionality

- Implement token refresh endpoint
- Add refresh token validation
- Update authentication middleware

Closes #123
```

### 代码审查

Pull Request需要满足：

1. 所有测试通过
2. 代码覆盖率不低于80%
3. 通过代码风格检查
4. 至少一个维护者审查通过
5. 更新相关文档

## 📞 技术支持

如有开发相关问题：

- **文档**: 查看项目文档
- **Issues**: 在GitHub上创建Issue
- **讨论**: 参与GitHub Discussions
- **邮箱**: dev@xiaoxuebao.com

---

*最后更新: 2024年1月1日*
