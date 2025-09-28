"""
知识库API测试
测试知识库相关的API端点
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


class TestKnowledgeAPI:
    """知识库API测试类"""
    
    def test_create_category_success(self, client: TestClient, test_data_factory):
        """测试成功创建分类"""
        category_data = test_data_factory.create_category_data("API测试分类")
        
        response = client.post("/api/v1/knowledge/categories", json=category_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["name"] == "API测试分类"
    
    def test_create_category_validation_error(self, client: TestClient):
        """测试创建分类验证错误"""
        invalid_data = {"name": ""}  # 空名称
        
        response = client.post("/api/v1/knowledge/categories", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"
        assert "validation_errors" in data
    
    def test_get_categories_list(self, client: TestClient, setup_test_data):
        """测试获取分类列表"""
        response = client.get("/api/v1/knowledge/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
    
    def test_get_category_by_id(self, client: TestClient, setup_test_data):
        """测试根据ID获取分类"""
        category = setup_test_data["category"]
        
        response = client.get(f"/api/v1/knowledge/categories/{category.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == category.id
        assert data["data"]["name"] == category.name
    
    def test_get_category_not_found(self, client: TestClient):
        """测试获取不存在的分类"""
        response = client.get("/api/v1/knowledge/categories/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert "不存在" in data["message"]
    
    def test_update_category(self, client: TestClient, setup_test_data):
        """测试更新分类"""
        category = setup_test_data["category"]
        update_data = {"name": "更新后的分类名称", "description": "更新后的描述"}
        
        response = client.put(f"/api/v1/knowledge/categories/{category.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["name"] == "更新后的分类名称"
        assert data["data"]["description"] == "更新后的描述"
    
    def test_delete_category(self, client: TestClient, test_data_factory, db_session):
        """测试删除分类"""
        # 创建一个可删除的分类
        from app.models.knowledge import KnowledgeCategory
        category_data = test_data_factory.create_category_data("可删除分类")
        category = KnowledgeCategory(**category_data)
        db_session.add(category)
        db_session.commit()
        
        response = client.delete(f"/api/v1/knowledge/categories/{category.id}")
        
        assert response.status_code == 204
    
    def test_create_medical_term(self, client: TestClient, setup_test_data, test_data_factory):
        """测试创建医学术语"""
        category = setup_test_data["category"]
        term_data = test_data_factory.create_medical_term_data("API测试术语")
        term_data["category_id"] = category.id
        
        response = client.post("/api/v1/knowledge/terms", json=term_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["term"] == "API测试术语"
        assert data["data"]["category_id"] == category.id
    
    def test_search_medical_terms(self, client: TestClient, setup_test_data):
        """测试搜索医学术语"""
        term = setup_test_data["term"]
        
        response = client.get(f"/api/v1/knowledge/terms/search?query={term.term[:3]}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
    
    def test_search_medical_terms_with_category(self, client: TestClient, setup_test_data):
        """测试按分类搜索医学术语"""
        term = setup_test_data["term"]
        category = setup_test_data["category"]
        
        response = client.get(f"/api/v1/knowledge/terms/search?query=术语&category_id={category.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
    
    def test_knowledge_search(self, client: TestClient, setup_test_data):
        """测试知识库全文搜索"""
        search_data = {
            "query": "术语",
            "type": "term",
            "limit": 10
        }
        
        response = client.post("/api/v1/knowledge/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "terms" in data["data"]
        assert "total_count" in data["data"]
    
    def test_get_related_content(self, client: TestClient, setup_test_data):
        """测试获取相关内容"""
        term = setup_test_data["term"]
        
        related_data = {
            "content_type": "term",
            "content_id": term.id,
            "max_results": 5
        }
        
        response = client.post("/api/v1/knowledge/related", json=related_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "items" in data["data"]
        assert "total_count" in data["data"]
    
    def test_bulk_import_terms(self, client: TestClient, setup_test_data, test_data_factory):
        """测试批量导入术语"""
        category = setup_test_data["category"]
        
        import_data = {
            "import_type": "terms",
            "items": [
                {
                    **test_data_factory.create_medical_term_data("批量API术语1"),
                    "category_id": category.id
                },
                {
                    **test_data_factory.create_medical_term_data("批量API术语2"),
                    "category_id": category.id
                }
            ]
        }
        
        response = client.post("/api/v1/knowledge/import", json=import_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["success_count"] == 2
        assert data["data"]["error_count"] == 0
    
    def test_get_knowledge_stats(self, client: TestClient, setup_test_data):
        """测试获取知识库统计"""
        response = client.get("/api/v1/knowledge/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "total_categories" in data["data"]
        assert "total_terms" in data["data"]
        assert "recently_added" in data["data"]
    
    def test_get_category_tree(self, client: TestClient, setup_test_data):
        """测试获取分类树"""
        response = client.get("/api/v1/knowledge/categories/tree")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)


class TestKnowledgeAPIAuthentication:
    """知识库API认证测试"""
    
    def test_create_category_requires_admin(self, client: TestClient, test_data_factory):
        """测试创建分类需要管理员权限"""
        category_data = test_data_factory.create_category_data("需要权限的分类")
        
        # 不提供认证信息
        response = client.post("/api/v1/knowledge/categories", json=category_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"
        assert "认证" in data["message"] or "unauthorized" in data["message"].lower()
    
    def test_update_category_requires_admin(self, client: TestClient, setup_test_data):
        """测试更新分类需要管理员权限"""
        category = setup_test_data["category"]
        update_data = {"name": "需要权限更新"}
        
        response = client.put(f"/api/v1/knowledge/categories/{category.id}", json=update_data)
        
        assert response.status_code == 401
    
    def test_delete_category_requires_admin(self, client: TestClient, setup_test_data):
        """测试删除分类需要管理员权限"""
        category = setup_test_data["category"]
        
        response = client.delete(f"/api/v1/knowledge/categories/{category.id}")
        
        assert response.status_code == 401


class TestKnowledgeAPIRateLimit:
    """知识库API限流测试"""
    
    @pytest.mark.asyncio
    async def test_search_rate_limit(self, async_client: AsyncClient, setup_test_data):
        """测试搜索API限流"""
        # 快速发送多个请求
        responses = []
        for i in range(35):  # 超过限制的30次
            response = await async_client.get(f"/api/v1/knowledge/terms/search?query=test{i}")
            responses.append(response)
        
        # 检查是否有限流响应
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "应该触发限流"


class TestKnowledgeAPIPerformance:
    """知识库API性能测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_search_requests(self, async_client: AsyncClient, setup_test_data, performance_test_config):
        """测试并发搜索请求"""
        import asyncio
        import time
        
        async def search_request():
            start_time = time.time()
            response = await async_client.get("/api/v1/knowledge/terms/search?query=术语")
            end_time = time.time()
            return response, end_time - start_time
        
        # 并发请求
        tasks = [search_request() for _ in range(performance_test_config["concurrent_requests"])]
        results = await asyncio.gather(*tasks)
        
        # 检查所有请求都成功
        for response, duration in results:
            assert response.status_code == 200
            assert duration < performance_test_config["max_response_time"]
    
    def test_large_category_list_performance(self, client: TestClient, db_session, test_data_factory, performance_test_config):
        """测试大量分类列表的性能"""
        import time
        
        # 创建大量分类
        from app.models.knowledge import KnowledgeCategory
        categories = []
        for i in range(100):
            category_data = test_data_factory.create_category_data(f"性能测试分类{i}")
            category = KnowledgeCategory(**category_data)
            categories.append(category)
        
        db_session.add_all(categories)
        db_session.commit()
        
        # 测试性能
        start_time = time.time()
        response = client.get("/api/v1/knowledge/categories")
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < performance_test_config["max_response_time"]
        
        data = response.json()
        assert len(data["data"]) >= 100
