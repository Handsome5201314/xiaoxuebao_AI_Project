"""
小雪宝API网关
负责请求路由、认证、限流等功能
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import asyncio
import structlog
from contextlib import asynccontextmanager
import os
from typing import Dict, Any

# 配置日志
logger = structlog.get_logger()

# 服务配置
SERVICES = {
    "knowledge": "http://knowledge-service:8001",
    "search": "http://search-service:8002", 
    "users": "http://user-service:8003"
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("API网关启动中...")
    yield
    logger.info("API网关关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="小雪宝API网关",
    description="白血病AI关爱助手API网关",
    version="1.0.0",
    lifespan=lifespan
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 生产环境应该限制具体域名
)

# HTTP客户端
http_client = httpx.AsyncClient(timeout=30.0)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = asyncio.get_event_loop().time()
    
    # 记录请求
    logger.info(
        "请求开始",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host
    )
    
    response = await call_next(request)
    
    # 记录响应
    process_time = asyncio.get_event_loop().time() - start_time
    logger.info(
        "请求完成",
        status_code=response.status_code,
        process_time=f"{process_time:.3f}s"
    )
    
    return response

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """简单的限流中间件"""
    # 这里可以实现更复杂的限流逻辑
    # 目前只是简单的示例
    return await call_next(request)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用小雪宝API网关",
        "version": "1.0.0",
        "services": list(SERVICES.keys())
    }

@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(service_name: str, path: str, request: Request):
    """代理请求到相应的微服务"""
    
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"服务 {service_name} 不存在")
    
    service_url = SERVICES[service_name]
    target_url = f"{service_url}/{path}"
    
    # 获取请求体
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # 获取查询参数
    query_params = dict(request.query_params)
    
    # 获取请求头
    headers = dict(request.headers)
    # 移除可能导致问题的头部
    headers.pop("host", None)
    headers.pop("content-length", None)
    
    try:
        # 转发请求
        response = await http_client.request(
            method=request.method,
            url=target_url,
            params=query_params,
            headers=headers,
            content=body
        )
        
        # 返回响应
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except httpx.TimeoutException:
        logger.error("请求超时", service=service_name, url=target_url)
        raise HTTPException(status_code=504, detail="服务请求超时")
    
    except httpx.ConnectError:
        logger.error("服务连接失败", service=service_name, url=target_url)
        raise HTTPException(status_code=503, detail=f"服务 {service_name} 不可用")
    
    except Exception as e:
        logger.error("请求处理失败", error=str(e), service=service_name)
        raise HTTPException(status_code=500, detail="内部服务器错误")

@app.get("/api/services/status")
async def services_status():
    """检查所有微服务状态"""
    status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            response = await http_client.get(f"{service_url}/health", timeout=5.0)
            status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": service_url,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            status[service_name] = {
                "status": "unhealthy",
                "url": service_url,
                "error": str(e)
            }
    
    return {"services": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
