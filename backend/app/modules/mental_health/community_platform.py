"""
社区支持网络模块
构建线上支持社区和心理健康教育平台
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from enum import Enum

from app.core.logging import get_logger
from app.models.mental_health import CommunityPost, CommunityReply
from app.core.security_enhanced import SecurityValidator

logger = get_logger(__name__)


class UserRole(Enum):
    """用户角色"""
    PARENT = "parent"
    EXPERT = "expert"
    MODERATOR = "moderator"
    ADMIN = "admin"


class PostCategory(Enum):
    """帖子分类"""
    EXPERIENCE_SHARING = "experience_sharing"
    QUESTION_ANSWER = "question_answer"
    RESOURCE_SHARING = "resource_sharing"
    EMOTIONAL_SUPPORT = "emotional_support"
    EXPERT_ADVICE = "expert_advice"
    CRISIS_SUPPORT = "crisis_support"


@dataclass
class CommunityUser:
    """社区用户"""
    user_id: str
    username: str
    role: UserRole
    reputation_score: int
    join_date: datetime
    last_active: datetime
    expertise_areas: List[str]
    is_verified: bool


@dataclass
class SupportGroup:
    """支持小组"""
    group_id: str
    name: str
    description: str
    category: str
    member_count: int
    is_private: bool
    moderators: List[str]
    created_at: datetime
    meeting_schedule: Dict[str, Any]


@dataclass
class EducationalResource:
    """教育资源"""
    resource_id: str
    title: str
    content_type: str  # article, video, webinar, course
    category: str
    target_audience: str
    difficulty_level: str
    content_url: str
    description: str
    tags: List[str]
    rating: float
    view_count: int
    created_at: datetime


@dataclass
class CommunityEvent:
    """社区活动"""
    event_id: str
    title: str
    description: str
    event_type: str  # webinar, workshop, support_group, expert_session
    start_time: datetime
    duration_minutes: int
    max_participants: int
    current_participants: int
    facilitator: str
    registration_required: bool
    is_free: bool


class CommunityModerationEngine:
    """社区内容审核引擎"""
    
    def __init__(self):
        self.security_validator = SecurityValidator()
        self.sensitive_keywords = self._load_sensitive_keywords()
        self.auto_moderation_rules = self._load_moderation_rules()
    
    def _load_sensitive_keywords(self) -> Dict[str, List[str]]:
        """加载敏感词库"""
        return {
            "crisis": ["自杀", "自残", "结束生命", "不想活", "想死"],
            "inappropriate": ["暴力", "仇恨", "歧视", "攻击"],
            "spam": ["广告", "推销", "链接", "微信", "QQ"],
            "medical": ["诊断", "药物", "治疗方案", "医生建议"]
        }
    
    def _load_moderation_rules(self) -> Dict[str, Any]:
        """加载审核规则"""
        return {
            "auto_flag_crisis": True,
            "auto_remove_spam": True,
            "require_expert_review_medical": True,
            "max_post_length": 5000,
            "max_links_per_post": 2,
            "min_account_age_days": 1
        }
    
    async def moderate_content(
        self,
        content: str,
        user_id: str,
        content_type: str = "post"
    ) -> Dict[str, Any]:
        """内容审核"""
        
        try:
            moderation_result = {
                "approved": True,
                "flags": [],
                "actions": [],
                "confidence": 1.0,
                "review_required": False
            }
            
            # 基础安全检查
            if not self.security_validator.validate_input(content):
                moderation_result["approved"] = False
                moderation_result["flags"].append("安全检查失败")
                return moderation_result
            
            # 敏感词检测
            crisis_detected = self._detect_crisis_content(content)
            if crisis_detected:
                moderation_result["flags"].append("危机内容")
                moderation_result["actions"].append("立即通知专业人员")
                moderation_result["review_required"] = True
            
            # 垃圾内容检测
            spam_score = self._detect_spam_content(content)
            if spam_score > 0.7:
                moderation_result["approved"] = False
                moderation_result["flags"].append("疑似垃圾内容")
            
            # 医疗建议检测
            medical_advice = self._detect_medical_advice(content)
            if medical_advice:
                moderation_result["flags"].append("包含医疗建议")
                moderation_result["actions"].append("需要专家审核")
                moderation_result["review_required"] = True
            
            # 内容质量评估
            quality_score = self._assess_content_quality(content)
            moderation_result["confidence"] = quality_score
            
            return moderation_result
            
        except Exception as e:
            logger.error(f"内容审核失败: {str(e)}")
            return {
                "approved": False,
                "flags": ["审核系统错误"],
                "actions": ["人工审核"],
                "confidence": 0.0,
                "review_required": True
            }
    
    def _detect_crisis_content(self, content: str) -> bool:
        """检测危机内容"""
        crisis_keywords = self.sensitive_keywords.get("crisis", [])
        content_lower = content.lower()
        
        for keyword in crisis_keywords:
            if keyword in content_lower:
                return True
        
        # 检测危机表达模式
        crisis_patterns = [
            "不想活了", "活着没意思", "想要结束", "没有希望"
        ]
        
        for pattern in crisis_patterns:
            if pattern in content_lower:
                return True
        
        return False
    
    def _detect_spam_content(self, content: str) -> float:
        """检测垃圾内容"""
        spam_indicators = 0
        total_indicators = 5
        
        # 检查重复字符
        if len(set(content)) / len(content) < 0.3:
            spam_indicators += 1
        
        # 检查链接数量
        link_count = content.count("http") + content.count("www.")
        if link_count > self.auto_moderation_rules["max_links_per_post"]:
            spam_indicators += 1
        
        # 检查垃圾关键词
        spam_keywords = self.sensitive_keywords.get("spam", [])
        for keyword in spam_keywords:
            if keyword in content.lower():
                spam_indicators += 1
                break
        
        # 检查长度
        if len(content) > self.auto_moderation_rules["max_post_length"]:
            spam_indicators += 1
        
        # 检查大写字母比例
        if sum(1 for c in content if c.isupper()) / len(content) > 0.5:
            spam_indicators += 1
        
        return spam_indicators / total_indicators
    
    def _detect_medical_advice(self, content: str) -> bool:
        """检测医疗建议"""
        medical_keywords = self.sensitive_keywords.get("medical", [])
        content_lower = content.lower()
        
        for keyword in medical_keywords:
            if keyword in content_lower:
                return True
        
        # 检测医疗建议模式
        medical_patterns = [
            "建议服用", "推荐药物", "应该吃", "停止用药", "增加剂量"
        ]
        
        for pattern in medical_patterns:
            if pattern in content_lower:
                return True
        
        return False
    
    def _assess_content_quality(self, content: str) -> float:
        """评估内容质量"""
        quality_score = 0.5  # 基础分数
        
        # 长度适中
        if 50 <= len(content) <= 1000:
            quality_score += 0.2
        
        # 包含问号（提问）
        if "?" in content or "？" in content:
            quality_score += 0.1
        
        # 情感表达
        emotion_words = ["感谢", "帮助", "支持", "理解", "困惑", "担心"]
        if any(word in content for word in emotion_words):
            quality_score += 0.2
        
        return min(1.0, quality_score)


class CommunityRecommendationEngine:
    """社区推荐引擎"""
    
    def __init__(self):
        self.user_interests = {}
        self.content_categories = {}
    
    async def recommend_posts(
        self,
        user_id: str,
        user_profile: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """推荐帖子"""
        
        try:
            # 获取用户兴趣
            interests = await self._analyze_user_interests(user_id, user_profile)
            
            # 获取候选帖子
            candidate_posts = await self._get_candidate_posts()
            
            # 计算推荐分数
            scored_posts = []
            for post in candidate_posts:
                score = self._calculate_recommendation_score(post, interests, user_profile)
                scored_posts.append((post, score))
            
            # 排序并返回
            scored_posts.sort(key=lambda x: x[1], reverse=True)
            return [post for post, score in scored_posts[:limit]]
            
        except Exception as e:
            logger.error(f"帖子推荐失败: {str(e)}")
            return []
    
    async def recommend_support_groups(
        self,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> List[SupportGroup]:
        """推荐支持小组"""
        
        try:
            # 基于用户情况推荐相关小组
            recommendations = []
            
            child_age = user_profile.get("child_age", 8)
            concerns = user_profile.get("concerns", [])
            
            # 年龄相关小组
            if child_age <= 5:
                recommendations.append(self._create_sample_group(
                    "学前儿童家长支持群", "为学前儿童家长提供育儿支持和经验分享"
                ))
            elif child_age <= 12:
                recommendations.append(self._create_sample_group(
                    "小学生家长互助群", "小学阶段儿童心理发展和学习支持"
                ))
            else:
                recommendations.append(self._create_sample_group(
                    "青少年家长交流群", "青春期心理健康和亲子关系"
                ))
            
            # 关注点相关小组
            if "anxiety" in concerns:
                recommendations.append(self._create_sample_group(
                    "儿童焦虑症家长支持群", "专门针对焦虑症儿童的家长支持"
                ))
            
            if "behavior" in concerns:
                recommendations.append(self._create_sample_group(
                    "行为问题应对群", "儿童行为管理和正面管教"
                ))
            
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"支持小组推荐失败: {str(e)}")
            return []
    
    async def recommend_educational_resources(
        self,
        user_profile: Dict[str, Any],
        learning_preferences: Dict[str, Any] = None
    ) -> List[EducationalResource]:
        """推荐教育资源"""
        
        try:
            recommendations = []
            
            child_age = user_profile.get("child_age", 8)
            experience_level = user_profile.get("parenting_experience", "beginner")
            available_time = learning_preferences.get("available_time_minutes", 30) if learning_preferences else 30
            
            # 基础育儿资源
            if experience_level == "beginner":
                recommendations.append(EducationalResource(
                    resource_id="basic_parenting_001",
                    title="儿童心理发展基础知识",
                    content_type="article",
                    category="child_development",
                    target_audience="新手家长",
                    difficulty_level="beginner",
                    content_url="/resources/basic-child-development",
                    description="了解儿童各阶段心理发展特点和需求",
                    tags=["发展心理学", "育儿基础", "儿童心理"],
                    rating=4.8,
                    view_count=1250,
                    created_at=datetime.utcnow()
                ))
            
            # 年龄特定资源
            if child_age <= 5:
                recommendations.append(EducationalResource(
                    resource_id="preschool_001",
                    title="学前儿童情绪管理指南",
                    content_type="video",
                    category="emotional_development",
                    target_audience="学前儿童家长",
                    difficulty_level="intermediate",
                    content_url="/resources/preschool-emotions",
                    description="帮助学前儿童识别和表达情绪的实用方法",
                    tags=["情绪管理", "学前教育", "亲子互动"],
                    rating=4.9,
                    view_count=890,
                    created_at=datetime.utcnow()
                ))
            
            # 时间适配资源
            if available_time < 15:
                recommendations.append(EducationalResource(
                    resource_id="quick_tips_001",
                    title="5分钟育儿小贴士",
                    content_type="article",
                    category="quick_tips",
                    target_audience="忙碌家长",
                    difficulty_level="beginner",
                    content_url="/resources/quick-parenting-tips",
                    description="简短实用的育儿建议和技巧",
                    tags=["快速学习", "实用技巧", "时间管理"],
                    rating=4.6,
                    view_count=2100,
                    created_at=datetime.utcnow()
                ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"教育资源推荐失败: {str(e)}")
            return []
    
    async def _analyze_user_interests(
        self,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> Dict[str, float]:
        """分析用户兴趣"""
        
        interests = {
            "emotional_support": 0.5,
            "practical_advice": 0.5,
            "expert_guidance": 0.5,
            "peer_experience": 0.5,
            "educational_content": 0.5
        }
        
        # 基于用户档案调整兴趣权重
        if user_profile.get("parenting_experience") == "beginner":
            interests["educational_content"] += 0.3
            interests["expert_guidance"] += 0.2
        
        concerns = user_profile.get("concerns", [])
        if "anxiety" in concerns:
            interests["emotional_support"] += 0.3
            interests["expert_guidance"] += 0.2
        
        if "behavior" in concerns:
            interests["practical_advice"] += 0.3
            interests["peer_experience"] += 0.2
        
        # 归一化
        total = sum(interests.values())
        interests = {k: v/total for k, v in interests.items()}
        
        return interests
    
    async def _get_candidate_posts(self) -> List[Dict[str, Any]]:
        """获取候选帖子"""
        # 这里应该从数据库获取帖子
        # 模拟数据用于演示
        return [
            {
                "post_id": "post_001",
                "title": "如何帮助焦虑的孩子",
                "category": "emotional_support",
                "tags": ["焦虑", "情绪支持", "实用建议"],
                "author_role": "expert",
                "like_count": 45,
                "reply_count": 12,
                "created_at": datetime.utcnow() - timedelta(days=1)
            },
            {
                "post_id": "post_002", 
                "title": "分享我家孩子克服社交恐惧的经历",
                "category": "experience_sharing",
                "tags": ["社交恐惧", "成功经验", "家长分享"],
                "author_role": "parent",
                "like_count": 32,
                "reply_count": 8,
                "created_at": datetime.utcnow() - timedelta(days=2)
            }
        ]
    
    def _calculate_recommendation_score(
        self,
        post: Dict[str, Any],
        user_interests: Dict[str, float],
        user_profile: Dict[str, Any]
    ) -> float:
        """计算推荐分数"""
        
        score = 0.0
        
        # 基于分类的兴趣匹配
        category = post.get("category", "")
        if category in user_interests:
            score += user_interests[category] * 0.4
        
        # 基于标签的匹配
        post_tags = post.get("tags", [])
        user_concerns = user_profile.get("concerns", [])
        tag_match = len(set(post_tags) & set(user_concerns)) / max(len(post_tags), 1)
        score += tag_match * 0.3
        
        # 基于作者角色的偏好
        author_role = post.get("author_role", "")
        if author_role == "expert":
            score += user_interests.get("expert_guidance", 0) * 0.2
        elif author_role == "parent":
            score += user_interests.get("peer_experience", 0) * 0.2
        
        # 基于受欢迎程度
        popularity = (post.get("like_count", 0) + post.get("reply_count", 0)) / 100
        score += min(popularity, 0.1)
        
        return score
    
    def _create_sample_group(self, name: str, description: str) -> SupportGroup:
        """创建示例支持小组"""
        return SupportGroup(
            group_id=f"group_{hash(name)}",
            name=name,
            description=description,
            category="support",
            member_count=np.random.randint(20, 200),
            is_private=False,
            moderators=["moderator_001"],
            created_at=datetime.utcnow() - timedelta(days=np.random.randint(30, 365)),
            meeting_schedule={"frequency": "weekly", "day": "Sunday", "time": "20:00"}
        )


class CommunityEventManager:
    """社区活动管理器"""

    def __init__(self):
        self.event_templates = self._load_event_templates()

    def _load_event_templates(self) -> Dict[str, Any]:
        """加载活动模板"""
        return {
            "expert_webinar": {
                "title_template": "专家讲座：{topic}",
                "duration_minutes": 60,
                "max_participants": 100,
                "registration_required": True,
                "is_free": True
            },
            "parent_workshop": {
                "title_template": "家长工作坊：{topic}",
                "duration_minutes": 90,
                "max_participants": 30,
                "registration_required": True,
                "is_free": True
            },
            "support_group_meeting": {
                "title_template": "{group_name}支持小组会议",
                "duration_minutes": 120,
                "max_participants": 15,
                "registration_required": False,
                "is_free": True
            },
            "crisis_support_session": {
                "title_template": "危机干预支持会议",
                "duration_minutes": 45,
                "max_participants": 10,
                "registration_required": True,
                "is_free": True
            }
        }

    async def create_scheduled_events(self, month_ahead: int = 1) -> List[CommunityEvent]:
        """创建预定活动"""

        try:
            events = []
            base_date = datetime.utcnow()

            # 每周专家讲座
            for week in range(4 * month_ahead):
                event_date = base_date + timedelta(weeks=week, days=2)  # 每周三
                event_date = event_date.replace(hour=20, minute=0, second=0, microsecond=0)

                topics = [
                    "儿童焦虑症的识别与应对",
                    "青春期心理发展特点",
                    "家庭沟通技巧提升",
                    "儿童注意力问题解决方案"
                ]

                topic = topics[week % len(topics)]

                events.append(CommunityEvent(
                    event_id=f"webinar_{event_date.strftime('%Y%m%d')}",
                    title=f"专家讲座：{topic}",
                    description=f"由专业心理咨询师主讲的{topic}专题讲座",
                    event_type="webinar",
                    start_time=event_date,
                    duration_minutes=60,
                    max_participants=100,
                    current_participants=0,
                    facilitator="专业心理咨询师",
                    registration_required=True,
                    is_free=True
                ))

            # 每月家长工作坊
            for month in range(month_ahead):
                event_date = base_date + timedelta(days=30*month + 15)  # 每月中旬
                event_date = event_date.replace(hour=14, minute=0, second=0, microsecond=0)

                workshop_topics = [
                    "正面管教技巧实践",
                    "亲子关系建设",
                    "儿童情绪调节训练",
                    "家庭危机应对策略"
                ]

                topic = workshop_topics[month % len(workshop_topics)]

                events.append(CommunityEvent(
                    event_id=f"workshop_{event_date.strftime('%Y%m%d')}",
                    title=f"家长工作坊：{topic}",
                    description=f"互动式{topic}工作坊，包含理论学习和实践练习",
                    event_type="workshop",
                    start_time=event_date,
                    duration_minutes=90,
                    max_participants=30,
                    current_participants=0,
                    facilitator="资深家庭教育专家",
                    registration_required=True,
                    is_free=True
                ))

            return events

        except Exception as e:
            logger.error(f"创建预定活动失败: {str(e)}")
            return []

    async def recommend_events_for_user(
        self,
        user_profile: Dict[str, Any],
        upcoming_events: List[CommunityEvent]
    ) -> List[CommunityEvent]:
        """为用户推荐活动"""

        try:
            recommendations = []
            user_concerns = user_profile.get("concerns", [])
            child_age = user_profile.get("child_age", 8)
            available_times = user_profile.get("available_times", ["evening"])

            for event in upcoming_events:
                score = self._calculate_event_relevance_score(
                    event, user_concerns, child_age, available_times
                )

                if score > 0.5:
                    recommendations.append(event)

            # 按相关性排序
            recommendations.sort(
                key=lambda e: self._calculate_event_relevance_score(
                    e, user_concerns, child_age, available_times
                ),
                reverse=True
            )

            return recommendations[:5]

        except Exception as e:
            logger.error(f"活动推荐失败: {str(e)}")
            return []

    def _calculate_event_relevance_score(
        self,
        event: CommunityEvent,
        user_concerns: List[str],
        child_age: int,
        available_times: List[str]
    ) -> float:
        """计算活动相关性分数"""

        score = 0.0

        # 基于关注点的匹配
        event_title_lower = event.title.lower()
        for concern in user_concerns:
            if concern in event_title_lower:
                score += 0.4

        # 基于年龄的匹配
        if child_age <= 5 and "学前" in event.title:
            score += 0.3
        elif 6 <= child_age <= 12 and ("小学" in event.title or "儿童" in event.title):
            score += 0.3
        elif child_age >= 13 and ("青春期" in event.title or "青少年" in event.title):
            score += 0.3

        # 基于时间偏好的匹配
        event_hour = event.start_time.hour
        if "evening" in available_times and 18 <= event_hour <= 21:
            score += 0.2
        elif "afternoon" in available_times and 13 <= event_hour <= 17:
            score += 0.2
        elif "morning" in available_times and 9 <= event_hour <= 12:
            score += 0.2

        # 基于活动类型的偏好
        if event.event_type == "webinar":
            score += 0.1  # 网络讲座通常更受欢迎

        return min(score, 1.0)


class CommunityAnalytics:
    """社区分析器"""

    def __init__(self):
        pass

    async def generate_community_insights(
        self,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """生成社区洞察报告"""

        try:
            # 模拟社区数据分析
            insights = {
                "user_engagement": {
                    "active_users": 1250,
                    "new_users": 180,
                    "retention_rate": 0.78,
                    "avg_session_duration_minutes": 25
                },
                "content_metrics": {
                    "total_posts": 450,
                    "total_replies": 1200,
                    "expert_posts": 85,
                    "most_popular_categories": [
                        {"category": "emotional_support", "post_count": 120},
                        {"category": "practical_advice", "post_count": 95},
                        {"category": "experience_sharing", "post_count": 80}
                    ]
                },
                "support_effectiveness": {
                    "crisis_interventions": 12,
                    "successful_referrals": 35,
                    "peer_support_connections": 89,
                    "expert_response_time_hours": 4.2
                },
                "trending_topics": [
                    {"topic": "学校焦虑", "mention_count": 67},
                    {"topic": "睡眠问题", "mention_count": 54},
                    {"topic": "同伴关系", "mention_count": 48},
                    {"topic": "学习压力", "mention_count": 42}
                ],
                "community_health": {
                    "positive_sentiment_ratio": 0.72,
                    "help_request_fulfillment_rate": 0.85,
                    "moderator_intervention_rate": 0.03,
                    "user_satisfaction_score": 4.3
                }
            }

            return insights

        except Exception as e:
            logger.error(f"社区洞察生成失败: {str(e)}")
            return {}

    async def identify_at_risk_users(self) -> List[Dict[str, Any]]:
        """识别需要关注的用户"""

        try:
            # 基于行为模式识别需要关注的用户
            at_risk_indicators = [
                {
                    "user_id": "user_001",
                    "risk_factors": ["频繁发布危机内容", "社交互动减少"],
                    "risk_level": "high",
                    "recommended_actions": ["专业干预", "一对一支持"],
                    "last_activity": datetime.utcnow() - timedelta(days=2)
                },
                {
                    "user_id": "user_002",
                    "risk_factors": ["长期负面情绪表达", "求助频率增加"],
                    "risk_level": "medium",
                    "recommended_actions": ["增加关注", "推荐专业资源"],
                    "last_activity": datetime.utcnow() - timedelta(hours=6)
                }
            ]

            return at_risk_indicators

        except Exception as e:
            logger.error(f"风险用户识别失败: {str(e)}")
            return []


class CommunityPlatform:
    """社区平台主控制器"""

    def __init__(self):
        self.moderation_engine = CommunityModerationEngine()
        self.recommendation_engine = CommunityRecommendationEngine()
        self.event_manager = CommunityEventManager()
        self.analytics = CommunityAnalytics()

    async def initialize_community_features(self) -> Dict[str, Any]:
        """初始化社区功能"""

        try:
            # 创建预定活动
            upcoming_events = await self.event_manager.create_scheduled_events()

            # 生成社区洞察
            community_insights = await self.analytics.generate_community_insights()

            # 识别需要关注的用户
            at_risk_users = await self.analytics.identify_at_risk_users()

            initialization_result = {
                "status": "success",
                "features_enabled": [
                    "内容审核系统",
                    "智能推荐引擎",
                    "活动管理系统",
                    "社区分析工具",
                    "危机干预机制"
                ],
                "upcoming_events_count": len(upcoming_events),
                "community_health_score": community_insights.get("community_health", {}).get("user_satisfaction_score", 0),
                "at_risk_users_count": len(at_risk_users),
                "moderation_rules_active": len(self.moderation_engine.auto_moderation_rules),
                "initialized_at": datetime.utcnow().isoformat()
            }

            logger.info(f"社区平台初始化成功: {json.dumps(initialization_result, ensure_ascii=False)}")
            return initialization_result

        except Exception as e:
            logger.error(f"社区平台初始化失败: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "initialized_at": datetime.utcnow().isoformat()
            }

    async def get_personalized_community_experience(
        self,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取个性化社区体验"""

        try:
            # 推荐帖子
            recommended_posts = await self.recommendation_engine.recommend_posts(
                user_id, user_profile
            )

            # 推荐支持小组
            recommended_groups = await self.recommendation_engine.recommend_support_groups(
                user_id, user_profile
            )

            # 推荐教育资源
            recommended_resources = await self.recommendation_engine.recommend_educational_resources(
                user_profile
            )

            # 推荐活动
            upcoming_events = await self.event_manager.create_scheduled_events()
            recommended_events = await self.event_manager.recommend_events_for_user(
                user_profile, upcoming_events
            )

            personalized_experience = {
                "user_id": user_id,
                "recommendations": {
                    "posts": [
                        {
                            "post_id": post.get("post_id"),
                            "title": post.get("title"),
                            "category": post.get("category"),
                            "author_role": post.get("author_role")
                        }
                        for post in recommended_posts[:5]
                    ],
                    "support_groups": [
                        {
                            "group_id": group.group_id,
                            "name": group.name,
                            "description": group.description,
                            "member_count": group.member_count
                        }
                        for group in recommended_groups[:3]
                    ],
                    "educational_resources": [
                        {
                            "resource_id": resource.resource_id,
                            "title": resource.title,
                            "content_type": resource.content_type,
                            "difficulty_level": resource.difficulty_level,
                            "rating": resource.rating
                        }
                        for resource in recommended_resources[:5]
                    ],
                    "events": [
                        {
                            "event_id": event.event_id,
                            "title": event.title,
                            "event_type": event.event_type,
                            "start_time": event.start_time.isoformat(),
                            "duration_minutes": event.duration_minutes
                        }
                        for event in recommended_events[:3]
                    ]
                },
                "community_status": {
                    "user_role": user_profile.get("role", "parent"),
                    "reputation_score": user_profile.get("reputation_score", 100),
                    "community_contributions": user_profile.get("post_count", 0),
                    "support_connections": user_profile.get("connections", 0)
                },
                "generated_at": datetime.utcnow().isoformat()
            }

            return personalized_experience

        except Exception as e:
            logger.error(f"个性化社区体验生成失败: {str(e)}")
            return {
                "user_id": user_id,
                "error": "个性化推荐生成失败",
                "generated_at": datetime.utcnow().isoformat()
            }
