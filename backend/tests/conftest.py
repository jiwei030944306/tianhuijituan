"""
测试配置 - 数据库隔离和共享 Fixtures

使用内存 SQLite 数据库进行测试隔离（测试环境仍可使用 SQLite）
"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.main import app
from app.core.database import get_db


# 创建内存测试数据库引擎
# 注：测试环境使用内存数据库以实现快速隔离
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# 创建测试会话工厂
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    创建测试数据库会话
    
    每个测试函数使用独立的数据库实例
    测试结束后自动清理
    """
    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # 清理所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    创建测试客户端
    
    使用依赖注入覆盖数据库会话
    """
    from httpx import AsyncClient
    
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_question_data():
    """示例题目数据"""
    return {
        "type": "single_choice",
        "difficulty": "easy",
        "stem": "测试题目内容",
        "answer": "A",
        "options": [
            {"key": "A", "value": "选项A"},
            {"key": "B", "value": "选项B"},
            {"key": "C", "value": "选项C"},
            {"key": "D", "value": "选项D"}
        ],
        "topics": ["数学", "代数"],
        "category": "常考题",
        "analysis": "测试解析"
    }


@pytest.fixture
def sample_upload_data():
    """示例上传数据"""
    return {
        "folder_code": "m7s9m2",
        "education_level": "初中",
        "subject": "数学",
        "batch_id": "20260222-150000-abc123",
        "display_name": "测试上传批次",
        "original_filename": "test.zip",
        "teacher_name": "张老师",
        "file_count": 10,
        "image_count": 5,
        "status": "completed"
    }
