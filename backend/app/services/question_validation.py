"""
议题数据验证服务
验证上传的议题数据是否符合标准
"""
import logging
from typing import Tuple, List, Dict, Any

logger = logging.getLogger(__name__)

# ==================== 常量定义 ====================

# 必填字段
REQUIRED_FIELDS = ["stem", "answer", "type"]

# 56 个标准题型（来自 frontend/src/types/question.ts）
VALID_QUESTION_TYPES = {
    # 通用题型（5 个）
    "single_choice",      # 选择题
    "multiple_choice",    # 多选题
    "basic_fill",         # 填空题
    "subjective",         # 解答题
    "true_false",         # 判断题
    
    # 语文题型（12 个）
    "character_writing",      # 汉字书写
    "translation",            # 翻译
    "basic_knowledge",        # 基础知识
    "dictation",              # 默写
    "language_usage",         # 语言运用
    "reading_writing",        # 综合读写
    "classic_reading",        # 名著阅读
    "modern_reading",         # 现代文阅读
    "poetry_appreciation",    # 古诗词赏析
    "classical_chinese",      # 文言文阅读
    "composition",            # 作文
    "integrated_learning",    # 综合性学习
    
    # 数学题型（1 个）
    "calculation",            # 计算题
    
    # 英语题型（19 个）
    "listening",              # 听力题
    "cloze",                  # 完形填空
    "reading_comprehension",  # 阅读理解
    "information_matching",   # 信息匹配
    "word_selection",         # 选词填空
    "passage_fill",           # 短文填空
    "grammar_fill",           # 语法填空
    "other_reading",          # 其他阅读题型
    "dialogue_fill",          # 对话填空
    "spelling",               # 单词拼写
    "word_formation",         # 词性转换
    "sentence_transformation",# 句型转换
    "error_correction",       # 句子改错
    "sentence_completion",    # 完成句子
    "passage_correction",     # 短文改错
    "writing",                # 书面表达
    "vocabulary_usage",       # 词汇应用
    
    # 物理题型（7 个）
    "choice_explanation",     # 选择说明题
    "drawing",                # 作图题
    "short_answer",           # 简答题
    "experiment_inquiry",     # 实验探究题
    "comprehensive",          # 综合能力题
    "science_reading",        # 科普阅读题
    "experiment",             # 实验题
    
    # 化学题型（7 个）
    "choice_fill",            # 选择填充题
    "deduction",              # 推断题
    "process_flow",           # 工艺流程题
    "science_inquiry",        # 科学探究题
    "comprehensive_application",  # 综合应用题
    
    # 生物题型（1 个）
    "material_analysis",      # 材料分析题
    
    # 历史题型（3 个）
    "analysis",               # 辨析题
    "material",               # 材料题
    "essay",                  # 论述题
    
    # 地理题型（1 个）
    "matching",               # 连线题
    
    # 道法/政治题型（11 个）
    "evaluation",             # 评析题
    "opinion",                # 阐述见解题
    "reasoning",              # 判断说理题
    "scenario_inquiry",       # 情境探究题
    "explanation",            # 分析说明题
    "comprehensive_inquiry",  # 综合探究题
    "analysis_evaluation",    # 辨析评析题
    "chart",                  # 图表题
    "inquiry",                # 探究类试题
}

# 5 级标准难度
VALID_DIFFICULTIES = {
    "easy",           # 易
    "medium_easy",    # 较易
    "medium",         # 中档
    "medium_hard",    # 较难
    "hard"            # 难
}

# 4 种标准状态
VALID_STATUSES = {
    "active",         # 待标化
    "error",          # 异常
    "waste",          # 废题
    "confirmed"       # 已确认
}

# 5 类题类
VALID_CATEGORIES = {
    "frequent",       # 常考题
    "error_prone",    # 易错题
    "good",           # 好题
    "final",          # 压轴题
    "selected"        # 优选题
}


# ==================== 验证函数 ====================

def validate_question(question: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证单个议题数据
    
    Args:
        question: 议题数据字典
        
    Returns:
        (是否有效，错误消息列表)
    """
    errors = []
    
    # 1. 检查必填字段
    for field in REQUIRED_FIELDS:
        if field not in question or not question[field]:
            # 特殊处理：答案可以是空字符串（某些题目可能暂时没答案）
            if field == "answer":
                logger.warning(f"议题 {question.get('id', 'unknown')} 缺少答案（已允许，但建议补充）")
                continue
            errors.append(f"缺少必填字段：{field}")
    
    # 2. 验证题干不为空
    if not question.get("stem", "").strip():
        errors.append("题干不能为空")
    
    # 3. 验证题型有效性
    q_type = question.get("type")
    if q_type:
        if q_type not in VALID_QUESTION_TYPES:
            errors.append(f"无效的题型：'{q_type}'（应该是 56 个标准题型之一）")
    
    # 4. 验证难度有效性
    difficulty = question.get("difficulty")
    if difficulty:
        if difficulty not in VALID_DIFFICULTIES:
            errors.append(f"无效的难度：'{difficulty}'（应该是 5 级难度之一：easy/medium_easy/medium/medium_hard/hard）")
    
    # 5. 验证状态有效性
    status = question.get("status")
    if status:
        if status not in VALID_STATUSES:
            errors.append(f"无效的状态：'{status}'（应该是 4 种状态之一：active/error/waste/confirmed）")
    
    # 6. 验证题类有效性
    category = question.get("category")
    if category:
        if category not in VALID_CATEGORIES:
            errors.append(f"无效的题类：'{category}'（应该是 5 类之一：frequent/error_prone/good/final/selected）")
    
    # 7. 验证选择题选项（如果是选择题）
    if q_type in ["single_choice", "multiple_choice"]:
        options = question.get("options", [])
        if not options or len(options) < 2:
            errors.append("选择题必须至少有 2 个选项")
        
        # 验证每个选项的内容
        for i, opt in enumerate(options):
            if not opt.get("content", "").strip():
                errors.append(f"选项 {i+1} 的内容为空")
    
    # 8. 验证年级范围（如果有）
    grade = question.get("grade")
    if grade:
        if not isinstance(grade, int) or grade < 1 or grade > 12:
            errors.append(f"无效的年级：{grade}（应该是 1-12 之间的整数）")
    
    # 9. 验证学段（如果有）
    education_level = question.get("educationLevel") or question.get("education_level")
    if education_level:
        if education_level not in ["初中", "高中"]:
            errors.append(f"无效的学段：'{education_level}'（应该是'初中'或'高中'）")
    
    return len(errors) == 0, errors


def validate_questions_batch(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量验证议题数据
    
    Args:
        questions: 议题数据列表
        
    Returns:
        验证结果字典：
        {
            "total": 总数,
            "valid": 有效数量,
            "invalid": 无效数量,
            "errors": [
                {"question_index": 0, "question_id": "xxx", "errors": ["错误 1", "错误 2"]},
                ...
            ]
        }
    """
    result = {
        "total": len(questions),
        "valid": 0,
        "invalid": 0,
        "errors": []
    }
    
    for i, question in enumerate(questions):
        is_valid, errors = validate_question(question)
        
        if is_valid:
            result["valid"] += 1
        else:
            result["invalid"] += 1
            result["errors"].append({
                "question_index": i,
                "question_id": question.get("id", f"index_{i}"),
                "errors": errors
            })
    
    return result


# ==================== 辅助函数 ====================

def get_valid_question_types() -> set:
    """获取所有有效的题型"""
    return VALID_QUESTION_TYPES


def get_valid_difficulties() -> set:
    """获取所有有效的难度"""
    return VALID_DIFFICULTIES


def normalize_question_type(chinese_or_english: str) -> str:
    """
    标准化题型为英文值
    
    Args:
        chinese_or_english: 中文或英文题型
        
    Returns:
        英文题型标识符
        
    Raises:
        ValueError: 如果题型无效
    """
    # 中文题型到英文的映射
    CHINESE_TO_ENGLISH = {
        "选择题": "single_choice",
        "多选题": "multiple_choice",
        "填空题": "basic_fill",
        "解答题": "subjective",
        "判断题": "true_false",
        "计算题": "calculation",
        # ... 可以根据需要扩展
    }
    
    # 如果已经是英文，验证有效性
    if chinese_or_english in VALID_QUESTION_TYPES:
        return chinese_or_english
    
    # 如果是中文，转换并验证
    if chinese_or_english in CHINESE_TO_ENGLISH:
        return CHINESE_TO_ENGLISH[chinese_or_english]
    
    raise ValueError(f"无效的题型：'{chinese_or_english}'")


def format_validation_report(validation_result: Dict[str, Any]) -> str:
    """
    格式化验证报告
    
    Args:
        validation_result: validate_questions_batch 的返回值
        
    Returns:
        格式化的文本报告
    """
    lines = [
        "========== 议题数据验证报告 ==========",
        f"总数量：{validation_result['total']}",
        f"有效：{validation_result['valid']}",
        f"无效：{validation_result['invalid']}",
        ""
    ]
    
    if validation_result["errors"]:
        lines.append("错误详情:")
        for error_info in validation_result["errors"]:
            lines.append(f"  - 议题 {error_info['question_id']} (索引：{error_info['question_index']})")
            for error_msg in error_info["errors"]:
                lines.append(f"    • {error_msg}")
    else:
        lines.append("✓ 所有议题数据验证通过")
    
    lines.append("=" * 40)
    
    return "\n".join(lines)
