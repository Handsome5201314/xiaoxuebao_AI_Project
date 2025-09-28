"""
测试配置文件
提供测试用的数据库、客户端等配置
"""

import pytest
import asyncio
import tempfile
import os
from typing import AsyncGenerator, Generator, Dict, Any
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.core.cache import cache_manager
from app.core.container import container
from app.services.knowledge import KnowledgeService
from app.services.user import UserService
from app.services.auth import AuthService

# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_xiaoxuebao.db"

# 创建测试数据库引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

# 创建测试会话
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    """创建测试数据库会话"""
    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # 清理表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def async_client():
    """创建异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password",
        "full_name": "Test User"
    }

@pytest.fixture
def sample_knowledge_category():
    """示例知识库分类数据"""
    return {
        "name": "测试分类",
        "slug": "test-category",
        "description": "测试分类描述",
        "icon": "test-icon",
        "color": "#ff0000"
    }

@pytest.fixture
def sample_medical_term():
    """示例医学术语数据"""
    return {
        "term": "急性淋巴细胞白血病",
        "slug": "acute-lymphoblastic-leukemia",
        "definition": "一种起源于淋巴细胞的急性白血病",
        "explanation": "ALL是儿童最常见的恶性肿瘤之一",
        "category_id": 1,
        "synonyms": ["ALL", "急性淋巴性白血病"],
        "source": "NCCN指南"
    }

@pytest.fixture
def mock_cache_manager():
    """模拟缓存管理器"""
    mock_cache = Mock()
    mock_cache.get = AsyncMock(return_value=None)
    mock_cache.set = AsyncMock(return_value=True)
    mock_cache.delete = AsyncMock(return_value=True)
    mock_cache.exists = AsyncMock(return_value=False)
    mock_cache.clear_pattern = AsyncMock(return_value=0)
    mock_cache.get_stats = Mock(return_value={
        "hits": 0,
        "misses": 0,
        "hit_rate": 0.0,
        "memory_cache_size": 0
    })
    return mock_cache

@pytest.fixture
def mock_redis():
    """模拟Redis客户端"""
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    mock_redis.exists = AsyncMock(return_value=0)
    mock_redis.keys = AsyncMock(return_value=[])
    return mock_redis

@pytest.fixture
async def knowledge_service(db_session):
    """知识库服务实例"""
    return KnowledgeService(db_session)

@pytest.fixture
async def user_service(db_session):
    """用户服务实例"""
    return UserService(db_session)

@pytest.fixture
async def auth_service(db_session):
    """认证服务实例"""
    return AuthService(db_session)

@pytest.fixture
def test_data_factory():
    """测试数据工厂"""
    class TestDataFactory:
        @staticmethod
        def create_user_data(username: str = "testuser", email: str = "test@example.com") -> Dict[str, Any]:
            return {
                "username": username,
                "email": email,
                "password": "TestPassword123!",
                "full_name": f"Test User {username}",
                "is_active": True
            }

        @staticmethod
        def create_category_data(name: str = "测试分类") -> Dict[str, Any]:
            return {
                "name": name,
                "description": f"{name}的描述",
                "icon": "test-icon",
                "color": "#ff0000",
                "sort_order": 1
            }

        @staticmethod
        def create_medical_term_data(term: str = "测试术语") -> Dict[str, Any]:
            return {
                "term": term,
                "definition": f"{term}的定义",
                "explanation": f"{term}的详细解释",
                "synonyms": [f"{term}同义词"],
                "source": "测试来源"
            }

        @staticmethod
        def create_article_data(title: str = "测试文章") -> Dict[str, Any]:
            return {
                "title": title,
                "content": f"{title}的内容",
                "summary": f"{title}的摘要",
                "is_published": True,
                "tags": ["测试", "文章"]
            }

    return TestDataFactory()

@pytest.fixture
async def setup_test_data(db_session, test_data_factory):
    """设置测试数据"""
    from app.models.knowledge import KnowledgeCategory, MedicalTerm
    from app.models.user import User

    # 创建测试分类
    category_data = test_data_factory.create_category_data()
    category = KnowledgeCategory(**category_data)
    db_session.add(category)
    await db_session.flush()

    # 创建测试用户
    user_data = test_data_factory.create_user_data()
    user = User(**user_data)
    db_session.add(user)
    await db_session.flush()

    # 创建测试术语
    term_data = test_data_factory.create_medical_term_data()
    term_data["category_id"] = category.id
    term = MedicalTerm(**term_data)
    db_session.add(term)
    await db_session.flush()

    await db_session.commit()

    return {
        "category": category,
        "user": user,
        "term": term
    }

@pytest.fixture
def performance_test_config():
    """性能测试配置"""
    return {
        "max_response_time": 1.0,  # 最大响应时间（秒）
        "concurrent_requests": 10,  # 并发请求数
        "test_duration": 30,       # 测试持续时间（秒）
        "acceptable_error_rate": 0.01  # 可接受的错误率
    }
