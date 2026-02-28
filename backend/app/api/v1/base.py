"""
题目基础API路由

提供题目的基础CRUD操作
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import question as crud_question
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    StatisticsResponse
)

router = APIRouter()


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取统计数据

    返回总题数、各题型分布、标签统计
    """
    return await crud_question.get_statistics(db)


@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    type: Optional[str] = Query(None, description="题目类型"),
    difficulty: Optional[str] = Query(None, description="难度"),
    status: Optional[str] = Query(None, description="状态"),
    subject: Optional[str] = Query(None, description="科目"),
    grade: Optional[int] = Query(None, description="年级"),
    education_level: Optional[str] = Query(None, description="学段"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取题目列表

    支持按类型、难度、状态、科目、年级、学段筛选
    """
    questions = await crud_question.get_questions(
        db, skip=skip, limit=limit, type=type, difficulty=difficulty, status=status,
        subject=subject, grade=grade, education_level=education_level
    )
    return questions


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取题目详情
    """
    question = await crud_question.get_question(db, question_id=question_id)
    if not question:
        raise HTTPException(
            status_code=404,
            detail=f"题目 {question_id} 不存在"
        )
    return question


@router.post("/", response_model=QuestionResponse, status_code=201)
async def create_question(
    question: QuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建题目
    """
    try:
        return await crud_question.create_question(db, question)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"创建题目失败: {str(e)}"
        )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question: QuestionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新题目
    """
    db_question = await crud_question.get_question(db, question_id)
    if not db_question:
        raise HTTPException(
            status_code=404,
            detail=f"题目 {question_id} 不存在"
        )

    try:
        return await crud_question.update_question(db, question_id, question)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"更新题目失败: {str(e)}"
        )


@router.delete("/{question_id}", status_code=204)
async def delete_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除题目
    """
    db_question = await crud_question.get_question(db, question_id)
    if not db_question:
        raise HTTPException(
            status_code=404,
            detail=f"题目 {question_id} 不存在"
        )

    await crud_question.delete_question(db, question_id=question_id)
    return None
