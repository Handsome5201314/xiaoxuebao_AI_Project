from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse, 
    ArticleListResponse, ArticleVersionResponse
)
from app.schemas.user import UserResponse
from app.services.article import ArticleService, get_article_service
from app.services.auth import get_current_user_service, get_current_active_user_service

router = APIRouter(prefix="/articles", tags=["文章管理"])

@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    current_user: UserResponse = Depends(get_current_active_user_service),
    article_service: ArticleService = Depends(get_article_service)
):
    """创建新文章"""
    try:
        article = await article_service.create_article(article_data, current_user)
        return article
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建文章失败: {str(e)}"
        )

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    article_service: ArticleService = Depends(get_article_service)
):
    """根据ID获取文章"""
    article = await article_service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 增加浏览计数
    await article_service.increment_view_count(article_id)
    
    return article

@router.get("/slug/{slug}", response_model=ArticleResponse)
async def get_article_by_slug(
    slug: str,
    article_service: ArticleService = Depends(get_article_service)
):
    """根据slug获取文章"""
    article = await article_service.get_article_by_slug(slug)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 增加浏览计数
    await article_service.increment_view_count(article.id)
    
    return article

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: UserResponse = Depends(get_current_active_user_service),
    article_service: ArticleService = Depends(get_article_service)
):
    """更新文章"""
    try:
        article = await article_service.update_article(article_id, article_data, current_user)
        return article
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新文章失败: {str(e)}"
        )

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    current_user: UserResponse = Depends(get_current_active_user_service),
    article_service: ArticleService = Depends(get_article_service)
):
    """删除文章"""
    try:
        success = await article_service.delete_article(article_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除文章失败"
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文章失败: {str(e)}"
        )

@router.get("", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    author_id: Optional[int] = Query(None, description="作者ID"),
    is_published: Optional[bool] = Query(None, description="是否发布"),
    search_query: Optional[str] = Query(None, description="搜索关键词"),
    article_service: ArticleService = Depends(get_article_service)
):
    """获取文章列表"""
    try:
        result = await article_service.list_articles(
            page=page,
            page_size=page_size,
            category_id=category_id,
            author_id=author_id,
            is_published=is_published,
            search_query=search_query
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文章列表失败: {str(e)}"
        )

@router.get("/{article_id}/versions", response_model=List[ArticleVersionResponse])
async def get_article_versions(
    article_id: int,
    article_service: ArticleService = Depends(get_article_service)
):
    """获取文章版本历史"""
    try:
        versions = await article_service.get_article_versions(article_id)
        return versions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取版本历史失败: {str(e)}"
        )

@router.get("/{article_id}/versions/{version_number}", response_model=ArticleVersionResponse)
async def get_article_version(
    article_id: int,
    version_number: int,
    article_service: ArticleService = Depends(get_article_service)
):
    """获取特定版本的文章"""
    version = await article_service.get_article_version(article_id, version_number)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    return version

@router.post("/{article_id}/restore/{version_number}", response_model=ArticleResponse)
async def restore_article_version(
    article_id: int,
    version_number: int,
    current_user: UserResponse = Depends(get_current_active_user_service),
    article_service: ArticleService = Depends(get_article_service)
):
    """恢复文章到特定版本"""
    try:
        article = await article_service.restore_article_version(article_id, version_number, current_user)
        return article
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复版本失败: {str(e)}"
        )

@router.get("/{article_id}/related", response_model=List[ArticleResponse])
async def get_related_articles(
    article_id: int,
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    article_service: ArticleService = Depends(get_article_service)
):
    """获取相关文章"""
    try:
        related_articles = await article_service.get_related_articles(article_id, limit)
        return related_articles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相关文章失败: {str(e)}"
        )