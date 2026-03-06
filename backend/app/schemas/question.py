"""
题目数据验证模型
"""
from typing import List, Optional, Union, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, field_validator, field_serializer, model_validator
from datetime import datetime
import json


# ==================== 值域枚举定义 ====================

class QuestionType(int, Enum):
    """题目类型枚举（数字值）"""
    SINGLE_CHOICE = 1      # 选择题
    FILL_BLANK = 2         # 填空题
    MULTIPLE_CHOICE = 3    # 多选题
    TRUE_FALSE = 4         # 判断题
    SHORT_ANSWER = 9       # 解答题


# 题型中文映射
QUESTION_TYPE_LABELS = {
    1: '选择题',
    2: '填空题',
    3: '多选题',
    4: '判断题',
    9: '解答题',
}


class Difficulty(str, Enum):
    """难度等级枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class EducationLevel(str, Enum):
    """学段枚举"""
    JUNIOR = "初中"
    SENIOR = "高中"


class QuestionStatus(str, Enum):
    """题目状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    PENDING = "pending"
    REJECTED = "rejected"


class QuestionCategory(str, Enum):
    """题类枚举"""
    BASIC = "基础题"
    IMPROVE = "提高题"
    EXTEND = "拓展题"
    INNOVATE = "创新题"
    FINAL = "压轴题"


# ==================== Schema 定义 ====================

class QuestionBase(BaseModel):
    """题目基础模型"""
    question_number: Optional[int] = Field(None, description="题目编号")
    type: QuestionType = Field(..., description="题目类型")
    difficulty: Optional[Difficulty] = Field(None, description="最终难度")
    status: QuestionStatus = Field(default=QuestionStatus.ACTIVE, description="状态")
    stem: str = Field(..., description="题干")
    answer: str = Field(..., description="答案")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="选项")
    stem_images: Optional[List[Dict[str, str]]] = Field(None, description="题干图片")
    topics: Optional[List[str]] = Field(None, description="最终知识点")
    category: Optional[QuestionCategory] = Field(None, description="最终题类")
    analysis: Optional[str] = Field(None, description="原始解析")
    comment: Optional[str] = Field(None, description="人工备注")
    status_message: Optional[str] = Field(None, description="系统状态消息")

    # AI 建议字段
    ai_grade: Optional[str] = Field(None, description="AI建议年级")
    ai_difficulty: Optional[Difficulty] = Field(None, description="AI建议难度")
    ai_topics: Optional[List[str]] = Field(None, description="AI建议知识点")
    ai_category: Optional[QuestionCategory] = Field(None, description="AI建议题类")
    ai_analysis: Optional[str] = Field(None, description="AI生成解析")
    ai_reasoning: Optional[str] = Field(None, description="AI推理过程")
    ai_model: Optional[str] = Field(None, description="AI模型")
    ai_optimized_at: Optional[datetime] = Field(None, description="AI处理时间")
    is_ai_optimized: Optional[int] = Field(0, description="是否已AI处理（0/1）")

    confirmed_at: Optional[datetime] = Field(None, description="确认入库时间")

    # 分类信息字段
    subject: Optional[str] = Field(None, description="科目")
    grade: Optional[int] = Field(None, ge=7, le=12, description="年级（7-12）")
    education_level: Optional[EducationLevel] = Field(None, description="学段")
    source_folder: Optional[str] = Field(None, description="来源文件夹")
    source: Optional[str] = Field(None, description="来源")
    version: Optional[int] = Field(1, description="版本号")

    @model_validator(mode='after')
    def validate_business_rules(self) -> 'QuestionBase':
        """业务规则校验"""
        # 1. 选择题必须有选项
        if self.type in (QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE):
            if not self.options:
                raise ValueError('选择题必须有选项')

        # 2. 年级与学段对应
        if self.grade and self.education_level:
            if 7 <= self.grade <= 9 and self.education_level != EducationLevel.JUNIOR:
                raise ValueError('年级 7-9 对应学段应为"初中"')
            if 10 <= self.grade <= 12 and self.education_level != EducationLevel.SENIOR:
                raise ValueError('年级 10-12 对应学段应为"高中"')

        return self


class QuestionCreate(QuestionBase):
    """创建题目模型"""
    pass


class QuestionUpdate(BaseModel):
    """更新题目模型（所有字段可选）"""
    question_number: Optional[int] = Field(None, description="题目编号")
    type: Optional[QuestionType] = Field(None, description="题目类型")
    difficulty: Optional[Difficulty] = Field(None, description="最终难度")
    status: Optional[QuestionStatus] = Field(None, description="状态")
    stem: Optional[str] = Field(None, description="题干")
    answer: Optional[str] = Field(None, description="答案")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="选项")
    stem_images: Optional[List[Dict[str, str]]] = Field(None, description="题干图片")
    topics: Optional[List[str]] = Field(None, description="最终知识点")
    category: Optional[QuestionCategory] = Field(None, description="最终题类")
    analysis: Optional[str] = Field(None, description="原始解析")
    comment: Optional[str] = Field(None, description="人工备注")
    status_message: Optional[str] = Field(None, description="系统状态消息")

    ai_grade: Optional[str] = Field(None, description="AI建议年级")
    ai_difficulty: Optional[Difficulty] = Field(None, description="AI建议难度")
    ai_topics: Optional[List[str]] = Field(None, description="AI建议知识点")
    ai_category: Optional[QuestionCategory] = Field(None, description="AI建议题类")
    ai_analysis: Optional[str] = Field(None, description="AI生成解析")
    ai_reasoning: Optional[str] = Field(None, description="AI推理过程")
    ai_model: Optional[str] = Field(None, description="AI模型")
    ai_optimized_at: Optional[datetime] = Field(None, description="AI处理时间")
    is_ai_optimized: Optional[int] = Field(None, description="是否已AI处理")

    confirmed_at: Optional[datetime] = Field(None, description="确认入库时间")

    # 分类信息字段
    subject: Optional[str] = Field(None, description="科目")
    grade: Optional[int] = Field(None, ge=7, le=12, description="年级（7-12）")
    education_level: Optional[EducationLevel] = Field(None, description="学段")
    source_folder: Optional[str] = Field(None, description="来源文件夹")
    source: Optional[str] = Field(None, description="来源")
    version: Optional[int] = Field(None, description="版本号")

    @model_validator(mode='after')
    def validate_business_rules(self) -> 'QuestionUpdate':
        """业务规则校验（更新时只校验提供的字段）"""
        # 选择题必须有选项
        if self.type in (QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE):
            if self.options is not None and len(self.options) == 0:
                raise ValueError('选择题必须有选项')

        # 年级与学段对应
        if self.grade and self.education_level:
            if 7 <= self.grade <= 9 and self.education_level != EducationLevel.JUNIOR:
                raise ValueError('年级 7-9 对应学段应为"初中"')
            if 10 <= self.grade <= 12 and self.education_level != EducationLevel.SENIOR:
                raise ValueError('年级 10-12 对应学段应为"高中"')

        return self


class QuestionResponse(QuestionBase):
    """题目响应模型"""
    id: str = Field(..., description="题目ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    # 相似题字段
    is_duplicate: Optional[bool] = Field(False, description="是否为相似题")
    duplicate_group_id: Optional[str] = Field(None, description="相似题组ID")
    duplicate_checked_at: Optional[datetime] = Field(None, description="相似度检测时间")

    @field_validator('options', 'stem_images', 'topics', 'ai_topics', mode='before')
    @classmethod
    def parse_json_fields(cls, v: Any) -> Optional[Union[List, dict]]:
        """解析JSON字符串字段"""
        if v is None:
            return None
        if isinstance(v, (list, dict)):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    @field_serializer('created_at', 'updated_at', 'duplicate_checked_at')
    @classmethod
    def serialize_datetime(cls, dt: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        if dt is None:
            return None
        return dt.isoformat()

    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    """统计数据响应模型"""
    total: int = Field(..., description="总题数")
    with_analysis: int = Field(..., description="有解析的题目数")
    with_images: int = Field(..., description="有图片的题目数")
    with_topics: int = Field(..., description="有知识点的题目数")
    by_type: dict = Field(..., description="按题型统计")


class ConflictCheckRequest(BaseModel):
    """冲突检测请求模型"""
    folder_code: str = Field(..., description="文件夹短代码")
    teacher_name: str = Field(..., description="老师姓名")
    original_filename: str = Field(..., description="原始文件名")


class QuestionBulkUpdateItem(QuestionUpdate):
    """批量更新单项"""
    id: str = Field(..., description="题目ID")


class QuestionBulkUpdateRequest(BaseModel):
    """批量更新请求模型"""
    batch_id: str = Field(..., description="批次ID")
    questions: List[QuestionBulkUpdateItem] = Field(..., description="要更新的题目列表")
