from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class VoiceprintFeature(BaseModel):
    """声纹特征模型"""
    embedding: List[float] = Field(..., description="声纹嵌入向量")
    model_name: str = Field(..., description="使用的模型名称")
    sample_rate: int = Field(default=16000, description="音频采样率")
    duration: float = Field(..., description="音频时长(秒)")
    quality_score: float = Field(..., ge=0, le=1, description="音频质量评分")
    embedding_version: Optional[str] = Field(default="v1.0", description="嵌入版本")


class VoiceprintMatch(BaseModel):
    """声纹匹配结果"""
    success: bool = Field(..., description="是否识别成功")
    voiceprint_id: Optional[str] = Field(None, description="匹配的声纹ID")
    employee_id: Optional[int] = Field(None, description="匹配的员工ID")
    confidence: float = Field(..., ge=0, le=1, description="匹配置信度")
    threshold: float = Field(..., description="匹配阈值")
    audio_url: str = Field(..., description="音频文件URL")
    all_matches: List[Dict[str, Any]] = Field(default=[], description="所有匹配结果")
    processing_time: float = Field(default=0, description="处理耗时(毫秒)")


class VoiceprintRegisterRequest(BaseModel):
    """声纹注册请求"""
    employee_id: int = Field(..., description="员工ID")
    sample_index: int = Field(..., ge=1, le=5, description="样本索引")


class VoiceprintRegisterResponse(BaseModel):
    """声纹注册响应"""
    success: bool = Field(True, description="操作是否成功")
    voiceprint_id: str = Field(..., description="声纹ID")
    sample_index: int = Field(..., description="样本索引")
    message: str = Field(..., description="响应消息")


class VoiceprintRecognizeRequest(BaseModel):
    """声纹识别请求"""
    meeting_id: Optional[int] = Field(None, description="会议ID")


class VoiceprintRecognizeResponse(BaseModel):
    """声纹识别响应"""
    success: bool = Field(..., description="识别是否成功")
    confidence: float = Field(..., ge=0, le=1, description="匹配置信度")
    threshold: float = Field(..., description="匹配阈值")
    identified_employee: Optional[Dict[str, Any]] = Field(None, description="识别的员工信息")
    audio_url: str = Field(..., description="音频文件URL")
    processing_time: float = Field(..., description="处理耗时(毫秒)")
    all_matches: List[Dict[str, Any]] = Field(default=[], description="所有匹配结果")


class VoiceprintStatusResponse(BaseModel):
    """声纹状态响应"""
    employee_id: int = Field(..., description="员工ID")
    employee_name: str = Field(..., description="员工姓名")
    registered_count: int = Field(..., description="已注册样本数量")
    required_count: int = Field(..., description="需要的样本数量")
    is_complete: bool = Field(..., description="是否完成注册")
    voiceprints: List[Dict[str, Any]] = Field(..., description="声纹样本列表")


class VoiceprintDeleteResponse(BaseModel):
    """声纹删除响应"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field(..., description="响应消息")


class VoiceprintStats(BaseModel):
    """声纹统计"""
    total_employees: int = Field(..., description="总员工数")
    registered_employees: int = Field(..., description="已注册员工数")
    total_voiceprints: int = Field(..., description="总声纹数")
    avg_quality_score: float = Field(..., description="平均质量评分")
    registration_rate: float = Field(..., description="注册率")


class VoiceprintQualityAnalysis(BaseModel):
    """声纹质量分析"""
    voiceprint_id: str = Field(..., description="声纹ID")
    duration: float = Field(..., description="音频时长")
    signal_to_noise_ratio: float = Field(..., description="信噪比(dB)")
    zero_crossing_rate: float = Field(..., description="过零率")
    spectral_centroid: float = Field(..., description="频谱重心")
    spectral_bandwidth: float = Field(..., description="频谱带宽")
    spectral_rolloff: float = Field(..., description="频谱滚降点")
    mfcc_stats: Dict[str, float] = Field(..., description="MFCC统计信息")
    quality_score: float = Field(..., description="综合质量评分")
    quality_level: str = Field(..., description="质量等级")
    is_suitable: bool = Field(..., description="是否适合声纹提取")


class RecognitionLogResponse(BaseModel):
    """识别日志响应"""
    id: int
    employee_id: Optional[int]
    audio_url: Optional[str]
    audio_duration: Optional[float]
    matched_voiceprint_id: Optional[str]
    confidence_score: float
    threshold_used: float
    is_success: bool
    processing_time: Optional[float]
    model_version: Optional[str]
    top_candidates: Optional[List[Dict[str, Any]]]
    error_message: Optional[str]
    created_at: datetime


class RecognitionStatsResponse(BaseModel):
    """识别统计响应"""
    total_recognitions: int = Field(..., description="总识别次数")
    successful_recognitions: int = Field(..., description="成功识别次数")
    success_rate: float = Field(..., description="识别成功率")
    avg_confidence: float = Field(..., description="平均置信度")
    avg_processing_time: float = Field(..., description="平均处理时间")
    today_recognitions: int = Field(..., description="今日识别次数")
    accuracy_by_threshold: Dict[str, float] = Field(..., description="不同阈值下的准确率")


class VoiceprintComparison(BaseModel):
    """声纹对比"""
    voiceprint1_id: str = Field(..., description="声纹1 ID")
    voiceprint2_id: str = Field(..., description="声纹2 ID")
    similarity: float = Field(..., ge=0, le=1, description="相似度")
    is_same_person: bool = Field(..., description="是否为同一人")
    confidence: float = Field(..., ge=0, le=1, description="判断置信度")


class BatchRecognitionRequest(BaseModel):
    """批量识别请求"""
    meeting_id: Optional[int] = Field(None, description="会议ID")
    audio_files: List[str] = Field(..., description="音频文件列表")


class BatchRecognitionResponse(BaseModel):
    """批量识别响应"""
    total_files: int = Field(..., description="总文件数")
    successful_recognitions: int = Field(..., description="成功识别数")
    failed_recognitions: int = Field(..., description="失败识别数")
    results: List[VoiceprintRecognizeResponse] = Field(..., description="识别结果列表")
    processing_time: float = Field(..., description="总处理时间")


class VoiceprintUpdateRequest(BaseModel):
    """声纹更新请求"""
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="质量评分")
    is_active: Optional[bool] = Field(None, description="是否激活")


class VoiceprintUpdateResponse(BaseModel):
    """声纹更新响应"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field(..., description="响应消息")
    updated_fields: List[str] = Field(..., description="更新的字段列表")