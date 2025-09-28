#!/usr/bin/env python3
"""
小雪宝AI助手开发服务器启动脚本
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查基础依赖"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlalchemy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} 未安装")
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install fastapi uvicorn pydantic sqlalchemy")
        return False
    
    return True

def setup_environment():
    """设置环境变量"""
    env_vars = {
        'DATABASE_URL': 'sqlite+aiosqlite:///./xiaoxuebao.db',
        'SECRET_KEY': 'dev-secret-key-change-in-production',
        'JWT_SECRET': 'dev-jwt-secret-change-in-production',
        'DEBUG': 'true',
        'LOG_LEVEL': 'DEBUG',
        'APP_NAME': '小雪宝AI助手',
        'APP_VERSION': '1.0.0'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"设置环境变量: {key}={value}")

def create_directories():
    """创建必要的目录"""
    directories = ['logs', 'uploads', 'static']
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"创建目录: {dir_path}")

def main():
    """主函数"""
    print("🚀 启动小雪宝AI助手开发服务器...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置环境
    setup_environment()
    
    # 创建目录
    create_directories()
    
    print("\n" + "=" * 50)
    print("🎉 环境准备完成，启动服务器...")
    print("📍 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔧 管理界面: http://localhost:8000/redoc")
    print("=" * 50)
    
    try:
        # 启动服务器
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
