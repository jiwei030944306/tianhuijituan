"""
用户相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, description="密码")


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应模型"""
    id: str = Field(..., description="用户ID")
    role: str = Field(default="teacher", description="角色")
    is_active: bool = Field(default=True, description="是否活跃")
    created_at: Optional[datetime] = Field(None, description="创建时间")

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = Field(None, description="用户名")
