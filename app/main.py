from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uvicorn
from loguru import logger
import os

from app.core.config import settings
from app.models.database import engine, Base
from app.core.minio_client import minio_client
from app.routers import emotion, auth, employee, voiceprint, meeting, speech, upload, system
from app.core.exceptions import VoiceprintException
from app.services.voiceprint_service import VoiceprintService
from app.services.emotion_service import EmotionService
from app.utils.audio_compat import check_audio_backend


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting Voice Recognition System...")
    
    # 创建数据库表
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    # 初始化MinIO桶
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET):
            minio_client.make_bucket(settings.MINIO_BUCKET)
            logger.info(f"MinIO bucket '{settings.MINIO_BUCKET}' created")
        else:
            logger.info(f"MinIO bucket '{settings.MINIO_BUCKET}' already exists")
    except Exception as e:
        logger.error(f"Failed to initialize MinIO: {e}")
        raise
    
    # 设置Hugging Face镜像（如果在中国大陆）
    if os.getenv("USE_HF_MIRROR", "false").lower() == "true":
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        logger.info("Using Hugging Face mirror: https://hf-mirror.com")
    
    # 验证音频处理栈兼容性
    from app.utils.audio_compat import verify_audio_stack
    verify_audio_stack()
    
    # 预加载声纹识别模型
    voiceprint_model_loaded = await VoiceprintService.initialize_model()
    if voiceprint_model_loaded:
        logger.info("Voiceprint model initialized successfully")
    else:
        logger.warning("Voiceprint recognition will be unavailable - run download script to get models")
    
    # 预加载情绪识别模型
    emotion_model_loaded = await EmotionService.initialize_model()
    if emotion_model_loaded:
        logger.info("Emotion recognition model initialized successfully")
    else:
        logger.warning("Emotion recognition will be unavailable - run download script to get models")
    
    # 创建必要的目录
    for directory in [settings.UPLOAD_DIR, settings.TEMP_DIR, "logs"]:
        os.makedirs(directory, exist_ok=True)
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down Voice Recognition System...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="企业级声纹识别系统 - 基于开源技术的解决方案",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加受信任主机中间件
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # 生产环境应该设置具体主机
    )


# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录请求日志
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s - "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )
    
    return response


# 全局异常处理
@app.exception_handler(VoiceprintException)
async def voiceprint_exception_handler(request: Request, exc: VoiceprintException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


# 健康检查
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        # 检查MinIO连接
        minio_client.list_buckets()
        
        # 检查声纹模型
        voiceprint_service = VoiceprintService()
        vp_model_status = await voiceprint_service.check_model_status()
        
        # 检查情绪识别模型
        emotion_service = EmotionService()
        emo_model_status = await emotion_service.check_model_status()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.APP_VERSION,
            "services": {
                "database": "healthy",
                "minio": "healthy",
                "voiceprint_model": "healthy" if vp_model_status else "unavailable",
                "emotion_model": "healthy" if emo_model_status else "unavailable"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


# 根路径
@app.get("/", tags=["Root"])
async def root():
    """根路径信息"""
    return {
        "message": "声纹识别系统API",
        "version": settings.APP_VERSION,
        "docs_url": "/docs" if settings.DEBUG else None,
        "status": "running"
    }


# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(employee.router, prefix="/api/employee", tags=["员工管理"])
app.include_router(voiceprint.router, prefix="/api/voiceprint", tags=["声纹管理"])
app.include_router(meeting.router, prefix="/api/meeting", tags=["会议管理"])
app.include_router(speech.router, prefix="/api/speech", tags=["语音识别"])
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])
app.include_router(emotion.router, prefix="/api/emotion", tags=["情绪识别"])
app.include_router(system.router, prefix="/api/system", tags=["系统管理"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
        log_level="info"
    )