"""
题目数据模型
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Question(Base):
    """题目模型"""
    __tablename__ = "questions"

    id = Column(String(100), primary_key=True, comment="题目ID")
    question_number = Column(Integer, comment="题目编号")
    type = Column(String(50), nullable=False, comment="题目类型")
    difficulty = Column(String(10), nullable=True, comment="最终难度")
    status = Column(String(20), nullable=False, default="active", comment="状态")
    stem = Column(Text, nullable=False, comment="题干")
    options = Column(Text, comment="选项（JSON字符串）")
    stem_images = Column(Text, comment="题干图片（JSON字符串）")
    topics = Column(Text, comment="最终知识点（JSON字符串）")
    category = Column(String(20), comment="最终题类")
    answer = Column(Text, nullable=False, comment="答案")
    analysis = Column(Text, comment="原始解析")
    comment = Column(Text, comment="人工备注")
    status_message = Column(Text, comment="系统状态消息")

    # AI 结果字段
    ai_grade = Column(String(20), comment="AI建议年级")
    ai_difficulty = Column(String(10), comment="AI建议难度")
    ai_topics = Column(Text, comment="AI建议知识点（JSON字符串）")
    ai_category = Column(String(20), comment="AI建议题类")
    ai_analysis = Column(Text, comment="AI生成解析")
    ai_reasoning = Column(Text, comment="AI推理过程")
    ai_model = Column(String(100), comment="AI模型")
    ai_optimized_at = Column(DateTime, comment="AI处理时间")
    is_ai_optimized = Column(Integer, default=0, comment="是否AI已处理（0/1）")

    # 人工确认字段
    confirmed_at = Column(DateTime, comment="确认入库时间")

    # 相似题检测字段
    is_duplicate = Column(Boolean, default=False, comment="是否为相似题")
    duplicate_group_id = Column(String(50), comment="相似题组ID")
    duplicate_checked_at = Column(DateTime, comment="相似度检测时间")

    # 分类信息字段
    subject = Column(String(20), comment="科目：数学、语文、英语等")
    grade = Column(Integer, comment="年级：7-12")
    education_level = Column(String(10), comment="学段：初中、高中")
    source_folder = Column(String(200), comment="来源文件夹名称")
    source = Column(String(200), comment="来源试卷")
    version = Column(Integer, nullable=False, default=1, comment="乐观锁版本")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    attributes = relationship("QuestionAttribute", back_populates="question", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_questions_type', 'type'),
        Index('idx_questions_difficulty', 'difficulty'),
        Index('idx_questions_status', 'status'),
        Index('idx_questions_subject', 'subject'),
        Index('idx_questions_grade', 'grade'),
        Index('idx_questions_education_level', 'education_level'),
        Index('idx_questions_subject_grade', 'subject', 'grade'),
        # 性能优化索引
        Index('idx_questions_source_folder', 'source_folder'),
        Index('idx_questions_source', 'source'),
        Index('idx_questions_created_at', 'created_at'),
        Index('idx_questions_updated_at', 'updated_at'),
        # 相似题筛选索引
        Index('idx_questions_is_duplicate', 'is_duplicate'),
        Index('idx_questions_duplicate_group_id', 'duplicate_group_id'),
    )

    def __repr__(self):
        return f"<Question(id={self.id}, type={self.type}, difficulty={self.difficulty}, status={self.status})>"