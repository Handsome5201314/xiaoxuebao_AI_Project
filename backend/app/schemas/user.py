from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.user import UserRole

# 基础用户模型
class UserBase(BaseModel):
    email: EmailStr
    display_name: str = Field(..., min_length=2, max_length=200)

# 用户创建
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

# 用户更新
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    display_name: Optional[str] = Field(None, min_length=2, max_length=200)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

# 用户响应
class User(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 用户响应别名（API兼容性）
UserResponse = User

# 用户详情（包含个人信息）
class UserDetail(User):
    profile: Optional['UserProfile'] = None

# 用户登录
class UserLogin(BaseModel):
    email: str
    password: str

# 用户令牌
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 令牌数据
class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

# 用户个人信息
class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    specialty: Optional[str] = None
    experience_level: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    user_id: int

class UserProfile(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 密码重置
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)

# 用户列表响应
class UserList(BaseModel):
    users: List[User]
    total_count: int
    page: int
    page_size: int

# 更新密码
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

# 验证器示例
@validator('username')
def validate_username(cls, v):
    if not v.isalnum():
        raise ValueError('用户名只能包含字母和数字')
    return v