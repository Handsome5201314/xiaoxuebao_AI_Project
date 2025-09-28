"""
依赖注入容器
提供服务注册、依赖解析、生命周期管理等功能
"""

import inspect
from typing import Any, Dict, Type, TypeVar, Callable, Optional, Union, get_type_hints
from functools import wraps
from enum import Enum
from dataclasses import dataclass
from contextlib import asynccontextmanager

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class ServiceLifetime(Enum):
    """服务生命周期"""
    SINGLETON = "singleton"  # 单例
    SCOPED = "scoped"       # 作用域
    TRANSIENT = "transient" # 瞬态

@dataclass
class ServiceDescriptor:
    """服务描述符"""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    dependencies: Optional[Dict[str, Type]] = None

class DependencyInjectionContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._building: set = set()  # 防止循环依赖
    
    def register_singleton(
        self, 
        service_type: Type[T], 
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None,
        instance: Optional[T] = None
    ) -> 'DependencyInjectionContainer':
        """注册单例服务"""
        return self._register_service(
            service_type, 
            implementation_type, 
            factory, 
            instance, 
            ServiceLifetime.SINGLETON
        )
    
    def register_scoped(
        self, 
        service_type: Type[T], 
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None
    ) -> 'DependencyInjectionContainer':
        """注册作用域服务"""
        return self._register_service(
            service_type, 
            implementation_type, 
            factory, 
            None, 
            ServiceLifetime.SCOPED
        )
    
    def register_transient(
        self, 
        service_type: Type[T], 
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None
    ) -> 'DependencyInjectionContainer':
        """注册瞬态服务"""
        return self._register_service(
            service_type, 
            implementation_type, 
            factory, 
            None, 
            ServiceLifetime.TRANSIENT
        )
    
    def _register_service(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]],
        factory: Optional[Callable[[], T]],
        instance: Optional[T],
        lifetime: ServiceLifetime
    ) -> 'DependencyInjectionContainer':
        """注册服务"""
        
        # 如果提供了实例，直接注册为单例
        if instance is not None:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                instance=instance,
                lifetime=ServiceLifetime.SINGLETON
            )
            self._singletons[service_type] = instance
            logger.debug(f"注册实例服务: {service_type.__name__}")
            return self
        
        # 确定实现类型
        impl_type = implementation_type or service_type
        
        # 分析依赖
        dependencies = self._analyze_dependencies(impl_type)
        
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=impl_type,
            factory=factory,
            lifetime=lifetime,
            dependencies=dependencies
        )
        
        logger.debug(f"注册服务: {service_type.__name__} -> {impl_type.__name__} ({lifetime.value})")
        return self
    
    def _analyze_dependencies(self, impl_type: Type) -> Dict[str, Type]:
        """分析构造函数依赖"""
        dependencies = {}
        
        try:
            # 获取构造函数签名
            init_signature = inspect.signature(impl_type.__init__)
            type_hints = get_type_hints(impl_type.__init__)
            
            for param_name, param in init_signature.parameters.items():
                if param_name == 'self':
                    continue
                
                # 获取参数类型
                param_type = type_hints.get(param_name, param.annotation)
                
                if param_type != inspect.Parameter.empty:
                    dependencies[param_name] = param_type
                    
        except Exception as e:
            logger.warning(f"分析依赖失败 {impl_type.__name__}: {str(e)}")
        
        return dependencies
    
    def resolve(self, service_type: Type[T]) -> T:
        """解析服务"""
        if service_type in self._building:
            raise ValueError(f"检测到循环依赖: {service_type.__name__}")
        
        # 检查是否已注册
        if service_type not in self._services:
            raise ValueError(f"服务未注册: {service_type.__name__}")
        
        descriptor = self._services[service_type]
        
        # 单例模式
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]
            
            instance = self._create_instance(descriptor)
            self._singletons[service_type] = instance
            return instance
        
        # 作用域模式
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if service_type in self._scoped_instances:
                return self._scoped_instances[service_type]
            
            instance = self._create_instance(descriptor)
            self._scoped_instances[service_type] = instance
            return instance
        
        # 瞬态模式
        else:
            return self._create_instance(descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """创建服务实例"""
        
        # 如果有预设实例，直接返回
        if descriptor.instance is not None:
            return descriptor.instance
        
        # 如果有工厂方法，使用工厂创建
        if descriptor.factory is not None:
            return descriptor.factory()
        
        # 使用构造函数创建
        impl_type = descriptor.implementation_type
        
        # 标记正在构建，防止循环依赖
        self._building.add(descriptor.service_type)
        
        try:
            # 解析依赖
            dependencies = {}
            if descriptor.dependencies:
                for param_name, param_type in descriptor.dependencies.items():
                    dependencies[param_name] = self.resolve(param_type)
            
            # 创建实例
            instance = impl_type(**dependencies)
            logger.debug(f"创建服务实例: {impl_type.__name__}")
            
            return instance
            
        finally:
            self._building.discard(descriptor.service_type)
    
    def clear_scoped(self):
        """清除作用域实例"""
        self._scoped_instances.clear()
        logger.debug("清除作用域实例")
    
    def is_registered(self, service_type: Type) -> bool:
        """检查服务是否已注册"""
        return service_type in self._services
    
    def get_service_info(self, service_type: Type) -> Optional[ServiceDescriptor]:
        """获取服务信息"""
        return self._services.get(service_type)
    
    def list_services(self) -> Dict[Type, ServiceDescriptor]:
        """列出所有注册的服务"""
        return self._services.copy()

# 全局容器实例
container = DependencyInjectionContainer()

# 装饰器
def injectable(lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
    """可注入装饰器"""
    def decorator(cls: Type[T]) -> Type[T]:
        # 自动注册服务
        if lifetime == ServiceLifetime.SINGLETON:
            container.register_singleton(cls)
        elif lifetime == ServiceLifetime.SCOPED:
            container.register_scoped(cls)
        else:
            container.register_transient(cls)
        
        return cls
    
    return decorator

def inject(service_type: Type[T]) -> T:
    """注入依赖"""
    return container.resolve(service_type)

# FastAPI依赖函数生成器
def create_dependency(service_type: Type[T]) -> Callable[[], T]:
    """创建FastAPI依赖函数"""
    def dependency() -> T:
        return container.resolve(service_type)
    
    return dependency

# 作用域管理器
@asynccontextmanager
async def scoped_container():
    """作用域容器上下文管理器"""
    try:
        yield container
    finally:
        container.clear_scoped()

# 服务配置
def configure_services():
    """配置服务"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import get_db
    from app.services.knowledge import KnowledgeService
    from app.services.user import UserService
    from app.services.auth import AuthService
    from app.core.cache import CacheManager, cache_manager
    from app.core.performance_monitor import PerformanceMonitor, get_performance_monitor
    
    # 注册核心服务
    container.register_singleton(CacheManager, instance=cache_manager)
    container.register_singleton(PerformanceMonitor, factory=get_performance_monitor)
    
    # 注册业务服务
    container.register_scoped(KnowledgeService)
    container.register_scoped(UserService)
    container.register_scoped(AuthService)
    
    logger.info("服务配置完成")

# 服务定位器模式（备用）
class ServiceLocator:
    """服务定位器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._container = container
        return cls._instance
    
    def get_service(self, service_type: Type[T]) -> T:
        """获取服务"""
        return self._container.resolve(service_type)
    
    def register_service(
        self, 
        service_type: Type[T], 
        implementation: Union[Type[T], T, Callable[[], T]],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ):
        """注册服务"""
        if isinstance(implementation, type):
            # 注册类型
            if lifetime == ServiceLifetime.SINGLETON:
                self._container.register_singleton(service_type, implementation)
            elif lifetime == ServiceLifetime.SCOPED:
                self._container.register_scoped(service_type, implementation)
            else:
                self._container.register_transient(service_type, implementation)
        elif callable(implementation):
            # 注册工厂
            if lifetime == ServiceLifetime.SINGLETON:
                self._container.register_singleton(service_type, factory=implementation)
            elif lifetime == ServiceLifetime.SCOPED:
                self._container.register_scoped(service_type, factory=implementation)
            else:
                self._container.register_transient(service_type, factory=implementation)
        else:
            # 注册实例
            self._container.register_singleton(service_type, instance=implementation)

# 全局服务定位器
service_locator = ServiceLocator()

# 便捷函数
def get_service(service_type: Type[T]) -> T:
    """获取服务的便捷函数"""
    return container.resolve(service_type)

def register_service(
    service_type: Type[T], 
    implementation: Union[Type[T], T, Callable[[], T]] = None,
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
):
    """注册服务的便捷函数"""
    if implementation is None:
        implementation = service_type
    
    service_locator.register_service(service_type, implementation, lifetime)
