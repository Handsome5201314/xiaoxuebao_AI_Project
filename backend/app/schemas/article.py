from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.article import ArticleStatus

# 基础文章模型
class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)  # Markdown内容
    excerpt: Optional[str] = Field(None, max_length=1000)
    status: ArticleStatus = ArticleStatus.DRAFT
    is_featured: bool = False

# 文章创建
class ArticleCreate(ArticleBase):
    category_id: Optional[int] = None
    tag_names: Optional[List[str]] = None

# 文章更新
class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=1000)
    status: Optional[ArticleStatus] = None
    is_featured: Optional[bool] = None
    category_id: Optional[int] = None
    tag_names: Optional[List[str]] = None

# 文章响应（包含作者信息）
class Article(ArticleBase):
    id: int
    slug: str
    html_content: Optional[str] = None
    view_count: int
    like_count: int
    comment_count: int
    author_id: int
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    # 关系字段（可选加载）
    author: Optional['User'] = None
    category: Optional['KnowledgeCategory'] = None
    tags: Optional[List['Tag']] = None

    class Config:
        from_attributes = True

# 文章响应别名（API兼容性）
ArticleResponse = Article

# 文章版本响应
class ArticleVersionResponse(BaseModel):
    id: int
    article_id: int
    version: int
    content: str
    change_summary: Optional[str] = None
    edit_type: str
    created_at: datetime
    editor: Optional['User'] = None

    class Config:
        from_attributes = True

# 文章列表项（简化版）
class ArticleListItem(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    author_id: int
    author_name: Optional[str]
    category_id: Optional[int]
    category_name: Optional[str]
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    published_at: Optional[datetime] = None
    status: ArticleStatus

    class Config:
        from_attributes = True

# 文章列表响应
class ArticleList(BaseModel):
    articles: List[ArticleListItem]
    total_count: int
    page: int
    page_size: int
    total_pages: int

# 文章列表响应别名（API兼容性）
ArticleListResponse = ArticleList

# 文章编辑历史
class ArticleEditBase(BaseModel):
    content: str
    change_summary: Optional[str] = Field(None, max_length=500)
    edit_type: str = "update"

class ArticleEditCreate(ArticleEditBase):
    article_id: int
    editor_id: int

class ArticleEdit(ArticleEditBase):
    id: int
    article_id: int
    editor_id: int
    version: int
    created_at: datetime

    # 关系字段
    editor: Optional['User'] = None

    class Config:
        from_attributes = True

# 标签模型
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    slug: str
    created_at: datetime
    article_count: Optional[int] = None  # 文章数量统计

    class Config:
        from_attributes = True

# 评论模型
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class CommentCreate(CommentBase):
    article_id: int
    parent_id: Optional[int] = None

class Comment(CommentBase):
    id: int
    article_id: int
    user_id: int
    parent_id: Optional[int] = None
    is_approved: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # 关系字段
    user: Optional['User'] = None
    article: Optional['Article'] = None

    class Config:
        from_attributes = True

# 搜索参数
class ArticleSearchParams(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    status: Optional[ArticleStatus] = None
    author: Optional[str] = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"

# 文章统计
class ArticleStats(BaseModel):
    total_articles: int
    published_articles: int
    draft_articles: int
    total_views: int
    total_likes: int
    total_comments: int

# 验证器
@validator('title')
def validate_title(cls, v):
    if not v.strip():
        raise ValueError('标题不能为空')
    return v.strip()

@validator('content')
def validate_content(cls, v):
    if not v.strip():
        raise ValueError('内容不能为空')
    return v.strip()