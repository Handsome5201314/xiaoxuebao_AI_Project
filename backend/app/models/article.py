from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class ArticleStatus(enum.Enum):
    """文章状态枚举"""
    DRAFT = "draft"      # 草稿
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"   # 已归档
    REVIEW = "review"     # 审核中

class Article(Base):
    """文章模型"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(300), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)  # Markdown内容
    html_content = Column(Text)  # 渲染后的HTML
    excerpt = Column(String(1000))  # 摘要
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT, nullable=False)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # 外键关系
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"))
    
    # 关系
    author = relationship("User", back_populates="articles")
    category = relationship("KnowledgeCategory", back_populates="articles")
    tags = relationship("ArticleTag", secondary="article_tag_association", back_populates="articles")
    edits = relationship("ArticleEdit", back_populates="article")
    comments = relationship("Comment", back_populates="article")
    
    def __repr__(self):
        return f"<Article {self.title}>"

class ArticleEdit(Base):
    """文章编辑历史模型"""
    __tablename__ = "article_edits"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    editor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)  # 编辑时的Markdown内容
    change_summary = Column(String(500))  # 修改摘要
    edit_type = Column(String(50))  # 编辑类型：create, update, revert
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    article = relationship("Article", back_populates="edits")
    editor = relationship("User", back_populates="edits")
    
    def __repr__(self):
        return f"<ArticleEdit {self.article_id} v{self.version}>"

class Tag(Base):
    """标签模型"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500))
    
    # 关系
    articles = relationship("Article", secondary="article_tag_association", back_populates="tags")
    
    def __repr__(self):
        return f"<Tag {self.name}>"

class ArticleTagAssociation(Base):
    """文章-标签关联表"""
    __tablename__ = "article_tag_association"
    
    article_id = Column(Integer, ForeignKey("articles.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Comment(Base):
    """评论模型"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"))  # 父评论ID
    is_approved = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    article = relationship("Article", back_populates="comments")
    user = relationship("User")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<Comment {self.id}>"