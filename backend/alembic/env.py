from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 导入 Base 和所有模型
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.database import Base
from backend.app.models.question import Question  # noqa
from backend.app.models.upload_record import UploadRecord  # noqa
from backend.app.models.user import User  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_value(key: str, default=None):
    """
    从 Alembic config 或环境变量获取配置值
    
    优先级：
    1. Alembic config 中的值
    2. 环境变量
    3. 默认值
    """
    # 首先尝试从 Alembic config 获取
    value = config.get_main_option(key)
    if value is not None:
        return value
    
    # 从环境变量获取
    import os
    value = os.getenv(key)
    if value is not None:
        return value
    
    return default


def run_migrations_offline() -> None:
    """
    在"离线"模式下运行迁移。
    
    此模式不需要数据库引擎，而是从配置中读取 URL。
    """
    url = get_value("sqlalchemy.url")
    
    if not url:
        raise ValueError("DATABASE_URL 未配置。请设置 alembic.ini 中的 sqlalchemy.url 或 DATABASE_URL 环境变量")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在"在线"模式下运行迁移。
    
    此模式需要数据库引擎和连接。
    """
    # 从配置或环境变量获取数据库 URL
    url = get_value("sqlalchemy.url")
    
    if not url:
        raise ValueError("DATABASE_URL 未配置。请设置 alembic.ini 中的 sqlalchemy.url 或 DATABASE_URL 环境变量")
    
    # 确保使用正确的驱动
    if "postgresql" in url and "asyncpg" not in url:
        # 如果是 PostgreSQL 但没有指定 asyncpg，自动添加
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    
    # 创建连接配置
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
