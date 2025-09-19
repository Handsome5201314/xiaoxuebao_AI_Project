"""
测试配置文件
提供测试用的数据库、客户端等配置
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

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
