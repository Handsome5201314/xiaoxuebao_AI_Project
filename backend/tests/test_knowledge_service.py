"""
知识库服务测试
测试知识库相关的业务逻辑
"""

import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.knowledge import KnowledgeService
from app.models.knowledge import KnowledgeCategory, MedicalTerm
from app.schemas.knowledge import KnowledgeCategoryCreate, MedicalTermCreate
from app.core.exceptions import XiaoxuebaoException


class TestKnowledgeService:
    """知识库服务测试类"""
    
    @pytest.mark.asyncio
    async def test_create_category_success(self, knowledge_service: KnowledgeService, test_data_factory):
        """测试成功创建分类"""
        category_data = KnowledgeCategoryCreate(**test_data_factory.create_category_data("新分类"))
        
        category = await knowledge_service.create_category(category_data)
        
        assert category is not None
        assert category.name == "新分类"
        assert category.slug == "新分类"  # 简化的slug生成
        assert category.description == "新分类的描述"
    
    @pytest.mark.asyncio
    async def test_create_category_duplicate_name(self, knowledge_service: KnowledgeService, setup_test_data, test_data_factory):
        """测试创建重复名称的分类"""
        existing_category = setup_test_data["category"]
        category_data = KnowledgeCategoryCreate(**test_data_factory.create_category_data(existing_category.name))
        
        with pytest.raises(XiaoxuebaoException) as exc_info:
            await knowledge_service.create_category(category_data)
        
        assert exc_info.value.error_code == "CATEGORY_NAME_EXISTS"
    
    @pytest.mark.asyncio
    async def test_get_category_by_id(self, knowledge_service: KnowledgeService, setup_test_data):
        """测试根据ID获取分类"""
        existing_category = setup_test_data["category"]
        
        category = await knowledge_service.get_category(existing_category.id)
        
        assert category is not None
        assert category.id == existing_category.id
        assert category.name == existing_category.name
    
    @pytest.mark.asyncio
    async def test_get_category_not_found(self, knowledge_service: KnowledgeService):
        """测试获取不存在的分类"""
        category = await knowledge_service.get_category(999)
        
        assert category is None
    
    @pytest.mark.asyncio
    async def test_list_categories_with_cache(self, knowledge_service: KnowledgeService, setup_test_data, mock_cache_manager):
        """测试获取分类列表（带缓存）"""
        with patch('app.services.knowledge.cache_manager', mock_cache_manager):
            categories = await knowledge_service.list_categories()
            
            assert len(categories) >= 1
            assert any(cat.name == setup_test_data["category"].name for cat in categories)
            
            # 验证缓存调用
            mock_cache_manager.get.assert_called()
            mock_cache_manager.set.assert_called()
    
    @pytest.mark.asyncio
    async def test_list_categories_include_inactive(self, knowledge_service: KnowledgeService, db_session, test_data_factory):
        """测试获取分类列表包含未激活的"""
        # 创建未激活的分类
        inactive_category_data = test_data_factory.create_category_data("未激活分类")
        inactive_category = KnowledgeCategory(**inactive_category_data, is_active=False)
        db_session.add(inactive_category)
        await db_session.commit()
        
        # 不包含未激活的
        active_categories = await knowledge_service.list_categories(include_inactive=False)
        inactive_names = [cat.name for cat in active_categories if not cat.is_active]
        assert "未激活分类" not in inactive_names
        
        # 包含未激活的
        all_categories = await knowledge_service.list_categories(include_inactive=True)
        all_names = [cat.name for cat in all_categories]
        assert "未激活分类" in all_names
    
    @pytest.mark.asyncio
    async def test_create_medical_term_success(self, knowledge_service: KnowledgeService, setup_test_data, test_data_factory):
        """测试成功创建医学术语"""
        category = setup_test_data["category"]
        term_data = test_data_factory.create_medical_term_data("新术语")
        term_data["category_id"] = category.id
        
        term_create = MedicalTermCreate(**term_data)
        term = await knowledge_service.create_medical_term(term_create)
        
        assert term is not None
        assert term.term == "新术语"
        assert term.category_id == category.id
        assert term.definition == "新术语的定义"
    
    @pytest.mark.asyncio
    async def test_create_medical_term_duplicate(self, knowledge_service: KnowledgeService, setup_test_data, test_data_factory):
        """测试创建重复的医学术语"""
        existing_term = setup_test_data["term"]
        term_data = test_data_factory.create_medical_term_data(existing_term.term)
        term_data["category_id"] = existing_term.category_id
        
        term_create = MedicalTermCreate(**term_data)
        
        with pytest.raises(XiaoxuebaoException) as exc_info:
            await knowledge_service.create_medical_term(term_create)
        
        assert "已存在" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_search_medical_terms(self, knowledge_service: KnowledgeService, setup_test_data):
        """测试搜索医学术语"""
        existing_term = setup_test_data["term"]
        
        # 搜索术语名称
        results = await knowledge_service.search_medical_terms(existing_term.term[:3])
        assert len(results) >= 1
        assert any(term.term == existing_term.term for term in results)
        
        # 搜索定义
        results = await knowledge_service.search_medical_terms("定义")
        assert len(results) >= 1
        
        # 按分类搜索
        results = await knowledge_service.search_medical_terms("术语", existing_term.category_id)
        assert len(results) >= 1
    
    @pytest.mark.asyncio
    async def test_search_medical_terms_no_results(self, knowledge_service: KnowledgeService):
        """测试搜索医学术语无结果"""
        results = await knowledge_service.search_medical_terms("不存在的术语")
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_get_category_tree(self, knowledge_service: KnowledgeService, db_session, test_data_factory):
        """测试获取分类树形结构"""
        # 创建父分类
        parent_data = test_data_factory.create_category_data("父分类")
        parent_category = KnowledgeCategory(**parent_data)
        db_session.add(parent_category)
        await db_session.flush()
        
        # 创建子分类
        child_data = test_data_factory.create_category_data("子分类")
        child_data["parent_id"] = parent_category.id
        child_category = KnowledgeCategory(**child_data)
        db_session.add(child_category)
        await db_session.commit()
        
        tree = await knowledge_service.get_category_tree()
        
        assert len(tree) >= 1
        # 验证树形结构
        parent_node = next((node for node in tree if node["category"].name == "父分类"), None)
        assert parent_node is not None
        assert len(parent_node["children"]) >= 1
        assert parent_node["children"][0]["category"].name == "子分类"
    
    @pytest.mark.asyncio
    async def test_delete_category_with_children(self, knowledge_service: KnowledgeService, db_session, test_data_factory):
        """测试删除有子分类的分类"""
        # 创建父分类
        parent_data = test_data_factory.create_category_data("父分类删除测试")
        parent_category = KnowledgeCategory(**parent_data)
        db_session.add(parent_category)
        await db_session.flush()
        
        # 创建子分类
        child_data = test_data_factory.create_category_data("子分类删除测试")
        child_data["parent_id"] = parent_category.id
        child_category = KnowledgeCategory(**child_data)
        db_session.add(child_category)
        await db_session.commit()
        
        with pytest.raises(XiaoxuebaoException) as exc_info:
            await knowledge_service.delete_category(parent_category.id)
        
        assert "子分类" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_knowledge_stats(self, knowledge_service: KnowledgeService, setup_test_data):
        """测试获取知识库统计信息"""
        stats = await knowledge_service.get_knowledge_stats()
        
        assert "total_categories" in stats
        assert "total_terms" in stats
        assert "total_guidelines" in stats
        assert "recently_added" in stats
        
        assert stats["total_categories"] >= 1
        assert stats["total_terms"] >= 1
    
    @pytest.mark.asyncio
    async def test_bulk_import_terms(self, knowledge_service: KnowledgeService, setup_test_data, test_data_factory):
        """测试批量导入术语"""
        category = setup_test_data["category"]
        
        import_data = {
            "import_type": "terms",
            "items": [
                {
                    **test_data_factory.create_medical_term_data("批量术语1"),
                    "category_id": category.id
                },
                {
                    **test_data_factory.create_medical_term_data("批量术语2"),
                    "category_id": category.id
                }
            ]
        }
        
        from app.schemas.knowledge import BulkImportRequest
        bulk_request = BulkImportRequest(**import_data)
        
        result = await knowledge_service.bulk_import(bulk_request)
        
        assert result["success_count"] == 2
        assert result["error_count"] == 0
    
    @pytest.mark.asyncio
    async def test_bulk_import_with_errors(self, knowledge_service: KnowledgeService, setup_test_data, test_data_factory):
        """测试批量导入包含错误的数据"""
        existing_term = setup_test_data["term"]
        
        import_data = {
            "import_type": "terms",
            "items": [
                {
                    **test_data_factory.create_medical_term_data("新批量术语"),
                    "category_id": existing_term.category_id
                },
                {
                    **test_data_factory.create_medical_term_data(existing_term.term),  # 重复术语
                    "category_id": existing_term.category_id
                }
            ]
        }
        
        from app.schemas.knowledge import BulkImportRequest
        bulk_request = BulkImportRequest(**import_data)
        
        result = await knowledge_service.bulk_import(bulk_request)
        
        assert result["success_count"] == 1
        assert result["error_count"] == 1
        assert len(result["errors"]) == 1


class TestKnowledgeServicePerformance:
    """知识库服务性能测试"""
    
    @pytest.mark.asyncio
    async def test_search_performance(self, knowledge_service: KnowledgeService, setup_test_data, performance_test_config):
        """测试搜索性能"""
        import time
        
        start_time = time.time()
        results = await knowledge_service.search_medical_terms("术语")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < performance_test_config["max_response_time"]
    
    @pytest.mark.asyncio
    async def test_list_categories_performance(self, knowledge_service: KnowledgeService, performance_test_config):
        """测试分类列表性能"""
        import time
        
        start_time = time.time()
        categories = await knowledge_service.list_categories()
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < performance_test_config["max_response_time"]
