from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc, and_, or_
from fastapi import HTTPException, status, UploadFile

from app.core.database import get_db
from app.models.knowledge import (
    KnowledgeCategory, MedicalTerm, MedicalGuideline,
    ArticleCategory, KnowledgeGraphNode, KnowledgeGraphEdge
)
from app.models.article import Article
from app.schemas.knowledge import (
    KnowledgeCategoryCreate, KnowledgeCategoryUpdate, MedicalTermCreate,
    MedicalTermUpdate, MedicalGuidelineCreate, MedicalGuidelineUpdate,
    KnowledgeSearchParams, RelatedContentRequest, BulkImportRequest
)
from app.services.auth import get_current_user_service

class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # 知识库分类管理
    async def create_category(self, category_data: KnowledgeCategoryCreate) -> KnowledgeCategory:
        """创建知识库分类"""
        # 检查名称是否已存在
        result = await self.db.execute(
            select(KnowledgeCategory).where(KnowledgeCategory.name == category_data.name)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分类名称 '{category_data.name}' 已存在"
            )
        
        # 生成slug
        slug = self._generate_slug(category_data.name)
        
        category = KnowledgeCategory(
            name=category_data.name,
            slug=slug,
            description=category_data.description,
            icon=category_data.icon,
            color=category_data.color,
            sort_order=category_data.sort_order,
            parent_id=category_data.parent_id
        )
        
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        
        return category
    
    async def get_category(self, category_id: int) -> Optional[KnowledgeCategory]:
        """根据ID获取分类"""
        result = await self.db.execute(
            select(KnowledgeCategory).where(KnowledgeCategory.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_category_by_slug(self, slug: str) -> Optional[KnowledgeCategory]:
        """根据slug获取分类"""
        result = await self.db.execute(
            select(KnowledgeCategory).where(KnowledgeCategory.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def update_category(self, category_id: int, update_data: KnowledgeCategoryUpdate) -> KnowledgeCategory:
        """更新分类"""
        category = await self.get_category(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(category, field, value)
        
        # 如果名称改变，更新slug
        if 'name' in update_dict:
            category.slug = self._generate_slug(update_dict['name'])
        
        category.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(category)
        
        return category
    
    async def delete_category(self, category_id: int) -> bool:
        """删除分类"""
        category = await self.get_category(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        
        # 检查是否有子分类
        result = await self.db.execute(
            select(KnowledgeCategory).where(KnowledgeCategory.parent_id == category_id)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法删除包含子分类的分类"
            )
        
        # 检查是否有文章关联
        result = await self.db.execute(
            select(ArticleCategory).where(ArticleCategory.category_id == category_id)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法删除有关联文章的分类"
            )
        
        await self.db.delete(category)
        await self.db.commit()
        return True
    
    async def list_categories(self, include_inactive: bool = False) -> List[KnowledgeCategory]:
        """获取分类列表"""
        query = select(KnowledgeCategory)
        if not include_inactive:
            query = query.where(KnowledgeCategory.is_active == True)
        
        query = query.order_by(KnowledgeCategory.sort_order, KnowledgeCategory.name)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_category_tree(self) -> List[Dict[str, Any]]:
        """获取分类树形结构"""
        categories = await self.list_categories(include_inactive=True)
        return self._build_category_tree(categories)
    
    def _build_category_tree(self, categories: List[KnowledgeCategory]) -> List[Dict[str, Any]]:
        """构建分类树形结构"""
        category_dict = {cat.id: {"category": cat, "children": []} for cat in categories}
        tree = []
        
        for cat in categories:
            if cat.parent_id is None:
                tree.append(category_dict[cat.id])
            else:
                parent = category_dict.get(cat.parent_id)
                if parent:
                    parent["children"].append(category_dict[cat.id])
        
        return tree
    
    # 医学术语管理
    async def create_medical_term(self, term_data: MedicalTermCreate) -> MedicalTerm:
        """创建医学术语"""
        # 检查术语是否已存在
        result = await self.db.execute(
            select(MedicalTerm).where(MedicalTerm.term == term_data.term)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"医学术语 '{term_data.term}' 已存在"
            )
        
        # 生成slug
        slug = self._generate_slug(term_data.term)
        
        term = MedicalTerm(
            term=term_data.term,
            slug=slug,
            definition=term_data.definition,
            explanation=term_data.explanation,
            synonyms=term_data.synonyms,
            related_terms=term_data.related_terms,
            source=term_data.source,
            category_id=term_data.category_id
        )
        
        self.db.add(term)
        await self.db.commit()
        await self.db.refresh(term)
        
        return term
    
    async def get_medical_term(self, term_id: int) -> Optional[MedicalTerm]:
        """根据ID获取医学术语"""
        result = await self.db.execute(
            select(MedicalTerm).where(MedicalTerm.id == term_id)
        )
        return result.scalar_one_or_none()
    
    async def search_medical_terms(self, query: str, category_id: Optional[int] = None) -> List[MedicalTerm]:
        """搜索医学术语"""
        search_query = select(MedicalTerm).where(
            or_(
                MedicalTerm.term.ilike(f"%{query}%"),
                MedicalTerm.definition.ilike(f"%{query}%"),
                MedicalTerm.explanation.ilike(f"%{query}%")
            )
        )
        
        if category_id:
            search_query = search_query.where(MedicalTerm.category_id == category_id)
        
        search_query = search_query.order_by(desc(MedicalTerm.created_at))
        result = await self.db.execute(search_query)
        return result.scalars().all()
    
    # 医疗指南管理
    async def create_medical_guideline(self, guideline_data: MedicalGuidelineCreate) -> MedicalGuideline:
        """创建医疗指南"""
        # 检查标题是否已存在
        result = await self.db.execute(
            select(MedicalGuideline).where(MedicalGuideline.title == guideline_data.title)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"指南标题 '{guideline_data.title}' 已存在"
            )
        
        # 生成slug
        slug = self._generate_slug(guideline_data.title)
        
        guideline = MedicalGuideline(
            title=guideline_data.title,
            slug=slug,
            content=guideline_data.content,
            source_organization=guideline_data.source_organization,
            version=guideline_data.version,
            publish_date=datetime.utcnow()
        )
        
        self.db.add(guideline)
        await self.db.commit()
        await self.db.refresh(guideline)
        
        return guideline
    
    # 知识搜索功能
    async def search_knowledge(self, search_params: KnowledgeSearchParams) -> Dict[str, Any]:
        """知识库全文搜索"""
        results = {
            "articles": [],
            "terms": [],
            "guidelines": [],
            "total_count": 0
        }
        
        # 搜索文章
        if not search_params.type or search_params.type == "article":
            article_query = select(Article).where(
                and_(
                    Article.is_published == True,
                    Article.is_deleted == False,
                    or_(
                        Article.title.ilike(f"%{search_params.query}%"),
                        Article.content.ilike(f"%{search_params.query}%"),
                        Article.summary.ilike(f"%{search_params.query}%")
                    )
                )
            )
            
            if search_params.category:
                category = await self.get_category_by_slug(search_params.category)
                if category:
                    article_query = article_query.where(Article.category_id == category.id)
            
            article_query = article_query.order_by(desc(Article.created_at))
            article_result = await self.db.execute(article_query)
            results["articles"] = article_result.scalars().all()
        
        # 搜索医学术语
        if not search_params.type or search_params.type == "term":
            term_results = await self.search_medical_terms(search_params.query)
            results["terms"] = term_results
        
        # 计算总数
        results["total_count"] = len(results["articles"]) + len(results["terms"]) + len(results["guidelines"])
        
        return results
    
    # 相关内容推荐
    async def get_related_content(self, request: RelatedContentRequest) -> Dict[str, Any]:
        """获取相关内容推荐"""
        related_items = []
        
        if request.content_type == "article":
            # 基于文章分类和标签的推荐
            article = await self.db.get(Article, request.content_id)
            if article:
                # 简单实现：同分类的其他文章
                related_articles = await self.db.execute(
                    select(Article)
                    .where(
                        and_(
                            Article.id != request.content_id,
                            Article.is_published == True,
                            Article.is_deleted == False,
                            Article.category_id == article.category_id
                        )
                    )
                    .order_by(desc(Article.view_count))
                    .limit(request.max_results)
                )
                related_items = related_articles.scalars().all()
        
        return {
            "items": related_items,
            "total_count": len(related_items),
            "max_similarity": 0.8,  # 模拟相似度
            "min_similarity": 0.3
        }
    
    # 批量导入功能
    async def bulk_import(self, import_data: BulkImportRequest) -> Dict[str, Any]:
        """批量导入知识数据"""
        success_count = 0
        error_count = 0
        errors = []
        
        for item in import_data.items:
            try:
                if import_data.import_type == "terms":
                    term_data = MedicalTermCreate(**item)
                    await self.create_medical_term(term_data)
                    success_count += 1
                
                elif import_data.import_type == "guidelines":
                    guideline_data = MedicalGuidelineCreate(**item)
                    await self.create_medical_guideline(guideline_data)
                    success_count += 1
                
                else:
                    errors.append({
                        "item": item,
                        "error": f"不支持的导入类型: {import_data.import_type}"
                    })
                    error_count += 1
                    
            except Exception as e:
                errors.append({
                    "item": item,
                    "error": str(e)
                })
                error_count += 1
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }
    
    # 工具函数
    def _generate_slug(self, text: str) -> str:
        """生成URL友好的slug"""
        # 转换为小写
        slug = text.lower()
        # 替换中文空格和特殊字符
        slug = re.sub(r'[\s\u3000]+', '-', slug)
        # 移除特殊字符
        slug = re.sub(r'[^\w\-]', '', slug)
        # 移除连续的连字符
        slug = re.sub(r'-+', '-', slug)
        # 移除首尾的连字符
        slug = slug.strip('-')
        
        return slug
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        # 文章统计
        article_count = await self.db.scalar(
            select(func.count(Article.id)).where(
                and_(
                    Article.is_published == True,
                    Article.is_deleted == False
                )
            )
        )
        
        # 术语统计
        term_count = await self.db.scalar(select(func.count(MedicalTerm.id)))
        
        # 指南统计
        guideline_count = await self.db.scalar(select(func.count(MedicalGuideline.id)))
        
        # 分类统计
        category_count = await self.db.scalar(
            select(func.count(KnowledgeCategory.id)).where(KnowledgeCategory.is_active == True)
        )
        
        # 最近添加统计
        recent_articles = await self.db.scalar(
            select(func.count(Article.id)).where(
                Article.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        )
        
        recent_terms = await self.db.scalar(
            select(func.count(MedicalTerm.id)).where(
                MedicalTerm.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        )
        
        return {
            "total_articles": article_count or 0,
            "total_terms": term_count or 0,
            "total_guidelines": guideline_count or 0,
            "total_categories": category_count or 0,
            "recently_added": {
                "articles": recent_articles or 0,
                "terms": recent_terms or 0,
                "total": (recent_articles or 0) + (recent_terms or 0)
            }
        }

# 依赖注入函数
async def get_knowledge_service(db: AsyncSession = Depends(get_db)) -> KnowledgeService:
    """获取知识库服务实例"""
    return KnowledgeService(db)