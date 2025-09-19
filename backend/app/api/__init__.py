from fastapi import APIRouter
from app.api.v1 import articles, auth, users, knowledge, search, monitoring

# 创建主API路由
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(articles.router, prefix="/articles", tags=["文章"])
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(search.router, prefix="/search", tags=["搜索"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["监控"])

# 导出路由
__all__ = ["api_router"]