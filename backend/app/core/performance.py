"""
性能监控模块
提供性能指标收集、监控和优化建议
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import psutil
import structlog

from app.core.logging import get_logger

logger = get_logger("performance")

@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    name: str
    value: float
    timestamp: datetime
    unit: str = "ms"
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class SystemMetrics:
    """系统指标"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    timestamp: datetime

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.system_metrics_history: deque = deque(maxlen=100)
        self.request_times: Dict[str, List[float]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.active_connections = 0
        self.total_requests = 0
        
    def record_metric(self, metric: PerformanceMetric) -> None:
        """记录性能指标"""
        self.metrics_history.append(metric)
        
        # 记录到日志
        logger.info(
            "性能指标",
            name=metric.name,
            value=metric.value,
            unit=metric.unit,
            tags=metric.tags
        )
    
    def record_request_time(self, endpoint: str, duration: float) -> None:
        """记录请求时间"""
        self.request_times[endpoint].append(duration)
        self.total_requests += 1
        
        # 保持最近100个请求的时间
        if len(self.request_times[endpoint]) > 100:
            self.request_times[endpoint] = self.request_times[endpoint][-100:]
    
    def record_error(self, endpoint: str, error_type: str) -> None:
        """记录错误"""
        error_key = f"{endpoint}:{error_type}"
        self.error_counts[error_key] += 1
    
    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """获取端点统计信息"""
        times = self.request_times.get(endpoint, [])
        if not times:
            return {}
        
        return {
            "count": len(times),
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "p95_time": self._percentile(times, 95),
            "p99_time": self._percentile(times, 99)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            memory_available_mb = memory.available / 1024 / 1024
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            disk_free_gb = disk.free / 1024 / 1024 / 1024
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                timestamp=datetime.now()
            )
            
            self.system_metrics_history.append(metrics)
            
            # 检查系统健康状态
            await self._check_system_health(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"系统指标收集失败: {e}")
            return SystemMetrics(
                cpu_percent=0,
                memory_percent=0,
                memory_used_mb=0,
                memory_available_mb=0,
                disk_usage_percent=0,
                disk_free_gb=0,
                timestamp=datetime.now()
            )
    
    async def _check_system_health(self, metrics: SystemMetrics) -> None:
        """检查系统健康状态"""
        warnings = []
        
        # CPU使用率检查
        if metrics.cpu_percent > 80:
            warnings.append(f"CPU使用率过高: {metrics.cpu_percent:.1f}%")
        
        # 内存使用率检查
        if metrics.memory_percent > 85:
            warnings.append(f"内存使用率过高: {metrics.memory_percent:.1f}%")
        
        # 磁盘使用率检查
        if metrics.disk_usage_percent > 90:
            warnings.append(f"磁盘使用率过高: {metrics.disk_usage_percent:.1f}%")
        
        # 记录警告
        for warning in warnings:
            logger.warning("系统健康警告", warning=warning)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        # 计算平均响应时间
        all_times = []
        for times in self.request_times.values():
            all_times.extend(times)
        
        avg_response_time = sum(all_times) / len(all_times) if all_times else 0
        
        # 计算错误率
        total_errors = sum(self.error_counts.values())
        error_rate = (total_errors / self.total_requests * 100) if self.total_requests > 0 else 0
        
        # 获取最新系统指标
        latest_system_metrics = None
        if self.system_metrics_history:
            latest_system_metrics = self.system_metrics_history[-1]
        
        return {
            "total_requests": self.total_requests,
            "avg_response_time": round(avg_response_time, 2),
            "error_rate": round(error_rate, 2),
            "active_connections": self.active_connections,
            "system_metrics": {
                "cpu_percent": latest_system_metrics.cpu_percent if latest_system_metrics else 0,
                "memory_percent": latest_system_metrics.memory_percent if latest_system_metrics else 0,
                "disk_usage_percent": latest_system_metrics.disk_usage_percent if latest_system_metrics else 0
            } if latest_system_metrics else None,
            "endpoint_stats": {
                endpoint: self.get_endpoint_stats(endpoint)
                for endpoint in self.request_times.keys()
            },
            "error_counts": dict(self.error_counts)
        }
    
    def get_slow_queries(self, threshold: float = 1000.0) -> List[Dict[str, Any]]:
        """获取慢查询列表"""
        slow_queries = []
        
        for endpoint, times in self.request_times.items():
            slow_times = [t for t in times if t > threshold]
            if slow_times:
                slow_queries.append({
                    "endpoint": endpoint,
                    "count": len(slow_times),
                    "avg_time": sum(slow_times) / len(slow_times),
                    "max_time": max(slow_times)
                })
        
        return sorted(slow_queries, key=lambda x: x["avg_time"], reverse=True)
    
    def get_performance_recommendations(self) -> List[str]:
        """获取性能优化建议"""
        recommendations = []
        
        # 检查响应时间
        all_times = []
        for times in self.request_times.values():
            all_times.extend(times)
        
        if all_times:
            avg_time = sum(all_times) / len(all_times)
            if avg_time > 500:
                recommendations.append("平均响应时间过长，建议优化数据库查询和添加缓存")
        
        # 检查错误率
        total_errors = sum(self.error_counts.values())
        if self.total_requests > 0:
            error_rate = total_errors / self.total_requests * 100
            if error_rate > 5:
                recommendations.append(f"错误率过高 ({error_rate:.1f}%)，建议检查错误日志")
        
        # 检查系统资源
        if self.system_metrics_history:
            latest = self.system_metrics_history[-1]
            if latest.cpu_percent > 70:
                recommendations.append("CPU使用率较高，建议优化代码或增加服务器资源")
            if latest.memory_percent > 80:
                recommendations.append("内存使用率较高，建议检查内存泄漏或增加内存")
            if latest.disk_usage_percent > 85:
                recommendations.append("磁盘使用率较高，建议清理日志文件或增加存储空间")
        
        return recommendations

# 全局性能监控器实例
performance_monitor = PerformanceMonitor()

def monitor_performance(func_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name_actual = func_name or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                
                # 记录成功指标
                duration = (time.time() - start_time) * 1000
                metric = PerformanceMetric(
                    name=f"{func_name_actual}_duration",
                    value=duration,
                    timestamp=datetime.now(),
                    unit="ms"
                )
                performance_monitor.record_metric(metric)
                
                return result
                
            except Exception as e:
                # 记录错误
                performance_monitor.record_error(func_name_actual, type(e).__name__)
                raise
        
        return wrapper
    return decorator

class PerformanceService:
    """性能服务类"""
    
    @staticmethod
    async def start_system_monitoring() -> None:
        """启动系统监控"""
        logger.info("启动系统性能监控...")
        
        while True:
            try:
                await performance_monitor.collect_system_metrics()
                await asyncio.sleep(60)  # 每分钟收集一次
            except Exception as e:
                logger.error(f"系统监控失败: {e}")
                await asyncio.sleep(60)
    
    @staticmethod
    def get_performance_dashboard() -> Dict[str, Any]:
        """获取性能仪表板数据"""
        return {
            "summary": performance_monitor.get_performance_summary(),
            "slow_queries": performance_monitor.get_slow_queries(),
            "recommendations": performance_monitor.get_performance_recommendations(),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def record_api_request(endpoint: str, duration: float, status_code: int) -> None:
        """记录API请求"""
        performance_monitor.record_request_time(endpoint, duration)
        
        if status_code >= 400:
            performance_monitor.record_error(endpoint, f"HTTP_{status_code}")
    
    @staticmethod
    def record_database_operation(operation: str, duration: float, success: bool) -> None:
        """记录数据库操作"""
        metric = PerformanceMetric(
            name=f"db_{operation}",
            value=duration,
            timestamp=datetime.now(),
            unit="ms",
            tags={"success": str(success)}
        )
        performance_monitor.record_metric(metric)
        
        if not success:
            performance_monitor.record_error("database", operation)
