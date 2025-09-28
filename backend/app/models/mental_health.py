"""
心理健康相关数据模型
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class Child(BaseModel):
    """儿童信息模型"""
    __tablename__ = "children"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, comment="儿童姓名")
    age = Column(Integer, nullable=False, comment="年龄")
    gender = Column(String(10), nullable=False, comment="性别")
    birth_date = Column(DateTime, nullable=True, comment="出生日期")
    
    # 关联信息
    parent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    school_info = Column(JSON, nullable=True, comment="学校信息")
    medical_history = Column(JSON, nullable=True, comment="医疗史")
    
    # 心理健康基础信息
    personality_traits = Column(JSON, nullable=True, comment="性格特征")
    interests = Column(JSON, nullable=True, comment="兴趣爱好")
    communication_preferences = Column(JSON, nullable=True, comment="沟通偏好")
    
    # 关系
    parent = relationship("User", back_populates="children")
    emotion_records = relationship("EmotionRecord", back_populates="child")
    psychological_profiles = relationship("PsychologicalProfile", back_populates="child")
    intervention_sessions = relationship("InterventionSession", back_populates="child")


class EmotionRecord(BaseModel):
    """情绪记录模型"""
    __tablename__ = "emotion_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False)
    
    # 情绪数据
    emotion_type = Column(String(50), nullable=False, comment="情绪类型")
    intensity = Column(Float, nullable=False, comment="情绪强度 0-1")
    confidence = Column(Float, nullable=False, comment="识别置信度 0-1")
    
    # 多模态数据
    text_content = Column(Text, nullable=True, comment="文字内容")
    audio_features = Column(JSON, nullable=True, comment="音频特征")
    visual_features = Column(JSON, nullable=True, comment="视觉特征")
    physiological_data = Column(JSON, nullable=True, comment="生理数据")
    
    # 上下文信息
    context = Column(JSON, nullable=True, comment="情境信息")
    trigger_events = Column(JSON, nullable=True, comment="触发事件")
    environment = Column(String(100), nullable=True, comment="环境")
    
    # 时间信息
    recorded_at = Column(DateTime, default=datetime.utcnow, comment="记录时间")
    duration = Column(Integer, nullable=True, comment="持续时间(秒)")
    
    # 关系
    child = relationship("Child", back_populates="emotion_records")


class PsychologicalProfile(BaseModel):
    """心理画像模型"""
    __tablename__ = "psychological_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False)
    
    # 心理特征
    emotional_patterns = Column(JSON, nullable=False, comment="情绪模式")
    stress_triggers = Column(JSON, nullable=True, comment="压力触发因素")
    coping_mechanisms = Column(JSON, nullable=True, comment="应对机制")
    social_preferences = Column(JSON, nullable=True, comment="社交偏好")
    
    # 发展阶段
    developmental_stage = Column(String(50), nullable=False, comment="发展阶段")
    cognitive_level = Column(String(50), nullable=True, comment="认知水平")
    emotional_maturity = Column(Float, nullable=True, comment="情绪成熟度")
    
    # 风险评估
    risk_factors = Column(JSON, nullable=True, comment="风险因素")
    protective_factors = Column(JSON, nullable=True, comment="保护因素")
    overall_risk_level = Column(String(20), nullable=False, comment="整体风险等级")
    
    # 推荐策略
    recommended_interventions = Column(JSON, nullable=True, comment="推荐干预策略")
    parent_guidance = Column(JSON, nullable=True, comment="家长指导建议")
    
    # 版本控制
    version = Column(Integer, default=1, comment="版本号")
    is_active = Column(Boolean, default=True, comment="是否为当前版本")
    
    # 关系
    child = relationship("Child", back_populates="psychological_profiles")


class InterventionSession(BaseModel):
    """干预会话模型"""
    __tablename__ = "intervention_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False)
    
    # 会话信息
    session_type = Column(String(50), nullable=False, comment="会话类型")
    intervention_method = Column(String(100), nullable=False, comment="干预方法")
    target_emotion = Column(String(50), nullable=True, comment="目标情绪")
    
    # 会话内容
    activities = Column(JSON, nullable=True, comment="活动内容")
    dialogue_history = Column(JSON, nullable=True, comment="对话历史")
    multimedia_content = Column(JSON, nullable=True, comment="多媒体内容")
    
    # 效果评估
    pre_session_mood = Column(Float, nullable=True, comment="会话前情绪评分")
    post_session_mood = Column(Float, nullable=True, comment="会话后情绪评分")
    engagement_level = Column(Float, nullable=True, comment="参与度")
    effectiveness_score = Column(Float, nullable=True, comment="有效性评分")
    
    # 时间信息
    start_time = Column(DateTime, default=datetime.utcnow, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    duration = Column(Integer, nullable=True, comment="持续时间(分钟)")
    
    # 关系
    child = relationship("Child", back_populates="intervention_sessions")


class ParentGuidance(BaseModel):
    """家长指导模型"""
    __tablename__ = "parent_guidance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False)
    
    # 指导内容
    guidance_type = Column(String(50), nullable=False, comment="指导类型")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="指导内容")
    recommendations = Column(JSON, nullable=True, comment="具体建议")
    
    # 情境信息
    trigger_situation = Column(String(200), nullable=True, comment="触发情况")
    child_emotion_state = Column(String(50), nullable=True, comment="儿童情绪状态")
    urgency_level = Column(String(20), nullable=False, comment="紧急程度")
    
    # 反馈
    parent_feedback = Column(JSON, nullable=True, comment="家长反馈")
    effectiveness_rating = Column(Float, nullable=True, comment="有效性评分")
    implementation_status = Column(String(20), nullable=True, comment="实施状态")
    
    # 关系
    parent = relationship("User")
    child = relationship("Child")


class CommunityPost(BaseModel):
    """社区帖子模型"""
    __tablename__ = "community_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 帖子内容
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    category = Column(String(50), nullable=False, comment="分类")
    tags = Column(JSON, nullable=True, comment="标签")
    
    # 状态
    is_anonymous = Column(Boolean, default=False, comment="是否匿名")
    is_expert_verified = Column(Boolean, default=False, comment="专家认证")
    status = Column(String(20), default="published", comment="状态")
    
    # 统计
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    reply_count = Column(Integer, default=0, comment="回复数")
    
    # 关系
    author = relationship("User")
    replies = relationship("CommunityReply", back_populates="post")


class CommunityReply(BaseModel):
    """社区回复模型"""
    __tablename__ = "community_replies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("community_posts.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_reply_id = Column(UUID(as_uuid=True), ForeignKey("community_replies.id"), nullable=True)
    
    # 回复内容
    content = Column(Text, nullable=False, comment="回复内容")
    is_expert_reply = Column(Boolean, default=False, comment="专家回复")
    is_anonymous = Column(Boolean, default=False, comment="是否匿名")
    
    # 统计
    like_count = Column(Integer, default=0, comment="点赞数")
    
    # 关系
    post = relationship("CommunityPost", back_populates="replies")
    author = relationship("User")
    parent_reply = relationship("CommunityReply", remote_side=[id])
    child_replies = relationship("CommunityReply")


class MentalHealthAlert(BaseModel):
    """心理健康预警模型"""
    __tablename__ = "mental_health_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False)
    
    # 预警信息
    alert_type = Column(String(50), nullable=False, comment="预警类型")
    severity_level = Column(String(20), nullable=False, comment="严重程度")
    description = Column(Text, nullable=False, comment="预警描述")
    
    # 触发条件
    trigger_data = Column(JSON, nullable=False, comment="触发数据")
    risk_indicators = Column(JSON, nullable=True, comment="风险指标")
    
    # 处理状态
    status = Column(String(20), default="active", comment="状态")
    handled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    handled_at = Column(DateTime, nullable=True, comment="处理时间")
    resolution_notes = Column(Text, nullable=True, comment="处理说明")
    
    # 关系
    child = relationship("Child")
    handler = relationship("User")
