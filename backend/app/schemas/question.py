"""
题目数据验证模型
"""
from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, field_validator, field_serializer
from datetime import datetime
import json


class QuestionBase(BaseModel):
    """题目基础模型"""
    question_number: Optional[int] = Field(None, description="题目编号")
    type: str = Field(..., description="题目类型")
    difficulty: Optional[str] = Field(None, description="最终难度（5级中文）")
    status: str = Field(default="active", description="状态")
    stem: str = Field(..., description="题干")
    answer: str = Field(..., description="答案")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="选项")
    stem_images: Optional[List[Dict[str, str]]] = Field(None, description="题干图片")
    topics: Optional[List[str]] = Field(None, description="最终知识点")
    category: Optional[str] = Field(None, description="最终题类")
    analysis: Optional[str] = Field(None, description="原始解析")
    comment: Optional[str] = Field(None, description="人工备注")
    status_message: Optional[str] = Field(None, description="系统状态消息")

    # AI 建议字段
    ai_grade: Optional[str] = Field(None, description="AI建议年级")
    ai_difficulty: Optional[str] = Field(None, description="AI建议难度")
    ai_topics: Optional[List[str]] = Field(None, description="AI建议知识点")
    ai_category: Optional[str] = Field(None, description="AI建议题类")
    ai_analysis: Optional[str] = Field(None, description="AI生成解析")
    ai_reasoning: Optional[str] = Field(None, description="AI推理过程")
    ai_model: Optional[str] = Field(None, description="AI模型")
    ai_optimized_at: Optional[datetime] = Field(None, description="AI处理时间")
    is_ai_optimized: Optional[int] = Field(0, description="是否已AI处理（0/1）")

    confirmed_at: Optional[datetime] = Field(None, description="确认入库时间")

    # 分类信息字段
    subject: Optional[str] = Field(None, description="科目")
    grade: Optional[int] = Field(None, description="年级")
    education_level: Optional[str] = Field(None, description="学段")
    source_folder: Optional[str] = Field(None, description="来源文件夹")
    source: Optional[str] = Field(None, description="来源")
    version: Optional[int] = Field(1, description="版本号")


class QuestionCreate(QuestionBase):
    """创建题目模型"""
    pass


class QuestionUpdate(BaseModel):
    """更新题目模型（所有字段可选）"""
    question_number: Optional[int] = Field(None, description="题目编号")
    type: Optional[str] = Field(None, description="题目类型")
    difficulty: Optional[str] = Field(None, description="最终难度")
    status: Optional[str] = Field(None, description="状态")
    stem: Optional[str] = Field(None, description="题干")
    answer: Optional[str] = Field(None, description="答案")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="选项")
    stem_images: Optional[List[Dict[str, str]]] = Field(None, description="题干图片")
    topics: Optional[List[str]] = Field(None, description="最终知识点")
    category: Optional[str] = Field(None, description="最终题类")
    analysis: Optional[str] = Field(None, description="原始解析")
    comment: Optional[str] = Field(None, description="人工备注")
    status_message: Optional[str] = Field(None, description="系统状态消息")

    ai_grade: Optional[str] = Field(None, description="AI建议年级")
    ai_difficulty: Optional[str] = Field(None, description="AI建议难度")
    ai_topics: Optional[List[str]] = Field(None, description="AI建议知识点")
    ai_category: Optional[str] = Field(None, description="AI建议题类")
    ai_analysis: Optional[str] = Field(None, description="AI生成解析")
    ai_reasoning: Optional[str] = Field(None, description="AI推理过程")
    ai_model: Optional[str] = Field(None, description="AI模型")
    ai_optimized_at: Optional[datetime] = Field(None, description="AI处理时间")
    is_ai_optimized: Optional[int] = Field(None, description="是否已AI处理")

    confirmed_at: Optional[datetime] = Field(None, description="确认入库时间")

    # 分类信息字段
    subject: Optional[str] = Field(None, description="科目")
    grade: Optional[int] = Field(None, description="年级")
    education_level: Optional[str] = Field(None, description="学段")
    source_folder: Optional[str] = Field(None, description="来源文件夹")
    source: Optional[str] = Field(None, description="来源")
    version: Optional[int] = Field(None, description="版本号")


class QuestionResponse(QuestionBase):
    """题目响应模型"""
    id: str = Field(..., description="题目ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

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

    @field_serializer('created_at', 'updated_at')
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
