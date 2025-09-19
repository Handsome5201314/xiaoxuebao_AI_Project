from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.core.database import get_db
from app.schemas.knowledge import KnowledgeSearchParams
from app.services.knowledge import KnowledgeService, get_knowledge_service

router = APIRouter(prefix="/search", tags=["搜索"])

@router.get("", response_model=Dict[str, Any])
async def search_all(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类slug"),
    type: Optional[str] = Query(None, description="内容类型: article, term, guideline"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("relevance", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向: asc, desc"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """全局搜索"""
    try:
        search_params = KnowledgeSearchParams(
            query=q,
            category=category,
            type=type,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        results = await knowledge_service.search_knowledge(search_params)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )

@router.get("/articles", response_model=Dict[str, Any])
async def search_articles(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类slug"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """搜索文章"""
    try:
        search_params = KnowledgeSearchParams(
            query=q,
            category=category,
            type="article",
            page=page,
            page_size=page_size
        )
        
        results = await knowledge_service.search_knowledge(search_params)
        return {"articles": results.get("articles", []), "total_count": results.get("total_count", 0)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索文章失败: {str(e)}"
        )

@router.get("/terms", response_model=Dict[str, Any])
async def search_terms(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类slug"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """搜索医学术语"""
    try:
        search_params = KnowledgeSearchParams(
            query=q,
            category=category,
            type="term",
            page=page,
            page_size=page_size
        )
        
        results = await knowledge_service.search_knowledge(search_params)
        return {"terms": results.get("terms", []), "total_count": results.get("total_count", 0)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索医学术语失败: {str(e)}"
        )

@router.get("/guidelines", response_model=Dict[str, Any])
async def search_guidelines(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类slug"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """搜索医疗指南"""
    try:
        search_params = KnowledgeSearchParams(
            query=q,
            category=category,
            type="guideline",
            page=page,
            page_size=page_size
        )
        
        results = await knowledge_service.search_knowledge(search_params)
        return {"guidelines": results.get("guidelines", []), "total_count": results.get("total_count", 0)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索医疗指南失败: {str(e)}"
        )

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="搜索建议关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """获取搜索建议"""
    try:
        # 这里可以实现搜索建议逻辑，比如从数据库获取热门搜索词等
        suggestions = [
            {"text": f"{q} 相关文章", "type": "article"},
            {"text": f"{q} 医学术语", "type": "term"},
            {"text": f"{q} 诊疗指南", "type": "guideline"}
        ]
        
        return {"suggestions": suggestions[:limit]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取搜索建议失败: {str(e)}"
        )