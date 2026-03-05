"""
数据库连接配置
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
import os
import logging
import asyncio

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


async def check_database_connection(max_retries: int = 3, retry_delay: float = 1.0) -> tuple[bool, str]:
    """
    检查数据库连接是否正常

    Args:
        max_retries: 最大重试次数
        retry_delay: 重试间隔（秒）

    Returns:
        (is_connected, message): 连接状态和消息
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as session:
                # 执行简单查询验证连接
                await session.execute(text("SELECT 1"))
            return True, "数据库连接正常"
        except Exception as e:
            last_error = e
            logger.warning(
                f"数据库连接检查失败 (尝试 {attempt + 1}/{max_retries}): {type(e).__name__}: {str(e)}"
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)

    error_msg = f"数据库连接失败: {type(last_error).__name__}: {str(last_error)}"
    logger.error(error_msg)
    return False, error_msg


async def init_database_connection():
    """
    初始化数据库连接（应用启动时调用）

    验证数据库连接并记录连接池状态
    """
    is_connected, message = await check_database_connection()

    if is_connected:
        logger.info(f"✓ {message}")
        logger.info(
            f"连接池配置: pool_size={settings.DATABASE_POOL_SIZE}, "
            f"max_overflow={settings.DATABASE_MAX_OVERFLOW}"
        )
    else:
        logger.error(f"✗ {message}")
        # 不抛出异常，允许应用启动（便于调试）
        # 生产环境可以考虑抛出异常阻止启动
        # raise RuntimeError(message)