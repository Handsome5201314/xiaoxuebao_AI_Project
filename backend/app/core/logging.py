"""
日志配置模块
提供结构化的日志记录功能
"""

import structlog
import logging
import sys
from typing import Any, Dict
from app.core.config_simple import settings

def configure_logging() -> None:
    """配置结构化日志"""
    
    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # 配置structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """获取结构化日志记录器"""
    return structlog.get_logger(name)

class LoggerMixin:
    """日志记录混入类"""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """获取日志记录器"""
        return get_logger(self.__class__.__name__)

def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: str = None,
    **kwargs
) -> None:
    """记录API请求日志"""
    logger = get_logger("api")
    logger.info(
        "API请求",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
        user_id=user_id,
        **kwargs
    )

def log_database_operation(
    operation: str,
    table: str,
    duration: float,
    success: bool,
    **kwargs
) -> None:
    """记录数据库操作日志"""
    logger = get_logger("database")
    logger.info(
        "数据库操作",
        operation=operation,
        table=table,
        duration_ms=round(duration * 1000, 2),
        success=success,
        **kwargs
    )

def log_search_operation(
    query: str,
    results_count: int,
    duration: float,
    user_id: str = None,
    **kwargs
) -> None:
    """记录搜索操作日志"""
    logger = get_logger("search")
    logger.info(
        "搜索操作",
        query=query,
        results_count=results_count,
        duration_ms=round(duration * 1000, 2),
        user_id=user_id,
        **kwargs
    )

def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    user_id: str = None,
    **kwargs
) -> None:
    """记录错误日志"""
    logger = get_logger("error")
    logger.error(
        "系统错误",
        error_type=type(error).__name__,
        error_message=str(error),
        user_id=user_id,
        context=context or {},
        **kwargs
    )

def log_security_event(
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    **kwargs
) -> None:
    """记录安全事件日志"""
    logger = get_logger("security")
    logger.warning(
        "安全事件",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        **kwargs
    )

# 初始化日志配置
configure_logging()
