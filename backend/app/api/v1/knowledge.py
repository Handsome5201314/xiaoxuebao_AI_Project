from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.schemas.knowledge import (
    KnowledgeCategoryCreate, KnowledgeCategoryUpdate, KnowledgeCategory,
    MedicalTermCreate, MedicalTermUpdate, MedicalTerm,
    MedicalGuidelineCreate, MedicalGuidelineUpdate, MedicalGuideline,
    KnowledgeSearchParams, RelatedContentRequest, BulkImportRequest,
    KnowledgeStats
)
from app.schemas.user import UserResponse
from app.services.knowledge import KnowledgeService, get_knowledge_service
from app.services.auth import get_current_user_service, get_current_active_user_service, get_current_admin_user_service

router = APIRouter(prefix="/knowledge", tags=["知识库管理"])

# 知识库分类管理
@router.post("/categories", response_model=KnowledgeCategory, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: KnowledgeCategoryCreate,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """创建知识库分类"""
    try:
        category = await knowledge_service.create_category(category_data)
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分类失败: {str(e)}"
        )

@router.get("/categories", response_model=List[KnowledgeCategory])
async def list_categories(
    include_inactive: bool = Query(False, description="是否包含未激活分类"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """获取分类列表"""
    try:
        categories = await knowledge_service.list_categories(include_inactive)
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类列表失败: {str(e)}"
        )

@router.get("/categories/tree", response_model=List[Dict[str, Any]])
async def get_category_tree(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """获取分类树形结构"""
    try:
        tree = await knowledge_service.get_category_tree()
        return tree
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类树失败: {str(e)}"
        )

@router.get("/categories/{category_id}", response_model=KnowledgeCategory)
async def get_category(
    category_id: int,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """根据ID获取分类"""
    category = await knowledge_service.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    return category

@router.put("/categories/{category_id}", response_model=KnowledgeCategory)
async def update_category(
    category_id: int,
    category_data: KnowledgeCategoryUpdate,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """更新分类"""
    try:
        category = await knowledge_service.update_category(category_id, category_data)
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新分类失败: {str(e)}"
        )

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """删除分类"""
    try:
        success = await knowledge_service.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除分类失败"
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分类失败: {str(e)}"
        )

# 医学术语管理
@router.post("/terms", response_model=MedicalTerm, status_code=status.HTTP_201_CREATED)
async def create_medical_term(
    term_data: MedicalTermCreate,
    current_user: UserResponse = Depends(get_current_active_user_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """创建医学术语"""
    try:
        term = await knowledge_service.create_medical_term(term_data)
        return term
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建医学术语失败: {str(e)}"
        )

@router.get("/terms/search", response_model=List[MedicalTerm])
async def search_medical_terms(
    query: str = Query(..., description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """搜索医学术语"""
    try:
        terms = await knowledge_service.search_medical_terms(query, category_id)
        return terms
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索医学术语失败: {str(e)}"
        )

# 医疗指南管理
@router.post("/guidelines", response_model=MedicalGuideline, status_code=status.HTTP_201_CREATED)
async def create_medical_guideline(
    guideline_data: MedicalGuidelineCreate,
    current_user: UserResponse = Depends(get_current_active_user_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """创建医疗指南"""
    try:
        guideline = await knowledge_service.create_medical_guideline(guideline_data)
        return guideline
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建医疗指南失败: {str(e)}"
        )

# 知识搜索
@router.post("/search", response_model=Dict[str, Any])
async def search_knowledge(
    search_params: KnowledgeSearchParams,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """知识库全文搜索"""
    try:
        results = await knowledge_service.search_knowledge(search_params)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )

# 相关内容推荐
@router.post("/related", response_model=Dict[str, Any])
async def get_related_content(
    request: RelatedContentRequest,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """获取相关内容推荐"""
    try:
        results = await knowledge_service.get_related_content(request)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相关内容失败: {str(e)}"
        )

# 批量导入
@router.post("/import", response_model=Dict[str, Any])
async def bulk_import_knowledge(
    import_data: BulkImportRequest,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """批量导入知识数据"""
    try:
        result = await knowledge_service.bulk_import(import_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入失败: {str(e)}"
        )

# 知识库统计
@router.get("/stats", response_model=KnowledgeStats)
async def get_knowledge_stats(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """获取知识库统计信息"""
    try:
        stats = await knowledge_service.get_knowledge_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )

# 文件导入
@router.post("/import/file")
async def import_knowledge_from_file(
    file: UploadFile = File(...),
    import_type: str = Query(..., description="导入类型: terms, guidelines"),
    current_user: UserResponse = Depends(get_current_admin_user_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """从文件导入知识数据"""
    try:
        # 读取文件内容
        content = await file.read()
        # 解析文件内容（这里需要根据实际文件格式实现）
        # 例如：JSON、CSV等格式的解析
        import_data = {"items": [], "import_type": import_type}
        
        result = await knowledge_service.bulk_import(import_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件导入失败: {str(e)}"
        )