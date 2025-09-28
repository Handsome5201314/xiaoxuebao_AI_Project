"""
API路由管理器
提供版本化的API路由管理和自动注册功能
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.core.logging import get_logger
from app.core.container import container, create_dependency

logger = get_logger(__name__)

class APIRouterManager:
    """API路由管理器"""

    def __init__(self):
        self.routers: Dict[str, APIRouter] = {}
        self.main_router = APIRouter()

    def register_v1_routes(self) -> APIRouter:
        """注册V1版本路由"""
        v1_router = APIRouter(prefix="/v1")

        try:
            # 动态导入路由模块
            from app.api.v1 import articles, auth, users, knowledge, search, monitoring, mental_health

            # 注册各个模块的路由
            route_configs = [
                (articles.router, "/articles", ["文章管理"]),
                (auth.router, "/auth", ["身份认证"]),
                (users.router, "/users", ["用户管理"]),
                (knowledge.router, "/knowledge", ["知识库管理"]),
                (search.router, "/search", ["搜索服务"]),
                (monitoring.router, "/monitoring", ["系统监控"]),
                (mental_health.router, "/mental-health", ["儿童心理健康"]),
            ]

            for router, prefix, tags in route_configs:
                v1_router.include_router(
                    router,
                    prefix=prefix,
                    tags=tags
                )
                logger.info(f"注册路由: {prefix} - {tags}")

            self.routers["v1"] = v1_router
            logger.info("V1版本路由注册完成")

        except ImportError as e:
            logger.error(f"导入路由模块失败: {str(e)}")
            raise

        return v1_router

    def create_main_router(self) -> APIRouter:
        """创建主路由"""
        # 注册V1路由
        v1_router = self.register_v1_routes()
        self.main_router.include_router(v1_router)

        # 添加根级别的路由
        @self.main_router.get("/versions")
        async def get_api_versions():
            """获取API版本信息"""
            from app.schemas.response import success_response

            versions = {
                "v1": {
                    "version": "1.0.0",
                    "status": "stable",
                    "endpoints": len([route for route in v1_router.routes]),
                    "base_url": "/api/v1"
                }
            }

            return success_response(
                data=versions,
                message="API版本信息获取成功"
            )

        logger.info("主路由创建完成")
        return self.main_router

# 创建路由管理器实例
router_manager = APIRouterManager()

# 创建主API路由
api_router = router_manager.create_main_router()

# 导出路由
__all__ = ["api_router", "router_manager"]