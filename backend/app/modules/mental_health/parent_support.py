"""
家长协同支持模块
为家长提供指导、教育和协同干预功能
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from app.core.logging import get_logger
from app.models.mental_health import Child, ParentGuidance, EmotionRecord
from app.modules.mental_health.psychological_profiler import PsychologicalProfileResult

logger = get_logger(__name__)


@dataclass
class ParentGuidanceRecommendation:
    """家长指导建议"""
    guidance_id: str
    title: str
    category: str  # communication, behavior_management, emotional_support, crisis_intervention
    urgency_level: str  # low, medium, high, urgent
    description: str
    specific_actions: List[str]
    what_to_say: List[str]
    what_not_to_say: List[str]
    expected_outcomes: List[str]
    follow_up_timeline: str
    resources: List[Dict[str, str]]


@dataclass
class ParentEducationContent:
    """家长教育内容"""
    content_id: str
    title: str
    category: str
    age_group: str
    difficulty_level: str  # beginner, intermediate, advanced
    content_type: str  # article, video, interactive, checklist
    content: str
    key_takeaways: List[str]
    practical_exercises: List[Dict[str, Any]]
    estimated_time_minutes: int


@dataclass
class FamilyInterventionPlan:
    """家庭干预计划"""
    plan_id: str
    child_id: str
    parent_id: str
    intervention_goals: List[str]
    family_activities: List[Dict[str, Any]]
    parent_strategies: List[Dict[str, Any]]
    progress_milestones: List[Dict[str, Any]]
    review_schedule: List[datetime]
    success_metrics: List[str]
    created_at: datetime
    updated_at: datetime


class ParentGuidanceEngine:
    """家长指导引擎"""
    
    def __init__(self):
        self.guidance_templates = self._load_guidance_templates()
        self.communication_strategies = self._load_communication_strategies()
        self.crisis_protocols = self._load_crisis_protocols()
    
    def _load_guidance_templates(self) -> Dict[str, Any]:
        """加载指导模板"""
        return {
            "anxiety_support": {
                "title": "帮助焦虑的孩子",
                "what_to_say": [
                    "我理解你现在感到担心，这很正常",
                    "我们一起想办法解决这个问题",
                    "你很勇敢，我相信你能处理好"
                ],
                "what_not_to_say": [
                    "没什么好担心的",
                    "你想太多了",
                    "别这么敏感"
                ],
                "actions": [
                    "保持冷静，用温和的语调说话",
                    "倾听孩子的担忧，不要立即否定",
                    "教授简单的放松技巧",
                    "建立可预测的日常routine"
                ]
            },
            "anger_management": {
                "title": "应对孩子的愤怒情绪",
                "what_to_say": [
                    "我看到你很生气，告诉我发生了什么",
                    "生气是正常的感受，但我们需要用合适的方式表达",
                    "让我们一起想想更好的解决办法"
                ],
                "what_not_to_say": [
                    "不许发脾气",
                    "你这样很丢人",
                    "再这样我就不理你了"
                ],
                "actions": [
                    "保持自己的情绪稳定",
                    "给孩子时间冷静下来",
                    "帮助孩子识别愤怒的触发因素",
                    "教授健康的情绪表达方式"
                ]
            },
            "sadness_comfort": {
                "title": "安慰悲伤的孩子",
                "what_to_say": [
                    "我看到你很难过，我在这里陪着你",
                    "告诉我什么让你感到伤心",
                    "哭出来没关系，这能帮助你感觉好一些"
                ],
                "what_not_to_say": [
                    "别哭了，没什么大不了的",
                    "你应该坚强一点",
                    "其他孩子都没有这样"
                ],
                "actions": [
                    "提供身体安慰（拥抱、轻拍）",
                    "耐心倾听，不急于解决问题",
                    "验证孩子的感受",
                    "在适当时候提供解决方案"
                ]
            }
        }
    
    def _load_communication_strategies(self) -> Dict[str, Any]:
        """加载沟通策略"""
        return {
            "active_listening": {
                "name": "积极倾听",
                "techniques": [
                    "全神贯注地听孩子说话",
                    "重复孩子说的话以确认理解",
                    "询问开放性问题",
                    "避免立即给出建议或判断"
                ],
                "examples": [
                    "你是说...？",
                    "听起来你感到...",
                    "告诉我更多关于..."
                ]
            },
            "emotion_validation": {
                "name": "情绪验证",
                "techniques": [
                    "承认孩子的感受是真实的",
                    "帮助孩子给情绪命名",
                    "表达理解和共情",
                    "避免最小化或否定情绪"
                ],
                "examples": [
                    "你的感受很重要",
                    "任何人遇到这种情况都会感到...",
                    "我理解为什么你会有这种感觉"
                ]
            },
            "collaborative_problem_solving": {
                "name": "协作解决问题",
                "techniques": [
                    "与孩子一起定义问题",
                    "头脑风暴可能的解决方案",
                    "评估每个方案的优缺点",
                    "让孩子参与决策过程"
                ],
                "examples": [
                    "我们一起想想可以怎么办",
                    "你觉得哪个方法最好？",
                    "如果这样做会发生什么？"
                ]
            }
        }
    
    def _load_crisis_protocols(self) -> Dict[str, Any]:
        """加载危机处理协议"""
        return {
            "severe_anxiety": {
                "immediate_actions": [
                    "保持冷静，用平静的声音说话",
                    "帮助孩子进行深呼吸",
                    "移除或减少刺激源",
                    "使用接地技巧（5-4-3-2-1感官法）"
                ],
                "when_to_seek_help": [
                    "焦虑持续超过2周",
                    "严重影响日常功能",
                    "出现身体症状",
                    "孩子表达自伤想法"
                ]
            },
            "aggressive_behavior": {
                "immediate_actions": [
                    "确保所有人的安全",
                    "保持冷静，不要以暴制暴",
                    "给孩子空间冷静",
                    "事后讨论更好的表达方式"
                ],
                "when_to_seek_help": [
                    "攻击行为频繁发生",
                    "造成伤害或财产损失",
                    "孩子无法控制自己",
                    "家庭关系严重受损"
                ]
            },
            "withdrawal_isolation": {
                "immediate_actions": [
                    "尊重孩子需要独处的时间",
                    "定期检查，表达关心",
                    "提供低压力的陪伴机会",
                    "保持日常routine"
                ],
                "when_to_seek_help": [
                    "孤立行为持续超过1周",
                    "完全拒绝社交接触",
                    "学业或生活功能严重下降",
                    "出现抑郁症状"
                ]
            }
        }
    
    async def generate_parent_guidance(
        self,
        child_emotion_state: str,
        situation_context: Dict[str, Any],
        child_age: int,
        parent_experience_level: str = "beginner"
    ) -> ParentGuidanceRecommendation:
        """生成家长指导建议"""
        
        try:
            # 确定指导类型
            guidance_type = self._determine_guidance_type(child_emotion_state, situation_context)
            
            # 获取基础模板
            template = self.guidance_templates.get(guidance_type, {})
            
            # 根据年龄和情境调整
            adjusted_guidance = self._adjust_for_age_and_context(
                template, child_age, situation_context
            )
            
            # 根据家长经验水平调整
            final_guidance = self._adjust_for_parent_level(
                adjusted_guidance, parent_experience_level
            )
            
            # 确定紧急程度
            urgency = self._assess_urgency(child_emotion_state, situation_context)
            
            return ParentGuidanceRecommendation(
                guidance_id=f"guidance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                title=final_guidance.get("title", "家长指导"),
                category=guidance_type,
                urgency_level=urgency,
                description=final_guidance.get("description", ""),
                specific_actions=final_guidance.get("actions", []),
                what_to_say=final_guidance.get("what_to_say", []),
                what_not_to_say=final_guidance.get("what_not_to_say", []),
                expected_outcomes=final_guidance.get("expected_outcomes", []),
                follow_up_timeline=final_guidance.get("follow_up", "24小时内观察"),
                resources=final_guidance.get("resources", [])
            )
            
        except Exception as e:
            logger.error(f"家长指导生成失败: {str(e)}")
            return self._create_default_guidance()
    
    def _determine_guidance_type(
        self, 
        emotion_state: str, 
        context: Dict[str, Any]
    ) -> str:
        """确定指导类型"""
        
        emotion_mapping = {
            "anxious": "anxiety_support",
            "worried": "anxiety_support",
            "fearful": "anxiety_support",
            "angry": "anger_management",
            "frustrated": "anger_management",
            "irritated": "anger_management",
            "sad": "sadness_comfort",
            "depressed": "sadness_comfort",
            "lonely": "sadness_comfort"
        }
        
        return emotion_mapping.get(emotion_state, "general_support")
    
    def _adjust_for_age_and_context(
        self, 
        template: Dict[str, Any], 
        age: int, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据年龄和情境调整指导"""
        
        adjusted = template.copy()
        
        # 年龄调整
        if age < 6:
            # 学前儿童：更简单的语言，更多身体安慰
            adjusted["what_to_say"] = [
                phrase.replace("我理解", "妈妈/爸爸知道") 
                for phrase in adjusted.get("what_to_say", [])
            ]
            adjusted["actions"] = ["提供更多身体安慰"] + adjusted.get("actions", [])
        elif age > 12:
            # 青少年：更尊重独立性，更多讨论
            adjusted["actions"] = [
                action.replace("教授", "讨论") 
                for action in adjusted.get("actions", [])
            ]
        
        # 情境调整
        if context.get("location") == "public":
            adjusted["actions"] = [
                "先移到私密空间" if "公共场所" not in action else action
                for action in adjusted.get("actions", [])
            ]
        
        return adjusted
    
    def _adjust_for_parent_level(
        self, 
        guidance: Dict[str, Any], 
        level: str
    ) -> Dict[str, Any]:
        """根据家长经验水平调整"""
        
        adjusted = guidance.copy()
        
        if level == "beginner":
            # 新手家长：更详细的步骤，更多解释
            adjusted["description"] = "详细步骤指导：" + adjusted.get("description", "")
            adjusted["resources"] = [
                {"type": "video", "title": "基础育儿技巧", "url": "#"},
                {"type": "article", "title": "儿童情绪发展", "url": "#"}
            ]
        elif level == "advanced":
            # 有经验的家长：更简洁，更多高级策略
            adjusted["actions"] = adjusted.get("actions", [])[:3]  # 只保留核心建议
        
        return adjusted
    
    def _assess_urgency(
        self, 
        emotion_state: str, 
        context: Dict[str, Any]
    ) -> str:
        """评估紧急程度"""
        
        high_urgency_emotions = ["panic", "rage", "despair", "suicidal"]
        medium_urgency_emotions = ["severe_anxiety", "intense_anger", "deep_sadness"]
        
        if emotion_state in high_urgency_emotions:
            return "urgent"
        elif emotion_state in medium_urgency_emotions:
            return "high"
        elif context.get("intensity", 0) > 0.8:
            return "high"
        elif context.get("duration_hours", 0) > 24:
            return "medium"
        else:
            return "low"
    
    def _create_default_guidance(self) -> ParentGuidanceRecommendation:
        """创建默认指导"""
        return ParentGuidanceRecommendation(
            guidance_id="default_guidance",
            title="一般性家长指导",
            category="general_support",
            urgency_level="low",
            description="保持冷静，倾听孩子，提供支持",
            specific_actions=["倾听孩子的感受", "保持耐心", "寻求专业帮助"],
            what_to_say=["我在这里支持你", "告诉我你的感受"],
            what_not_to_say=["别想太多", "这没什么大不了的"],
            expected_outcomes=["孩子感到被理解", "情况逐步改善"],
            follow_up_timeline="24小时",
            resources=[]
        )


class ParentEducationService:
    """家长教育服务"""

    def __init__(self):
        self.education_content = self._load_education_content()
        self.learning_paths = self._create_learning_paths()

    def _load_education_content(self) -> Dict[str, Any]:
        """加载教育内容"""
        return {
            "child_development": {
                "0-5": [
                    {
                        "title": "学前儿童情绪发展特点",
                        "content": "学前儿童的情绪发展具有以下特点：情绪表达直接、变化快速、需要成人帮助调节...",
                        "key_takeaways": [
                            "情绪变化是正常的发展过程",
                            "成人的回应影响情绪发展",
                            "建立安全依恋关系很重要"
                        ],
                        "exercises": [
                            {"name": "情绪命名游戏", "description": "帮助孩子识别和命名情绪"},
                            {"name": "情绪温度计", "description": "用视觉工具表示情绪强度"}
                        ]
                    }
                ],
                "6-12": [
                    {
                        "title": "学龄期儿童心理特点",
                        "content": "学龄期儿童开始发展更复杂的情绪理解能力，同伴关系变得重要...",
                        "key_takeaways": [
                            "同伴关系对心理发展很重要",
                            "学业压力可能影响情绪",
                            "自我概念开始形成"
                        ],
                        "exercises": [
                            {"name": "友谊技能练习", "description": "角色扮演社交场景"},
                            {"name": "学习压力管理", "description": "制定学习计划和休息时间"}
                        ]
                    }
                ],
                "13-17": [
                    {
                        "title": "青少年心理发展",
                        "content": "青少年期是身心快速发展的时期，情绪波动较大，寻求独立...",
                        "key_takeaways": [
                            "情绪波动是正常的",
                            "需要平衡独立和支持",
                            "身份认同是重要任务"
                        ],
                        "exercises": [
                            {"name": "价值观探索", "description": "讨论个人价值观和目标"},
                            {"name": "沟通技巧练习", "description": "学习有效的亲子沟通"}
                        ]
                    }
                ]
            },
            "communication_skills": [
                {
                    "title": "有效的亲子沟通",
                    "content": "良好的沟通是建立亲子关系的基础。包括积极倾听、情绪验证、开放式提问等技巧...",
                    "key_takeaways": [
                        "倾听比说话更重要",
                        "验证孩子的感受",
                        "避免批判性语言"
                    ],
                    "exercises": [
                        {"name": "每日聊天时间", "description": "设定专门的亲子交流时间"},
                        {"name": "情绪检查", "description": "定期询问孩子的感受"}
                    ]
                }
            ],
            "behavior_management": [
                {
                    "title": "正面管教策略",
                    "content": "正面管教注重教育而非惩罚，帮助孩子学会自我管理和责任感...",
                    "key_takeaways": [
                        "设定清晰的界限和期望",
                        "使用自然后果而非惩罚",
                        "表扬具体行为而非笼统夸奖"
                    ],
                    "exercises": [
                        {"name": "家庭规则制定", "description": "与孩子一起制定家庭规则"},
                        {"name": "行为奖励系统", "description": "建立积极行为的奖励机制"}
                    ]
                }
            ]
        }

    def _create_learning_paths(self) -> Dict[str, Any]:
        """创建学习路径"""
        return {
            "new_parent": {
                "name": "新手家长基础课程",
                "duration_weeks": 4,
                "modules": [
                    "儿童发展基础",
                    "基本沟通技巧",
                    "情绪支持方法",
                    "行为引导策略"
                ]
            },
            "challenging_behavior": {
                "name": "应对挑战行为",
                "duration_weeks": 6,
                "modules": [
                    "理解行为背后的需求",
                    "预防策略",
                    "积极干预技巧",
                    "危机处理",
                    "长期行为改变",
                    "家庭支持系统"
                ]
            },
            "emotional_support": {
                "name": "情绪支持专家",
                "duration_weeks": 8,
                "modules": [
                    "情绪发展理论",
                    "情绪识别技巧",
                    "情绪调节教学",
                    "焦虑管理",
                    "抑郁预防",
                    "创伤知情护理",
                    "专业资源对接",
                    "家庭韧性建设"
                ]
            }
        }

    async def recommend_education_content(
        self,
        child_age: int,
        parent_concerns: List[str],
        parent_experience_level: str,
        available_time_minutes: int = 30
    ) -> List[ParentEducationContent]:
        """推荐教育内容"""

        try:
            recommendations = []

            # 根据年龄推荐发展相关内容
            age_group = self._get_age_group(child_age)
            dev_content = self.education_content["child_development"].get(age_group, [])

            for content in dev_content:
                if content.get("estimated_time", 30) <= available_time_minutes:
                    recommendations.append(self._create_education_content(
                        content, "child_development", age_group
                    ))

            # 根据家长关注点推荐内容
            for concern in parent_concerns:
                if concern in ["communication", "talking"]:
                    comm_content = self.education_content["communication_skills"]
                    for content in comm_content:
                        recommendations.append(self._create_education_content(
                            content, "communication_skills", "all_ages"
                        ))

                elif concern in ["behavior", "discipline"]:
                    behavior_content = self.education_content["behavior_management"]
                    for content in behavior_content:
                        recommendations.append(self._create_education_content(
                            content, "behavior_management", "all_ages"
                        ))

            # 根据经验水平调整难度
            filtered_recommendations = self._filter_by_experience_level(
                recommendations, parent_experience_level
            )

            return filtered_recommendations[:5]  # 返回前5个推荐

        except Exception as e:
            logger.error(f"教育内容推荐失败: {str(e)}")
            return []

    def _get_age_group(self, age: int) -> str:
        """获取年龄组"""
        if age <= 5:
            return "0-5"
        elif age <= 12:
            return "6-12"
        else:
            return "13-17"

    def _create_education_content(
        self,
        content_data: Dict[str, Any],
        category: str,
        age_group: str
    ) -> ParentEducationContent:
        """创建教育内容对象"""

        return ParentEducationContent(
            content_id=f"{category}_{age_group}_{hash(content_data['title'])}",
            title=content_data["title"],
            category=category,
            age_group=age_group,
            difficulty_level="beginner",
            content_type="article",
            content=content_data["content"],
            key_takeaways=content_data.get("key_takeaways", []),
            practical_exercises=content_data.get("exercises", []),
            estimated_time_minutes=content_data.get("estimated_time", 20)
        )

    def _filter_by_experience_level(
        self,
        content_list: List[ParentEducationContent],
        level: str
    ) -> List[ParentEducationContent]:
        """根据经验水平过滤内容"""

        if level == "beginner":
            return [c for c in content_list if c.difficulty_level in ["beginner"]]
        elif level == "intermediate":
            return [c for c in content_list if c.difficulty_level in ["beginner", "intermediate"]]
        else:
            return content_list


class FamilyInterventionPlanner:
    """家庭干预计划制定器"""

    def __init__(self):
        self.intervention_templates = self._load_intervention_templates()

    def _load_intervention_templates(self) -> Dict[str, Any]:
        """加载干预模板"""
        return {
            "anxiety_family_plan": {
                "goals": [
                    "减少孩子的焦虑水平",
                    "提高家庭应对焦虑的能力",
                    "建立支持性家庭环境"
                ],
                "family_activities": [
                    {
                        "name": "家庭放松时间",
                        "description": "每天晚上进行15分钟的家庭放松活动",
                        "frequency": "每日",
                        "participants": ["全家"],
                        "materials": ["舒缓音乐", "瑜伽垫"]
                    },
                    {
                        "name": "担忧分享圈",
                        "description": "每周家庭会议分享各自的担忧和解决方案",
                        "frequency": "每周",
                        "participants": ["全家"],
                        "materials": ["谈话棒", "记录本"]
                    }
                ],
                "parent_strategies": [
                    {
                        "strategy": "情绪验证",
                        "description": "当孩子表达焦虑时，首先验证其感受",
                        "example": "我理解你对考试感到紧张，这很正常"
                    },
                    {
                        "strategy": "渐进暴露",
                        "description": "逐步帮助孩子面对恐惧的情况",
                        "example": "先在家练习演讲，再到小群体，最后到班级"
                    }
                ]
            },
            "behavior_family_plan": {
                "goals": [
                    "改善孩子的行为表现",
                    "增强家庭规则的一致性",
                    "提高亲子关系质量"
                ],
                "family_activities": [
                    {
                        "name": "家庭规则制定",
                        "description": "全家一起制定和修订家庭规则",
                        "frequency": "每月",
                        "participants": ["全家"],
                        "materials": ["白板", "彩色笔"]
                    },
                    {
                        "name": "积极行为庆祝",
                        "description": "每周庆祝孩子的积极行为",
                        "frequency": "每周",
                        "participants": ["全家"],
                        "materials": ["奖励贴纸", "庆祝活动"]
                    }
                ],
                "parent_strategies": [
                    {
                        "strategy": "一致性执行",
                        "description": "父母双方保持规则执行的一致性",
                        "example": "事先商定规则和后果，避免当场争论"
                    },
                    {
                        "strategy": "正面强化",
                        "description": "及时表扬和奖励积极行为",
                        "example": "看到你主动收拾玩具，真是太棒了！"
                    }
                ]
            }
        }

    async def create_family_intervention_plan(
        self,
        child_id: str,
        parent_id: str,
        psychological_profile: PsychologicalProfileResult,
        family_goals: List[str],
        family_constraints: Dict[str, Any] = None
    ) -> FamilyInterventionPlan:
        """创建家庭干预计划"""

        try:
            # 确定主要干预重点
            primary_concerns = self._identify_primary_concerns(psychological_profile)

            # 选择合适的干预模板
            template = self._select_intervention_template(primary_concerns)

            # 个性化调整
            customized_plan = self._customize_plan(
                template, psychological_profile, family_goals, family_constraints
            )

            # 设置进度里程碑
            milestones = self._create_progress_milestones(customized_plan)

            # 制定复查时间表
            review_schedule = self._create_review_schedule()

            return FamilyInterventionPlan(
                plan_id=f"plan_{child_id}_{datetime.utcnow().strftime('%Y%m%d')}",
                child_id=child_id,
                parent_id=parent_id,
                intervention_goals=customized_plan["goals"],
                family_activities=customized_plan["family_activities"],
                parent_strategies=customized_plan["parent_strategies"],
                progress_milestones=milestones,
                review_schedule=review_schedule,
                success_metrics=customized_plan.get("success_metrics", []),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"家庭干预计划创建失败: {str(e)}")
            return self._create_default_plan(child_id, parent_id)

    def _identify_primary_concerns(
        self,
        profile: PsychologicalProfileResult
    ) -> List[str]:
        """识别主要关注点"""

        concerns = []

        # 基于风险评估
        risk_factors = profile.risk_assessment.get("risk_factors", [])
        if "anxiety" in risk_factors:
            concerns.append("anxiety")
        if "behavioral_issues" in risk_factors:
            concerns.append("behavior")
        if "social_difficulties" in risk_factors:
            concerns.append("social")

        # 基于情绪模式
        for pattern in profile.emotional_patterns:
            if pattern.pattern_type == "stress_response" and pattern.intensity > 0.7:
                concerns.append("stress_management")
            elif pattern.pattern_type == "social_anxiety":
                concerns.append("social")

        return list(set(concerns))

    def _select_intervention_template(self, concerns: List[str]) -> Dict[str, Any]:
        """选择干预模板"""

        if "anxiety" in concerns or "stress_management" in concerns:
            return self.intervention_templates["anxiety_family_plan"]
        elif "behavior" in concerns:
            return self.intervention_templates["behavior_family_plan"]
        else:
            # 默认综合计划
            return {
                "goals": ["促进孩子心理健康发展", "增强家庭凝聚力"],
                "family_activities": [],
                "parent_strategies": []
            }

    def _customize_plan(
        self,
        template: Dict[str, Any],
        profile: PsychologicalProfileResult,
        family_goals: List[str],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """个性化调整计划"""

        customized = template.copy()

        # 整合家庭目标
        if family_goals:
            customized["goals"].extend(family_goals)

        # 根据约束条件调整
        if constraints:
            time_constraint = constraints.get("available_time_per_day", 60)
            if time_constraint < 30:
                # 时间有限，简化活动
                customized["family_activities"] = [
                    activity for activity in customized["family_activities"]
                    if activity.get("duration_minutes", 30) <= time_constraint
                ]

        # 根据孩子年龄调整
        child_age = constraints.get("child_age", 8) if constraints else 8
        if child_age < 6:
            # 学前儿童：更多游戏化活动
            for activity in customized["family_activities"]:
                activity["description"] = activity["description"].replace("讨论", "游戏")

        return customized

    def _create_progress_milestones(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建进度里程碑"""

        milestones = []

        # 短期里程碑（1-2周）
        milestones.append({
            "timeline": "2周",
            "description": "家庭成员熟悉新的活动和策略",
            "success_criteria": ["活动参与率达到80%", "策略使用频率增加"],
            "measurement_method": "家长记录和观察"
        })

        # 中期里程碑（4-6周）
        milestones.append({
            "timeline": "6周",
            "description": "观察到孩子行为或情绪的积极变化",
            "success_criteria": ["目标行为改善30%", "情绪稳定性提升"],
            "measurement_method": "行为记录表和情绪评估"
        })

        # 长期里程碑（8-12周）
        milestones.append({
            "timeline": "12周",
            "description": "建立稳定的家庭支持模式",
            "success_criteria": ["家庭关系质量提升", "孩子自我调节能力增强"],
            "measurement_method": "家庭功能评估和专业评估"
        })

        return milestones

    def _create_review_schedule(self) -> List[datetime]:
        """创建复查时间表"""

        now = datetime.utcnow()
        schedule = []

        # 每2周复查一次，共6次
        for i in range(6):
            review_date = now + timedelta(weeks=2*(i+1))
            schedule.append(review_date)

        return schedule

    def _create_default_plan(self, child_id: str, parent_id: str) -> FamilyInterventionPlan:
        """创建默认计划"""

        return FamilyInterventionPlan(
            plan_id=f"default_plan_{child_id}",
            child_id=child_id,
            parent_id=parent_id,
            intervention_goals=["促进孩子健康发展"],
            family_activities=[],
            parent_strategies=[],
            progress_milestones=[],
            review_schedule=[],
            success_metrics=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
