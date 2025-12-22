from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class EmotionDetectionModel(Base):
    """情绪检测记录模型"""
    __tablename__ = "emotion_detections"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    detection_id = Column(String(64), unique=True, index=True, comment="检测唯一ID")
    
    # 关联信息
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True, comment="员工ID")
    meeting_id = Column(Integer, ForeignKey("meetings.meeting_id"), nullable=True, comment="会议ID")
    
    # 情绪检测结果
    dominant_emotion = Column(String(50), nullable=False, comment="主要情绪")
    confidence_score = Column(Float, nullable=False, comment="置信度")
    emotion_probabilities = Column(JSON, nullable=False, comment="各情绪概率分布")
    intensity = Column(Float, nullable=False, comment="情绪强度")
    complexity = Column(Float, nullable=False, comment="情绪复杂度")
    
    # 音频信息
    audio_url = Column(Text, nullable=True, comment="音频文件URL")
    audio_duration = Column(Float, nullable=False, comment="音频时长（秒）")
    audio_quality_score = Column(Float, nullable=False, comment="音频质量评分")
    
    # 分析结果
    emotion_analysis = Column(JSON, nullable=True, comment="详细情绪分析")
    
    # 技术信息
    model_name = Column(String(200), nullable=False, comment="使用的模型名称")
    model_version = Column(String(50), nullable=True, comment="模型版本")
    processing_time = Column(Float, nullable=False, comment="处理时间（秒）")
    
    # 状态信息
    is_success = Column(Boolean, nullable=False, default=True, comment="是否成功")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    employee = relationship("EmployeeModel", back_populates="emotion_detections")
    meeting = relationship("MeetingModel", back_populates="emotion_detections")
    
    # 反向关系
    feedbacks = relationship("EmotionFeedbackModel", back_populates="detection", cascade="all, delete-orphan")


class EmotionFeedbackModel(Base):
    """情绪检测反馈模型"""
    __tablename__ = "emotion_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联检测记录
    detection_id = Column(String(64), ForeignKey("emotion_detections.detection_id"), nullable=False, comment="检测ID")
    
    # 用户反馈
    user_emotion = Column(String(50), nullable=True, comment="用户自评情绪")
    accuracy_rating = Column(Integer, nullable=True, comment="准确度评分(1-5)")
    comments = Column(Text, nullable=True, comment="评论")
    
    # 反馈分析
    is_accurate = Column(Boolean, nullable=True, comment="是否准确")
    emotion_discrepancy = Column(String(50), nullable=True, comment="情绪差异")
    improvement_suggestions = Column(Text, nullable=True, comment="改进建议")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="反馈时间")
    
    # 关系
    detection = relationship("EmotionDetectionModel", back_populates="feedbacks")


class EmotionSummaryModel(Base):
    """情绪汇总模型"""
    __tablename__ = "emotion_summaries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 汇总信息
    summary_date = Column(String(10), nullable=False, index=True, comment="汇总日期")
    summary_type = Column(String(20), nullable=False, comment="汇总类型(daily/weekly/monthly)")
    
    # 统计数据
    employee_count = Column(Integer, nullable=False, default=0, comment="员工数量")
    total_detections = Column(Integer, nullable=False, default=0, comment="总检测次数")
    successful_detections = Column(Integer, nullable=False, default=0, comment="成功检测次数")
    
    # 情绪统计
    emotion_distribution = Column(JSON, nullable=False, comment="情绪分布统计")
    average_confidence = Column(Float, nullable=False, default=0.0, comment="平均置信度")
    average_intensity = Column(Float, nullable=False, default=0.0, comment="平均情绪强度")
    average_complexity = Column(Float, nullable=False, default=0.0, comment="平均情绪复杂度")
    
    # 质量统计
    quality_distribution = Column(JSON, nullable=False, comment="音频质量分布")
    
    # 模型性能
    model_performance = Column(JSON, nullable=True, comment="模型性能指标")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")


class EmotionAlertModel(Base):
    """情绪预警模型"""
    __tablename__ = "emotion_alerts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_id = Column(String(64), unique=True, index=True, comment="预警唯一ID")
    
    # 关联信息
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, comment="员工ID")
    
    # 预警信息
    alert_type = Column(String(50), nullable=False, comment="预警类型")
    severity = Column(String(20), nullable=False, comment="严重程度(low/medium/high/critical)")
    title = Column(String(200), nullable=False, comment="预警标题")
    description = Column(Text, nullable=False, comment="预警描述")
    
    # 情绪状态
    emotion_state = Column(JSON, nullable=False, comment="预警时的情绪状态")
    duration_minutes = Column(Integer, nullable=False, comment="持续时间（分钟）")
    threshold_exceeded = Column(JSON, nullable=False, comment="超出阈值的指标")
    
    # 处理信息
    is_resolved = Column(Boolean, nullable=False, default=False, comment="是否已解决")
    resolution_method = Column(String(100), nullable=True, comment="解决方法")
    resolution_notes = Column(Text, nullable=True, comment="解决备注")
    
    # 建议措施
    recommendations = Column(JSON, nullable=True, comment="建议措施")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="解决时间")
    
    # 关系
    employee = relationship("EmployeeModel", back_populates="emotion_alerts")


class EmotionInsightModel(Base):
    """情绪洞察模型"""
    __tablename__ = "emotion_insights"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    insight_id = Column(String(64), unique=True, index=True, comment="洞察唯一ID")
    
    # 关联信息
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, comment="员工ID")
    
    # 洞察信息
    analysis_period = Column(String(50), nullable=False, comment="分析周期")
    insight_type = Column(String(50), nullable=False, comment="洞察类型")
    
    # 情绪模式
    emotional_patterns = Column(JSON, nullable=False, comment="情绪模式")
    mood_trend = Column(String(50), nullable=False, comment="情绪趋势")
    stability_score = Column(Float, nullable=False, comment="情绪稳定性评分")
    
    # 触发因素和建议
    triggers = Column(JSON, nullable=True, comment="情绪触发因素")
    recommendations = Column(JSON, nullable=True, comment="建议")
    
    # 压力指标
    stress_indicators = Column(JSON, nullable=True, comment="压力指标")
    wellness_score = Column(Float, nullable=True, comment="健康度评分")
    
    # 数据统计
    data_points_count = Column(Integer, nullable=False, comment="数据点数量")
    confidence_level = Column(Float, nullable=False, comment="洞察置信度")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    employee = relationship("EmployeeModel", back_populates="emotion_insights")


class EmotionComparisonModel(Base):
    """情绪对比模型"""
    __tablename__ = "emotion_comparisons"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comparison_id = Column(String(64), unique=True, index=True, comment="对比唯一ID")
    
    # 关联信息
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, comment="员工ID")
    
    # 对比信息
    comparison_type = Column(String(50), nullable=False, comment="对比类型")
    comparison_period = Column(String(50), nullable=False, comment="对比周期")
    
    # 情绪数据
    baseline_emotion = Column(JSON, nullable=False, comment="基线情绪")
    current_emotion = Column(JSON, nullable=False, comment="当前情绪")
    changes = Column(JSON, nullable=False, comment="情绪变化")
    significant_changes = Column(JSON, nullable=False, comment="显著变化")
    
    # 统计信息
    change_magnitude = Column(Float, nullable=False, comment="变化幅度")
    trend_direction = Column(String(20), nullable=False, comment="趋势方向")
    statistical_significance = Column(Float, nullable=True, comment="统计显著性")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    employee = relationship("EmployeeModel", back_populates="emotion_comparisons")