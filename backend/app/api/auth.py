"""
认证 API 路由

提供用户注册、登录、获取当前用户等认证相关接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, get_current_user
from app.core.database import get_db
from app.crud import user as user_crud
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册

    创建新用户账户，用户名和邮箱必须唯一
    """
    # 检查用户名是否已存在
    existing_user = await user_crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )

    # 检查邮箱是否已存在（如果提供了邮箱）
    if user.email:
        existing_email = await user_crud.get_user_by_email(db, user.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

    # 创建用户
    new_user = await user_crud.create_user(db, user)

    return UserResponse(
        id=str(new_user.id),
        username=new_user.username,
        email=new_user.email,
        role="admin" if new_user.is_superuser else "teacher",
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录

    OAuth2 密码模式登录，返回 JWT 令牌
    """
    # 验证用户凭据
    user = await user_crud.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 创建访问令牌（使用用户 ID 作为 subject）
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户信息

    需要认证，返回当前登录用户的详细信息
    """
    # 从 token 中获取用户 ID
    user_id = current_user.get("username")  # 实际是 user_id

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )

    # 从数据库获取用户信息
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role="admin" if user.is_superuser else "teacher",
        is_active=user.is_active,
        created_at=user.created_at
    )