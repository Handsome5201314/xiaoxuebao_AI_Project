"""
数据库查询优化器
提供查询缓存、批量操作、查询分析等功能
"""

import time
import hashlib
from typing import Any, Dict, List, Optional, Callable, TypeVar, Union
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload, joinedload
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.logging import get_logger
from app.core.cache import cache_manager, cached
from app.core.performance_monitor import get_performance_monitor

logger = get_logger(__name__)

T = TypeVar('T')

@dataclass
class QueryOptimizationConfig:
    """查询优化配置"""
    enable_cache: bool = True
    cache_ttl: int = 300  # 5分钟
    enable_monitoring: bool = True
    enable_batch_loading: bool = True
    max_batch_size: int = 100

class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self, config: Optional[QueryOptimizationConfig] = None):
        self.config = config or QueryOptimizationConfig()
        self.performance_monitor = get_performance_monitor()
    
    def _generate_cache_key(self, query: str, params: Dict[str, Any] = None) -> str:
        """生成查询缓存键"""
        key_data = f"{query}:{params or {}}"
        return f"query:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    async def execute_with_cache(
        self,
        session: AsyncSession,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        cache_ttl: Optional[int] = None
    ) -> Any:
        """执行带缓存的查询"""
        if not self.config.enable_cache:
            return await self._execute_query(session, query, params)
        
        cache_key = self._generate_cache_key(query, params)
        ttl = cache_ttl or self.config.cache_ttl
        
        # 尝试从缓存获取
        cached_result = await cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug(f"查询缓存命中: {cache_key}")
            return cached_result
        
        # 执行查询
        result = await self._execute_query(session, query, params)
        
        # 存储到缓存
        await cache_manager.set(cache_key, result, ttl)
        logger.debug(f"查询结果已缓存: {cache_key}")
        
        return result
    
    async def _execute_query(
        self,
        session: AsyncSession,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """执行查询"""
        if self.config.enable_monitoring:
            async with self.performance_monitor.monitor_query(query, params):
                if params:
                    result = await session.execute(text(query), params)
                else:
                    result = await session.execute(text(query))
                return result.fetchall()
        else:
            if params:
                result = await session.execute(text(query), params)
            else:
                result = await session.execute(text(query))
            return result.fetchall()
    
    async def batch_load_related(
        self,
        session: AsyncSession,
        model_class: type,
        ids: List[int],
        relationships: List[str] = None
    ) -> List[Any]:
        """批量加载相关数据"""
        if not ids:
            return []
        
        # 分批处理大量ID
        batch_size = self.config.max_batch_size
        all_results = []
        
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            
            query = select(model_class).where(model_class.id.in_(batch_ids))
            
            # 添加预加载关系
            if relationships:
                for rel in relationships:
                    if hasattr(model_class, rel):
                        query = query.options(selectinload(getattr(model_class, rel)))
            
            result = await session.execute(query)
            batch_results = result.scalars().all()
            all_results.extend(batch_results)
        
        return all_results
    
    def optimize_query_with_joins(
        self,
        base_query: Any,
        join_relationships: List[str] = None,
        load_strategy: str = "selectinload"
    ) -> Any:
        """优化查询的JOIN策略"""
        if not join_relationships:
            return base_query
        
        optimized_query = base_query
        
        for relationship in join_relationships:
            if load_strategy == "selectinload":
                optimized_query = optimized_query.options(selectinload(relationship))
            elif load_strategy == "joinedload":
                optimized_query = optimized_query.options(joinedload(relationship))
        
        return optimized_query

# 查询优化装饰器
def optimized_query(
    cache_ttl: int = 300,
    enable_cache: bool = True,
    enable_monitoring: bool = True
):
    """查询优化装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            config = QueryOptimizationConfig(
                enable_cache=enable_cache,
                cache_ttl=cache_ttl,
                enable_monitoring=enable_monitoring
            )
            optimizer = QueryOptimizer(config)
            
            # 将优化器传递给函数
            kwargs['query_optimizer'] = optimizer
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# 批量操作优化器
class BatchOperationOptimizer:
    """批量操作优化器"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    async def batch_insert(
        self,
        session: AsyncSession,
        model_class: type,
        data_list: List[Dict[str, Any]]
    ) -> List[Any]:
        """批量插入"""
        if not data_list:
            return []
        
        created_objects = []
        
        for i in range(0, len(data_list), self.batch_size):
            batch_data = data_list[i:i + self.batch_size]
            
            # 创建对象
            batch_objects = [model_class(**data) for data in batch_data]
            
            # 批量添加
            session.add_all(batch_objects)
            await session.flush()  # 获取ID但不提交
            
            created_objects.extend(batch_objects)
        
        await session.commit()
        return created_objects
    
    async def batch_update(
        self,
        session: AsyncSession,
        model_class: type,
        updates: List[Dict[str, Any]]
    ) -> int:
        """批量更新"""
        if not updates:
            return 0
        
        updated_count = 0
        
        for i in range(0, len(updates), self.batch_size):
            batch_updates = updates[i:i + self.batch_size]
            
            for update_data in batch_updates:
                obj_id = update_data.pop('id')
                result = await session.execute(
                    text(f"UPDATE {model_class.__tablename__} SET {', '.join(f'{k} = :{k}' for k in update_data.keys())} WHERE id = :id"),
                    {**update_data, 'id': obj_id}
                )
                updated_count += result.rowcount
        
        await session.commit()
        return updated_count

# 查询分析器
class QueryAnalyzer:
    """查询分析器"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def analyze_query_plan(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析查询执行计划"""
        try:
            # PostgreSQL EXPLAIN ANALYZE
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = await self.session.execute(text(explain_query), params or {})
            plan = result.fetchone()[0]
            
            return {
                "execution_time": plan[0]["Execution Time"],
                "planning_time": plan[0]["Planning Time"],
                "total_cost": plan[0]["Plan"]["Total Cost"],
                "actual_rows": plan[0]["Plan"]["Actual Rows"],
                "plan_details": plan[0]["Plan"]
            }
        except Exception as e:
            logger.error(f"查询计划分析失败: {str(e)}")
            return {"error": str(e)}
    
    async def suggest_indexes(self, table_name: str, columns: List[str]) -> List[str]:
        """建议索引"""
        suggestions = []
        
        # 单列索引建议
        for column in columns:
            suggestions.append(f"CREATE INDEX idx_{table_name}_{column} ON {table_name}({column});")
        
        # 复合索引建议（如果有多个列）
        if len(columns) > 1:
            column_list = ", ".join(columns)
            suggestions.append(f"CREATE INDEX idx_{table_name}_{'_'.join(columns)} ON {table_name}({column_list});")
        
        return suggestions

# 全局查询优化器实例
_global_optimizer: Optional[QueryOptimizer] = None

def get_query_optimizer() -> QueryOptimizer:
    """获取全局查询优化器实例"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = QueryOptimizer()
    return _global_optimizer

# 便捷函数
async def execute_optimized_query(
    session: AsyncSession,
    query: str,
    params: Optional[Dict[str, Any]] = None,
    cache_ttl: int = 300
) -> Any:
    """执行优化的查询"""
    optimizer = get_query_optimizer()
    return await optimizer.execute_with_cache(session, query, params, cache_ttl)

async def batch_load_models(
    session: AsyncSession,
    model_class: type,
    ids: List[int],
    relationships: List[str] = None
) -> List[Any]:
    """批量加载模型"""
    optimizer = get_query_optimizer()
    return await optimizer.batch_load_related(session, model_class, ids, relationships)
