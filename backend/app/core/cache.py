"""
缓存管理模块
提供Redis缓存、内存缓存等功能
"""

import json
import pickle
from typing import Any, Optional, Union, List, Dict
from functools import wraps
import asyncio
import time
from datetime import datetime, timedelta

import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("cache")

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Any] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    async def initialize(self) -> None:
        """初始化缓存连接"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.REDIS_POOL_SIZE
            )
            
            # 测试连接
            await self.redis_client.ping()
            logger.info("Redis缓存连接成功")
            
        except Exception as e:
            logger.error(f"Redis缓存连接失败: {e}")
            self.redis_client = None
    
    async def close(self) -> None:
        """关闭缓存连接"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis缓存连接已关闭")
    
    def _serialize_value(self, value: Any) -> str:
        """序列化值"""
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value)
        else:
            return pickle.dumps(value).hex()
    
    def _deserialize_value(self, value: str, is_pickled: bool = False) -> Any:
        """反序列化值"""
        if is_pickled:
            return pickle.loads(bytes.fromhex(value))
        else:
            return json.loads(value)
    
    async def get(self, key: str, use_memory: bool = True) -> Optional[Any]:
        """获取缓存值"""
        # 先检查内存缓存
        if use_memory and key in self.memory_cache:
            cache_item = self.memory_cache[key]
            if cache_item["expires_at"] > datetime.now():
                self.cache_stats["hits"] += 1
                logger.debug(f"内存缓存命中: {key}")
                return cache_item["value"]
            else:
                # 过期，删除
                del self.memory_cache[key]
        
        # 检查Redis缓存
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value is not None:
                    # 检查是否是pickle数据
                    is_pickled = await self.redis_client.get(f"{key}:pickled")
                    result = self._deserialize_value(value, bool(is_pickled))
                    self.cache_stats["hits"] += 1
                    logger.debug(f"Redis缓存命中: {key}")
                    return result
            except Exception as e:
                logger.error(f"Redis缓存获取失败: {key}, 错误: {e}")
        
        self.cache_stats["misses"] += 1
        logger.debug(f"缓存未命中: {key}")
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None,
        use_memory: bool = True
    ) -> bool:
        """设置缓存值"""
        try:
            # 设置内存缓存
            if use_memory:
                expires_at = datetime.now() + timedelta(seconds=expire or 3600)
                self.memory_cache[key] = {
                    "value": value,
                    "expires_at": expires_at
                }
            
            # 设置Redis缓存
            if self.redis_client:
                serialized_value = self._serialize_value(value)
                is_pickled = not isinstance(value, (str, int, float, bool))
                
                await self.redis_client.set(key, serialized_value, ex=expire)
                if is_pickled:
                    await self.redis_client.set(f"{key}:pickled", "1", ex=expire)
            
            self.cache_stats["sets"] += 1
            logger.debug(f"缓存设置成功: {key}")
            return True
            
        except Exception as e:
            logger.error(f"缓存设置失败: {key}, 错误: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            # 删除内存缓存
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # 删除Redis缓存
            if self.redis_client:
                await self.redis_client.delete(key)
                await self.redis_client.delete(f"{key}:pickled")
            
            self.cache_stats["deletes"] += 1
            logger.debug(f"缓存删除成功: {key}")
            return True
            
        except Exception as e:
            logger.error(f"缓存删除失败: {key}, 错误: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        # 检查内存缓存
        if key in self.memory_cache:
            cache_item = self.memory_cache[key]
            if cache_item["expires_at"] > datetime.now():
                return True
            else:
                del self.memory_cache[key]
        
        # 检查Redis缓存
        if self.redis_client:
            try:
                return await self.redis_client.exists(key) > 0
            except Exception as e:
                logger.error(f"Redis缓存检查失败: {key}, 错误: {e}")
        
        return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        deleted_count = 0
        
        # 清除内存缓存
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
            deleted_count += 1
        
        # 清除Redis缓存
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    deleted_count += await self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis缓存模式清除失败: {pattern}, 错误: {e}")
        
        logger.info(f"缓存模式清除完成: {pattern}, 删除数量: {deleted_count}")
        return deleted_count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "deletes": self.cache_stats["deletes"],
            "hit_rate": round(hit_rate, 2),
            "memory_cache_size": len(self.memory_cache),
            "redis_connected": self.redis_client is not None
        }

# 全局缓存管理器实例
cache_manager = CacheManager()

def cache_key(prefix: str, *args, **kwargs) -> str:
    """生成缓存键"""
    key_parts = [prefix]
    
    # 添加位置参数
    for arg in args:
        if isinstance(arg, (str, int, float)):
            key_parts.append(str(arg))
    
    # 添加关键字参数
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float)):
            key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)

def cached(
    expire: int = 3600,
    key_prefix: str = "cache",
    use_memory: bool = True
):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key_str = cache_key(
                key_prefix,
                func.__name__,
                *args,
                **kwargs
            )
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key_str, use_memory)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            await cache_manager.set(cache_key_str, result, expire, use_memory)
            
            return result
        
        return wrapper
    return decorator

class CacheService:
    """缓存服务类"""
    
    @staticmethod
    async def cache_categories(expire: int = 1800) -> None:
        """缓存分类列表"""
        from app.services.knowledge import KnowledgeService
        
        service = KnowledgeService()
        categories = await service.list_categories()
        
        await cache_manager.set(
            "categories:list",
            categories,
            expire
        )
        
        logger.info(f"分类列表已缓存，过期时间: {expire}秒")
    
    @staticmethod
    async def cache_search_results(
        query: str,
        results: List[Dict],
        expire: int = 600
    ) -> None:
        """缓存搜索结果"""
        cache_key_str = cache_key("search", query)
        await cache_manager.set(cache_key_str, results, expire)
        
        logger.info(f"搜索结果已缓存: {query}")
    
    @staticmethod
    async def invalidate_category_cache() -> None:
        """清除分类相关缓存"""
        await cache_manager.clear_pattern("categories:*")
        logger.info("分类缓存已清除")
    
    @staticmethod
    async def invalidate_search_cache() -> None:
        """清除搜索相关缓存"""
        await cache_manager.clear_pattern("search:*")
        logger.info("搜索缓存已清除")
    
    @staticmethod
    async def warm_up_cache() -> None:
        """预热缓存"""
        logger.info("开始缓存预热...")
        
        try:
            # 缓存分类列表
            await CacheService.cache_categories()
            
            # 缓存热门搜索
            popular_queries = [
                "白血病",
                "急性淋巴细胞白血病",
                "化疗",
                "骨髓移植"
            ]
            
            for query in popular_queries:
                # 这里可以预执行搜索并缓存结果
                pass
            
            logger.info("缓存预热完成")
            
        except Exception as e:
            logger.error(f"缓存预热失败: {e}")

# 缓存装饰器示例
@cached(expire=1800, key_prefix="categories")
async def get_cached_categories():
    """获取缓存的分类列表"""
    from app.services.knowledge import KnowledgeService
    
    service = KnowledgeService()
    return await service.list_categories()

@cached(expire=600, key_prefix="search")
async def get_cached_search_results(query: str, category_id: Optional[int] = None):
    """获取缓存的搜索结果"""
    from app.services.knowledge import KnowledgeService
    
    service = KnowledgeService()
    return await service.search_knowledge({
        "query": query,
        "category_id": category_id,
        "limit": 20
    })
