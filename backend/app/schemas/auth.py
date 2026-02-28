"""
认证相关Pydantic模型
用于请求和响应的数据验证
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class Token(BaseModel):
    """
    令牌响应模型
    
    用于返回JWT访问令牌
    
    Attributes:
        access_token: JWT访问令牌字符串
        token_type: 令牌类型（默认为bearer）
        expires_in: 令牌过期时间（秒）
    """
    access_token: str = Field(..., description="JWT访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class TokenData(BaseModel):
    """
    令牌数据模型
    
    用于存储从JWT令牌中解码的用户信息
    
    Attributes:
        user_id: 用户ID（从令牌的sub字段提取）
    """
    user_id: Optional[str] = Field(None, description="用户ID")


class UserBase(BaseModel):
    """
    用户基础模型
    
    包含用户的基本信息字段
    
    Attributes:
        username: 用户名
        email: 邮箱地址
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """验证用户名只能包含字母、数字和下划线"""
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserCreate(UserBase):
    """
    用户创建模型
    
    用于用户注册时的数据验证
    
    Attributes:
        username: 用户名
        email: 邮箱地址
        password: 密码（至少8位）
    """
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    
    @validator('password')
    def password_strength(cls, v):
        """验证密码强度（至少包含一个大写字母、一个小写字母和一个数字）"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class UserUpdate(BaseModel):
    """
    用户更新模型
    
    用于更新用户信息时的数据验证
    
    Attributes:
        username: 新用户名（可选）
        email: 新邮箱地址（可选）
        password: 新密码（可选）
        is_active: 账户状态（可选，仅管理员可修改）
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = Field(None)
    
    @validator('password')
    def password_strength(cls, v):
        """验证密码强度"""
        if v is None:
            return v
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class UserResponse(UserBase):
    """
    用户响应模型
    
    用于返回给客户端的用户信息（不包含敏感字段）
    
    Attributes:
        id: 用户ID
        username: 用户名
        email: 邮箱地址
        is_active: 账户是否激活
        is_superuser: 是否为超级管理员
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2024-01-15T08:30:00",
                "updated_at": "2024-01-15T08:30:00"
            }
        }


class UserLogin(BaseModel):
    """
    用户登录模型
    
    用于用户登录时的数据验证（JSON格式）
    
    Attributes:
        username: 用户名
        password: 密码
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=8, max_length=100, description="密码")
