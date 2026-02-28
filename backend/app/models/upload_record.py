"""
上传记录数据模型
用于记录P1中心的上传历史，支持冲突检测和文件管理
"""
from sqlalchemy import Column, String, Integer, BigInteger, Text, DateTime, Date, JSON, UniqueConstraint, Index
from sqlalchemy.sql import func
from app.core.database import Base


class UploadRecord(Base):
    """上传记录模型"""
    __tablename__ = "upload_records"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录ID")
    
    # 主文件夹信息（学科学段）
    folder_code = Column(String(10), nullable=False, comment="学科学段短代码，如：h7s9m2")
    education_level = Column(String(20), nullable=False, comment="学段中文，如：高中")
    subject = Column(String(20), nullable=False, comment="学科中文，如：数学")
    
    # 上传批次信息
    batch_id = Column(String(30), nullable=False, comment="批次ID：YYYYMMDD-HHMMSS-XXXXXX")
    record_date = Column(Date, nullable=False, comment="记录日期")
    
    # 完整路径
    full_path = Column(String(500), nullable=False, comment="完整存储路径")
    
    # 上传者信息
    teacher_id = Column(Integer, nullable=True, comment="老师ID（预留）")
    teacher_name = Column(String(50), nullable=True, comment="老师姓名，如：张老师")
    
    # 文件信息
    display_name = Column(String(255), nullable=False, comment="显示名称，如：期中考试")
    original_filename = Column(String(255), nullable=False, comment="原始文件名，如：期中考试.zip")
    file_size = Column(BigInteger, nullable=True, comment="文件大小（字节）")
    file_count = Column(Integer, nullable=True, comment="题目数量")
    image_count = Column(Integer, nullable=True, comment="图片数量")
    
    # 状态
    status = Column(String(20), nullable=False, default="completed", comment="状态：pending/processing/completed/error")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 扩展字段（注意：不能使用metadata，因为是SQLAlchemy保留字）
    extra_data = Column(JSON, nullable=True, comment="扩展信息（JSON格式）")
    
    # 时间戳
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now(), comment="上传时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 唯一约束：同一天同一文件夹下批次ID唯一
    __table_args__ = (
        UniqueConstraint('folder_code', 'record_date', 'batch_id', name='uix_upload_folder_date_batch'),
        # 索引
        Index('idx_upload_folder', 'folder_code'),
        Index('idx_upload_date', 'record_date'),
        Index('idx_upload_teacher', 'teacher_name', 'record_date'),
        Index('idx_upload_status', 'status'),
        Index('idx_upload_filename', 'folder_code', 'teacher_name', 'record_date', 'original_filename'),
        # 性能优化索引
        Index('idx_upload_batch_id', 'batch_id'),
    )

    def __repr__(self):
        return f"<UploadRecord(id={self.id}, folder_code={self.folder_code}, batch_id={self.batch_id})>"
