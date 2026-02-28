"""
上传相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConflictCheckRequest(BaseModel):
    """冲突检测请求"""
    original_filename: str = Field(..., description="原始文件名，如：期中考试.zip")
    folder_code: str = Field(..., description="学科学段短代码，如：h7s9m2")
    teacher_name: str = Field(..., description="老师姓名，如：张老师")


class ExistingRecordInfo(BaseModel):
    """已有记录信息"""
    batch_id: str = Field(..., description="批次ID")
    display_name: str = Field(..., description="显示名称")
    uploaded_at: datetime = Field(..., description="上传时间")
    file_count: Optional[int] = Field(None, description="题目数量")


class ConflictCheckResponse(BaseModel):
    """冲突检测响应"""
    conflict: bool = Field(..., description="是否冲突")
    existing_record: Optional[ExistingRecordInfo] = Field(None, description="已有记录信息")
    message: str = Field(..., description="提示信息")
    options: list[str] = Field(default=["覆盖", "重命名", "取消"], description="操作选项")


class UploadFolderRequest(BaseModel):
    """上传文件夹请求（用于文档说明，实际使用FormData）"""
    folder_name: str = Field(..., description="文件夹显示名称")
    subject: str = Field(..., description="学科中文")
    subject_code: str = Field(..., description="学科英文代码")
    grade: int = Field(..., description="年级（7-12）")
    education_level: str = Field(..., description="学段")
    folder_code: str = Field(..., description="学科学段短代码")
    teacher_name: str = Field(..., description="老师姓名")
    conflict_action: str = Field(default="new", description="冲突处理方式：new/overwrite/rename/cancel")


class UploadFolderResponse(BaseModel):
    """上传文件夹响应"""
    success: bool = Field(..., description="是否成功")
    batch_id: str = Field(..., description="批次ID")
    folder_code: str = Field(..., description="学科学段短代码")
    record_date: str = Field(..., description="记录日期")
    full_path: str = Field(..., description="完整路径")
    display_name: str = Field(..., description="显示名称")
    question_count: int = Field(..., description="题目数量")
    image_count: int = Field(..., description="图片数量")
    uploaded_at: datetime = Field(..., description="上传时间")
    operations_file: str = Field(..., description="操作记录文件名")
