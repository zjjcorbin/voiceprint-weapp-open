from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class VoiceprintModel(Base):
    """声纹模型"""
    __tablename__ = "voiceprints"
    
    voiceprint_id = Column(String(64), primary_key=True, index=True, comment="声纹唯一ID")
    
    # 关联员工
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, comment="员工ID")
    
    # 音频信息
    audio_sample_url = Column(Text, nullable=False, comment="音频样本URL")
    sample_duration = Column(Float, nullable=False, comment="样本时长（秒）")
    sample_rate = Column(Integer, nullable=False, comment="采样率")
    
    # 声纹特征
    feature_data = Column(JSON, nullable=False, comment="声纹特征向量")
    feature_model = Column(String(200), nullable=False, comment="特征提取模型")
    embedding_version = Column(String(50), nullable=True, comment="嵌入向量版本")
    
    # 质量评估
    quality_score = Column(Float, nullable=False, comment="音频质量评分")
    clarity_score = Column(Float, nullable=True, comment="清晰度评分")
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, comment="是否活跃")
    is_verified = Column(Boolean, default=False, nullable=False, comment="是否已验证")
    
    # 其他信息
    device_info = Column(JSON, nullable=True, comment="录音设备信息")
    environment_info = Column(JSON, nullable=True, comment="环境信息")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_used_at = Column(DateTime(timezone=True), nullable=True, comment="最后使用时间")
    
    # 关系
    employee = relationship("EmployeeModel", back_populates="voiceprints")
    recognition_logs = relationship("RecognitionLogModel", back_populates="voiceprint", cascade="all, delete-orphan")


class RecognitionLogModel(Base):
    """识别日志模型"""
    __tablename__ = "recognition_logs"
    
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联信息
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True, comment="员工ID")
    voiceprint_id = Column(String(64), ForeignKey("voiceprints.voiceprint_id"), nullable=True, comment="匹配的声纹ID")
    
    # 音频信息
    audio_url = Column(Text, nullable=True, comment="音频文件URL")
    audio_duration = Column(Float, nullable=True, comment="音频时长（秒）")
    
    # 识别结果
    confidence_score = Column(Float, nullable=True, comment="置信度")
    threshold_used = Column(Float, nullable=True, comment="使用的阈值")
    is_success = Column(Boolean, nullable=False, comment="是否识别成功")
    
    # 候选信息
    top_candidates = Column(JSON, nullable=True, comment="前N个候选结果")
    
    # 技术信息
    model_version = Column(String(100), nullable=True, comment="使用的模型版本")
    processing_time = Column(Float, nullable=True, comment="处理时间（秒）")
    
    # 其他信息
    ip_address = Column(String(45), nullable=True, comment="客户端IP")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    employee = relationship("EmployeeModel", back_populates="recognition_logs")
    voiceprint = relationship("VoiceprintModel", back_populates="recognition_logs")