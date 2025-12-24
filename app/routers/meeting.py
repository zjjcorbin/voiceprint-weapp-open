from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.database import get_db
from app.core.security import get_current_user
from app.models.user import UserModel

router = APIRouter()


@router.get("/")
async def get_meetings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取会议列表"""
    return {"message": "会议列表接口", "skip": skip, "limit": limit}


@router.post("/")
async def create_meeting(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """创建会议"""
    return {"message": "创建会议接口"}