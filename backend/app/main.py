from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import uuid
from typing import Dict, Any

from app.core.config_simple import settings
from app.api import api_router
from app.core.database import engine, Base
from app.core.redis import redis_client
from app.core.logging import get_logger, log_api_request, log_error
from app.core.exceptions import XiaoxuebaoException, create_http_exception
from app.core.cache import cache_manager
from app.core.performance_monitor import get_performance_monitor
from app.core.rate_limiter import rate_limiter, rate_limit_middleware
from app.core.security_enhanced import request_security
from app.schemas.response import (
    error_response, validation_error_response, ValidationErrorDetail, success_response
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger = get_logger("startup")
    logger.info("小雪宝API服务启动中...")

    try:
        # 初始化缓存
        await cache_manager.initialize()
        logger.info("缓存系统初始化完成")

        # 初始化限流器
        await rate_limiter.initialize()
        logger.info("限流系统初始化完成")

        # 创建数据库表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建完成")

        # 初始化性能监控
        performance_monitor = get_performance_monitor()
        logger.info("性能监控系统初始化完成")

        # 缓存预热
        from app.core.cache import CacheService
        await CacheService.warm_up_cache()

    except Exception as e:
        logger.error("服务初始化失败", error=str(e))
        raise

    yield

    # 关闭时执行
    logger.info("小雪宝API服务关闭中...")
    try:
        await cache_manager.close()
        await redis_client.close()
        await engine.dispose()
        logger.info("资源清理完成")
    except Exception as e:
        logger.error("资源清理失败", error=str(e))

app = FastAPI(
    title="小雪宝Wiki API",
    description="白血病知识库Wiki系统API文档",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流中间件
app.middleware("http")(rate_limit_middleware)

# 安全中间件
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """安全检查中间件"""
    try:
        # 验证请求安全性
        await request_security.validate_request(request)

        # 添加安全响应头
        response = await call_next(request)

        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"

        return response

    except Exception as e:
        logger.error(f"安全检查失败: {str(e)}")
        return JSONResponse(
            status_code=400,
            content=error_response(
                message="请求不符合安全要求",
                error_code="SECURITY_VIOLATION"
            )
        )

# 请求日志和性能监控中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    # 将request_id添加到请求状态中
    request.state.request_id = request_id

    # 记录请求开始
    logger = get_logger("request")
    logger.info(
        "请求开始",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown"
    )

    try:
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"

        # 记录请求完成
        log_api_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=process_time,
            request_id=request_id
        )

        return response

    except Exception as e:
        # 记录错误
        log_error(e, context={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown"
        })
        raise

# 全局异常处理器
@app.exception_handler(XiaoxuebaoException)
async def xiaoxuebao_exception_handler(request: Request, exc: XiaoxuebaoException):
    """处理自定义异常"""
    request_id = getattr(request.state, 'request_id', None)

    log_error(exc, context={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path
    })

    http_exc = create_http_exception(exc)
    response_content = error_response(
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details,
        request_id=request_id
    )

    return JSONResponse(
        status_code=http_exc.status_code,
        content=response_content
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    request_id = getattr(request.state, 'request_id', None)

    validation_errors = []
    for error in exc.errors():
        validation_errors.append(ValidationErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            value=error.get("input", "")
        ))

    logger = get_logger("validation_error")
    logger.warning(
        "请求验证失败",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        errors=exc.errors()
    )

    response_content = validation_error_response(
        validation_errors=validation_errors,
        request_id=request_id
    )

    return JSONResponse(
        status_code=422,
        content=response_content
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    request_id = getattr(request.state, 'request_id', None)

    logger = get_logger("http_error")
    logger.warning(
        "HTTP异常",
        request_id=request_id,
        status_code=exc.status_code,
        detail=exc.detail,
        method=request.method,
        path=request.url.path
    )

    response_content = error_response(
        message=str(exc.detail),
        error_code="HTTP_ERROR",
        request_id=request_id
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    request_id = getattr(request.state, 'request_id', None)

    log_error(exc, context={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host if request.client else "unknown"
    })

    response_content = error_response(
        message="内部服务器错误",
        error_code="INTERNAL_ERROR",
        request_id=request_id
    )

    return JSONResponse(
        status_code=500,
        content=response_content
    )

# 包含API路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root(request: Request):
    """根路径"""
    request_id = getattr(request.state, 'request_id', None)
    from app.schemas.response import success_response

    return success_response(
        data={
            "service": "小雪宝Wiki API",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs_url": "/docs"
        },
        message="欢迎使用小雪宝Wiki API",
        request_id=request_id
    )

@app.get("/health")
async def health_check(request: Request):
    """健康检查"""
    import psutil
    from datetime import datetime

    request_id = getattr(request.state, 'request_id', None)
    start_time = time.time()

    # 检查各个组件状态
    dependencies = {}

    # 检查数据库
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        dependencies["database"] = {"status": "healthy", "response_time": time.time() - start_time}
    except Exception as e:
        dependencies["database"] = {"status": "unhealthy", "error": str(e)}

    # 检查Redis
    try:
        redis_start = time.time()
        await redis_client.ping()
        dependencies["redis"] = {"status": "healthy", "response_time": time.time() - redis_start}
    except Exception as e:
        dependencies["redis"] = {"status": "unhealthy", "error": str(e)}

    # 检查缓存
    cache_stats = cache_manager.get_stats()
    dependencies["cache"] = {"status": "healthy", "stats": cache_stats}

    # 系统信息
    system_info = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }

    from app.schemas.response import HealthCheckResponse

    health_data = HealthCheckResponse(
        status="healthy" if all(dep.get("status") == "healthy" for dep in dependencies.values()) else "degraded",
        version=settings.APP_VERSION,
        uptime=time.time() - start_time,  # 这里应该是实际的启动时间
        dependencies=dependencies
    )

    return success_response(
        data=health_data.dict(),
        message="健康检查完成",
        request_id=request_id
    )

@app.get("/metrics")
async def get_metrics(request: Request):
    """获取性能指标"""
    request_id = getattr(request.state, 'request_id', None)

    performance_monitor = get_performance_monitor()
    performance_report = performance_monitor.get_performance_report()

    return success_response(
        data=performance_report,
        message="性能指标获取成功",
        request_id=request_id
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)