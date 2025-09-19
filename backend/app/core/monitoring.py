"""
监控模块
提供应用监控、指标收集、告警等功能
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from prometheus_client import Counter, Histogram, Gauge, start_http_server
from app.core.config import settings
from app.core.logging import get_logger, log_error
from app.core.performance import performance_monitor

logger = get_logger("monitoring")

# Prometheus指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')
DATABASE_CONNECTIONS = Gauge('database_connections', 'Database connections')
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['cache_type'])
ERROR_COUNT = Counter('errors_total', 'Total errors', ['error_type', 'endpoint'])

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: str
    threshold: float
    duration: int  # 持续时间（秒）
    severity: str  # critical, warning, info
    enabled: bool = True
    last_triggered: Optional[datetime] = None

@dataclass
class Alert:
    """告警"""
    rule_name: str
    message: str
    severity: str
    timestamp: datetime
    resolved: bool = False

class MonitoringService:
    """监控服务"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.health_checks: Dict[str, bool] = {}
        
        # 初始化告警规则
        self._init_alert_rules()
        
        # 启动Prometheus服务器
        self._start_prometheus_server()
    
    def _init_alert_rules(self) -> None:
        """初始化告警规则"""
        self.alert_rules = [
            AlertRule(
                name="high_cpu_usage",
                condition="cpu_percent > 80",
                threshold=80.0,
                duration=300,  # 5分钟
                severity="warning"
            ),
            AlertRule(
                name="high_memory_usage",
                condition="memory_percent > 85",
                threshold=85.0,
                duration=300,
                severity="critical"
            ),
            AlertRule(
                name="high_disk_usage",
                condition="disk_usage_percent > 90",
                threshold=90.0,
                duration=600,  # 10分钟
                severity="critical"
            ),
            AlertRule(
                name="high_error_rate",
                condition="error_rate > 5",
                threshold=5.0,
                duration=300,
                severity="warning"
            ),
            AlertRule(
                name="slow_response_time",
                condition="avg_response_time > 1000",
                threshold=1000.0,
                duration=600,
                severity="warning"
            ),
            AlertRule(
                name="database_connection_failure",
                condition="database_health == False",
                threshold=0.0,
                duration=60,
                severity="critical"
            ),
            AlertRule(
                name="redis_connection_failure",
                condition="redis_health == False",
                threshold=0.0,
                duration=60,
                severity="critical"
            )
        ]
    
    def _start_prometheus_server(self) -> None:
        """启动Prometheus服务器"""
        try:
            start_http_server(9090)
            logger.info("Prometheus监控服务器启动在端口9090")
        except Exception as e:
            logger.error(f"Prometheus服务器启动失败: {e}")
    
    async def start_monitoring(self) -> None:
        """启动监控服务"""
        logger.info("启动应用监控服务...")
        
        # 启动系统监控
        asyncio.create_task(self._monitor_system_metrics())
        
        # 启动健康检查
        asyncio.create_task(self._monitor_health_checks())
        
        # 启动告警检查
        asyncio.create_task(self._monitor_alerts())
        
        logger.info("监控服务启动完成")
    
    async def _monitor_system_metrics(self) -> None:
        """监控系统指标"""
        while True:
            try:
                # 收集系统指标
                system_metrics = await performance_monitor.collect_system_metrics()
                
                # 记录指标历史
                self.metrics_history["cpu_percent"].append(system_metrics.cpu_percent)
                self.metrics_history["memory_percent"].append(system_metrics.memory_percent)
                self.metrics_history["disk_usage_percent"].append(system_metrics.disk_usage_percent)
                
                # 更新Prometheus指标
                self._update_prometheus_metrics(system_metrics)
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"系统指标监控失败: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_health_checks(self) -> None:
        """监控健康检查"""
        while True:
            try:
                # 检查数据库连接
                self.health_checks["database"] = await self._check_database_health()
                
                # 检查Redis连接
                self.health_checks["redis"] = await self._check_redis_health()
                
                # 检查Elasticsearch连接
                self.health_checks["elasticsearch"] = await self._check_elasticsearch_health()
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_alerts(self) -> None:
        """监控告警"""
        while True:
            try:
                await self._check_alert_rules()
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"告警监控失败: {e}")
                await asyncio.sleep(60)
    
    async def _check_database_health(self) -> bool:
        """检查数据库健康状态"""
        try:
            from app.core.database import engine
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    async def _check_redis_health(self) -> bool:
        """检查Redis健康状态"""
        try:
            from app.core.redis import redis_client
            await redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return False
    
    async def _check_elasticsearch_health(self) -> bool:
        """检查Elasticsearch健康状态"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.ELASTICSEARCH_URL}/_cluster/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Elasticsearch健康检查失败: {e}")
            return False
    
    def _update_prometheus_metrics(self, system_metrics) -> None:
        """更新Prometheus指标"""
        # 这里可以添加更多自定义指标
        pass
    
    async def _check_alert_rules(self) -> None:
        """检查告警规则"""
        current_time = datetime.now()
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # 检查是否在冷却期内
            if (rule.last_triggered and 
                current_time - rule.last_triggered < timedelta(seconds=rule.duration)):
                continue
            
            # 评估告警条件
            if await self._evaluate_alert_condition(rule):
                await self._trigger_alert(rule)
                rule.last_triggered = current_time
    
    async def _evaluate_alert_condition(self, rule: AlertRule) -> bool:
        """评估告警条件"""
        try:
            # 获取当前指标值
            metrics = await self._get_current_metrics()
            
            # 简单的条件评估（实际应该使用更复杂的表达式解析器）
            if rule.condition == "cpu_percent > 80":
                return metrics.get("cpu_percent", 0) > rule.threshold
            elif rule.condition == "memory_percent > 85":
                return metrics.get("memory_percent", 0) > rule.threshold
            elif rule.condition == "disk_usage_percent > 90":
                return metrics.get("disk_usage_percent", 0) > rule.threshold
            elif rule.condition == "error_rate > 5":
                return metrics.get("error_rate", 0) > rule.threshold
            elif rule.condition == "avg_response_time > 1000":
                return metrics.get("avg_response_time", 0) > rule.threshold
            elif rule.condition == "database_health == False":
                return not self.health_checks.get("database", True)
            elif rule.condition == "redis_health == False":
                return not self.health_checks.get("redis", True)
            
            return False
            
        except Exception as e:
            logger.error(f"告警条件评估失败: {rule.name}, 错误: {e}")
            return False
    
    async def _get_current_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        # 获取系统指标
        system_metrics = await performance_monitor.collect_system_metrics()
        
        # 获取性能摘要
        performance_summary = performance_monitor.get_performance_summary()
        
        return {
            "cpu_percent": system_metrics.cpu_percent,
            "memory_percent": system_metrics.memory_percent,
            "disk_usage_percent": system_metrics.disk_usage_percent,
            "error_rate": performance_summary.get("error_rate", 0),
            "avg_response_time": performance_summary.get("avg_response_time", 0),
            "database_health": self.health_checks.get("database", True),
            "redis_health": self.health_checks.get("redis", True)
        }
    
    async def _trigger_alert(self, rule: AlertRule) -> None:
        """触发告警"""
        alert = Alert(
            rule_name=rule.name,
            message=f"告警: {rule.name} - 当前值超过阈值 {rule.threshold}",
            severity=rule.severity,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        
        # 记录告警日志
        logger.warning(f"告警触发: {rule.name}, 严重程度: {rule.severity}")
        
        # 发送告警通知
        await self._send_alert_notification(alert)
    
    async def _send_alert_notification(self, alert: Alert) -> None:
        """发送告警通知"""
        try:
            if settings.SMTP_HOST and settings.SMTP_USER:
                await self._send_email_alert(alert)
            else:
                logger.warning(f"邮件配置未完成，无法发送告警通知: {alert.message}")
                
        except Exception as e:
            logger.error(f"发送告警通知失败: {e}")
    
    async def _send_email_alert(self, alert: Alert) -> None:
        """发送邮件告警"""
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USER
            msg['To'] = settings.SMTP_USER  # 发送给自己
            msg['Subject'] = f"小雪宝系统告警 - {alert.severity.upper()}"
            
            body = f"""
告警详情:
- 规则: {alert.rule_name}
- 消息: {alert.message}
- 严重程度: {alert.severity}
- 时间: {alert.timestamp}
- 系统: 小雪宝AI助手
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"告警邮件发送成功: {alert.rule_name}")
            
        except Exception as e:
            logger.error(f"发送告警邮件失败: {e}")
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """获取监控仪表板数据"""
        return {
            "system_metrics": {
                "cpu_percent": self.metrics_history["cpu_percent"][-1] if self.metrics_history["cpu_percent"] else 0,
                "memory_percent": self.metrics_history["memory_percent"][-1] if self.metrics_history["memory_percent"] else 0,
                "disk_usage_percent": self.metrics_history["disk_usage_percent"][-1] if self.metrics_history["disk_usage_percent"] else 0,
            },
            "health_checks": self.health_checks,
            "alerts": [
                {
                    "rule_name": alert.rule_name,
                    "message": alert.message,
                    "severity": alert.severity,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved
                }
                for alert in self.alerts[-10:]  # 最近10个告警
            ],
            "performance": performance_monitor.get_performance_summary(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取告警历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            {
                "rule_name": alert.rule_name,
                "message": alert.message,
                "severity": alert.severity,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved
            }
            for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]
    
    def resolve_alert(self, alert_id: int) -> bool:
        """解决告警"""
        try:
            if 0 <= alert_id < len(self.alerts):
                self.alerts[alert_id].resolved = True
                logger.info(f"告警已解决: {self.alerts[alert_id].rule_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"解决告警失败: {e}")
            return False

# 全局监控服务实例
monitoring_service = MonitoringService()

async def start_monitoring():
    """启动监控服务"""
    await monitoring_service.start_monitoring()

def get_monitoring_dashboard():
    """获取监控仪表板"""
    return monitoring_service.get_monitoring_dashboard()

def get_alert_history(hours: int = 24):
    """获取告警历史"""
    return monitoring_service.get_alert_history(hours)
