"""
性能监控模块
提供查询性能分析、慢查询检测、连接池监控等功能
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Callable
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import text, event
from sqlalchemy.pool import Pool
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import weakref

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class QueryStats:
    """查询统计信息"""
    query_hash: str
    query_pattern: str  # 参数化的查询模式
    execution_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    max_time: float = 0.0
    min_time: float = float('inf')
    last_executed: Optional[datetime] = None
    error_count: int = 0
    
    def update(self, execution_time: float, is_error: bool = False) -> None:
        """更新统计信息"""
        self.execution_count += 1
        if is_error:
            self.error_count += 1
        else:
            self.total_time += execution_time
            self.avg_time = self.total_time / (self.execution_count - self.error_count)
            self.max_time = max(self.max_time, execution_time)
            self.min_time = min(self.min_time, execution_time)
        self.last_executed = datetime.utcnow()

@dataclass
class SlowQuery:
    """慢查询记录"""
    query: str
    execution_time: float
    timestamp: datetime
    stack_trace: Optional[str] = None
    session_info: Dict[str, Any] = field(default_factory=dict)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, engine: AsyncEngine, slow_query_threshold: float = 1.0):
        self.engine = engine
        self.slow_query_threshold = slow_query_threshold
        self.query_stats: Dict[str, QueryStats] = {}
        self.slow_queries: deque = deque(maxlen=1000)  # 最多保存1000条慢查询
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'pool_size': 0,
            'checked_out': 0,
            'overflow': 0,
            'invalid': 0
        }
        self._lock = threading.Lock()
        self._setup_event_listeners()
    
    def _setup_event_listeners(self) -> None:
        """设置事件监听器"""
        # 监听连接池事件
        @event.listens_for(self.engine.sync_engine.pool, "connect")
        def on_connect(dbapi_conn, connection_record):
            with self._lock:
                self.connection_stats['total_connections'] += 1
                logger.debug("数据库连接建立", total=self.connection_stats['total_connections'])
        
        @event.listens_for(self.engine.sync_engine.pool, "checkout")
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            with self._lock:
                self.connection_stats['active_connections'] += 1
                self.connection_stats['checked_out'] += 1
        
        @event.listens_for(self.engine.sync_engine.pool, "checkin")
        def on_checkin(dbapi_conn, connection_record):
            with self._lock:
                self.connection_stats['active_connections'] -= 1
    
    def _normalize_query(self, query: str) -> str:
        """标准化查询，移除参数值以便统计"""
        import re
        # 简单的参数化：替换数字和字符串字面量
        normalized = re.sub(r'\b\d+\b', '?', query)
        normalized = re.sub(r"'[^']*'", "'?'", normalized)
        normalized = re.sub(r'"[^"]*"', '"?"', normalized)
        return normalized
    
    @asynccontextmanager
    async def monitor_query(self, query: str, params: Optional[Dict[str, Any]] = None):
        """查询监控上下文管理器"""
        start_time = time.time()
        query_hash = str(hash(query))
        normalized_query = self._normalize_query(query)
        
        try:
            yield
            execution_time = time.time() - start_time
            
            # 更新统计信息
            with self._lock:
                if query_hash not in self.query_stats:
                    self.query_stats[query_hash] = QueryStats(
                        query_hash=query_hash,
                        query_pattern=normalized_query
                    )
                self.query_stats[query_hash].update(execution_time, is_error=False)
            
            # 检查是否为慢查询
            if execution_time > self.slow_query_threshold:
                slow_query = SlowQuery(
                    query=query,
                    execution_time=execution_time,
                    timestamp=datetime.utcnow(),
                    session_info={'params': params}
                )
                self.slow_queries.append(slow_query)
                
                logger.warning(
                    "检测到慢查询",
                    query=query[:200],
                    execution_time=execution_time,
                    threshold=self.slow_query_threshold
                )
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            # 更新错误统计
            with self._lock:
                if query_hash not in self.query_stats:
                    self.query_stats[query_hash] = QueryStats(
                        query_hash=query_hash,
                        query_pattern=normalized_query
                    )
                self.query_stats[query_hash].update(execution_time, is_error=True)
            
            logger.error(
                "查询执行失败",
                query=query[:200],
                error=str(e),
                execution_time=execution_time
            )
            raise
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        with self._lock:
            # 获取连接池状态
            pool = self.engine.sync_engine.pool
            pool_status = {
                'size': pool.size(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'checked_in': pool.checkedin()
            }
            
            # 获取慢查询统计
            slow_query_count = len(self.slow_queries)
            recent_slow_queries = list(self.slow_queries)[-10:]  # 最近10条慢查询
            
            # 获取查询统计
            top_slow_queries = sorted(
                self.query_stats.values(),
                key=lambda x: x.avg_time,
                reverse=True
            )[:10]
            
            most_frequent_queries = sorted(
                self.query_stats.values(),
                key=lambda x: x.execution_count,
                reverse=True
            )[:10]
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'connection_pool': pool_status,
                'query_statistics': {
                    'total_queries': sum(stat.execution_count for stat in self.query_stats.values()),
                    'unique_queries': len(self.query_stats),
                    'slow_query_count': slow_query_count,
                    'error_count': sum(stat.error_count for stat in self.query_stats.values())
                },
                'top_slow_queries': [
                    {
                        'pattern': stat.query_pattern[:100],
                        'avg_time': stat.avg_time,
                        'max_time': stat.max_time,
                        'execution_count': stat.execution_count,
                        'error_count': stat.error_count
                    }
                    for stat in top_slow_queries
                ],
                'most_frequent_queries': [
                    {
                        'pattern': stat.query_pattern[:100],
                        'execution_count': stat.execution_count,
                        'avg_time': stat.avg_time,
                        'error_count': stat.error_count
                    }
                    for stat in most_frequent_queries
                ],
                'recent_slow_queries': [
                    {
                        'query': sq.query[:100],
                        'execution_time': sq.execution_time,
                        'timestamp': sq.timestamp.isoformat()
                    }
                    for sq in recent_slow_queries
                ]
            }
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        with self._lock:
            self.query_stats.clear()
            self.slow_queries.clear()
            logger.info("性能统计信息已重置")

# 全局性能监控实例
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控实例"""
    global _performance_monitor
    if _performance_monitor is None:
        from app.core.database import engine
        _performance_monitor = PerformanceMonitor(engine)
    return _performance_monitor

async def monitor_database_query(
    session: AsyncSession,
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> Any:
    """监控数据库查询的装饰器函数"""
    monitor = get_performance_monitor()
    async with monitor.monitor_query(query, params):
        if params:
            result = await session.execute(text(query), params)
        else:
            result = await session.execute(text(query))
        return result
