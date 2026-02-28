"""
CRUD 操作测试
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.question import create_question, get_question, get_questions, update_question, delete_question
from app.schemas.question import QuestionCreate, QuestionUpdate


class TestQuestionCRUD:
    """题目 CRUD 操作测试"""

    @pytest.mark.asyncio
    async def test_crud_create_question(self, db_session: AsyncSession):
        """测试创建题目 - 成功场景"""
        question_data = QuestionCreate(
            type="single_choice",
            difficulty="easy",
            stem="测试题目",
            answer="A",
            options=[{"key": "A", "value": "选项A"}]
        )
        
        result = await create_question(db_session, question_data)
        
        assert result.id is not None
        assert result.stem == "测试题目"
        assert result.type == "single_choice"

    @pytest.mark.asyncio
    async def test_crud_get_question(self, db_session: AsyncSession):
        """测试获取单个题目"""
        # 先创建题目
        question_data = QuestionCreate(
            type="single_choice",
            stem="测试获取题目",
            answer="A"
        )
        created = await create_question(db_session, question_data)
        
        # 获取题目
        result = await get_question(db_session, created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.stem == "测试获取题目"

    @pytest.mark.asyncio
    async def test_crud_get_question_not_found(self, db_session: AsyncSession):
        """测试获取不存在的题目"""
        result = await get_question(db_session, "nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_crud_get_questions(self, db_session: AsyncSession):
        """测试获取题目列表"""
        # 创建多个题目
        for i in range(3):
            question_data = QuestionCreate(
                type="single_choice",
                stem=f"测试题目{i}",
                answer="A"
            )
            await create_question(db_session, question_data)
        
        # 获取列表
        questions = await get_questions(db_session, skip=0, limit=10)
        
        assert len(questions) >= 3

    @pytest.mark.asyncio
    async def test_crud_get_questions_with_filter(self, db_session: AsyncSession):
        """测试带筛选条件的查询"""
        # 创建不同类型的题目
        for qtype in ["single_choice", "multiple_choice"]:
            question_data = QuestionCreate(
                type=qtype,
                stem=f"测试题目-{qtype}",
                answer="A"
            )
            await create_question(db_session, question_data)
        
        # 筛选查询
        questions = await get_questions(db_session, type="single_choice")
        
        assert all(q.type == "single_choice" for q in questions)

    @pytest.mark.asyncio
    async def test_crud_update_question(self, db_session: AsyncSession):
        """测试更新题目"""
        # 创建题目
        question_data = QuestionCreate(
            type="single_choice",
            stem="原始题目",
            answer="A"
        )
        created = await create_question(db_session, question_data)
        
        # 更新题目
        update_data = QuestionUpdate(stem="更新后的题目")
        result = await update_question(db_session, created.id, update_data)
        
        assert result is not None
        assert result.stem == "更新后的题目"

    @pytest.mark.asyncio
    async def test_crud_delete_question(self, db_session: AsyncSession):
        """测试删除题目"""
        # 创建题目
        question_data = QuestionCreate(
            type="single_choice",
            stem="待删除题目",
            answer="A"
        )
        created = await create_question(db_session, question_data)
        
        # 删除题目
        result = await delete_question(db_session, created.id)
        assert result is True
        
        # 验证已删除
        deleted = await get_question(db_session, created.id)
        assert deleted is None
