"""
扩展属性模型

支持Schema版本控制的题目扩展属性表
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuestionAttribute(Base):
    """题目扩展属性模型
    
    支持Schema版本控制，可以存储同一题目的多个版本属性
    """
    __tablename__ = "question_attributes"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    
    # 关联题目
    question_id = Column(
        String(100), 
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        comment="题目ID"
    )
    
    # Schema版本控制
    schema_version = Column(
        String(10), 
        nullable=False,
        comment="Schema版本，如：1.0, 2.0"
    )
    schema_name = Column(
        String(50), 
        nullable=False,
        comment="Schema名称，如：basic, advanced, ai_enhanced"
    )
    
    # 属性数据（JSONB）
    attribute_data = Column(
        Text,
        nullable=False,
        comment="属性数据（JSON字符串）"
    )
    
    # 有效性控制
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default='1',
        comment="是否生效"
    )
    valid_from = Column(
        DateTime,
        nullable=True,
        comment="生效时间"
    )
    valid_until = Column(
        DateTime,
        nullable=True,
        comment="失效时间"
    )
    
    # 迁移记录
    migration_notes = Column(
        Text,
        nullable=True,
        comment="迁移说明"
    )
    
    # 创建信息
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    created_by = Column(
        String(100),
        nullable=True,
        comment="创建者"
    )
    
    # 关联关系
    question = relationship("Question", back_populates="attributes")
    
    # 表约束
    __table_args__ = (
        # 唯一约束：同一题目的同一版本只能有一条记录
        UniqueConstraint('question_id', 'schema_version', name='uq_question_attribute_version'),
        
        # 索引
        Index('idx_qa_question_id', 'question_id'),
        Index('idx_qa_schema_version', 'schema_version'),
        Index('idx_qa_is_active', 'is_active'),
        Index('idx_qa_created_at', 'created_at'),
        
        # JSONB内容的GIN索引（PostgreSQL专用）
        # 注：如需JSON查询优化，可添加GIN索引
        # sa.Index('idx_qa_attr_gin', 'attribute_data', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<QuestionAttribute(id={self.id}, question_id={self.question_id}, schema_version={self.schema_version})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'schema_version': self.schema_version,
            'schema_name': self.schema_name,
            'attribute_data': self.attribute_data,
            'is_active': self.is_active,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'migration_notes': self.migration_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
