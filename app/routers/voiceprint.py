from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import time
import uuid

from app.models.database import get_db
from app.models.employee import EmployeeModel
from app.models.voiceprint import VoiceprintModel
from app.schemas.voiceprint import (
    VoiceprintRegisterRequest, VoiceprintRegisterResponse,
    VoiceprintRecognizeRequest, VoiceprintRecognizeResponse,
    VoiceprintStatusResponse, VoiceprintDeleteResponse
)
from app.services.voiceprint_service import voiceprint_service
from app.services.auth_service import get_current_user
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/register", response_model=VoiceprintRegisterResponse)
async def register_voiceprint(
    background_tasks: BackgroundTasks,
    employee_id: int,
    sample_index: int = 1,
    audio_file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    注册声纹
    
    - **employee_id**: 员工ID
    - **sample_index**: 样本索引 (1-5)
    - **audio_file**: 音频文件 (WAV格式)
    """
    try:
        # 验证员工存在
        stmt = await db.get(EmployeeModel, employee_id)
        if not stmt or stmt.status != 1:
            raise HTTPException(status_code=404, detail="员工不存在或已离职")
        
        # 验证样本数量限制
        existing_count = await db.execute(
            "SELECT COUNT(*) FROM voiceprints WHERE employee_id = %s AND is_active = 1",
            (employee_id,)
        )
        count = existing_count.scalar()
        
        if count >= 5:  # 最大5个样本
            raise HTTPException(status_code=400, detail="已达到最大样本数量限制")
        
        # 验证文件格式
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="请上传音频文件")
        
        # 读取音频数据
        audio_data = await audio_file.read()
        
        # 限制文件大小 (50MB)
        max_size = 50 * 1024 * 1024
        if len(audio_data) > max_size:
            raise HTTPException(status_code=400, detail="音频文件过大，最大50MB")
        
        # 注册声纹
        voiceprint_id = await voiceprint_service.register_voiceprint(
            employee_id=employee_id,
            audio_data=audio_data,
            sample_index=sample_index
        )
        
        # 后台任务：更新员工声纹状态
        background_tasks.add_task(update_employee_voiceprint_status, employee_id)
        
        return VoiceprintRegisterResponse(
            success=True,
            voiceprint_id=voiceprint_id,
            sample_index=sample_index,
            message="声纹注册成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"声纹注册失败: {str(e)}")


@router.post("/recognize", response_model=VoiceprintRecognizeResponse)
async def recognize_voiceprint(
    background_tasks: BackgroundTasks,
    meeting_id: Optional[int] = None,
    audio_file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    声纹识别
    
    - **meeting_id**: 会议ID (可选)
    - **audio_file**: 音频文件 (WAV格式)
    """
    try:
        # 验证文件格式
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="请上传音频文件")
        
        # 读取音频数据
        audio_data = await audio_file.read()
        
        # 限制文件大小
        max_size = 50 * 1024 * 1024
        if len(audio_data) > max_size:
            raise HTTPException(status_code=400, detail="音频文件过大，最大50MB")
        
        # 进行声纹识别
        start_time = time.time()
        result = await voiceprint_service.recognize_voiceprint(audio_data, meeting_id)
        processing_time = (time.time() - start_time) * 1000  # 转换为毫秒
        result.processing_time = processing_time
        
        # 后台任务：保存识别记录
        if meeting_id and result.employee_id:
            background_tasks.add_task(
                save_speech_record,
                meeting_id=meeting_id,
                employee_id=result.employee_id,
                audio_url=result.audio_url,
                confidence=result.confidence,
                duration=0  # 需要从音频中计算
            )
        
        # 如果有匹配的员工，获取员工信息
        employee_info = None
        if result.employee_id:
            employee = await db.get(EmployeeModel, result.employee_id)
            if employee:
                employee_info = {
                    "id": employee.id,
                    "employee_id": employee.employee_id,
                    "name": employee.name,
                    "department": employee.department,
                    "position": employee.position
                }
        
        return VoiceprintRecognizeResponse(
            success=result.success,
            confidence=result.confidence,
            threshold=result.threshold,
            identified_employee=employee_info,
            audio_url=result.audio_url,
            processing_time=result.processing_time,
            all_matches=result.all_matches
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"声纹识别失败: {str(e)}")


@router.get("/status/{employee_id}", response_model=VoiceprintStatusResponse)
async def get_voiceprint_status(
    employee_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取员工声纹注册状态"""
    try:
        # 验证员工存在
        employee = await db.get(EmployeeModel, employee_id)
        if not employee or employee.status != 1:
            raise HTTPException(status_code=404, detail="员工不存在或已离职")
        
        # 获取声纹信息
        voiceprints = await db.execute(
            "SELECT voiceprint_id, audio_sample_url, quality_score, created_at, sample_duration "
            "FROM voiceprints WHERE employee_id = %s AND is_active = 1 ORDER BY created_at DESC",
            (employee_id,)
        )
        
        voiceprints_data = []
        for vp in voiceprints.fetchall():
            voiceprints_data.append({
                "voiceprint_id": vp[0],
                "audio_sample_url": vp[1],
                "quality_score": vp[2],
                "created_at": vp[3].isoformat() if vp[3] else None,
                "sample_duration": vp[4]
            })
        
        # 获取配置的所需样本数量
        required_samples = 3  # 默认值，可以从配置表读取
        
        return VoiceprintStatusResponse(
            employee_id=employee_id,
            employee_name=employee.name,
            registered_count=len(voiceprints_data),
            required_count=required_samples,
            is_complete=len(voiceprints_data) >= required_samples,
            voiceprints=voiceprints_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取声纹状态失败: {str(e)}")


@router.delete("/{voiceprint_id}", response_model=VoiceprintDeleteResponse)
async def delete_voiceprint(
    voiceprint_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除声纹样本"""
    try:
        # 获取声纹信息
        voiceprint = await db.execute(
            "SELECT * FROM voiceprints WHERE voiceprint_id = %s",
            (voiceprint_id,)
        )
        vp_data = voiceprint.fetchone()
        
        if not vp_data:
            raise HTTPException(status_code=404, detail="声纹不存在")
        
        # 删除MinIO中的音频文件
        if vp_data[2]:  # audio_sample_url
            try:
                from app.core.minio_client import minio_client
                from app.core.config import settings
                
                # 从URL中提取object_name
                url_parts = vp_data[2].split('/')
                if len(url_parts) >= 5:
                    object_name = '/'.join(url_parts[-2:])
                    minio_client.remove_object(settings.MINIO_BUCKET, object_name)
                    
            except Exception as e:
                # 即使删除MinIO文件失败，也继续删除数据库记录
                print(f"Warning: Failed to delete MinIO file: {e}")
        
        # 删除数据库记录
        await db.execute(
            "DELETE FROM voiceprints WHERE voiceprint_id = %s",
            (voiceprint_id,)
        )
        await db.commit()
        
        # 后台任务：更新员工声纹状态
        background_tasks.add_task(update_employee_voiceprint_status, vp_data[1])  # employee_id
        
        return VoiceprintDeleteResponse(
            success=True,
            message="声纹删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除声纹失败: {str(e)}")


@router.get("/list", response_model=List[dict])
async def list_voiceprints(
    employee_id: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取声纹列表"""
    try:
        # 构建查询
        where_clause = "WHERE v.is_active = 1"
        params = []
        
        if employee_id:
            where_clause += " AND v.employee_id = %s"
            params.append(employee_id)
        
        # 分页
        offset = (page - 1) * size
        
        query = f"""
        SELECT 
            v.voiceprint_id,
            v.employee_id,
            e.name as employee_name,
            e.employee_id as employee_no,
            e.department,
            v.audio_sample_url,
            v.quality_score,
            v.sample_duration,
            v.created_at
        FROM voiceprints v
        LEFT JOIN employees e ON v.employee_id = e.id
        {where_clause}
        ORDER BY v.created_at DESC
        LIMIT %s OFFSET %s
        """
        
        params.extend([size, offset])
        
        result = await db.execute(query, params)
        voiceprints = []
        
        for row in result.fetchall():
            voiceprints.append({
                "voiceprint_id": row[0],
                "employee_id": row[1],
                "employee_name": row[2],
                "employee_no": row[3],
                "department": row[4],
                "audio_sample_url": row[5],
                "quality_score": row[6],
                "sample_duration": row[7],
                "created_at": row[8].isoformat() if row[8] else None
            })
        
        return voiceprints
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取声纹列表失败: {str(e)}")


# 后台任务函数
async def update_employee_voiceprint_status(employee_id: int):
    """更新员工声纹状态"""
    try:
        async with get_db() as db:
            # 这里可以添加更新逻辑，比如更新缓存或统计信息
            pass
    except Exception as e:
        print(f"Error updating employee voiceprint status: {e}")


async def save_speech_record(
    meeting_id: int,
    employee_id: int,
    audio_url: str,
    confidence: float,
    duration: float
):
    """保存发言记录"""
    try:
        async with get_db() as db:
            await db.execute(
                """INSERT INTO speech_records 
                   (meeting_id, employee_id, audio_url, confidence_score, 
                    start_time, end_time, duration, is_identified)
                   VALUES (%s, %s, %s, %s, NOW(), NOW(), %s, %s)""",
                (meeting_id, employee_id, audio_url, confidence, duration, True)
            )
            await db.commit()
    except Exception as e:
        print(f"Error saving speech record: {e}")