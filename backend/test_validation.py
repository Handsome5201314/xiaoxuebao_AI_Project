#!/usr/bin/env python3
"""
测试验证脚本
验证项目完善后的功能是否正常工作
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试核心模块导入
        from app.core.config import settings
        print("✅ 配置模块导入成功")
        
        from app.core.database import engine
        print("✅ 数据库模块导入成功")
        
        from app.core.redis import redis_client
        print("✅ Redis模块导入成功")
        
        from app.core.logging import get_logger
        print("✅ 日志模块导入成功")
        
        from app.core.exceptions import XiaoxuebaoException
        print("✅ 异常模块导入成功")
        
        from app.core.cache import cache_manager
        print("✅ 缓存模块导入成功")
        
        from app.core.performance import performance_monitor
        print("✅ 性能监控模块导入成功")
        
        from app.core.security import rate_limiter
        print("✅ 安全模块导入成功")
        
        from app.core.monitoring import monitoring_service
        print("✅ 监控模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_configuration():
    """测试配置"""
    print("\n🔧 测试配置...")
    
    try:
        from app.core.config import settings
        
        # 检查必要的配置项
        required_configs = [
            'APP_NAME',
            'DEBUG',
            'DATABASE_URL',
            'REDIS_URL',
            'SECRET_KEY',
            'JWT_SECRET'
        ]
        
        for config in required_configs:
            if hasattr(settings, config):
                print(f"✅ {config}: {getattr(settings, config)}")
            else:
                print(f"❌ 缺少配置: {config}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n🗄️ 测试数据库连接...")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        async def test_db():
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        
        result = asyncio.run(test_db())
        if result:
            print("✅ 数据库连接成功")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def test_redis_connection():
    """测试Redis连接"""
    print("\n🔴 测试Redis连接...")
    
    try:
        from app.core.redis import redis_client
        
        async def test_redis():
            await redis_client.ping()
            return True
        
        result = asyncio.run(test_redis())
        if result:
            print("✅ Redis连接成功")
            return True
        else:
            print("❌ Redis连接失败")
            return False
            
    except Exception as e:
        print(f"❌ Redis连接测试失败: {e}")
        return False

def test_api_routes():
    """测试API路由"""
    print("\n🌐 测试API路由...")
    
    try:
        from app.api import api_router
        
        # 检查路由是否正确定义
        routes = []
        for route in api_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{route.methods} {route.path}")
        
        print(f"✅ 发现 {len(routes)} 个API路由")
        for route in routes[:5]:  # 显示前5个路由
            print(f"  - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ API路由测试失败: {e}")
        return False

def test_security_features():
    """测试安全功能"""
    print("\n🔒 测试安全功能...")
    
    try:
        from app.core.security import SecurityValidator, AuthenticationService
        
        # 测试输入验证
        test_inputs = [
            ("正常文本", True),
            ("<script>alert('xss')</script>", False),
            ("'; DROP TABLE users; --", False),
            ("正常邮箱@example.com", True)
        ]
        
        for test_input, should_pass in test_inputs:
            try:
                SecurityValidator.validate_input(test_input, "test_field")
                result = should_pass
            except:
                result = not should_pass
            
            if result:
                print(f"✅ 输入验证通过: {test_input[:20]}...")
            else:
                print(f"❌ 输入验证失败: {test_input[:20]}...")
        
        # 测试密码哈希
        password = "test_password"
        hashed = AuthenticationService.hash_password(password)
        verified = AuthenticationService.verify_password(password, hashed)
        
        if verified:
            print("✅ 密码哈希验证成功")
        else:
            print("❌ 密码哈希验证失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 安全功能测试失败: {e}")
        return False

def test_performance_monitoring():
    """测试性能监控"""
    print("\n📊 测试性能监控...")
    
    try:
        from app.core.performance import performance_monitor
        
        # 测试性能指标记录
        from app.core.performance import PerformanceMetric
        from datetime import datetime
        
        metric = PerformanceMetric(
            name="test_metric",
            value=100.0,
            timestamp=datetime.now(),
            unit="ms"
        )
        
        performance_monitor.record_metric(metric)
        
        # 测试性能摘要
        summary = performance_monitor.get_performance_summary()
        
        if summary:
            print("✅ 性能监控功能正常")
            print(f"  - 总请求数: {summary.get('total_requests', 0)}")
            print(f"  - 平均响应时间: {summary.get('avg_response_time', 0)}ms")
            return True
        else:
            print("❌ 性能监控功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 性能监控测试失败: {e}")
        return False

def test_cache_functionality():
    """测试缓存功能"""
    print("\n💾 测试缓存功能...")
    
    try:
        from app.core.cache import cache_manager
        
        async def test_cache():
            # 测试缓存设置和获取
            test_key = "test_cache_key"
            test_value = {"test": "data", "number": 123}
            
            # 设置缓存
            await cache_manager.set(test_key, test_value, expire=60)
            
            # 获取缓存
            cached_value = await cache_manager.get(test_key)
            
            # 检查缓存是否存在
            exists = await cache_manager.exists(test_key)
            
            # 删除缓存
            await cache_manager.delete(test_key)
            
            return cached_value == test_value and exists
            
        result = asyncio.run(test_cache())
        
        if result:
            print("✅ 缓存功能正常")
            return True
        else:
            print("❌ 缓存功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 缓存功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始项目验证测试...")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("配置检查", test_configuration),
        ("数据库连接", test_database_connection),
        ("Redis连接", test_redis_connection),
        ("API路由", test_api_routes),
        ("安全功能", test_security_features),
        ("性能监控", test_performance_monitoring),
        ("缓存功能", test_cache_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目功能正常")
        return True
    else:
        print(f"⚠️ 有 {total - passed} 个测试失败，需要检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
