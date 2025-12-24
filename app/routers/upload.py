from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.core.security import get_current_user
from app.models.user import UserModel

router = APIRouter()


@router.post("/audio")
async def upload_audio(
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """上传音频文件"""
    if not audio_file.filename.endswith(('.wav', '.mp3', '.m4a', '.flac')):
        raise HTTPException(status_code=400, detail="不支持的音频格式")
    
    return {
        "message": "音频上传成功",
        "filename": audio_file.filename,
        "size": audio_file.size,
        "content_type": audio_file.content_type
    }


@router.post("/image")
async def upload_image(
    image_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """上传图片文件"""
    if not image_file.filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    
    return {
        "message": "图片上传成功",
        "filename": image_file.filename,
        "size": image_file.size,
        "content_type": image_file.content_type
    }