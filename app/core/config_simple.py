"""
简化配置类 - 不依赖pydantic
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SimpleSettings:
    """简化的配置类"""
    
    def __init__(self):
        # 应用基础配置
        self.APP_NAME = os.getenv("APP_NAME", "声纹识别系统")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.WORKERS = int(os.getenv("WORKERS", "1"))
        
        # 数据库配置
        self.DATABASE_URL = os.getenv("DATABASE_URL", "mysql+asyncmy://voiceprint:password@localhost:3306/voiceprint_system")
        
        # MinIO配置
        self.MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.MINIO_BUCKET = os.getenv("MINIO_BUCKET", "voiceprint-audio")
        self.MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        # 声纹识别配置
        self.VOICEPRINT_MODEL = os.getenv("VOICEPRINT_MODEL", "speechbrain/spkrec-ecapa-voxceleb")
        self.VOICEPRINT_THRESHOLD = float(os.getenv("VOICEPRINT_THRESHOLD", "0.75"))
        self.AUDIO_QUALITY_THRESHOLD = float(os.getenv("AUDIO_QUALITY_THRESHOLD", "0.6"))
        self.MIN_AUDIO_DURATION = float(os.getenv("MIN_AUDIO_DURATION", "3.0"))
        self.MAX_AUDIO_DURATION = float(os.getenv("MAX_AUDIO_DURATION", "30.0"))
        self.SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
        
        # 情绪识别配置
        self.EMOTION_MODEL = os.getenv("EMOTION_MODEL", "speechbrain/emotion-recognition-wav2vec2-IEMOCAP")
        self.EMOTION_CONFIDENCE_THRESHOLD = float(os.getenv("EMOTION_CONFIDENCE_THRESHOLD", "0.6"))
        self.SUPPORTED_EMOTIONS = os.getenv("SUPPORTED_EMOTIONS", "neutral,happy,sad,angry,fear,disgust,surprise")
        self.EMOTION_ANALYSIS_ENABLED = os.getenv("EMOTION_ANALYSIS_ENABLED", "true").lower() == "true"
        
        # 微信配置
        self.WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")
        self.WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")
        
        # JWT配置
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30 * 24 * 60"))  # 30天
        
        # 文件上传配置
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
        self.TEMP_DIR = os.getenv("TEMP_DIR", "temp")
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "50 * 1024 * 1024"))  # 50MB
        
        # Redis配置
        self.REDIS_URL = os.getenv("REDIS_URL")
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    
    @property
    def SUPPORTED_EMOTIONS_LIST(self) -> List[str]:
        """获取支持的情绪列表"""
        if isinstance(self.SUPPORTED_EMOTIONS, str):
            return [emotion.strip() for emotion in self.SUPPORTED_EMOTIONS.split(",") if emotion.strip()]
        elif isinstance(self.SUPPORTED_EMOTIONS, list):
            return self.SUPPORTED_EMOTIONS
        else:
            return ["neutral", "happy", "sad", "angry", "fear", "disgust", "surprise"]
    
    @property
    def minio_url(self) -> str:
        """获取MinIO访问URL"""
        protocol = "https" if self.MINIO_SECURE else "http"
        return f"{protocol}://{self.MINIO_ENDPOINT}"

# 创建全局设置实例
simple_settings = SimpleSettings()