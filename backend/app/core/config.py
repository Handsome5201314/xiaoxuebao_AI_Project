from pydantic import Field, field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
import os
from pathlib import Path

class Settings(BaseSettings):
    """应用配置类，使用Pydantic进行配置验证和类型检查"""

    # 应用配置
    APP_NAME: str = Field(default="小雪宝Wiki", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    DEBUG: bool = Field(default=False, env="DEBUG", description="调试模式")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT", description="运行环境")

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./xiaoxuebao.db",
        env="DATABASE_URL",
        description="数据库连接URL"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=5,
        env="DATABASE_POOL_SIZE",
        ge=1,
        le=50,
        description="数据库连接池大小"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=10,
        env="DATABASE_MAX_OVERFLOW",
        ge=0,
        le=100,
        description="数据库连接池最大溢出数"
    )
    
    # Redis配置
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        env="REDIS_URL",
        description="Redis连接URL"
    )
    REDIS_POOL_SIZE: int = Field(
        default=10,
        env="REDIS_POOL_SIZE",
        ge=1,
        le=100,
        description="Redis连接池大小"
    )

    # 安全配置
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY",
        min_length=32,
        description="JWT签名密钥"
    )
    ALGORITHM: str = Field(
        default="HS256",
        env="ALGORITHM",
        description="JWT签名算法"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24 * 7,
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
        ge=1,
        description="访问令牌过期时间（分钟）"
    )

    # CORS配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS",
        description="允许的CORS源"
    )
    
    # 文件上传配置
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    
    # 搜索配置
    ELASTICSEARCH_URL: str = Field(
        default="http://localhost:9200",
        env="ELASTICSEARCH_URL"
    )
    ELASTICSEARCH_INDEX: str = Field(
        default="xiaoxuebao_wiki",
        env="ELASTICSEARCH_INDEX"
    )
    
    # 邮件配置（可选）
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=None, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """验证密钥安全性"""
        if v == "your-secret-key-change-in-production":
            raise ValueError("生产环境必须更改默认密钥")
        return v

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """解析CORS源配置"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """验证数据库URL格式"""
        if not v:
            raise ValueError("数据库URL不能为空")
        return v

    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        allowed_envs = ["development", "testing", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"环境必须是以下之一: {', '.join(allowed_envs)}")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        validate_assignment = True

    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.ENVIRONMENT == "development"

    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return self.DATABASE_URL

# 全局配置实例
settings = Settings()

# 确保上传目录存在
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)