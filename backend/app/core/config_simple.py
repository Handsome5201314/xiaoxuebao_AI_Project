"""
简化配置文件 - 用于快速启动
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """简化的应用配置类"""

    # 应用配置
    APP_NAME: str = Field(default="小雪宝AI助手", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    DEBUG: bool = Field(default=True, description="调试模式")
    ENVIRONMENT: str = Field(default="development", description="运行环境")

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite:///./xiaoxuebao.db",
        description="数据库连接URL"
    )

    # Redis配置 (可选)
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis连接URL"
    )

    # 安全配置
    SECRET_KEY: str = Field(
        default="dev-secret-key-xiaoxuebao-2024-very-long-key-for-development",
        min_length=32,
        description="应用密钥"
    )

    # CORS配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"],
        description="允许的CORS源"
    )

    # 文件上传配置
    UPLOAD_DIR: str = Field(default="./uploads", description="上传目录")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略额外的环境变量

# 创建设置实例
settings = Settings()
