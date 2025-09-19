from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# 知识库分类模型
class KnowledgeCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    parent_id: Optional[int] = None

class KnowledgeCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None

class KnowledgeCategory(KnowledgeCategoryBase):
    id: int
    slug: str
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 关系字段
    parent: Optional['KnowledgeCategory'] = None
    children: Optional[List['KnowledgeCategory']] = None
    article_count: Optional[int] = None
    
    class Config:
        from_attributes = True

# 医学术语模型
class MedicalTermBase(BaseModel):
    term: str = Field(..., min_length=1, max_length=300)
    definition: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    synonyms: Optional[List[str]] = None
    related_terms: Optional[List[str]] = None
    source: Optional[str] = None
    is_approved: bool = False

class MedicalTermCreate(MedicalTermBase):
    category_id: Optional[int] = None

class MedicalTermUpdate(BaseModel):
    term: Optional[str] = Field(None, min_length=1, max_length=300)
    definition: Optional[str] = None
    explanation: Optional[str] = None
    synonyms: Optional[List[str]] = None
    related_terms: Optional[List[str]] = None
    source: Optional[str] = None
    is_approved: Optional[bool] = None
    category_id: Optional[int] = None

class MedicalTerm(MedicalTermBase):
    id: int
    slug: str
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 关系字段
    category: Optional[KnowledgeCategory] = None
    
    class Config:
        from_attributes = True

# 医疗指南模型
class MedicalGuidelineBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    source_organization: Optional[str] = None
    version: Optional[str] = None
    categories: Optional[List[str]] = None
    is_current: bool = True

class MedicalGuidelineCreate(MedicalGuidelineBase):
    pass

class MedicalGuidelineUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    source_organization: Optional[str] = None
    version: Optional[str] = None
    categories: Optional[List[str]] = None
    is_current: Optional[bool] = None

class MedicalGuideline(MedicalGuidelineBase):
    id: int
    slug: str
    publish_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 知识图谱模型
class KnowledgeGraphNodeBase(BaseModel):
    node_type: str
    node_id: int
    title: str = Field(..., min_length=1, max_length=500)
    content_summary: Optional[str] = None

class KnowledgeGraphNodeCreate(KnowledgeGraphNodeBase):
    vector_embedding: Optional[List[float]] = None

class KnowledgeGraphNode(KnowledgeGraphNodeBase):
    id: int
    vector_embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class KnowledgeGraphEdgeBase(BaseModel):
    source_node_id: int
    target_node_id: int
    relationship_type: str
    weight: float = 1.0
    description: Optional[str] = None

class KnowledgeGraphEdgeCreate(KnowledgeGraphEdgeBase):
    pass

class KnowledgeGraphEdge(KnowledgeGraphEdgeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 搜索和推荐模型
class KnowledgeSearchParams(BaseModel):
    query: str
    category: Optional[str] = None
    type: Optional[str] = None  # article, term, guideline
    page: int = 1
    page_size: int = 20
    sort_by: str = "relevance"
    sort_order: str = "desc"

class RelatedContentRequest(BaseModel):
    content_id: int
    content_type: str  # article, term, guideline
    max_results: int = 10
    min_similarity: float = 0.3

class RelatedContentResponse(BaseModel):
    items: List[Dict[str, Any]]
    total_count: int
    max_similarity: float
    min_similarity: float

# 知识库统计
class KnowledgeStats(BaseModel):
    total_articles: int
    total_terms: int
    total_guidelines: int
    total_categories: int
    recently_added: Dict[str, int]  # 最近添加统计

# 批量操作模型
class BulkImportRequest(BaseModel):
    items: List[Dict[str, Any]]
    import_type: str  # terms, guidelines, articles
    overwrite: bool = False

class BulkImportResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]

# 验证器
@validator('color')
def validate_color(cls, v):
    if v and not v.startswith('#'):
        raise ValueError('颜色格式必须为#开头')
    return v

@validator('weight')
def validate_weight(cls, v):
    if not 0 <= v <= 1:
        raise ValueError('权重必须在0-1之间')
    return v