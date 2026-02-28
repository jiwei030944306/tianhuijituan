"""
数据库连接配置
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 从环境变量读取数据库 URL（通过 config.py）
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# PostgreSQL 配置
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # 开发环境显示 SQL 日志
    pool_pre_ping=True,  # 连接前检查连接是否有效
    pool_size=settings.DATABASE_POOL_SIZE,  # 连接池大小
    max_overflow=settings.DATABASE_MAX_OVERFLOW,  # 最大溢出连接数
    pool_recycle=3600,  # 连接回收时间（秒）
    pool_timeout=30,  # 获取连接的超时时间（秒）
)
logger.info("PostgreSQL 数据库引擎初始化完成")


# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 创建Base类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    获取数据库会话的依赖函数

    优化说明：
    1. 只读操作不自动提交，减少不必要的commit
    2. 异常时记录详细日志，便于追踪问题
    3. async with 已自动关闭会话，移除冗余的 close()
    """
    session = AsyncSessionLocal()
    try:
        yield session
        # 注意：这里不自动commit，由各个CRUD操作自行决定是否commit
        # 只读操作（GET）不需要commit，避免不必要的性能开销
    except Exception as e:
        # 记录异常日志，包含异常类型和详细信息
        logger.error(f"Database session error: {type(e).__name__}: {str(e)}", exc_info=True)
        await session.rollback()
        raise
    finally:
        # async with 会自动关闭，但显式关闭确保资源释放
        await session.close()