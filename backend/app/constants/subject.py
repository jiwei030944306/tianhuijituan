"""
学科代码映射常量
统一管理学科代码与中文名的映射关系
"""

# 学科代码 -> 中文名
# 初中不带2，高中带2
SUBJECT_NAMES: dict[str, str] = {
    "chinese": "语文",
    "chinese2": "语文",
    "math": "数学",
    "math2": "数学",
    "english": "英语",
    "english2": "英语",
    "physics": "物理",
    "physics2": "物理",
    "chemistry": "化学",
    "chemistry2": "化学",
    "bio": "生物",
    "bio2": "生物",
    "geo": "地理",
    "geo2": "地理",
    "history": "历史",
    "history2": "历史",
    "politics": "政治",
    "politics2": "政治",
}

# 有效学科代码列表
VALID_SUBJECT_CODES = list(SUBJECT_NAMES.keys())


def get_subject_name(subject_code: str) -> str:
    """
    根据学科代码获取学科名称

    Args:
        subject_code: 学科代码，如 math, math2

    Returns:
        学科名称，如 "数学"
    """
    return SUBJECT_NAMES.get(subject_code, subject_code)


def get_education_level(subject_code: str) -> str:
    """
    根据学科代码判断学段

    Args:
        subject_code: 学科代码，如 math, math2

    Returns:
        学段名称："高中" 或 "初中"
    """
    return "高中" if subject_code.endswith("2") else "初中"


def get_grade_code(subject_code: str) -> str:
    """
    根据学科代码获取年级代码（已弃用，保留兼容）

    Args:
        subject_code: 学科代码

    Returns:
        年级代码
    """
    return "11" if subject_code.endswith("2") else "8"


def is_valid_subject_code(subject_code: str) -> bool:
    """
    检查学科代码是否有效

    Args:
        subject_code: 学科代码

    Returns:
        是否有效
    """
    return subject_code in VALID_SUBJECT_CODES


def get_subject_info(subject_code: str) -> dict:
    """
    获取学科完整信息

    Args:
        subject_code: 学科代码

    Returns:
        包含 subject_name, education_level 等信息的字典
    """
    return {
        "subject_code": subject_code,
        "subject_name": get_subject_name(subject_code),
        "education_level": get_education_level(subject_code),
        "grade": get_grade_code(subject_code),
    }