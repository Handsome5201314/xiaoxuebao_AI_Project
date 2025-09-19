"""
安全模块
提供API限流、安全防护、输入验证等功能
"""

import time
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
import re
import ipaddress

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import structlog

from app.core.config import settings
from app.core.logging import get_logger, log_security_event
from app.core.exceptions import AuthenticationException, ValidationException

logger = get_logger("security")

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT安全配置
security = HTTPBearer()

@dataclass
class RateLimitInfo:
    """限流信息"""
    requests: int
    window_start: float
    blocked: bool = False

class RateLimiter:
    """API限流器"""
    
    def __init__(self):
        self.rate_limits: Dict[str, Dict[str, RateLimitInfo]] = defaultdict(dict)
        self.blocked_ips: Dict[str, float] = {}
        self.suspicious_ips: Dict[str, int] = defaultdict(int)
        
        # 默认限流配置
        self.default_limits = {
            "api": {"requests": 100, "window": 3600},  # 每小时100次
            "search": {"requests": 50, "window": 3600},  # 每小时50次
            "auth": {"requests": 10, "window": 3600},  # 每小时10次
            "upload": {"requests": 5, "window": 3600},  # 每小时5次
        }
    
    def is_rate_limited(self, key: str, limit_type: str = "api") -> bool:
        """检查是否触发限流"""
        current_time = time.time()
        limit_config = self.default_limits.get(limit_type, self.default_limits["api"])
        
        # 清理过期的限流记录
        self._cleanup_expired_limits(current_time)
        
        # 获取或创建限流记录
        if key not in self.rate_limits[limit_type]:
            self.rate_limits[limit_type][key] = RateLimitInfo(
                requests=0,
                window_start=current_time
            )
        
        rate_info = self.rate_limits[limit_type][key]
        
        # 检查时间窗口
        if current_time - rate_info.window_start > limit_config["window"]:
            # 重置窗口
            rate_info.requests = 0
            rate_info.window_start = current_time
        
        # 增加请求计数
        rate_info.requests += 1
        
        # 检查是否超过限制
        if rate_info.requests > limit_config["requests"]:
            rate_info.blocked = True
            logger.warning(f"API限流触发: {key}, 类型: {limit_type}")
            return True
        
        return False
    
    def _cleanup_expired_limits(self, current_time: float) -> None:
        """清理过期的限流记录"""
        for limit_type in self.rate_limits:
            expired_keys = []
            for key, rate_info in self.rate_limits[limit_type].items():
                if current_time - rate_info.window_start > 3600:  # 1小时过期
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.rate_limits[limit_type][key]
    
    def block_ip(self, ip: str, duration: int = 3600) -> None:
        """封禁IP地址"""
        self.blocked_ips[ip] = time.time() + duration
        log_security_event("ip_blocked", ip_address=ip, duration=duration)
        logger.warning(f"IP地址被封禁: {ip}, 时长: {duration}秒")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """检查IP是否被封禁"""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                # 封禁已过期，删除记录
                del self.blocked_ips[ip]
        return False
    
    def record_suspicious_activity(self, ip: str) -> None:
        """记录可疑活动"""
        self.suspicious_ips[ip] += 1
        
        # 如果可疑活动过多，封禁IP
        if self.suspicious_ips[ip] > 10:
            self.block_ip(ip, 3600)  # 封禁1小时
            log_security_event("suspicious_activity", ip_address=ip, count=self.suspicious_ips[ip])
    
    def get_rate_limit_info(self, key: str, limit_type: str = "api") -> Dict[str, Any]:
        """获取限流信息"""
        if key not in self.rate_limits[limit_type]:
            return {"requests": 0, "limit": self.default_limits[limit_type]["requests"]}
        
        rate_info = self.rate_limits[limit_type][key]
        limit_config = self.default_limits[limit_type]
        
        return {
            "requests": rate_info.requests,
            "limit": limit_config["requests"],
            "window": limit_config["window"],
            "blocked": rate_info.blocked
        }

# 全局限流器实例
rate_limiter = RateLimiter()

class SecurityValidator:
    """安全验证器"""
    
    @staticmethod
    def validate_input(data: Any, field_name: str, max_length: int = 1000) -> bool:
        """验证输入数据"""
        if isinstance(data, str):
            # 检查长度
            if len(data) > max_length:
                raise ValidationException(f"{field_name}长度超过限制")
            
            # 检查SQL注入
            if SecurityValidator._contains_sql_injection(data):
                raise ValidationException(f"{field_name}包含非法字符")
            
            # 检查XSS
            if SecurityValidator._contains_xss(data):
                raise ValidationException(f"{field_name}包含非法脚本")
        
        return True
    
    @staticmethod
    def _contains_sql_injection(text: str) -> bool:
        """检查SQL注入"""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
            r"(--|#|\/\*|\*\/)",
            r"(\b(SCRIPT|JAVASCRIPT|VBSCRIPT)\b)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def _contains_xss(text: str) -> bool:
        """检查XSS攻击"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """验证密码强度"""
        if len(password) < 8:
            return False
        
        # 检查是否包含大小写字母、数字和特殊字符
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        return has_upper and has_lower and has_digit and has_special
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """清理输入数据"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 转义特殊字符
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text

class AuthenticationService:
    """认证服务"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise AuthenticationException("令牌无效")
    
    @staticmethod
    def generate_csrf_token() -> str:
        """生成CSRF令牌"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, session_token: str) -> bool:
        """验证CSRF令牌"""
        return token == session_token

class SecurityMiddleware:
    """安全中间件"""
    
    def __init__(self):
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
    
    async def process_request(self, request: Request) -> None:
        """处理请求安全检查"""
        client_ip = request.client.host
        
        # 检查IP是否被封禁
        if rate_limiter.is_ip_blocked(client_ip):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP地址已被封禁"
            )
        
        # 检查请求频率
        endpoint = request.url.path
        rate_limit_type = self._get_rate_limit_type(endpoint)
        
        if rate_limiter.is_rate_limited(client_ip, rate_limit_type):
            # 记录可疑活动
            rate_limiter.record_suspicious_activity(client_ip)
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )
        
        # 记录请求
        self.request_counts[client_ip].append(time.time())
        
        # 检查请求头安全
        await self._check_security_headers(request)
    
    def _get_rate_limit_type(self, endpoint: str) -> str:
        """获取限流类型"""
        if "/auth/" in endpoint:
            return "auth"
        elif "/search/" in endpoint:
            return "search"
        elif "/upload/" in endpoint:
            return "upload"
        else:
            return "api"
    
    async def _check_security_headers(self, request: Request) -> None:
        """检查安全头"""
        # 检查User-Agent
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            logger.warning(f"可疑User-Agent: {user_agent}, IP: {request.client.host}")
        
        # 检查Referer
        referer = request.headers.get("referer", "")
        if referer and not self._is_valid_referer(referer):
            logger.warning(f"可疑Referer: {referer}, IP: {request.client.host}")
    
    def _is_valid_referer(self, referer: str) -> bool:
        """检查Referer是否有效"""
        # 这里可以添加域名白名单检查
        return True

# 全局安全中间件实例
security_middleware = SecurityMiddleware()

def require_auth(func):
    """需要认证的装饰器"""
    async def wrapper(*args, **kwargs):
        # 这里应该检查JWT令牌
        # 简化实现，实际应该从请求中获取令牌
        return await func(*args, **kwargs)
    return wrapper

def rate_limit(limit_type: str = "api"):
    """限流装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里应该从请求中获取客户端IP
            # 简化实现
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_input(max_length: int = 1000):
    """输入验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 验证所有字符串参数
            for key, value in kwargs.items():
                if isinstance(value, str):
                    SecurityValidator.validate_input(value, key, max_length)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
