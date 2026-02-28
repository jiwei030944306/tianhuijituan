"""
用户 CRUD 操作

提供用户的数据库增删改查操作
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    根据用户名获取用户

    Args:
        db: 数据库会话
        username: 用户名

    Returns:
        用户对象，不存在则返回 None
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    根据邮箱获取用户

    Args:
        db: 数据库会话
        email: 邮箱地址

    Returns:
        用户对象，不存在则返回 None
    """
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    根据 ID 获取用户

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        用户对象，不存在则返回 None
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate, role: str = "teacher") -> User:
    """
    创建新用户

    Args:
        db: 数据库会话
        user: 用户创建数据
        role: 用户角色，默认为 teacher

    Returns:
        创建的用户对象
    """
    hashed_password = hash_password(user.password)
    
    db_user = User(
        username=user.username,
        email=user.email or f"{user.username}@example.com",  # 邮箱可选，提供默认值
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=(role == "admin")
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    验证用户凭据

    Args:
        db: 数据库会话
        username: 用户名
        password: 密码

    Returns:
        验证成功返回用户对象，失败返回 None
    """
    user = await get_user_by_username(db, username)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


async def update_user_password(db: AsyncSession, user_id: int, new_password: str) -> bool:
    """
    更新用户密码

    Args:
        db: 数据库会话
        user_id: 用户 ID
        new_password: 新密码

    Returns:
        更新成功返回 True
    """
    user = await get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.hashed_password = hash_password(new_password)
    await db.commit()
    
    return True


async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    """
    停用用户

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        停用成功返回 True
    """
    user = await get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.is_active = False
    await db.commit()
    
    return True