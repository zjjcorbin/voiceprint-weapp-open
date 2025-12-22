from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class MeetingModel(Base):
    """会议模型"""
    __tablename__ = "meetings"
    
    meeting_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_code = Column(String(50), unique=True, index=True, nullable=False, comment="会议编号")
    title = Column(String(200), nullable=False, comment="会议标题")
    description = Column(Text, nullable=True, comment="会议描述")
    
    # 会议信息
    organizer_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, comment="组织者ID")
    meeting_room = Column(String(100), nullable=True, comment="会议室")
    expected_duration = Column(Integer, nullable=False, comment="预计时长（分钟）")
    
    # 状态信息
    status = Column(String(20), default="scheduled", nullable=False, comment="会议状态")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否活跃")
    
    # 时间信息
    scheduled_start = Column(DateTime(timezone=True), nullable=False, comment="计划开始时间")
    scheduled_end = Column(DateTime(timezone=True), nullable=False, comment="计划结束时间")
    actual_start = Column(DateTime(timezone=True), nullable=True, comment="实际开始时间")
    actual_end = Column(DateTime(timezone=True), nullable=True, comment="实际结束时间")
    
    # 参会信息
    participants = Column(JSON, nullable=True, comment="参会人员列表")
    max_participants = Column(Integer, nullable=True, comment="最大参会人数")
    
    # 会议配置
    require_voiceprint = Column(Boolean, default=True, nullable=False, comment="是否需要声纹验证")
    enable_emotion_detection = Column(Boolean, default=True, nullable=False, comment="是否启用情绪检测")
    recording_enabled = Column(Boolean, default=False, nullable=False, comment="是否启用录音")
    
    # 其他信息
    meeting_password = Column(String(100), nullable=True, comment="会议密码")
    notes = Column(Text, nullable=True, comment="会议备注")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    organizer = relationship("EmployeeModel", back_populates="organized_meetings")
    emotion_detections = relationship("EmotionDetectionModel", back_populates="meeting", cascade="all, delete-orphan")