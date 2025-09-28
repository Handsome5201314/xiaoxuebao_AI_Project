"""
API限流中间件
提供基于IP、用户、端点的限流功能
"""

import time
import asyncio
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.response import error_response

logger = get_logger(__name__)

@dataclass
class RateLimitRule:
    """限流规则"""
    requests: int  # 请求数量
    window: int    # 时间窗口（秒）
    burst: Optional[int] = None  # 突发请求数量
    
class RateLimitConfig:
    """限流配置"""
    
    # 默认限流规则
    DEFAULT_RULES = {
        "global": RateLimitRule(requests=1000, window=60),  # 全局：每分钟1000请求
        "per_ip": RateLimitRule(requests=100, window=60),   # 每IP：每分钟100请求
        "per_user": RateLimitRule(requests=200, window=60), # 每用户：每分钟200请求
    }
    
    # 端点特定规则
    ENDPOINT_RULES = {
        "/api/v1/knowledge/search": RateLimitRule(requests=30, window=60),
        "/api/v1/auth/login": RateLimitRule(requests=5, window=300),  # 登录：5分钟5次
        "/api/v1/auth/register": RateLimitRule(requests=3, window=3600),  # 注册：1小时3次
    }

class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """消费令牌"""
        now = time.time()
        
        # 补充令牌
        time_passed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        self.last_refill = now
        
        # 检查是否有足够令牌
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class SlidingWindowCounter:
    """滑动窗口计数器"""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        """检查是否允许请求"""
        now = time.time()
        
        # 移除过期的请求记录
        while self.requests and self.requests[0] <= now - self.window_size:
            self.requests.popleft()
        
        # 检查是否超过限制
        if len(self.requests) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests.append(now)
        return True

class RateLimiter:
    """限流器"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.local_counters: Dict[str, SlidingWindowCounter] = {}
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.config = RateLimitConfig()
        
    async def initialize(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("限流器Redis连接成功")
        except Exception as e:
            logger.warning(f"限流器Redis连接失败，使用本地限流: {e}")
            self.redis_client = None
    
    async def is_allowed(
        self,
        key: str,
        rule: RateLimitRule,
        identifier: str = "default"
    ) -> tuple[bool, Dict[str, Any]]:
        """检查是否允许请求"""
        
        if self.redis_client:
            return await self._redis_rate_limit(key, rule)
        else:
            return await self._local_rate_limit(key, rule)
    
    async def _redis_rate_limit(
        self,
        key: str,
        rule: RateLimitRule
    ) -> tuple[bool, Dict[str, Any]]:
        """基于Redis的分布式限流"""
        try:
            pipe = self.redis_client.pipeline()
            now = int(time.time())
            window_start = now - rule.window
            
            # 使用有序集合实现滑动窗口
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, rule.window)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            is_allowed = current_requests < rule.requests
            
            info = {
                "limit": rule.requests,
                "remaining": max(0, rule.requests - current_requests - 1),
                "reset_time": now + rule.window,
                "retry_after": rule.window if not is_allowed else None
            }
            
            return is_allowed, info
            
        except Exception as e:
            logger.error(f"Redis限流检查失败: {e}")
            # 降级到本地限流
            return await self._local_rate_limit(key, rule)
    
    async def _local_rate_limit(
        self,
        key: str,
        rule: RateLimitRule
    ) -> tuple[bool, Dict[str, Any]]:
        """本地内存限流"""
        if key not in self.local_counters:
            self.local_counters[key] = SlidingWindowCounter(rule.window, rule.requests)
        
        counter = self.local_counters[key]
        is_allowed = counter.is_allowed()
        
        info = {
            "limit": rule.requests,
            "remaining": max(0, rule.requests - len(counter.requests)),
            "reset_time": int(time.time()) + rule.window,
            "retry_after": rule.window if not is_allowed else None
        }
        
        return is_allowed, info
    
    def get_rate_limit_key(self, request: Request, rule_type: str) -> str:
        """生成限流键"""
        if rule_type == "global":
            return "rate_limit:global"
        elif rule_type == "per_ip":
            client_ip = request.client.host if request.client else "unknown"
            return f"rate_limit:ip:{client_ip}"
        elif rule_type == "per_user":
            # 从请求中获取用户ID（需要在认证中间件中设置）
            user_id = getattr(request.state, 'user_id', 'anonymous')
            return f"rate_limit:user:{user_id}"
        elif rule_type == "per_endpoint":
            return f"rate_limit:endpoint:{request.url.path}"
        else:
            return f"rate_limit:custom:{rule_type}"
    
    async def check_rate_limits(self, request: Request) -> Optional[JSONResponse]:
        """检查所有适用的限流规则"""
        
        # 检查全局限流
        global_key = self.get_rate_limit_key(request, "global")
        is_allowed, info = await self.is_allowed(global_key, self.config.DEFAULT_RULES["global"])
        
        if not is_allowed:
            return self._create_rate_limit_response(info, "全局请求频率超限")
        
        # 检查IP限流
        ip_key = self.get_rate_limit_key(request, "per_ip")
        is_allowed, info = await self.is_allowed(ip_key, self.config.DEFAULT_RULES["per_ip"])
        
        if not is_allowed:
            return self._create_rate_limit_response(info, "IP请求频率超限")
        
        # 检查端点特定限流
        endpoint_path = request.url.path
        if endpoint_path in self.config.ENDPOINT_RULES:
            endpoint_key = self.get_rate_limit_key(request, "per_endpoint")
            rule = self.config.ENDPOINT_RULES[endpoint_path]
            is_allowed, info = await self.is_allowed(endpoint_key, rule)
            
            if not is_allowed:
                return self._create_rate_limit_response(info, f"端点 {endpoint_path} 请求频率超限")
        
        # 检查用户限流（如果已认证）
        if hasattr(request.state, 'user_id'):
            user_key = self.get_rate_limit_key(request, "per_user")
            is_allowed, info = await self.is_allowed(user_key, self.config.DEFAULT_RULES["per_user"])
            
            if not is_allowed:
                return self._create_rate_limit_response(info, "用户请求频率超限")
        
        return None
    
    def _create_rate_limit_response(self, info: Dict[str, Any], message: str) -> JSONResponse:
        """创建限流响应"""
        headers = {
            "X-RateLimit-Limit": str(info["limit"]),
            "X-RateLimit-Remaining": str(info["remaining"]),
            "X-RateLimit-Reset": str(info["reset_time"]),
        }
        
        if info.get("retry_after"):
            headers["Retry-After"] = str(info["retry_after"])
        
        response_content = error_response(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "limit": info["limit"],
                "remaining": info["remaining"],
                "reset_time": info["reset_time"],
                "retry_after": info.get("retry_after")
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=response_content,
            headers=headers
        )
    
    async def get_rate_limit_status(self, request: Request) -> Dict[str, Any]:
        """获取当前限流状态"""
        status = {}
        
        # 全局限流状态
        global_key = self.get_rate_limit_key(request, "global")
        _, global_info = await self.is_allowed(global_key, self.config.DEFAULT_RULES["global"])
        status["global"] = global_info
        
        # IP限流状态
        ip_key = self.get_rate_limit_key(request, "per_ip")
        _, ip_info = await self.is_allowed(ip_key, self.config.DEFAULT_RULES["per_ip"])
        status["ip"] = ip_info
        
        return status

# 全局限流器实例
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """限流中间件"""
    # 检查限流
    rate_limit_response = await rate_limiter.check_rate_limits(request)
    if rate_limit_response:
        return rate_limit_response
    
    # 继续处理请求
    response = await call_next(request)
    
    # 添加限流信息到响应头
    try:
        status = await rate_limiter.get_rate_limit_status(request)
        if "global" in status:
            response.headers["X-RateLimit-Limit"] = str(status["global"]["limit"])
            response.headers["X-RateLimit-Remaining"] = str(status["global"]["remaining"])
            response.headers["X-RateLimit-Reset"] = str(status["global"]["reset_time"])
    except Exception as e:
        logger.error(f"添加限流响应头失败: {e}")
    
    return response
