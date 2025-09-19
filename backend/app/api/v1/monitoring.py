"""
监控API端点
提供监控数据、告警管理等功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime

from app.core.monitoring import (
    monitoring_service, 
    get_monitoring_dashboard, 
    get_alert_history
)
from app.core.performance import performance_monitor
from app.core.cache import cache_manager
from app.core.logging import get_logger
from app.schemas.user import UserResponse
from app.services.auth import get_current_admin_user_service

router = APIRouter(prefix="/monitoring", tags=["监控管理"])
logger = get_logger("monitoring_api")

@router.get("/dashboard")
async def get_dashboard(
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """获取监控仪表板数据"""
    try:
        dashboard_data = get_monitoring_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error(f"获取监控仪表板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取监控数据失败"
        )

@router.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查各个服务的健康状态
        health_status = {
            "database": monitoring_service.health_checks.get("database", False),
            "redis": monitoring_service.health_checks.get("redis", False),
            "elasticsearch": monitoring_service.health_checks.get("elasticsearch", False),
            "timestamp": datetime.now().isoformat()
        }
        
        # 计算整体健康状态
        all_healthy = all(health_status.values())
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "services": health_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/metrics")
async def get_metrics(
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """获取系统指标"""
    try:
        # 获取性能指标
        performance_summary = performance_monitor.get_performance_summary()
        
        # 获取缓存统计
        cache_stats = cache_manager.get_stats()
        
        # 获取系统指标
        system_metrics = await performance_monitor.collect_system_metrics()
        
        return {
            "performance": performance_summary,
            "cache": cache_stats,
            "system": {
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "memory_used_mb": system_metrics.memory_used_mb,
                "memory_available_mb": system_metrics.memory_available_mb,
                "disk_usage_percent": system_metrics.disk_usage_percent,
                "disk_free_gb": system_metrics.disk_free_gb
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统指标失败"
        )

@router.get("/alerts")
async def get_alerts(
    hours: int = 24,
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """获取告警历史"""
    try:
        alerts = get_alert_history(hours)
        return {
            "alerts": alerts,
            "count": len(alerts),
            "hours": hours,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取告警历史失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取告警历史失败"
        )

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """解决告警"""
    try:
        success = monitoring_service.resolve_alert(alert_id)
        if success:
            return {"message": "告警已解决", "alert_id": alert_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="告警不存在"
            )
            
    except Exception as e:
        logger.error(f"解决告警失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="解决告警失败"
        )

@router.get("/performance/slow-queries")
async def get_slow_queries(
    threshold: float = 1000.0,
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """获取慢查询列表"""
    try:
        slow_queries = performance_monitor.get_slow_queries(threshold)
        return {
            "slow_queries": slow_queries,
            "threshold": threshold,
            "count": len(slow_queries),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取慢查询失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取慢查询失败"
        )

@router.get("/performance/recommendations")
async def get_performance_recommendations(
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """获取性能优化建议"""
    try:
        recommendations = performance_monitor.get_performance_recommendations()
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取性能建议失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取性能建议失败"
        )

@router.get("/cache/stats")
async def get_cache_stats(
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """获取缓存统计"""
    try:
        stats = cache_manager.get_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取缓存统计失败"
        )

@router.post("/cache/clear")
async def clear_cache(
    pattern: str = "*",
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """清除缓存"""
    try:
        deleted_count = await cache_manager.clear_pattern(pattern)
        return {
            "message": f"缓存清除完成",
            "pattern": pattern,
            "deleted_count": deleted_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清除缓存失败"
        )

@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_admin_user_service)
):
    """获取最近的日志"""
    try:
        # 这里应该从日志文件或日志系统获取最近的日志
        # 简化实现，返回示例数据
        return {
            "message": "日志功能需要配置日志收集系统",
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取日志失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志失败"
        )
