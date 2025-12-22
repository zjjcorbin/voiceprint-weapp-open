from fastapi import HTTPException


class VoiceprintException(Exception):
    """声纹识别系统异常"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "VOICEPRINT_ERROR",
        details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AudioProcessingError(VoiceprintException):
    """音频处理异常"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="AUDIO_PROCESSING_ERROR",
            details=details
        )


class ModelNotInitializedError(VoiceprintException):
    """模型未初始化异常"""
    
    def __init__(self, model_name: str):
        super().__init__(
            message=f"模型 {model_name} 未初始化",
            status_code=503,
            error_code="MODEL_NOT_INITIALIZED"
        )


class VoiceprintNotFoundError(VoiceprintException):
    """声纹未找到异常"""
    
    def __init__(self, message: str = "声纹未找到"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="VOICEPRINT_NOT_FOUND"
        )


class AuthenticationError(VoiceprintException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(VoiceprintException):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class DatabaseError(VoiceprintException):
    """数据库异常"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details
        )


class StorageError(VoiceprintException):
    """存储异常"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="STORAGE_ERROR",
            details=details
        )


class ValidationError(VoiceprintException):
    """数据验证异常"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


class RateLimitError(VoiceprintException):
    """频率限制异常"""
    
    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class EmotionDetectionError(VoiceprintException):
    """情绪检测异常"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="EMOTION_DETECTION_ERROR",
            details=details
        )