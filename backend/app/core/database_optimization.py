"""
数据库优化模块
提供数据库查询优化、索引管理等功能
"""

from sqlalchemy import text, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any
import asyncio
import time
from app.core.logging import get_logger, log_database_operation
from app.core.database import engine

logger = get_logger("database_optimization")

class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_indexes(self) -> None:
        """创建数据库索引"""
        logger.info("开始创建数据库索引...")
        
        indexes = [
            # 医学术语索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_terms_term ON medical_terms(term)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_terms_slug ON medical_terms(slug)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_terms_category ON medical_terms(category_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_terms_approved ON medical_terms(is_approved)",
            
            # 知识库分类索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_categories_slug ON knowledge_categories(slug)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_categories_active ON knowledge_categories(is_active)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_categories_parent ON knowledge_categories(parent_id)",
            
            # 医疗指南索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_guidelines_title ON medical_guidelines(title)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_guidelines_slug ON medical_guidelines(slug)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_guidelines_current ON medical_guidelines(is_current)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_guidelines_org ON medical_guidelines(source_organization)",
            
            # 文章索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_articles_title ON articles(title)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_articles_slug ON articles(slug)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_articles_published ON articles(is_published)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_articles_author ON articles(author_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_articles_category ON articles(category_id)",
            
            # 用户索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active ON users(is_active)",
            
            # 知识图谱索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_graph_nodes_type ON knowledge_graph_nodes(node_type)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_graph_nodes_id ON knowledge_graph_nodes(node_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_graph_edges_source ON knowledge_graph_edges(source_node_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_graph_edges_target ON knowledge_graph_edges(target_node_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_graph_edges_type ON knowledge_graph_edges(relationship_type)",
        ]
        
        for index_sql in indexes:
            try:
                start_time = time.time()
                await self.session.execute(text(index_sql))
                await self.session.commit()
                duration = time.time() - start_time
                
                log_database_operation(
                    operation="create_index",
                    table="various",
                    duration=duration,
                    success=True,
                    index_sql=index_sql
                )
                
                logger.info(f"索引创建成功: {index_sql}")
                
            except Exception as e:
                logger.error(f"索引创建失败: {index_sql}, 错误: {e}")
                await self.session.rollback()
        
        logger.info("数据库索引创建完成")
    
    async def create_full_text_indexes(self) -> None:
        """创建全文搜索索引"""
        logger.info("开始创建全文搜索索引...")
        
        # PostgreSQL全文搜索索引
        full_text_indexes = [
            # 医学术语全文搜索
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_terms_fts ON medical_terms USING gin(to_tsvector('chinese', term || ' ' || definition))",
            
            # 医疗指南全文搜索
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_medical_guidelines_fts ON medical_guidelines USING gin(to_tsvector('chinese', title || ' ' || content))",
            
            # 文章全文搜索
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_articles_fts ON articles USING gin(to_tsvector('chinese', title || ' ' || content))",
            
            # 知识库分类全文搜索
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_categories_fts ON knowledge_categories USING gin(to_tsvector('chinese', name || ' ' || description))",
        ]
        
        for index_sql in full_text_indexes:
            try:
                start_time = time.time()
                await self.session.execute(text(index_sql))
                await self.session.commit()
                duration = time.time() - start_time
                
                log_database_operation(
                    operation="create_fts_index",
                    table="various",
                    duration=duration,
                    success=True,
                    index_sql=index_sql
                )
                
                logger.info(f"全文搜索索引创建成功: {index_sql}")
                
            except Exception as e:
                logger.error(f"全文搜索索引创建失败: {index_sql}, 错误: {e}")
                await self.session.rollback()
        
        logger.info("全文搜索索引创建完成")
    
    async def analyze_tables(self) -> None:
        """分析表统计信息"""
        logger.info("开始分析表统计信息...")
        
        tables = [
            "medical_terms",
            "knowledge_categories", 
            "medical_guidelines",
            "articles",
            "users",
            "knowledge_graph_nodes",
            "knowledge_graph_edges"
        ]
        
        for table in tables:
            try:
                start_time = time.time()
                await self.session.execute(text(f"ANALYZE {table}"))
                await self.session.commit()
                duration = time.time() - start_time
                
                log_database_operation(
                    operation="analyze_table",
                    table=table,
                    duration=duration,
                    success=True
                )
                
                logger.info(f"表分析完成: {table}")
                
            except Exception as e:
                logger.error(f"表分析失败: {table}, 错误: {e}")
                await self.session.rollback()
        
        logger.info("表统计信息分析完成")
    
    async def get_index_usage_stats(self) -> Dict[str, Any]:
        """获取索引使用统计"""
        query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes 
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
        """)
        
        result = await self.session.execute(query)
        return result.fetchall()
    
    async def get_slow_queries(self) -> List[Dict[str, Any]]:
        """获取慢查询统计"""
        query = text("""
            SELECT 
                query,
                mean_time,
                calls,
                total_time,
                rows
            FROM pg_stat_statements 
            WHERE mean_time > 1000  -- 超过1秒的查询
            ORDER BY mean_time DESC 
            LIMIT 20
        """)
        
        result = await self.session.execute(query)
        return result.fetchall()
    
    async def optimize_queries(self) -> None:
        """优化查询性能"""
        logger.info("开始查询优化...")
        
        # 更新表统计信息
        await self.analyze_tables()
        
        # 清理未使用的索引
        await self.cleanup_unused_indexes()
        
        # 重建索引
        await self.rebuild_indexes()
        
        logger.info("查询优化完成")
    
    async def cleanup_unused_indexes(self) -> None:
        """清理未使用的索引"""
        logger.info("开始清理未使用的索引...")
        
        # 查找未使用的索引
        query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname
            FROM pg_stat_user_indexes 
            WHERE idx_scan = 0 
            AND schemaname = 'public'
            AND indexname NOT LIKE '%_pkey'
        """)
        
        result = await self.session.execute(query)
        unused_indexes = result.fetchall()
        
        for index in unused_indexes:
            try:
                drop_sql = f"DROP INDEX CONCURRENTLY IF EXISTS {index.indexname}"
                await self.session.execute(text(drop_sql))
                await self.session.commit()
                logger.info(f"删除未使用索引: {index.indexname}")
                
            except Exception as e:
                logger.error(f"删除索引失败: {index.indexname}, 错误: {e}")
                await self.session.rollback()
        
        logger.info("未使用索引清理完成")
    
    async def rebuild_indexes(self) -> None:
        """重建索引"""
        logger.info("开始重建索引...")
        
        # 重建关键索引
        rebuild_indexes = [
            "REINDEX INDEX CONCURRENTLY idx_medical_terms_fts",
            "REINDEX INDEX CONCURRENTLY idx_medical_guidelines_fts", 
            "REINDEX INDEX CONCURRENTLY idx_articles_fts",
        ]
        
        for rebuild_sql in rebuild_indexes:
            try:
                start_time = time.time()
                await self.session.execute(text(rebuild_sql))
                await self.session.commit()
                duration = time.time() - start_time
                
                log_database_operation(
                    operation="rebuild_index",
                    table="various",
                    duration=duration,
                    success=True,
                    index_sql=rebuild_sql
                )
                
                logger.info(f"索引重建成功: {rebuild_sql}")
                
            except Exception as e:
                logger.error(f"索引重建失败: {rebuild_sql}, 错误: {e}")
                await self.session.rollback()
        
        logger.info("索引重建完成")

async def optimize_database():
    """数据库优化主函数"""
    async with engine.begin() as conn:
        session = AsyncSession(conn)
        optimizer = DatabaseOptimizer(session)
        
        try:
            # 创建索引
            await optimizer.create_indexes()
            
            # 创建全文搜索索引
            await optimizer.create_full_text_indexes()
            
            # 分析表统计信息
            await optimizer.analyze_tables()
            
            # 优化查询
            await optimizer.optimize_queries()
            
            logger.info("数据库优化完成")
            
        except Exception as e:
            logger.error(f"数据库优化失败: {e}")
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(optimize_database())
