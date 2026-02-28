"""
统计信息API路由

提供系统统计数据接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import question as crud_question
from app.schemas.question import StatisticsResponse

router = APIRouter()


@router.get("/", response_model=StatisticsResponse)
async def get_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取统计数据

    返回总题数、各题型分布、标签统计
    """
    return await crud_question.get_statistics(db)
