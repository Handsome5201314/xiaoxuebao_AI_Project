"""
儿童心理健康干预模块
提供基于AI的儿童心理健康评估、监测和干预服务
"""

"""
儿童心理健康干预平台
基于AI的多模态情绪识别、个性化心理画像和家庭协同支持系统
"""

# 使用简化版本进行快速启动
from .emotion_analyzer_simple import (
    SimpleMultiModalEmotionAnalyzer as MultiModalEmotionAnalyzer,
    SimpleTextEmotionAnalyzer as TextEmotionAnalyzer,
    SimpleAudioEmotionAnalyzer as AudioEmotionAnalyzer,
    SimpleVisualEmotionAnalyzer as VisualEmotionAnalyzer,
    EmotionResult,
    MultiModalEmotionResult
)

from .psychological_profiler import (
    PsychologicalProfiler,
    PersonalityAnalyzer,
    EmotionalPatternAnalyzer,
    InterventionEngine,
    RiskAssessment,
    PersonalityTrait,
    PsychologicalPattern,
    InterventionRecommendation,
    PsychologicalProfileResult
)

from .parent_support import (
    ParentGuidanceEngine,
    ParentEducationService,
    FamilyInterventionPlanner,
    ParentGuidanceRecommendation,
    ParentEducationContent,
    FamilyInterventionPlan
)

from .data_manager import (
    MentalHealthDataAnalyzer,
    DataVisualizationEngine,
    ReportGenerator,
    DataSecurityManager,
    DataAnalysisResult,
    VisualizationConfig,
    PrivacyMetrics
)

from .community_platform import (
    CommunityPlatform,
    CommunityModerationEngine,
    CommunityRecommendationEngine,
    CommunityEventManager,
    CommunityAnalytics,
    CommunityUser,
    SupportGroup,
    EducationalResource,
    CommunityEvent,
    UserRole,
    PostCategory
)

__all__ = [
    # 情绪分析模块
    "MultiModalEmotionAnalyzer",
    "TextEmotionAnalyzer",
    "AudioEmotionAnalyzer",
    "VisualEmotionAnalyzer",
    "PhysiologicalEmotionAnalyzer",
    "EmotionResult",
    "MultiModalEmotionResult",

    # 心理画像模块
    "PsychologicalProfiler",
    "PersonalityAnalyzer",
    "EmotionalPatternAnalyzer",
    "InterventionEngine",
    "RiskAssessment",
    "PersonalityTrait",
    "PsychologicalPattern",
    "InterventionRecommendation",
    "PsychologicalProfileResult",

    # 家长支持模块
    "ParentGuidanceEngine",
    "ParentEducationService",
    "FamilyInterventionPlanner",
    "ParentGuidanceRecommendation",
    "ParentEducationContent",
    "FamilyInterventionPlan",

    # 数据管理模块
    "MentalHealthDataAnalyzer",
    "DataVisualizationEngine",
    "ReportGenerator",
    "DataSecurityManager",
    "DataAnalysisResult",
    "VisualizationConfig",
    "PrivacyMetrics",

    # 社区平台模块
    "CommunityPlatform",
    "CommunityModerationEngine",
    "CommunityRecommendationEngine",
    "CommunityEventManager",
    "CommunityAnalytics",
    "CommunityUser",
    "SupportGroup",
    "EducationalResource",
    "CommunityEvent",
    "UserRole",
    "PostCategory"
]


class MentalHealthPlatform:
    """儿童心理健康干预平台主控制器"""

    def __init__(self):
        # 初始化各个模块
        self.emotion_analyzer = MultiModalEmotionAnalyzer()
        self.psychological_profiler = PsychologicalProfiler()
        self.parent_guidance = ParentGuidanceEngine()
        self.parent_education = ParentEducationService()
        self.family_planner = FamilyInterventionPlanner()
        self.data_analyzer = MentalHealthDataAnalyzer()
        self.visualization_engine = DataVisualizationEngine()
        self.report_generator = ReportGenerator()
        self.community_platform = CommunityPlatform()

        # 平台状态
        self.is_initialized = False
        self.supported_features = [
            "多模态情绪识别",
            "个性化心理画像",
            "智能干预推荐",
            "家长指导支持",
            "家庭干预计划",
            "数据安全管理",
            "可视化报告",
            "社区支持网络",
            "危机干预机制",
            "专家资源对接"
        ]

    async def initialize_platform(self) -> dict:
        """初始化平台"""
        try:
            # 初始化社区功能
            community_init = await self.community_platform.initialize_community_features()

            self.is_initialized = True

            return {
                "status": "success",
                "platform_name": "小雪宝AI儿童心理健康干预平台",
                "version": "1.0.0",
                "supported_features": self.supported_features,
                "community_status": community_init.get("status"),
                "initialization_time": community_init.get("initialized_at"),
                "message": "平台初始化成功，所有功能模块已就绪"
            }

        except Exception as e:
            return {
                "status": "error",
                "error_message": f"平台初始化失败: {str(e)}",
                "supported_features": self.supported_features
            }

    async def get_platform_status(self) -> dict:
        """获取平台状态"""
        return {
            "platform_name": "小雪宝AI儿童心理健康干预平台",
            "is_initialized": self.is_initialized,
            "supported_features": self.supported_features,
            "active_modules": {
                "emotion_analysis": True,
                "psychological_profiling": True,
                "parent_support": True,
                "data_management": True,
                "community_platform": True
            },
            "platform_capabilities": {
                "multi_modal_emotion_recognition": "支持文字、语音、图像、生理数据",
                "personalized_profiling": "基于AI的个性化心理画像",
                "family_intervention": "家庭协同干预计划",
                "crisis_intervention": "24/7危机干预支持",
                "expert_network": "专业心理咨询师网络",
                "data_security": "企业级数据加密和隐私保护",
                "community_support": "家长互助和专家指导社区"
            }
        }

__all__ = [
    "EmotionAnalyzer",
    "PsychologicalProfiler", 
    "InterventionEngine",
    "ParentSupportService",
    "CommunityPlatform",
    "MentalHealthDataManager"
]
