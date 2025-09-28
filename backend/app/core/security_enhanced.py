"""
增强安全模块
提供输入验证、SQL注入防护、XSS防护、CSRF防护等功能
"""

import re
import html
import hashlib
import secrets
import base64
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
import bleach
from urllib.parse import urlparse

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import XiaoxuebaoException

logger = get_logger(__name__)

class SecurityValidator:
    """安全验证器"""
    
    # SQL注入检测模式
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)",
    ]
    
    # XSS检测模式
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
    ]
    
    # 路径遍历检测模式
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
    ]
    
    def __init__(self):
        self.sql_regex = re.compile("|".join(self.SQL_INJECTION_PATTERNS), re.IGNORECASE)
        self.xss_regex = re.compile("|".join(self.XSS_PATTERNS), re.IGNORECASE)
        self.path_regex = re.compile("|".join(self.PATH_TRAVERSAL_PATTERNS), re.IGNORECASE)
    
    def validate_sql_injection(self, value: str) -> bool:
        """检测SQL注入"""
        if not isinstance(value, str):
            return True
        
        if self.sql_regex.search(value):
            logger.warning(f"检测到SQL注入尝试: {value[:100]}")
            return False
        return True
    
    def validate_xss(self, value: str) -> bool:
        """检测XSS攻击"""
        if not isinstance(value, str):
            return True
        
        if self.xss_regex.search(value):
            logger.warning(f"检测到XSS攻击尝试: {value[:100]}")
            return False
        return True
    
    def validate_path_traversal(self, value: str) -> bool:
        """检测路径遍历攻击"""
        if not isinstance(value, str):
            return True
        
        if self.path_regex.search(value):
            logger.warning(f"检测到路径遍历攻击尝试: {value[:100]}")
            return False
        return True
    
    def sanitize_html(self, value: str) -> str:
        """清理HTML内容"""
        if not isinstance(value, str):
            return value
        
        # 允许的HTML标签和属性
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        allowed_attributes = {}
        
        return bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes, strip=True)
    
    def validate_input(self, value: Any, field_name: str = "input") -> Any:
        """综合输入验证"""
        if isinstance(value, str):
            # SQL注入检测
            if not self.validate_sql_injection(value):
                raise XiaoxuebaoException(
                    message=f"字段 {field_name} 包含非法字符",
                    error_code="INVALID_INPUT"
                )
            
            # XSS检测
            if not self.validate_xss(value):
                raise XiaoxuebaoException(
                    message=f"字段 {field_name} 包含非法脚本",
                    error_code="INVALID_INPUT"
                )
            
            # 路径遍历检测
            if not self.validate_path_traversal(value):
                raise XiaoxuebaoException(
                    message=f"字段 {field_name} 包含非法路径",
                    error_code="INVALID_INPUT"
                )
        
        elif isinstance(value, dict):
            # 递归验证字典
            for k, v in value.items():
                self.validate_input(k, f"{field_name}.key")
                self.validate_input(v, f"{field_name}.{k}")
        
        elif isinstance(value, list):
            # 递归验证列表
            for i, item in enumerate(value):
                self.validate_input(item, f"{field_name}[{i}]")
        
        return value

class PasswordSecurity:
    """密码安全管理"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.min_length = 8
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def validate_password_strength(self, password: str) -> tuple[bool, List[str]]:
        """验证密码强度"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"密码长度至少{self.min_length}位")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("密码必须包含大写字母")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("密码必须包含小写字母")
        
        if self.require_digits and not re.search(r'\d', password):
            errors.append("密码必须包含数字")
        
        if self.require_special and not re.search(f'[{re.escape(self.special_chars)}]', password):
            errors.append("密码必须包含特殊字符")
        
        # 检查常见弱密码
        weak_passwords = [
            "password", "123456", "qwerty", "admin", "root",
            "password123", "123456789", "12345678"
        ]
        if password.lower() in weak_passwords:
            errors.append("密码过于简单，请使用更复杂的密码")
        
        return len(errors) == 0, errors
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_secure_password(self, length: int = 12) -> str:
        """生成安全密码"""
        import string
        
        chars = string.ascii_letters + string.digits + self.special_chars
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # 确保包含所有必需的字符类型
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            password = password[:-1] + secrets.choice(string.ascii_uppercase)
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            password = password[:-1] + secrets.choice(string.ascii_lowercase)
        
        if self.require_digits and not re.search(r'\d', password):
            password = password[:-1] + secrets.choice(string.digits)
        
        if self.require_special and not re.search(f'[{re.escape(self.special_chars)}]', password):
            password = password[:-1] + secrets.choice(self.special_chars)
        
        return password

class TokenSecurity:
    """令牌安全管理"""
    
    def __init__(self):
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)  # JWT ID
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"令牌验证失败: {str(e)}")
            raise XiaoxuebaoException(
                message="无效的访问令牌",
                error_code="INVALID_TOKEN"
            )
    
    def create_csrf_token(self, user_id: str) -> str:
        """创建CSRF令牌"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        data = f"{user_id}:{timestamp}:{secrets.token_urlsafe(16)}"
        signature = hashlib.sha256(f"{data}:{self.secret_key}".encode()).hexdigest()
        token = base64.b64encode(f"{data}:{signature}".encode()).decode()
        return token
    
    def verify_csrf_token(self, token: str, user_id: str, max_age: int = 3600) -> bool:
        """验证CSRF令牌"""
        try:
            decoded = base64.b64decode(token.encode()).decode()
            parts = decoded.split(':')
            
            if len(parts) != 4:
                return False
            
            token_user_id, timestamp, nonce, signature = parts
            
            # 验证用户ID
            if token_user_id != user_id:
                return False
            
            # 验证时间戳
            token_time = int(timestamp)
            current_time = int(datetime.utcnow().timestamp())
            if current_time - token_time > max_age:
                return False
            
            # 验证签名
            data = f"{token_user_id}:{timestamp}:{nonce}"
            expected_signature = hashlib.sha256(f"{data}:{self.secret_key}".encode()).hexdigest()
            
            return secrets.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.warning(f"CSRF令牌验证失败: {str(e)}")
            return False

class RequestSecurity:
    """请求安全检查"""
    
    def __init__(self):
        self.validator = SecurityValidator()
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.allowed_content_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain"
        ]
    
    async def validate_request(self, request: Request) -> None:
        """验证请求安全性"""
        # 检查请求大小
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="请求体过大"
            )
        
        # 检查Content-Type
        content_type = request.headers.get("content-type", "").split(";")[0]
        if content_type and content_type not in self.allowed_content_types:
            logger.warning(f"不允许的Content-Type: {content_type}")
        
        # 检查User-Agent
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) > 500:
            logger.warning(f"可疑的User-Agent: {user_agent[:100]}")
        
        # 检查Referer（如果存在）
        referer = request.headers.get("referer")
        if referer:
            parsed_referer = urlparse(referer)
            if parsed_referer.hostname and parsed_referer.hostname not in settings.CORS_ORIGINS:
                logger.warning(f"可疑的Referer: {referer}")

# 全局安全实例
security_validator = SecurityValidator()
password_security = PasswordSecurity()
token_security = TokenSecurity()
request_security = RequestSecurity()

# 安全装饰器
def validate_input_security(func):
    """输入安全验证装饰器"""
    async def wrapper(*args, **kwargs):
        # 验证所有输入参数
        for arg in args:
            if hasattr(arg, '__dict__'):
                for field_name, field_value in arg.__dict__.items():
                    security_validator.validate_input(field_value, field_name)
        
        for key, value in kwargs.items():
            security_validator.validate_input(value, key)
        
        return await func(*args, **kwargs)
    
    return wrapper
