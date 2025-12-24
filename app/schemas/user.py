from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """用户响应模型"""
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    is_active: bool = Field(..., description="是否活跃")
    is_admin: bool = Field(..., description="是否管理员")
    is_verified: bool = Field(..., description="是否已验证")
    openid: Optional[str] = Field(None, description="微信OpenID")
    unionid: Optional[str] = Field(None, description="微信UnionID")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    real_name: Optional[str] = Field(None, description="真实姓名")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    login_count: int = Field(..., description="登录次数")
    preferences: Optional[str] = Field(None, description="用户偏好设置")
    notes: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """用户创建请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    password: str = Field(..., min_length=6, description="密码")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")


class UserUpdate(BaseModel):
    """用户更新请求模型"""
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    preferences: Optional[str] = Field(None, description="用户偏好设置")


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserLoginResponse(BaseModel):
    """用户登录响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间(秒)")
    user: UserResponse = Field(..., description="用户信息")