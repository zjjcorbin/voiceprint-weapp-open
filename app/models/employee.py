from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.models.database import Base


class EmployeeModel(Base):
    """员工模型"""
    __tablename__ = "employees"
    
    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_code = Column(String(50), unique=True, index=True, nullable=False, comment="员工编号")
    name = Column(String(100), nullable=False, comment="员工姓名")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    department = Column(String(100), nullable=True, comment="部门")
    position = Column(String(100), nullable=True, comment="职位")
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, comment="是否活跃")
    is_admin = Column(Boolean, default=False, nullable=False, comment="是否管理员")
    
    # 声纹注册状态
    voiceprint_registered = Column(Boolean, default=False, nullable=False, comment="是否已注册声纹")
    voiceprint_count = Column(Integer, default=0, nullable=False, comment="声纹样本数量")
    
    # 其他信息
    avatar_url = Column(Text, nullable=True, comment="头像URL")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    voiceprints = relationship("VoiceprintModel", back_populates="employee", cascade="all, delete-orphan")
    recognition_logs = relationship("RecognitionLogModel", back_populates="employee", cascade="all, delete-orphan")
    emotion_detections = relationship("EmotionDetectionModel", back_populates="employee", cascade="all, delete-orphan")
    emotion_alerts = relationship("EmotionAlertModel", back_populates="employee", cascade="all, delete-orphan")
    emotion_insights = relationship("EmotionInsightModel", back_populates="employee", cascade="all, delete-orphan")
    emotion_comparisons = relationship("EmotionComparisonModel", back_populates="employee", cascade="all, delete-orphan")