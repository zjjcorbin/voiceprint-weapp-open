from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.core.security import get_current_user, get_admin_user
from app.models.user import UserModel

router = APIRouter()


@router.get("/info")
async def get_system_info(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_admin_user)
):
    """获取系统信息（管理员权限）"""
    return {
        "system_name": "企业级声纹识别系统",
        "version": "1.0.0",
        "status": "running",
        "features": {
            "voiceprint_recognition": True,
            "emotion_recognition": True,
            "speech_recognition": True,
            "file_upload": True
        }
    }


@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_admin_user)
):
    """获取系统统计（管理员权限）"""
    return {
        "users_count": 0,
        "employees_count": 0,
        "voiceprints_count": 0,
        "meetings_count": 0,
        "storage_used": "0 MB"
    }