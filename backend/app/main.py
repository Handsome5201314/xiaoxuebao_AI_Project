from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import structlog

from app.core.config import settings
from app.api import api_router
from app.core.database import engine, Base
from app.core.redis import redis_client
from app.core.logging import get_logger, log_api_request, log_error
from app.core.exceptions import XiaoxuebaoException, create_http_exception

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger = get_logger("startup")
    logger.info("小雪宝API服务启动中...")
    
    try:
        # 创建数据库表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建完成")
    except Exception as e:
        logger.error("数据库初始化失败", error=str(e))
        raise
    
    yield
    
    # 关闭时执行
    logger.info("小雪宝API服务关闭中...")
    try:
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

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 记录请求开始
    logger = get_logger("request")
    logger.info(
        "请求开始",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    )
    
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录请求完成
        log_api_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=process_time
        )
        
        return response
        
    except Exception as e:
        # 记录错误
        log_error(e, context={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host
        })
        raise

# 全局异常处理器
@app.exception_handler(XiaoxuebaoException)
async def xiaoxuebao_exception_handler(request: Request, exc: XiaoxuebaoException):
    """处理自定义异常"""
    log_error(exc, context={
        "method": request.method,
        "path": request.url.path
    })
    
    http_exc = create_http_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    logger = get_logger("http_error")
    logger.warning(
        "HTTP异常",
        status_code=exc.status_code,
        detail=exc.detail,
        method=request.method,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    log_error(exc, context={
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "内部服务器错误",
            "error_code": "INTERNAL_ERROR"
        }
    )

# 包含API路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "欢迎使用小雪宝Wiki API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-09-19T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)