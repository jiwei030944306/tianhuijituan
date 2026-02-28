"""
安全工具模块 - 密码处理和权限控制
"""
from passlib.context import CryptContext
from enum import Enum
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.crud import user as user_crud

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    加密密码

    Args:
        password: 明文密码

    Returns:
        加密后的密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


async def get_current_user_from_db(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    从数据库获取完整的当前用户信息

    Args:
        current_user: token 解析出的用户信息（包含 user_id）
        db: 数据库会话

    Returns:
        包含完整用户信息的字典

    Raises:
        HTTPException: 用户不存在或已被禁用
    """
    user_id = current_user.get("username")  # 实际存储的是 user_id

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户标识"
        )

    user = await user_crud.get_user_by_id(db, user_id_int)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "role": "admin" if user.is_superuser else "teacher"
    }


async def require_admin(
    current_user: dict = Depends(get_current_user_from_db)
) -> dict:
    """
    要求管理员权限

    Args:
        current_user: 当前用户完整信息

    Returns:
        用户信息

    Raises:
        HTTPException: 权限不足
    """
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


async def require_teacher(
    current_user: dict = Depends(get_current_user_from_db)
) -> dict:
    """
    要求教师权限

    教师和管理员都具有此权限

    Args:
        current_user: 当前用户完整信息

    Returns:
        用户信息

    Raises:
        HTTPException: 权限不足
    """
    # 教师和管理员都有权限
    role = current_user.get("role")
    if role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要教师权限"
        )
    return current_user


async def require_active_user(
    current_user: dict = Depends(get_current_user_from_db)
) -> dict:
    """
    要求活跃用户（已登录且未被禁用）

    这是最基础的权限检查，任何已登录用户都可以通过

    Args:
        current_user: 当前用户完整信息

    Returns:
        用户信息
    """
    return current_user