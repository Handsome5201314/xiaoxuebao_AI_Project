"""Add database indexes for performance optimization

Revision ID: 001_add_database_indexes
Revises: 
Create Date: 2025-09-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_add_database_indexes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """添加数据库索引"""
    
    # 医学术语索引
    op.create_index('idx_medical_terms_term', 'medical_terms', ['term'])
    op.create_index('idx_medical_terms_slug', 'medical_terms', ['slug'])
    op.create_index('idx_medical_terms_category', 'medical_terms', ['category_id'])
    op.create_index('idx_medical_terms_approved', 'medical_terms', ['is_approved'])
    
    # 知识库分类索引
    op.create_index('idx_knowledge_categories_slug', 'knowledge_categories', ['slug'])
    op.create_index('idx_knowledge_categories_active', 'knowledge_categories', ['is_active'])
    op.create_index('idx_knowledge_categories_parent', 'knowledge_categories', ['parent_id'])
    
    # 医疗指南索引
    op.create_index('idx_medical_guidelines_title', 'medical_guidelines', ['title'])
    op.create_index('idx_medical_guidelines_slug', 'medical_guidelines', ['slug'])
    op.create_index('idx_medical_guidelines_current', 'medical_guidelines', ['is_current'])
    op.create_index('idx_medical_guidelines_org', 'medical_guidelines', ['source_organization'])
    
    # 文章索引
    op.create_index('idx_articles_title', 'articles', ['title'])
    op.create_index('idx_articles_slug', 'articles', ['slug'])
    op.create_index('idx_articles_published', 'articles', ['is_published'])
    op.create_index('idx_articles_author', 'articles', ['author_id'])
    op.create_index('idx_articles_category', 'articles', ['category_id'])
    
    # 用户索引
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_active', 'users', ['is_active'])
    
    # 知识图谱索引
    op.create_index('idx_knowledge_graph_nodes_type', 'knowledge_graph_nodes', ['node_type'])
    op.create_index('idx_knowledge_graph_nodes_id', 'knowledge_graph_nodes', ['node_id'])
    op.create_index('idx_knowledge_graph_edges_source', 'knowledge_graph_edges', ['source_node_id'])
    op.create_index('idx_knowledge_graph_edges_target', 'knowledge_graph_edges', ['target_node_id'])
    op.create_index('idx_knowledge_graph_edges_type', 'knowledge_graph_edges', ['relationship_type'])

def downgrade():
    """删除数据库索引"""
    
    # 删除医学术语索引
    op.drop_index('idx_medical_terms_term', 'medical_terms')
    op.drop_index('idx_medical_terms_slug', 'medical_terms')
    op.drop_index('idx_medical_terms_category', 'medical_terms')
    op.drop_index('idx_medical_terms_approved', 'medical_terms')
    
    # 删除知识库分类索引
    op.drop_index('idx_knowledge_categories_slug', 'knowledge_categories')
    op.drop_index('idx_knowledge_categories_active', 'knowledge_categories')
    op.drop_index('idx_knowledge_categories_parent', 'knowledge_categories')
    
    # 删除医疗指南索引
    op.drop_index('idx_medical_guidelines_title', 'medical_guidelines')
    op.drop_index('idx_medical_guidelines_slug', 'medical_guidelines')
    op.drop_index('idx_medical_guidelines_current', 'medical_guidelines')
    op.drop_index('idx_medical_guidelines_org', 'medical_guidelines')
    
    # 删除文章索引
    op.drop_index('idx_articles_title', 'articles')
    op.drop_index('idx_articles_slug', 'articles')
    op.drop_index('idx_articles_published', 'articles')
    op.drop_index('idx_articles_author', 'articles')
    op.drop_index('idx_articles_category', 'articles')
    
    # 删除用户索引
    op.drop_index('idx_users_username', 'users')
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_active', 'users')
    
    # 删除知识图谱索引
    op.drop_index('idx_knowledge_graph_nodes_type', 'knowledge_graph_nodes')
    op.drop_index('idx_knowledge_graph_nodes_id', 'knowledge_graph_nodes')
    op.drop_index('idx_knowledge_graph_edges_source', 'knowledge_graph_edges')
    op.drop_index('idx_knowledge_graph_edges_target', 'knowledge_graph_edges')
    op.drop_index('idx_knowledge_graph_edges_type', 'knowledge_graph_edges')
