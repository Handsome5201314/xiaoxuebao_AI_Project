import redis.asyncio as redis
from app.core.config import settings

# 创建Redis连接池
redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
    retry_on_timeout=True
)

async def get_redis():
    """获取Redis连接依赖"""
    return redis_client

# Redis工具函数
async def set_cache(key: str, value: str, expire: int = 3600):
    """设置缓存"""
    await redis_client.setex(key, expire, value)

async def get_cache(key: str):
    """获取缓存"""
    return await redis_client.get(key)

async def delete_cache(key: str):
    """删除缓存"""
    await redis_client.delete(key)

async def clear_cache(pattern: str = "*"):
    """清除匹配模式的缓存"""
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)

# 连接测试
async def test_redis_connection():
    """测试Redis连接"""
    try:
        pong = await redis_client.ping()
        return pong
    except Exception as e:
        raise ConnectionError(f"Redis连接失败: {e}")