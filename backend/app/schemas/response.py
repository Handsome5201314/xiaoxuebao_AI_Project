"""
API响应模型
定义统一的API响应格式和分页模型
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="响应状态")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SuccessResponse(BaseResponse[T]):
    """成功响应模型"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    message: str = Field(default="操作成功")

class ErrorResponse(BaseResponse[None]):
    """错误响应模型"""
    status: ResponseStatus = Field(default=ResponseStatus.ERROR)
    message: str = Field(description="错误消息")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    data: None = Field(default=None)

class StandardResponse(BaseModel):
    """标准响应模型"""
    success: bool = Field(description="操作是否成功")
    message: str = Field(description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(ge=1, description="当前页码")
    page_size: int = Field(ge=1, le=100, description="每页大小")
    total: int = Field(ge=0, description="总记录数")
    total_pages: int = Field(ge=0, description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")
    
    @classmethod
    def create(cls, page: int, page_size: int, total: int) -> "PaginationMeta":
        """创建分页元数据"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    message: str = Field(default="查询成功")
    data: List[T] = Field(description="数据列表")
    pagination: PaginationMeta = Field(description="分页信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(default=None)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SearchResponse(BaseModel, Generic[T]):
    """搜索响应模型"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    message: str = Field(default="搜索成功")
    data: List[T] = Field(description="搜索结果")
    total: int = Field(ge=0, description="总结果数")
    query: str = Field(description="搜索查询")
    search_time: float = Field(ge=0, description="搜索耗时(秒)")
    suggestions: Optional[List[str]] = Field(default=None, description="搜索建议")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="应用的过滤器")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(default=None)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(description="服务状态")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(description="服务版本")
    uptime: float = Field(description="运行时间(秒)")
    dependencies: Dict[str, Dict[str, Any]] = Field(description="依赖服务状态")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ValidationErrorDetail(BaseModel):
    """验证错误详情"""
    field: str = Field(description="字段名")
    message: str = Field(description="错误消息")
    value: Any = Field(description="错误值")

class ValidationErrorResponse(ErrorResponse):
    """验证错误响应"""
    error_code: str = Field(default="VALIDATION_ERROR")
    validation_errors: List[ValidationErrorDetail] = Field(description="验证错误列表")

class BulkOperationResponse(BaseModel):
    """批量操作响应模型"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    message: str = Field(default="批量操作完成")
    total_count: int = Field(ge=0, description="总操作数")
    success_count: int = Field(ge=0, description="成功数")
    error_count: int = Field(ge=0, description="失败数")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StatsResponse(BaseModel):
    """统计响应模型"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    message: str = Field(default="统计查询成功")
    data: Dict[str, Any] = Field(description="统计数据")
    period: Optional[str] = Field(default=None, description="统计周期")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="统计过滤器")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 响应构建器函数
def success_response(
    data: Any = None,
    message: str = "操作成功",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """构建成功响应"""
    return SuccessResponse(
        data=data,
        message=message,
        request_id=request_id
    ).dict()

def error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """构建错误响应"""
    return ErrorResponse(
        message=message,
        error_code=error_code,
        details=details,
        request_id=request_id
    ).dict()

def paginated_response(
    data: List[Any],
    page: int,
    page_size: int,
    total: int,
    message: str = "查询成功",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """构建分页响应"""
    pagination = PaginationMeta.create(page, page_size, total)
    return PaginatedResponse(
        data=data,
        pagination=pagination,
        message=message,
        request_id=request_id
    ).dict()

def search_response(
    data: List[Any],
    total: int,
    query: str,
    search_time: float,
    suggestions: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    message: str = "搜索成功",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """构建搜索响应"""
    return SearchResponse(
        data=data,
        total=total,
        query=query,
        search_time=search_time,
        suggestions=suggestions,
        filters=filters,
        message=message,
        request_id=request_id
    ).dict()

def bulk_operation_response(
    total_count: int,
    success_count: int,
    error_count: int,
    errors: List[Dict[str, Any]] = None,
    message: str = "批量操作完成",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """构建批量操作响应"""
    return BulkOperationResponse(
        total_count=total_count,
        success_count=success_count,
        error_count=error_count,
        errors=errors or [],
        message=message,
        request_id=request_id
    ).dict()

def validation_error_response(
    validation_errors: List[ValidationErrorDetail],
    message: str = "数据验证失败",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """构建验证错误响应"""
    return ValidationErrorResponse(
        message=message,
        validation_errors=validation_errors,
        request_id=request_id
    ).dict()
