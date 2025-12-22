from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.models.database import Base


class UserModel(Base):
    """用户模型"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    
    # 认证信息
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否活跃")
    is_admin = Column(Boolean, default=False, nullable=False, comment="是否管理员")
    is_verified = Column(Boolean, default=False, nullable=False, comment="是否已验证")
    
    # 微信相关
    openid = Column(String(100), unique=True, index=True, nullable=True, comment="微信OpenID")
    unionid = Column(String(100), nullable=True, comment="微信UnionID")
    session_key = Column(String(100), nullable=True, comment="微信会话密钥")
    
    # 个人信息
    nickname = Column(String(100), nullable=True, comment="昵称")
    avatar_url = Column(Text, nullable=True, comment="头像URL")
    real_name = Column(String(100), nullable=True, comment="真实姓名")
    
    # 状态信息
    last_login_at = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    login_count = Column(Integer, default=0, nullable=False, comment="登录次数")
    
    # 其他信息
    preferences = Column(Text, nullable=True, comment="用户偏好设置")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    # 可以在这里添加与其他模型的关系