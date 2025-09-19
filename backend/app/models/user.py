from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    EDITOR = "editor"
    READER = "reader"
    GUEST = "guest"

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.READER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    
    # 关系
    articles = relationship("Article", back_populates="author")
    edits = relationship("ArticleEdit", back_populates="editor")
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User {self.display_name}>"

class UserProfile(Base):
    """用户个人信息模型"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(Text)
    avatar_url = Column(String(500))
    location = Column(String(200))
    website = Column(String(500))
    specialty = Column(String(200))  # 医疗专业领域
    experience_level = Column(String(100))  # 经验级别
    
    # 关系
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile {self.user_id}>"