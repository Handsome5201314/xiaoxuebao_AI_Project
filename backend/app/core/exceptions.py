"""
自定义异常类
定义项目特定的异常类型
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class XiaoxuebaoException(Exception):
    """小雪宝基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class KnowledgeBaseException(XiaoxuebaoException):
    """知识库相关异常"""
    pass

class SearchException(XiaoxuebaoException):
    """搜索相关异常"""
    pass

class UserException(XiaoxuebaoException):
    """用户相关异常"""
    pass

class AuthenticationException(XiaoxuebaoException):
    """认证相关异常"""
    pass

class ValidationException(XiaoxuebaoException):
    """数据验证异常"""
    pass

class DatabaseException(XiaoxuebaoException):
    """数据库操作异常"""
    pass

class ExternalServiceException(XiaoxuebaoException):
    """外部服务异常"""
    pass

# 预定义的错误代码
class ErrorCodes:
    """错误代码常量"""
    
    # 通用错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    
    # 知识库错误
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"
    TERM_NOT_FOUND = "TERM_NOT_FOUND"
    GUIDELINE_NOT_FOUND = "GUIDELINE_NOT_FOUND"
    DUPLICATE_CATEGORY = "DUPLICATE_CATEGORY"
    DUPLICATE_TERM = "DUPLICATE_TERM"
    
    # 搜索错误
    SEARCH_QUERY_INVALID = "SEARCH_QUERY_INVALID"
    SEARCH_SERVICE_UNAVAILABLE = "SEARCH_SERVICE_UNAVAILABLE"
    ELASTICSEARCH_ERROR = "ELASTICSEARCH_ERROR"
    
    # 用户错误
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    
    # 认证错误
    TOKEN_INVALID = "TOKEN_INVALID"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # 数据库错误
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_TRANSACTION_ERROR = "DATABASE_TRANSACTION_ERROR"
    
    # 外部服务错误
    ELASTICSEARCH_CONNECTION_ERROR = "ELASTICSEARCH_CONNECTION_ERROR"
    REDIS_CONNECTION_ERROR = "REDIS_CONNECTION_ERROR"
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"

def create_http_exception(
    exception: XiaoxuebaoException,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> HTTPException:
    """将自定义异常转换为HTTP异常"""
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exception.message,
            "error_code": exception.error_code,
            "details": exception.details
        }
    )

def handle_database_exception(exception: Exception) -> HTTPException:
    """处理数据库异常"""
    from app.core.logging import log_error
    
    log_error(exception, context={"type": "database_error"})
    
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "message": "数据库操作失败",
            "error_code": ErrorCodes.DATABASE_QUERY_ERROR,
            "details": {"original_error": str(exception)}
        }
    )

def handle_validation_exception(exception: Exception) -> HTTPException:
    """处理验证异常"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "message": "数据验证失败",
            "error_code": ErrorCodes.VALIDATION_ERROR,
            "details": {"validation_error": str(exception)}
        }
    )

def handle_authentication_exception(exception: Exception) -> HTTPException:
    """处理认证异常"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "message": "认证失败",
            "error_code": ErrorCodes.UNAUTHORIZED,
            "details": {"auth_error": str(exception)}
        }
    )

def handle_not_found_exception(resource: str, resource_id: Any) -> HTTPException:
    """处理资源未找到异常"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "message": f"{resource}不存在",
            "error_code": ErrorCodes.NOT_FOUND,
            "details": {"resource": resource, "resource_id": str(resource_id)}
        }
    )
