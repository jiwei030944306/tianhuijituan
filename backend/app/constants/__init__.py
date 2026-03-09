"""
常量模块
"""
from app.constants.subject import (
    SUBJECT_NAMES,
    VALID_SUBJECT_CODES,
    get_subject_name,
    get_education_level,
    get_grade_code,
    is_valid_subject_code,
    get_subject_info,
)

__all__ = [
    "SUBJECT_NAMES",
    "VALID_SUBJECT_CODES",
    "get_subject_name",
    "get_education_level",
    "get_grade_code",
    "is_valid_subject_code",
    "get_subject_info",
]