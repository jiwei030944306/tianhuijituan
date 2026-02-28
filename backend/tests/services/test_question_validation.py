"""
"""
import pytest
from app.services.question_validation import (
    validate_question,
    validate_questions_batch,
    format_validation_report,
    get_valid_question_types,
    get_valid_difficulties,
    VALID_QUESTION_TYPES,
    VALID_DIFFICULTIES,
    VALID_STATUSES,
    VALID_CATEGORIES
)


class TestValidateQuestion:
    """测试单个题目验证功能"""

    def test_validate_question_success(self):
        """测试有效题目"""
        question = {
            "id": "test-001",
            "stem": "测试题目内容",
            "answer": "A",
            "type": "single_choice",
            "difficulty": "easy",
            "options": [
                {"label": "A", "content": "选项 A"},
                {"label": "B", "content": "选项 B"}
            ]
        }

        is_valid, errors = validate_question(question)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_question_missing_stem(self):
        """测试缺少题干的情况"""
        question = {
            "id": "test-002",
            "answer": "A",
            "type": "single_choice"
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "缺少必填字段：stem" in errors
        assert "题干不能为空" in errors

    def test_validate_question_missing_answer(self):
        """测试缺少答案的情况（允许但警告）"""
        question = {
            "id": "test-003",
            "stem": "测试题目",
            "type": "single_choice"
        }

        is_valid, errors = validate_question(question)

        # 答案缺少时应该仍然有效（根据验证逻辑，答案可以为空）
        assert is_valid is True

    def test_validate_question_missing_type(self):
        """测试缺少题型的情况"""
        question = {
            "id": "test-004",
            "stem": "测试题目",
            "answer": "A"
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "缺少必填字段：type" in errors

    def test_validate_question_invalid_type(self):
        """测试无效题型"""
        question = {
            "id": "test-005",
            "stem": "测试题目",
            "answer": "A",
            "type": "invalid_type"
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "无效的题型：'invalid_type'" in errors

    def test_validate_question_invalid_difficulty(self):
        """测试无效难度"""
        question = {
            "id": "test-006",
            "stem": "测试题目",
            "answer": "A",
            "type": "single_choice",
            "difficulty": "super_easy"
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "无效的难度：'super_easy'" in errors

    def test_validate_question_invalid_status(self):
        """测试无效状态"""
        question = {
            "id": "test-007",
            "stem": "测试题目",
            "answer": "A",
            "type": "single_choice",
            "status": "pending"
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "无效的状态：'pending'" in errors

    def test_validate_question_invalid_category(self):
        """测试无效题类"""
        question = {
            "id": "test-008",
            "stem": "测试题目",
            "answer": "A",
            "type": "single_choice",
            "category": "normal"
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "无效的题类：'normal'" in errors

    def test_validate_question_single_choice_no_options(self):
        """测试选择题缺少选项"""
        question = {
            "id": "test-009",
            "stem": "测试题目",
            "answer": "A",
            "type": "single_choice",
            "options": []
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "选择题必须至少有 2 个选项" in errors

    def test_validate_question_single_choice_one_option(self):
        """测试选择题只有一个选项"""
        question = {
            "id": "test-010",
            "stem": "测试题目",
            "answer": "A",
            "type": "single_choice",
            "options": [
                {"label": "A", "content": "选项 A"}
            ]
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "选择题必须至少有 2 个选项" in errors

    def test_validate_question_single_choice_empty_option_content(self):
        """测试选择题选项内容为空"""
        question = {
            "id": "test-011",
            "stem": "测试题目",
            "answer": "A",
            "type": "single_choice",
            "options": [
                {"label": "A", "content": "选项 A"},
                {"label": "B", "content": ""}
            ]
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "选项 2 的内容为空" in errors

    def test_validate_question_invalid_grade(self):
        """测试无效年级"""
        question = {
            "id": "test-012",
            "stem": "测试题目",
            "answer": "A",
            "type": "single_choice",
            "grade": 13
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "无效的年级：13" in errors

    def test_validate_question_invalid_education_level(self):
        """测试无效学段"""
        question = {
            "id": "test-013",
            "stem": "测试题目",
            "answer": "A",
            "type": "single_choice",
            "educationLevel": "小学"
        }

        is_valid, errors = validate_question(question)

        assert is_valid is False
        assert "无效的学段：'小学'" in errors

    def test_validate_question_basic_fill_type(self):
        """测试 basic_fill 题型（验证统一命名后的题型）"""
        question = {
            "id": "test-014",
            "stem": "填空题：____ is the capital of France.",
            "answer": "Paris",
            "type": "basic_fill",
            "difficulty": "medium"
        }

        is_valid, errors = validate_question(question)

        assert is_valid is True
        assert len(errors) == 0


class TestValidateQuestionsBatch:
    """测试批量验证功能"""

    def test_validate_questions_batch_all_valid(self):
        """测试所有题目都有效的情况"""
        questions = [
            {
                "id": "test-001",
                "stem": "题目 1",
                "answer": "A",
                "type": "single_choice"
            },
            {
                "id": "test-002",
                "stem": "题目 2",
                "answer": "B",
                "type": "multiple_choice"
            }
        ]

        result = validate_questions_batch(questions)

        assert result["total"] == 2
        assert result["valid"] == 2
        assert result["invalid"] == 0
        assert len(result["errors"]) == 0

    def test_validate_questions_batch_all_invalid(self):
        """测试所有题目都无效的情况"""
        questions = [
            {
                "id": "test-001",
                "answer": "A",  # 缺少 stem
                "type": "single_choice"
            },
            {
                "id": "test-002",
                "stem": "题目 2",
                "answer": "B",
                "type": "invalid_type"  # 无效题型
            }
        ]

        result = validate_questions_batch(questions)

        assert result["total"] == 2
        assert result["valid"] == 0
        assert result["invalid"] == 2
        assert len(result["errors"]) == 2

    def test_validate_questions_batch_mixed(self):
        """测试混合有效和无效题目"""
        questions = [
            {
                "id": "test-001",
                "stem": "有效题目",
                "answer": "A",
                "type": "single_choice"
            },
            {
                "id": "test-002",
                "answer": "A",  # 缺少 stem
                "type": "single_choice"
            },
            {
                "id": "test-003",
                "stem": "有效题目 2",
                "answer": "B",
                "type": "basic_fill"
            }
        ]

        result = validate_questions_batch(questions)

        assert result["total"] == 3
        assert result["valid"] == 2
        assert result["invalid"] == 1
        assert len(result["errors"]) == 1
        assert result["errors"][0]["question_id"] == "test-002"

    def test_validate_questions_batch_empty_list(self):
        """测试空列表"""
        questions = []

        result = validate_questions_batch(questions)

        assert result["total"] == 0
        assert result["valid"] == 0
        assert result["invalid"] == 0
        assert len(result["errors"]) == 0

    def test_validate_questions_batch_error_format(self):
        """测试错误信息格式"""
        questions = [
            {
                "id": "test-001",
                "answer": "A",  # 缺少 stem 和 type
                "type": "invalid_type"
            }
        ]

        result = validate_questions_batch(questions)

        assert len(result["errors"]) == 1
        error_info = result["errors"][0]
        assert "question_index" in error_info
        assert "question_id" in error_info
        assert "errors" in error_info
        assert error_info["question_index"] == 0
        assert error_info["question_id"] == "test-001"
        assert len(error_info["errors"]) > 0


class TestFormatValidationReport:
    """测试验证报告格式化功能"""

    def test_format_validation_report_all_valid(self):
        """测试格式化全有效的报告"""
        validation_result = {
            "total": 5,
            "valid": 5,
            "invalid": 0,
            "errors": []
        }

        report = format_validation_report(validation_result)

        assert "总数量：5" in report
        assert "有效：5" in report
        assert "无效：0" in report
        assert "所有议题数据验证通过" in report

    def test_format_validation_report_with_errors(self):
        """测试格式化有错误的报告"""
        validation_result = {
            "total": 3,
            "valid": 1,
            "invalid": 2,
            "errors": [
                {
                    "question_index": 0,
                    "question_id": "test-001",
                    "errors": ["缺少必填字段：stem", "无效题型"]
                },
                {
                    "question_index": 2,
                    "question_id": "test-003",
                    "errors": ["无效难度"]
                }
            ]
        }

        report = format_validation_report(validation_result)

        assert "总数量：3" in report
        assert "有效：1" in report
        assert "无效：2" in report
        assert "错误详情:" in report
        assert "test-001" in report
        assert "test-003" in report
        assert "缺少必填字段：stem" in report
        assert "无效题型" in report
        assert "无效难度" in report


class TestGetValidTypes:
    """测试获取有效类型集合的功能"""

    def test_get_valid_question_types(self):
        """测试获取有效题型集合"""
        valid_types = get_valid_question_types()

        assert isinstance(valid_types, set)
        assert "single_choice" in valid_types
        assert "multiple_choice" in valid_types
        assert "basic_fill" in valid_types
        assert "calculation" in valid_types
        assert "subjective" in valid_types

    def test_get_valid_difficulties(self):
        """测试获取有效难度集合"""
        valid_difficulties = get_valid_difficulties()

        assert isinstance(valid_difficulties, set)
        assert "easy" in valid_difficulties
        assert "medium_easy" in valid_difficulties
        assert "medium" in valid_difficulties
        assert "medium_hard" in valid_difficulties
        assert "hard" in valid_difficulties

    def test_valid_question_types_count(self):
        """测试有效题型数量"""
        # 应该有 56 个标准题型
        assert len(VALID_QUESTION_TYPES) == 56

    def test_valid_difficulties_count(self):
        """测试有效难度数量"""
        # 应该有 5 级难度
        assert len(VALID_DIFFICULTIES) == 5

    def test_valid_statuses_count(self):
        """测试有效状态数量"""
        # 应该有 4 种状态
        assert len(VALID_STATUSES) == 4

    def test_valid_categories_count(self):
        """测试有效题类数量"""
        # 应该有 5 类题类
        assert len(VALID_CATEGORIES) == 5
