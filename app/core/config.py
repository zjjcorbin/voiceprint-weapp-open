import os
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """应用配置"""
    
    from pydantic import field_validator
    
    @field_validator('SUPPORTED_EMOTIONS', mode='before')
    @classmethod
    def parse_supported_emotions(cls, v):
        """验证并转换SUPPORTED_EMOTIONS字段值"""
        if isinstance(v, str):
            # 如果是字符串，按逗号分割
            return [emotion.strip() for emotion in v.split(",") if emotion.strip()]
        elif isinstance(v, list):
            return v
        else:
            raise ValueError("SUPPORTED_EMOTIONS must be a string or list")
    
    # 应用基础配置
    APP_NAME: str = "声纹识别系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # 数据库配置
    DATABASE_URL: str = "mysql+asyncmy://voiceprint:password@localhost:3306/voiceprint_system"
    
    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "voiceprint-audio"
    MINIO_SECURE: bool = False
    
    # 声纹识别配置
    VOICEPRINT_MODEL: str = "speechbrain/spkrec-ecapa-voxceleb"
    VOICEPRINT_THRESHOLD: float = 0.75
    AUDIO_QUALITY_THRESHOLD: float = 0.6
    MIN_AUDIO_DURATION: float = 3.0
    MAX_AUDIO_DURATION: float = 30.0
    SAMPLE_RATE: int = 16000
    
    # 情绪识别配置
    EMOTION_MODEL: str = "speechbrain/emotion-recognition-wav2vec2-IEMOCAP"
    EMOTION_CONFIDENCE_THRESHOLD: float = 0.6
    SUPPORTED_EMOTIONS: list[str] = ["neutral", "happy", "sad", "angry", "fear", "disgust", "surprise"]
    EMOTION_ANALYSIS_ENABLED: bool = True
    
    # 微信配置
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Redis配置 (可选)
    REDIS_URL: Optional[str] = None
    
    @property
    def minio_url(self) -> str:
        """获取MinIO访问URL"""
        protocol = "https" if self.MINIO_SECURE else "http"
        return f"{protocol}://{self.MINIO_ENDPOINT}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()