from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.core.security import get_current_user
from app.models.user import UserModel

router = APIRouter()


@router.post("/recognize")
async def recognize_speech(
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """语音识别"""
    return {"message": "语音识别接口", "filename": audio_file.filename}


@router.get("/history")
async def get_speech_history(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取语音识别历史"""
    return {"message": "语音识别历史接口"}