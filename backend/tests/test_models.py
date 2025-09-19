"""
数据模型测试
测试数据库模型的功能
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import KnowledgeCategory, MedicalTerm, MedicalGuideline
from app.models.user import User
from app.models.article import Article

class TestKnowledgeCategory:
    """知识库分类模型测试"""
    
    @pytest.mark.asyncio
    async def test_create_category(self, db_session: AsyncSession, sample_knowledge_category):
        """测试创建分类"""
        category = KnowledgeCategory(**sample_knowledge_category)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        
        assert category.id is not None
        assert category.name == sample_knowledge_category["name"]
        assert category.slug == sample_knowledge_category["slug"]
    
    @pytest.mark.asyncio
    async def test_category_relationships(self, db_session: AsyncSession):
        """测试分类关系"""
        # 创建父分类
        parent = KnowledgeCategory(
            name="血液病",
            slug="hematology",
            description="血液系统疾病"
        )
        db_session.add(parent)
        await db_session.commit()
        await db_session.refresh(parent)
        
        # 创建子分类
        child = KnowledgeCategory(
            name="白血病",
            slug="leukemia",
            description="白血病相关",
            parent_id=parent.id
        )
        db_session.add(child)
        await db_session.commit()
        await db_session.refresh(child)
        
        assert child.parent_id == parent.id
        assert parent in child.parent

class TestMedicalTerm:
    """医学术语模型测试"""
    
    @pytest.mark.asyncio
    async def test_create_medical_term(self, db_session: AsyncSession, sample_medical_term):
        """测试创建医学术语"""
        # 先创建分类
        category = KnowledgeCategory(
            name="白血病",
            slug="leukemia",
            description="白血病相关术语"
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        
        # 创建医学术语
        term_data = sample_medical_term.copy()
        term_data["category_id"] = category.id
        term = MedicalTerm(**term_data)
        db_session.add(term)
        await db_session.commit()
        await db_session.refresh(term)
        
        assert term.id is not None
        assert term.term == sample_medical_term["term"]
        assert term.category_id == category.id
        assert term.category == category
    
    @pytest.mark.asyncio
    async def test_medical_term_synonyms(self, db_session: AsyncSession):
        """测试医学术语同义词"""
        term = MedicalTerm(
            term="急性淋巴细胞白血病",
            slug="acute-lymphoblastic-leukemia",
            definition="一种急性白血病",
            synonyms=["ALL", "急性淋巴性白血病"],
            related_terms=["白血病", "淋巴细胞"]
        )
        db_session.add(term)
        await db_session.commit()
        await db_session.refresh(term)
        
        assert "ALL" in term.synonyms
        assert "白血病" in term.related_terms

class TestMedicalGuideline:
    """医疗指南模型测试"""
    
    @pytest.mark.asyncio
    async def test_create_guideline(self, db_session: AsyncSession):
        """测试创建医疗指南"""
        guideline = MedicalGuideline(
            title="NCCN急性淋巴细胞白血病指南",
            slug="nccn-all-guidelines",
            content="NCCN指南内容...",
            source_organization="NCCN",
            version="2024.1",
            categories=["白血病", "ALL", "指南"]
        )
        db_session.add(guideline)
        await db_session.commit()
        await db_session.refresh(guideline)
        
        assert guideline.id is not None
        assert guideline.title == "NCCN急性淋巴细胞白血病指南"
        assert "白血病" in guideline.categories
        assert guideline.is_current == True

class TestUser:
    """用户模型测试"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession, sample_user_data):
        """测试创建用户"""
        user = User(**sample_user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
        assert user.is_active == True
    
    @pytest.mark.asyncio
    async def test_user_password_hashing(self, db_session: AsyncSession):
        """测试用户密码哈希"""
        user = User(
            username="test_user",
            email="test@example.com",
            password="plain_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 密码应该被哈希
        assert user.password != "plain_password"
        assert len(user.password) > 20  # 哈希后的密码应该更长

class TestArticle:
    """文章模型测试"""
    
    @pytest.mark.asyncio
    async def test_create_article(self, db_session: AsyncSession):
        """测试创建文章"""
        article = Article(
            title="白血病基础知识",
            slug="leukemia-basics",
            content="白血病是一种血液系统恶性肿瘤...",
            summary="白血病基础知识介绍",
            author_id=1,
            category_id=1
        )
        db_session.add(article)
        await db_session.commit()
        await db_session.refresh(article)
        
        assert article.id is not None
        assert article.title == "白血病基础知识"
        assert article.is_published == False  # 默认未发布
