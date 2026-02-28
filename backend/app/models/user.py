"""
用户模型定义
提供用户认证和授权所需的数据模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """
    用户模型
    
    用于存储用户认证和授权信息
    
    Attributes:
        id: 用户唯一标识
        username: 用户名，用于登录
        email: 邮箱地址
        hashed_password: 加密后的密码
        is_active: 账户是否激活
        is_superuser: 是否为超级管理员
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
