import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError as e:
        raise ImportError("需要安装 pydantic-settings: pip install pydantic-settings") from e

from typing import Optional, List

try:
    from pydantic import field_validator
except ImportError:
    try:
        from pydantic import validator as field_validator
    except ImportError:
        # 如果都没有，定义一个空的装饰器
        def field_validator(field_name, mode='before'):
            def decorator(func):
                return func
            return decorator


class Settings(BaseSettings):
    """应用配置"""
    
    @property
    def SUPPORTED_EMOTIONS_LIST(self) -> List[str]:
        """获取支持的情绪列表（处理字符串和列表两种格式）"""
        raw_value = getattr(self, 'SUPPORTED_EMOTIONS', [])
        if isinstance(raw_value, str):
            return [emotion.strip() for emotion in raw_value.split(",") if emotion.strip()]
        elif isinstance(raw_value, list):
            return raw_value
        else:
            return ["neutral", "happy", "sad", "angry", "fear", "disgust", "surprise"]
    
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
    SUPPORTED_EMOTIONS: str = "neutral,happy,sad,angry,fear,disgust,surprise"
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
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    @property
    def minio_url(self) -> str:
        """获取MinIO访问URL"""
        protocol = "https" if self.MINIO_SECURE else "http"
        return f"{protocol}://{self.MINIO_ENDPOINT}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 允许额外的字段


# 创建全局设置实例
settings = Settings()