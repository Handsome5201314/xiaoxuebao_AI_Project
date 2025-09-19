from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc, and_, or_
from fastapi import HTTPException, status, Depends

from app.core.database import get_db
from app.models.article import Article, ArticleVersion, ArticleCategory
from app.models.user import User
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse, 
    ArticleListResponse, ArticleVersionCreate, ArticleVersionResponse
)
from app.schemas.user import UserResponse
from app.services.auth import get_current_user_service

class ArticleService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_article(self, article_data: ArticleCreate, user: User) -> Article:
        """创建新文章"""
        # 检查slug是否已存在
        result = await self.db.execute(
            select(Article).where(Article.slug == article_data.slug)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"slug '{article_data.slug}' 已存在"
            )
        
        # 创建文章
        article = Article(
            title=article_data.title,
            slug=article_data.slug,
            content=article_data.content,
            html_content=article_data.html_content,
            summary=article_data.summary,
            author_id=user.id,
            is_published=article_data.is_published,
            allow_comments=article_data.allow_comments,
            meta_title=article_data.meta_title,
            meta_description=article_data.meta_description,
            meta_keywords=article_data.meta_keywords
        )
        
        self.db.add(article)
        await self.db.commit()
        await self.db.refresh(article)
        
        # 创建初始版本
        await self._create_version(article, user, "初始版本")
        
        return article
    
    async def _create_version(self, article: Article, user: User, change_note: str = None) -> ArticleVersion:
        """创建文章版本"""
        version = ArticleVersion(
            article_id=article.id,
            version_number=article.version,
            content=article.content,
            html_content=article.html_content,
            change_note=change_note,
            author_id=user.id
        )
        
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        
        return version
    
    async def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """根据ID获取文章"""
        result = await self.db.execute(
            select(Article).where(Article.id == article_id)
        )
        return result.scalar_one_or_none()
    
    async def get_article_by_slug(self, slug: str) -> Optional[Article]:
        """根据slug获取文章"""
        result = await self.db.execute(
            select(Article).where(Article.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def update_article(self, article_id: int, update_data: ArticleUpdate, user: User) -> Article:
        """更新文章"""
        article = await self.get_article_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
        
        # 检查权限
        if article.author_id != user.id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此文章"
            )
        
        # 更新字段
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(article, field, value)
        
        # 增加版本号
        article.version += 1
        article.updated_at = datetime.utcnow()
        
        # 创建新版本
        await self._create_version(article, user, update_data.change_note)
        
        await self.db.commit()
        await self.db.refresh(article)
        
        return article
    
    async def delete_article(self, article_id: int, user: User) -> bool:
        """删除文章"""
        article = await self.get_article_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
        
        # 检查权限
        if article.author_id != user.id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限删除此文章"
            )
        
        # 软删除
        article.is_deleted = True
        article.deleted_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def list_articles(
        self, 
        page: int = 1, 
        page_size: int = 20,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        is_published: Optional[bool] = None,
        search_query: Optional[str] = None
    ) -> ArticleListResponse:
        """获取文章列表"""
        query = select(Article).where(Article.is_deleted == False)
        
        # 添加过滤条件
        if category_id:
            query = query.where(Article.category_id == category_id)
        if author_id:
            query = query.where(Article.author_id == author_id)
        if is_published is not None:
            query = query.where(Article.is_published == is_published)
        if search_query:
            query = query.where(
                or_(
                    Article.title.ilike(f"%{search_query}%"),
                    Article.content.ilike(f"%{search_query}%"),
                    Article.summary.ilike(f"%{search_query}%")
                )
            )
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.db.execute(count_query)).scalar()
        
        # 分页和排序
        query = query.order_by(desc(Article.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        articles = result.scalars().all()
        
        return ArticleListResponse(
            articles=articles,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=(total_count + page_size - 1) // page_size
        )
    
    async def get_article_versions(self, article_id: int) -> List[ArticleVersion]:
        """获取文章版本历史"""
        result = await self.db.execute(
            select(ArticleVersion)
            .where(ArticleVersion.article_id == article_id)
            .order_by(desc(ArticleVersion.version_number))
        )
        return result.scalars().all()
    
    async def get_article_version(self, article_id: int, version_number: int) -> Optional[ArticleVersion]:
        """获取特定版本的文章"""
        result = await self.db.execute(
            select(ArticleVersion)
            .where(
                and_(
                    ArticleVersion.article_id == article_id,
                    ArticleVersion.version_number == version_number
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def restore_article_version(self, article_id: int, version_number: int, user: User) -> Article:
        """恢复文章到特定版本"""
        article = await self.get_article_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
        
        version = await self.get_article_version(article_id, version_number)
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="版本不存在"
            )
        
        # 恢复内容
        article.content = version.content
        article.html_content = version.html_content
        article.version += 1
        article.updated_at = datetime.utcnow()
        
        # 创建恢复版本
        await self._create_version(article, user, f"恢复到版本 {version_number}")
        
        await self.db.commit()
        await self.db.refresh(article)
        
        return article
    
    async def increment_view_count(self, article_id: int) -> None:
        """增加文章浏览计数"""
        article = await self.get_article_by_id(article_id)
        if article:
            article.view_count += 1
            await self.db.commit()
    
    async def get_related_articles(self, article_id: int, limit: int = 5) -> List[Article]:
        """获取相关文章（基于分类和标签）"""
        article = await self.get_article_by_id(article_id)
        if not article:
            return []
        
        # 简单的基于分类的相关文章推荐
        query = select(Article).where(
            and_(
                Article.id != article_id,
                Article.is_published == True,
                Article.is_deleted == False,
                Article.category_id == article.category_id
            )
        ).order_by(desc(Article.view_count)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

# 依赖注入函数
async def get_article_service(db: AsyncSession = Depends(get_db)) -> ArticleService:
    """获取文章服务实例"""
    return ArticleService(db)