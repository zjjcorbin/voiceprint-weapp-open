from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class EmotionResult(BaseModel):
    """情绪识别结果"""
    success: bool = Field(..., description="识别是否成功")
    emotion: str = Field(..., description="识别出的情绪")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    message: str = Field(..., description="结果消息")
    processing_time: float = Field(..., ge=0, description="处理时间（秒）")
    timestamp: str = Field(..., description="识别时间戳")


class EmotionFeature(BaseModel):
    """情绪特征"""
    model_config = {'protected_namespaces': ()}
    
    dominant_emotion: str = Field(..., description="主要情绪")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    emotion_probabilities: Dict[str, float] = Field(..., description="各情绪概率分布")
    intensity: float = Field(..., ge=0.0, le=1.0, description="情绪强度")
    complexity: float = Field(..., ge=0.0, le=1.0, description="情绪复杂度")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="音频质量评分")
    analysis: Dict[str, Any] = Field(default_factory=dict, description="情绪分析详情")
    audio_url: Optional[str] = Field(None, description="音频文件URL")
    audio_duration: float = Field(..., gt=0, description="音频时长（秒）")
    model_name: str = Field(..., description="使用的模型名称")
    processing_time: float = Field(..., ge=0, description="处理时间（秒）")


class EmotionDetectionRequest(BaseModel):
    """情绪检测请求"""
    employee_id: Optional[int] = Field(None, description="员工ID")
    meeting_id: Optional[int] = Field(None, description="会议ID")
    audio_data: bytes = Field(..., description="音频数据")
    require_analysis: bool = Field(True, description="是否需要详细分析")


class EmotionDetectionResponse(BaseModel):
    """情绪检测响应"""
    success: bool = Field(..., description="是否成功")
    emotion_feature: Optional[EmotionFeature] = Field(None, description="情绪特征")
    message: str = Field(..., description="响应消息")
    error_code: Optional[str] = Field(None, description="错误代码")


class EmotionBatchRequest(BaseModel):
    """批量情绪检测请求"""
    employee_id: Optional[int] = Field(None, description="员工ID")
    meeting_id: Optional[int] = Field(None, description="会议ID")
    audio_files: List[bytes] = Field(..., min_items=1, max_items=10, description="音频文件列表")
    require_analysis: bool = Field(True, description="是否需要详细分析")


class EmotionBatchResponse(BaseModel):
    """批量情绪检测响应"""
    success: bool = Field(..., description="是否成功")
    results: List[EmotionDetectionResponse] = Field(..., description="检测结果列表")
    total_count: int = Field(..., description="总检测数量")
    success_count: int = Field(..., description="成功检测数量")
    processing_time: float = Field(..., ge=0, description="总处理时间（秒）")


class EmotionAnalysis(BaseModel):
    """情绪分析结果"""
    employee_id: int = Field(..., description="员工ID")
    meeting_id: Optional[int] = Field(None, description="会议ID")
    emotion_trends: List[Dict[str, Any]] = Field(..., description="情绪趋势")
    emotion_distribution: Dict[str, float] = Field(..., description="情绪分布")
    average_intensity: float = Field(..., ge=0.0, le=1.0, description="平均情绪强度")
    emotional_stability: float = Field(..., ge=0.0, le=1.0, description="情绪稳定性")
    peak_emotions: List[Dict[str, Any]] = Field(..., description="情绪峰值")
    analysis_period: Dict[str, str] = Field(..., description="分析时间段")


class EmotionSummary(BaseModel):
    """情绪汇总"""
    date: str = Field(..., description="日期")
    employee_count: int = Field(..., description="员工数量")
    total_detections: int = Field(..., description="总检测次数")
    emotion_distribution: Dict[str, int] = Field(..., description="情绪分布统计")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="平均置信度")
    quality_distribution: Dict[str, int] = Field(..., description="音频质量分布")


class EmotionFeedback(BaseModel):
    """情绪反馈"""
    detection_id: str = Field(..., description="检测ID")
    user_emotion: str = Field(..., description="用户自评情绪")
    accuracy_rating: int = Field(..., ge=1, le=5, description="准确度评分(1-5)")
    comments: Optional[str] = Field(None, description="评论")
    timestamp: str = Field(..., description="反馈时间")


class EmotionInsight(BaseModel):
    """情绪洞察"""
    employee_id: int = Field(..., description="员工ID")
    period: str = Field(..., description="分析周期")
    emotional_patterns: List[Dict[str, Any]] = Field(..., description="情绪模式")
    triggers: List[str] = Field(..., description="情绪触发因素")
    recommendations: List[str] = Field(..., description="建议")
    mood_trend: str = Field(..., description="情绪趋势")
    stress_indicators: List[Dict[str, Any]] = Field(..., description="压力指标")


class EmotionComparison(BaseModel):
    """情绪对比"""
    employee_id: int = Field(..., description="员工ID")
    baseline_emotion: Dict[str, float] = Field(..., description="基线情绪")
    current_emotion: Dict[str, float] = Field(..., description="当前情绪")
    changes: Dict[str, float] = Field(..., description="情绪变化")
    significant_changes: List[str] = Field(..., description="显著变化")
    comparison_period: str = Field(..., description="对比周期")


class EmotionAlert(BaseModel):
    """情绪预警"""
    employee_id: int = Field(..., description="员工ID")
    alert_type: str = Field(..., description="预警类型")
    severity: str = Field(..., description="严重程度")
    emotion_state: Dict[str, float] = Field(..., description="情绪状态")
    duration: int = Field(..., description="持续时间（分钟）")
    threshold_exceeded: List[str] = Field(..., description="超出阈值的指标")
    recommendations: List[str] = Field(..., description="建议措施")
    created_at: str = Field(..., description="创建时间")


class EmotionStatistics(BaseModel):
    """情绪统计"""
    total_detections: int = Field(..., description="总检测次数")
    successful_detections: int = Field(..., description="成功检测次数")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="平均置信度")
    emotion_frequency: Dict[str, int] = Field(..., description="情绪频率统计")
    quality_distribution: Dict[str, int] = Field(..., description="质量分布")
    model_performance: Dict[str, float] = Field(..., description="模型性能指标")
    processing_time_stats: Dict[str, float] = Field(..., description="处理时间统计")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="错误率")