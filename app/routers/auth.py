from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.models.database import get_db
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserLogin, UserLoginResponse, UserResponse
from app.core.security import create_access_token, verify_password, get_password_hash, get_current_user
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    from sqlalchemy import select
    
    # 检查用户名是否已存在
    stmt = select(UserModel).where(UserModel.username == user_data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email:
        stmt = select(UserModel).where(UserModel.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = UserModel(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password,
        nickname=user_data.nickname,
        real_name=user_data.real_name
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=UserLoginResponse)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    from sqlalchemy import select
    
    # 查找用户
    stmt = select(UserModel).where(UserModel.username == user_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账户已被禁用"
        )
    
    # 更新登录信息
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    user.login_count += 1
    await db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.post("/logout")
async def logout():
    """用户登出（客户端删除token即可）"""
    return {"message": "登出成功"}