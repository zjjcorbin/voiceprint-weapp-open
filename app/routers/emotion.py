from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import asyncio
import uuid
import time
from loguru import logger

from app.models.database import get_db
from app.services.emotion_service import emotion_service
from app.schemas.emotion import (
    EmotionDetectionRequest, EmotionDetectionResponse, 
    EmotionBatchRequest, EmotionBatchResponse,
    EmotionAnalysis, EmotionSummary, EmotionFeedback,
    EmotionInsight, EmotionComparison, EmotionAlert,
    EmotionStatistics
)
from app.models.emotion import EmotionDetectionModel, EmotionFeedbackModel
from app.core.security import get_current_user
from app.models.user import UserModel

router = APIRouter()


@router.post("/detect", response_model=EmotionDetectionResponse)
async def detect_emotion(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    employee_id: Optional[int] = Form(None),
    meeting_id: Optional[int] = Form(None),
    require_analysis: bool = Form(True),
    current_user: UserModel = Depends(get_current_user)
):
    """检测语音情绪"""
    try:
        # 检查模型状态
        if not await emotion_service.check_model_status():
            raise HTTPException(status_code=503, detail="情绪识别服务未就绪")
        
        # 验证文件类型
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="请上传音频文件")
        
        # 读取音频数据
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="音频文件为空")
        
        # 检查文件大小（最大50MB）
        if len(audio_data) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="音频文件过大，请上传小于50MB的文件")
        
        # 生成检测ID
        detection_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 进行情绪检测
        emotion_result = await emotion_service.detect_emotion(
            audio_data=audio_data,
            employee_id=employee_id
        )
        
        # 更新处理时间
        processing_time = time.time() - start_time
        emotion_result.processing_time = processing_time
        
        # 构建响应
        response = EmotionDetectionResponse(
            success=True,
            emotion_feature=emotion_result,
            message="情绪检测完成",
            error_code=None
        )
        
        # 后台任务：保存检测结果到数据库
        background_tasks.add_task(
            save_emotion_detection,
            detection_id=detection_id,
            employee_id=employee_id,
            meeting_id=meeting_id,
            emotion_result=emotion_result,
            current_user_id=current_user.user_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Emotion detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"情绪检测失败: {str(e)}")


@router.post("/detect/batch", response_model=EmotionBatchResponse)
async def batch_detect_emotion(
    background_tasks: BackgroundTasks,
    audio_files: List[UploadFile] = File(...),
    employee_id: Optional[int] = Form(None),
    meeting_id: Optional[int] = Form(None),
    require_analysis: bool = Form(True),
    current_user: UserModel = Depends(get_current_user)
):
    """批量检测情绪"""
    try:
        # 检查模型状态
        if not await emotion_service.check_model_status():
            raise HTTPException(status_code=503, detail="情绪识别服务未就绪")
        
        # 验证文件数量
        if len(audio_files) > 10:
            raise HTTPException(status_code=400, detail="批量检测最多支持10个文件")
        
        # 验证文件类型
        for audio_file in audio_files:
            if not audio_file.content_type.startswith('audio/'):
                raise HTTPException(status_code=400, detail=f"文件 {audio_file.filename} 不是音频文件")
        
        start_time = time.time()
        results = []
        
        # 处理每个音频文件
        for i, audio_file in enumerate(audio_files):
            try:
                audio_data = await audio_file.read()
                
                if len(audio_data) == 0:
                    results.append(EmotionDetectionResponse(
                        success=False,
                        emotion_feature=None,
                        message=f"文件 {audio_file.filename} 为空",
                        error_code="EMPTY_FILE"
                    ))
                    continue
                
                # 进行情绪检测
                emotion_result = await emotion_service.detect_emotion(
                    audio_data=audio_data,
                    employee_id=employee_id
                )
                
                results.append(EmotionDetectionResponse(
                    success=True,
                    emotion_feature=emotion_result,
                    message=f"文件 {audio_file.filename} 检测完成",
                    error_code=None
                ))
                
            except Exception as e:
                logger.error(f"Failed to process audio {audio_file.filename}: {e}")
                results.append(EmotionDetectionResponse(
                    success=False,
                    emotion_feature=None,
                    message=f"文件 {audio_file.filename} 处理失败: {str(e)}",
                    error_code="PROCESSING_ERROR"
                ))
        
        # 计算统计信息
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r.success)
        
        response = EmotionBatchResponse(
            success=success_count > 0,
            results=results,
            total_count=len(audio_files),
            success_count=success_count,
            processing_time=total_time
        )
        
        # 后台任务：保存批量检测结果
        background_tasks.add_task(
            save_batch_emotion_detections,
            results=results,
            employee_id=employee_id,
            meeting_id=meeting_id,
            current_user_id=current_user.user_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch emotion detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"批量情绪检测失败: {str(e)}")


@router.post("/feedback/{detection_id}")
async def submit_emotion_feedback(
    detection_id: str,
    feedback: EmotionFeedback,
    current_user: UserModel = Depends(get_current_user)
):
    """提交情绪检测反馈"""
    try:
        async with get_db() as db:
            # 检查检测记录是否存在
            from sqlalchemy import select
            stmt = select(EmotionDetectionModel).where(
                EmotionDetectionModel.detection_id == detection_id
            )
            result = await db.execute(stmt)
            detection = result.scalar_one_or_none()
            
            if not detection:
                raise HTTPException(status_code=404, detail="检测记录不存在")
            
            # 创建反馈记录
            feedback_model = EmotionFeedbackModel(
                detection_id=detection_id,
                user_emotion=feedback.user_emotion,
                accuracy_rating=feedback.accuracy_rating,
                comments=feedback.comments,
                created_at=feedback.timestamp
            )
            
            # 分析反馈
            if feedback.user_emotion:
                feedback_model.is_accurate = (
                    feedback.user_emotion.lower() == detection.dominant_emotion.lower()
                )
                if not feedback_model.is_accurate:
                    feedback_model.emotion_discrepancy = (
                        f"检测: {detection.dominant_emotion}, 用户: {feedback.user_emotion}"
                    )
            
            db.add(feedback_model)
            await db.commit()
            
            logger.info(f"Emotion feedback submitted for detection {detection_id}")
            
            return {"message": "反馈提交成功", "feedback_id": feedback_model.id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit emotion feedback: {e}")
        raise HTTPException(status_code=500, detail="反馈提交失败")


@router.get("/statistics", response_model=EmotionStatistics)
async def get_emotion_statistics(
    employee_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user)
):
    """获取情绪检测统计信息"""
    try:
        async with get_db() as db:
            from sqlalchemy import select, func, and_
            
            # 构建查询条件
            conditions = []
            if employee_id:
                conditions.append(EmotionDetectionModel.employee_id == employee_id)
            if start_date:
                conditions.append(EmotionDetectionModel.created_at >= start_date)
            if end_date:
                conditions.append(EmotionDetectionModel.created_at <= end_date)
            
            # 基础统计
            base_query = select(
                func.count(EmotionDetectionModel.id).label('total_detections'),
                func.sum(func.cast(EmotionDetectionModel.is_success, int)).label('successful_detections'),
                func.avg(EmotionDetectionModel.confidence_score).label('avg_confidence'),
                func.avg(EmotionDetectionModel.processing_time).label('avg_processing_time')
            )
            
            if conditions:
                base_query = base_query.where(and_(*conditions))
            
            result = await db.execute(base_query)
            stats = result.first()
            
            # 计算错误率
            total = stats.total_detections or 0
            successful = stats.successful_detections or 0
            error_rate = (total - successful) / total if total > 0 else 0.0
            
            # 情绪频率统计
            emotion_freq_query = select(
                EmotionDetectionModel.dominant_emotion,
                func.count(EmotionDetectionModel.id).label('count')
            )
            
            if conditions:
                emotion_freq_query = emotion_freq_query.where(and_(*conditions))
            
            emotion_freq_query = emotion_freq_query.group_by(
                EmotionDetectionModel.dominant_emotion
            )
            
            freq_result = await db.execute(emotion_freq_query)
            emotion_frequency = {row.dominant_emotion: row.count for row in freq_result}
            
            # 质量分布统计
            quality_distribution = {"high": 0, "medium": 0, "low": 0}
            
            quality_query = select(EmotionDetectionModel.audio_quality_score)
            if conditions:
                quality_query = quality_query.where(and_(*conditions))
            
            quality_result = await db.execute(quality_query)
            for row in quality_result:
                score = row.audio_quality_score
                if score >= 0.8:
                    quality_distribution["high"] += 1
                elif score >= 0.5:
                    quality_distribution["medium"] += 1
                else:
                    quality_distribution["low"] += 1
            
            # 模型性能指标
            model_performance = {
                "average_confidence": float(stats.avg_confidence or 0.0),
                "average_processing_time": float(stats.avg_processing_time or 0.0),
                "success_rate": successful / total if total > 0 else 0.0,
                "error_rate": error_rate
            }
            
            # 处理时间统计
            processing_query = select(
                func.min(EmotionDetectionModel.processing_time).label('min_time'),
                func.max(EmotionDetectionModel.processing_time).label('max_time'),
                func.avg(EmotionDetectionModel.processing_time).label('avg_time')
            )
            
            if conditions:
                processing_query = processing_query.where(and_(*conditions))
            
            processing_result = await db.execute(processing_query)
            processing_stats = processing_result.first()
            
            processing_time_stats = {
                "min": float(processing_stats.min_time or 0.0),
                "max": float(processing_stats.max_time or 0.0),
                "average": float(processing_stats.avg_time or 0.0)
            }
            
            return EmotionStatistics(
                total_detections=total,
                successful_detections=successful,
                average_confidence=float(stats.avg_confidence or 0.0),
                emotion_frequency=emotion_frequency,
                quality_distribution=quality_distribution,
                model_performance=model_performance,
                processing_time_stats=processing_time_stats,
                error_rate=error_rate
            )
            
    except Exception as e:
        logger.error(f"Failed to get emotion statistics: {e}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")


@router.get("/history/{employee_id}")
async def get_emotion_history(
    employee_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: UserModel = Depends(get_current_user)
):
    """获取员工情绪检测历史"""
    try:
        async with get_db() as db:
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            
            stmt = (
                select(EmotionDetectionModel)
                .options(selectinload(EmotionDetectionModel.feedbacks))
                .where(EmotionDetectionModel.employee_id == employee_id)
                .order_by(EmotionDetectionModel.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            
            result = await db.execute(stmt)
            detections = result.scalars().all()
            
            history = []
            for detection in detections:
                feedbacks = [
                    {
                        "user_emotion": fb.user_emotion,
                        "accuracy_rating": fb.accuracy_rating,
                        "comments": fb.comments,
                        "is_accurate": fb.is_accurate,
                        "created_at": fb.created_at.isoformat() if fb.created_at else None
                    }
                    for fb in detection.feedbacks
                ]
                
                history.append({
                    "detection_id": detection.detection_id,
                    "dominant_emotion": detection.dominant_emotion,
                    "confidence": detection.confidence_score,
                    "intensity": detection.intensity,
                    "complexity": detection.complexity,
                    "quality_score": detection.audio_quality_score,
                    "audio_url": detection.audio_url,
                    "processing_time": detection.processing_time,
                    "created_at": detection.created_at.isoformat() if detection.created_at else None,
                    "feedbacks": feedbacks
                })
            
            return {
                "employee_id": employee_id,
                "history": history,
                "total_count": len(history)
            }
            
    except Exception as e:
        logger.error(f"Failed to get emotion history: {e}")
        raise HTTPException(status_code=500, detail="获取情绪历史失败")


@router.get("/model/status")
async def get_emotion_model_status():
    """获取情绪识别模型状态"""
    try:
        model_status = await emotion_service.check_model_status()
        
        return {
            "model_loaded": model_status,
            "service_status": "online" if model_status else "offline",
            "supported_emotions": [
                "neutral", "happy", "sad", "angry", 
                "fear", "disgust", "surprise"
            ],
            "max_file_size": "50MB",
            "supported_formats": ["audio/wav", "audio/mp3", "audio/m4a", "audio/ogg"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail="获取模型状态失败")


# 后台任务函数
async def save_emotion_detection(
    detection_id: str,
    employee_id: Optional[int],
    meeting_id: Optional[int],
    emotion_result,
    current_user_id: int
):
    """保存情绪检测结果到数据库"""
    try:
        async with get_db() as db:
            detection_model = EmotionDetectionModel(
                detection_id=detection_id,
                employee_id=employee_id,
                meeting_id=meeting_id,
                dominant_emotion=emotion_result.dominant_emotion,
                confidence_score=emotion_result.confidence,
                emotion_probabilities=emotion_result.emotion_probabilities,
                intensity=emotion_result.intensity,
                complexity=emotion_result.complexity,
                audio_url=emotion_result.audio_url,
                audio_duration=emotion_result.audio_duration,
                audio_quality_score=emotion_result.quality_score,
                emotion_analysis=emotion_result.analysis,
                model_name=emotion_result.model_name,
                processing_time=emotion_result.processing_time,
                is_success=True
            )
            
            db.add(detection_model)
            await db.commit()
            
    except Exception as e:
        logger.error(f"Failed to save emotion detection: {e}")


async def save_batch_emotion_detections(
    results: List[EmotionDetectionResponse],
    employee_id: Optional[int],
    meeting_id: Optional[int],
    current_user_id: int
):
    """保存批量情绪检测结果"""
    for result in results:
        if result.success and result.emotion_feature:
            detection_id = str(uuid.uuid4())
            await save_emotion_detection(
                detection_id=detection_id,
                employee_id=employee_id,
                meeting_id=meeting_id,
                emotion_result=result.emotion_feature,
                current_user_id=current_user_id
            )