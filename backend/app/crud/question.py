"""
题目CRUD操作
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate
import json


async def get_question(db: AsyncSession, question_id: str) -> Optional[Question]:
    """
    获取单个题目
    """
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    return result.scalar_one_or_none()


async def get_questions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    difficulty: Optional[str] = None,
    status: Optional[str] = None,
    subject: Optional[str] = None,
    grade: Optional[int] = None,
    education_level: Optional[str] = None
) -> List[Question]:
    """
    获取题目列表
    """
    query = select(Question)

    # 修复：忽略 "ALL" 值，表示"全部"不筛选
    if type and type != "ALL":
        query = query.where(Question.type == type)
    if difficulty and difficulty != "ALL":
        query = query.where(Question.difficulty == difficulty)
    if status and status != "ALL":
        query = query.where(Question.status == status)
    if subject and subject != "ALL":
        query = query.where(Question.subject == subject)
    if grade and grade != 0:  # 年级 0 表示"全部"
        query = query.where(Question.grade == grade)
    if education_level and education_level != "ALL":
        query = query.where(Question.education_level == education_level)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_question(
    db: AsyncSession,
    question: QuestionCreate
) -> Question:
    """
    创建题目
    """
    import uuid
    # 生成ID
    question_id = str(uuid.uuid4())

    db_question = Question(
        id=question_id,
        question_number=question.question_number,
        type=question.type,
        difficulty=question.difficulty,
        status=question.status,
        stem=question.stem,
        answer=question.answer,
        options=json.dumps(question.options) if question.options else None,
        stem_images=json.dumps(question.stem_images) if question.stem_images else None,
        topics=json.dumps(question.topics) if question.topics else None,
        category=question.category,
        analysis=question.analysis,
        comment=question.comment,
        subject=question.subject,
        grade=question.grade,
        education_level=question.education_level,
        source_folder=question.source_folder
    )

    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return db_question


async def update_question(
    db: AsyncSession,
    question_id: str,
    question: QuestionUpdate
) -> Optional[Question]:
    """
    更新题目
    """
    db_question = await get_question(db, question_id)
    if not db_question:
        return None

    update_data = question.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_question, field, value)

    await db.commit()
    await db.refresh(db_question)
    return db_question


async def delete_question(db: AsyncSession, question_id: str) -> bool:
    """
    删除题目
    """
    db_question = await get_question(db, question_id)
    if not db_question:
        return False
    
    await db.delete(db_question)
    await db.commit()
    return True


async def get_statistics(db: AsyncSession) -> dict:
    """
    获取统计数据
    优化：使用单个查询替代多个 COUNT 查询
    """
    from sqlalchemy import select, func, case
    
    # 单个查询获取所有计数（性能优化）
    stats = await db.execute(
        select(
            func.count(Question.id).label('total'),
            func.sum(case((Question.analysis != '', 1), else_=0)).label('with_analysis'),
            func.sum(case((Question.stem_images != '[]', 1), else_=0)).label('with_images'),
            func.sum(case((Question.topics != '[]', 1), else_=0)).label('with_topics'),
        )
    )
    row = stats.one()
    # 按题型统计
    type_counts = await db.execute(
        select(Question.type, func.count(Question.id))
        .group_by(Question.type)
    )
    by_type = {row[0]: row[1] for row in type_counts}
    return {
        "total": row.total or 0,
        "with_analysis": row.with_analysis or 0,
        "with_images": row.with_images or 0,
        "with_topics": row.with_topics or 0,
        "by_type": by_type
    }