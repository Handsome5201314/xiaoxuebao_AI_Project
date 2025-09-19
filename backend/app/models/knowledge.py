from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class KnowledgeCategory(Base):
    """知识库分类模型"""
    __tablename__ = "knowledge_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    description = Column(Text)
    icon = Column(String(100))  # 分类图标
    color = Column(String(20))  # 分类颜色
    sort_order = Column(Integer, default=0)  # 排序顺序
    is_active = Column(Boolean, default=True)
    
    # 层级关系
    parent_id = Column(Integer, ForeignKey("knowledge_categories.id"))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    parent = relationship("KnowledgeCategory", remote_side=[id], backref="children")
    articles = relationship("Article", back_populates="category")
    medical_terms = relationship("MedicalTerm", back_populates="category")
    
    def __repr__(self):
        return f"<KnowledgeCategory {self.name}>"

class MedicalTerm(Base):
    """医学术语模型"""
    __tablename__ = "medical_terms"
    
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(300), nullable=False)
    slug = Column(String(300), unique=True, index=True, nullable=False)
    definition = Column(Text, nullable=False)
    explanation = Column(Text)  # 详细解释
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"))
    synonyms = Column(ARRAY(String))  # 同义词数组
    related_terms = Column(ARRAY(String))  # 相关术语
    is_approved = Column(Boolean, default=False)
    source = Column(String(500))  # 来源
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    category = relationship("KnowledgeCategory", back_populates="medical_terms")
    
    def __repr__(self):
        return f"<MedicalTerm {self.term}>"

class MedicalGuideline(Base):
    """医疗指南模型"""
    __tablename__ = "medical_guidelines"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(300), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    source_organization = Column(String(200))  # 发布机构
    version = Column(String(100))
    publish_date = Column(DateTime(timezone=True))
    effective_date = Column(DateTime(timezone=True))
    is_current = Column(Boolean, default=True)
    
    # 分类
    categories = Column(ARRAY(String))  # 指南分类
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MedicalGuideline {self.title}>"

class KnowledgeGraphNode(Base):
    """知识图谱节点模型"""
    __tablename__ = "knowledge_graph_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    node_type = Column(String(100), nullable=False)  # article, term, guideline, etc.
    node_id = Column(Integer, nullable=False)  # 对应实体的ID
    title = Column(String(500), nullable=False)
    content_summary = Column(Text)
    vector_embedding = Column(ARRAY(Float))  # 向量嵌入
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<KnowledgeGraphNode {self.node_type}:{self.node_id}>"

class KnowledgeGraphEdge(Base):
    """知识图谱边模型"""
    __tablename__ = "knowledge_graph_edges"
    
    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("knowledge_graph_nodes.id"), nullable=False)
    target_node_id = Column(Integer, ForeignKey("knowledge_graph_nodes.id"), nullable=False)
    relationship_type = Column(String(100), nullable=False)  # related_to, synonym, etc.
    weight = Column(Float, default=1.0)  # 关系权重
    description = Column(String(500))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    source_node = relationship("KnowledgeGraphNode", foreign_keys=[source_node_id])
    target_node = relationship("KnowledgeGraphNode", foreign_keys=[target_node_id])
    
    def __repr__(self):
        return f"<KnowledgeGraphEdge {self.source_node_id}->{self.target_node_id}>"

class ArticleCategoryAssociation(Base):
    """文章-分类关联表（多对多）"""
    __tablename__ = "article_category_association"
    
    article_id = Column(Integer, ForeignKey("articles.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"), primary_key=True)
    confidence = Column(Float, default=1.0)  # 分类置信度
    created_at = Column(DateTime(timezone=True), server_default=func.now())