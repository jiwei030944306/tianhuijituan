"""
认证依赖模块
提供FastAPI依赖注入所需的认证相关依赖
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import TokenData

# OAuth2方案配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前用户依赖

    通过JWT令牌验证并获取当前登录用户

    Args:
        token: 从请求头中提取的JWT令牌
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 验证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解码JWT令牌（使用配置中心的密钥）
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    # 从数据库查询用户
    result = await db.execute(
        select(User).where(User.id == int(token_data.user_id))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户依赖

    验证用户账户是否处于激活状态

    Args:
        current_user: 当前用户对象

    Returns:
        当前用户对象

    Raises:
        HTTPException: 用户账户被禁用时抛出403错误
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    获取当前超级管理员用户依赖

    验证用户是否具有超级管理员权限

    Args:
        current_user: 当前用户对象

    Returns:
        当前用户对象

    Raises:
        HTTPException: 用户不是超级管理员时抛出403错误
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    return current_user