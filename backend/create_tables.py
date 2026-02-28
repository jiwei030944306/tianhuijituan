"""创建数据库表"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base
from app.models.question import Question
from app.models.upload_record import UploadRecord
from app.models.user import User

async def create_tables():
    """创建所有表"""
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    print("✓ 数据库表创建成功")

if __name__ == "__main__":
    asyncio.run(create_tables())
