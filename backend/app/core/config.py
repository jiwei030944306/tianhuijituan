"""
配置管理 - 使用Pydantic Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "智研题库云系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # JWT 配置（从环境变量读取）
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置（从环境变量读取）
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # CORS 配置（从环境变量读取）
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    
    # AI 服务配置
    GEMINI_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    DOUBAO_API_KEY: str | None = None
    
    # Redis 配置
    REDIS_URL: str | None = None
    
    # 文件上传配置
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # 速率限制配置
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # 管理员配置
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "Admin@123"
    ADMIN_EMAIL: str = "admin@example.com"
    
    # 其他配置
    TIMEZONE: str = "Asia/Shanghai"
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的字段


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
