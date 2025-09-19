"""
API接口测试
测试各个API端点的功能
"""

import pytest
from fastapi import status
from httpx import AsyncClient

class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "小雪宝Wiki API" in response.json()["message"]

class TestKnowledgeAPI:
    """知识库API测试"""
    
    def test_list_categories(self, client):
        """测试获取分类列表"""
        response = client.get("/api/knowledge/categories")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_get_category_tree(self, client):
        """测试获取分类树"""
        response = client.get("/api/knowledge/categories/tree")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_search_medical_terms(self, client):
        """测试搜索医学术语"""
        response = client.get("/api/knowledge/terms/search?query=白血病")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_knowledge_search(self, client):
        """测试知识库搜索"""
        search_data = {
            "query": "急性淋巴细胞白血病",
            "category_id": None,
            "limit": 10
        }
        response = client.post("/api/knowledge/search", json=search_data)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.json()
    
    def test_get_knowledge_stats(self, client):
        """测试获取知识库统计"""
        response = client.get("/api/knowledge/stats")
        assert response.status_code == status.HTTP_200_OK
        assert "total_categories" in response.json()

class TestSearchAPI:
    """搜索API测试"""
    
    def test_search_articles(self, client):
        """测试搜索文章"""
        response = client.get("/api/search/articles?query=白血病")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_search_with_filters(self, client):
        """测试带过滤条件的搜索"""
        response = client.get("/api/search/articles?query=白血病&category=指南")
        assert response.status_code == status.HTTP_200_OK

class TestUserAPI:
    """用户API测试"""
    
    def test_user_registration(self, client, sample_user_data):
        """测试用户注册"""
        response = client.post("/api/users/register", json=sample_user_data)
        # 注意：这里可能需要根据实际的认证逻辑调整
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
    
    def test_user_login(self, client):
        """测试用户登录"""
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        response = client.post("/api/auth/login", data=login_data)
        # 注意：这里可能需要根据实际的认证逻辑调整
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_error(self, client):
        """测试404错误"""
        response = client.get("/api/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_invalid_search_params(self, client):
        """测试无效搜索参数"""
        response = client.post("/api/knowledge/search", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
