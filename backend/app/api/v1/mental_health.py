"""
心理健康模块API路由
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.core.deps import get_current_user
from app.core.logging import get_logger
from app.modules.mental_health import (
    MentalHealthPlatform,
    MultiModalEmotionAnalyzer,
    PsychologicalProfiler,
    ParentGuidanceEngine,
    MentalHealthDataAnalyzer,
    CommunityPlatform
)
from app.schemas.response import StandardResponse

logger = get_logger(__name__)
router = APIRouter()

# 全局平台实例
mental_health_platform = MentalHealthPlatform()


@router.on_event("startup")
async def startup_mental_health():
    """启动时初始化心理健康平台"""
    try:
        init_result = await mental_health_platform.initialize_platform()
        logger.info(f"心理健康平台初始化: {init_result}")
    except Exception as e:
        logger.error(f"心理健康平台初始化失败: {str(e)}")


@router.get("/status", response_model=StandardResponse)
async def get_platform_status():
    """获取平台状态"""
    try:
        status = await mental_health_platform.get_platform_status()
        return StandardResponse(
            success=True,
            data=status,
            message="平台状态获取成功"
        )
    except Exception as e:
        logger.error(f"获取平台状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取平台状态失败")


@router.post("/emotion/analyze", response_model=StandardResponse)
async def analyze_emotion(
    text_data: Optional[str] = None,
    audio_file: Optional[UploadFile] = File(None),
    image_file: Optional[UploadFile] = File(None),
    child_age: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user)
):
    """多模态情绪分析"""
    try:
        # 处理上传的文件
        audio_data = None
        image_data = None
        
        if audio_file:
            audio_data = await audio_file.read()
        
        if image_file:
            image_data = await image_file.read()
        
        # 进行情绪分析
        result = await mental_health_platform.emotion_analyzer.analyze_multimodal_emotion(
            text_data=text_data,
            audio_data=audio_data,
            image_data=image_data,
            child_age=child_age,
            context=context
        )
        
        return StandardResponse(
            success=True,
            data={
                "primary_emotion": result.primary_emotion,
                "confidence": result.confidence,
                "intensity": result.intensity,
                "modality_results": {
                    modality: {
                        "emotion": res.emotion,
                        "confidence": res.confidence,
                        "intensity": res.intensity,
                        "valence": res.valence,
                        "arousal": res.arousal
                    }
                    for modality, res in result.modality_results.items()
                },
                "fusion_weights": result.fusion_weights,
                "timestamp": result.timestamp.isoformat()
            },
            message="情绪分析完成"
        )
        
    except Exception as e:
        logger.error(f"情绪分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="情绪分析失败")


@router.post("/profile/generate", response_model=StandardResponse)
async def generate_psychological_profile(
    child_id: str,
    child_age: int,
    behavioral_data: Optional[Dict[str, Any]] = None,
    family_context: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user)
):
    """生成心理画像"""
    try:
        # 这里应该从数据库获取情绪历史数据
        # 暂时使用空列表，实际应用中需要实现数据获取逻辑
        emotion_history = []
        
        profile = await mental_health_platform.psychological_profiler.generate_psychological_profile(
            child_id=child_id,
            emotion_history=emotion_history,
            child_age=child_age,
            behavioral_data=behavioral_data,
            family_context=family_context
        )
        
        return StandardResponse(
            success=True,
            data={
                "child_id": profile.child_id,
                "personality_traits": [
                    {
                        "name": trait.name,
                        "score": trait.score,
                        "confidence": trait.confidence,
                        "description": trait.description,
                        "development_stage": trait.development_stage
                    }
                    for trait in profile.personality_traits
                ],
                "emotional_patterns": [
                    {
                        "pattern_type": pattern.pattern_type,
                        "frequency": pattern.frequency,
                        "intensity": pattern.intensity,
                        "triggers": pattern.triggers,
                        "contexts": pattern.contexts,
                        "trend": pattern.trend
                    }
                    for pattern in profile.emotional_patterns
                ],
                "stress_triggers": profile.stress_triggers,
                "coping_mechanisms": profile.coping_mechanisms,
                "developmental_stage": profile.developmental_stage,
                "risk_assessment": profile.risk_assessment,
                "intervention_recommendations": [
                    {
                        "intervention_type": rec.intervention_type,
                        "priority": rec.priority,
                        "description": rec.description,
                        "activities": rec.activities,
                        "expected_outcome": rec.expected_outcome,
                        "duration_weeks": rec.duration_weeks,
                        "success_metrics": rec.success_metrics
                    }
                    for rec in profile.intervention_recommendations
                ],
                "confidence_score": profile.confidence_score,
                "last_updated": profile.last_updated.isoformat()
            },
            message="心理画像生成成功"
        )
        
    except Exception as e:
        logger.error(f"心理画像生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail="心理画像生成失败")


@router.post("/parent/guidance", response_model=StandardResponse)
async def get_parent_guidance(
    child_emotion_state: str,
    situation_context: Dict[str, Any],
    child_age: int,
    parent_experience_level: str = "beginner",
    current_user = Depends(get_current_user)
):
    """获取家长指导建议"""
    try:
        guidance = await mental_health_platform.parent_guidance.generate_parent_guidance(
            child_emotion_state=child_emotion_state,
            situation_context=situation_context,
            child_age=child_age,
            parent_experience_level=parent_experience_level
        )
        
        return StandardResponse(
            success=True,
            data={
                "guidance_id": guidance.guidance_id,
                "title": guidance.title,
                "category": guidance.category,
                "urgency_level": guidance.urgency_level,
                "description": guidance.description,
                "specific_actions": guidance.specific_actions,
                "what_to_say": guidance.what_to_say,
                "what_not_to_say": guidance.what_not_to_say,
                "expected_outcomes": guidance.expected_outcomes,
                "follow_up_timeline": guidance.follow_up_timeline,
                "resources": guidance.resources
            },
            message="家长指导建议生成成功"
        )
        
    except Exception as e:
        logger.error(f"家长指导生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail="家长指导生成失败")


@router.get("/parent/education", response_model=StandardResponse)
async def get_parent_education_content(
    child_age: int,
    parent_concerns: List[str] = [],
    parent_experience_level: str = "beginner",
    available_time_minutes: int = 30,
    current_user = Depends(get_current_user)
):
    """获取家长教育内容推荐"""
    try:
        content = await mental_health_platform.parent_education.recommend_education_content(
            child_age=child_age,
            parent_concerns=parent_concerns,
            parent_experience_level=parent_experience_level,
            available_time_minutes=available_time_minutes
        )
        
        return StandardResponse(
            success=True,
            data=[
                {
                    "content_id": item.content_id,
                    "title": item.title,
                    "category": item.category,
                    "age_group": item.age_group,
                    "difficulty_level": item.difficulty_level,
                    "content_type": item.content_type,
                    "content": item.content,
                    "key_takeaways": item.key_takeaways,
                    "practical_exercises": item.practical_exercises,
                    "estimated_time_minutes": item.estimated_time_minutes
                }
                for item in content
            ],
            message="教育内容推荐成功"
        )
        
    except Exception as e:
        logger.error(f"教育内容推荐失败: {str(e)}")
        raise HTTPException(status_code=500, detail="教育内容推荐失败")


@router.post("/data/analyze", response_model=StandardResponse)
async def analyze_mental_health_data(
    child_id: str,
    time_period_days: int = 30,
    current_user = Depends(get_current_user)
):
    """分析心理健康数据"""
    try:
        analysis = await mental_health_platform.data_analyzer.analyze_emotion_trends(
            child_id=child_id,
            time_period_days=time_period_days,
            user_id=current_user.id
        )
        
        return StandardResponse(
            success=True,
            data={
                "analysis_id": analysis.analysis_id,
                "child_id": analysis.child_id,
                "analysis_type": analysis.analysis_type,
                "time_period": analysis.time_period,
                "key_insights": analysis.key_insights,
                "trends": analysis.trends,
                "recommendations": analysis.recommendations,
                "confidence_score": analysis.confidence_score,
                "generated_at": analysis.generated_at.isoformat()
            },
            message="数据分析完成"
        )
        
    except Exception as e:
        logger.error(f"数据分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="数据分析失败")


@router.get("/community/personalized", response_model=StandardResponse)
async def get_personalized_community_experience(
    current_user = Depends(get_current_user)
):
    """获取个性化社区体验"""
    try:
        # 构建用户档案（实际应用中应从数据库获取）
        user_profile = {
            "child_age": 8,
            "concerns": ["anxiety", "behavior"],
            "parenting_experience": "beginner",
            "role": "parent",
            "reputation_score": 100,
            "post_count": 5,
            "connections": 3
        }
        
        experience = await mental_health_platform.community_platform.get_personalized_community_experience(
            user_id=current_user.id,
            user_profile=user_profile
        )
        
        return StandardResponse(
            success=True,
            data=experience,
            message="个性化社区体验获取成功"
        )
        
    except Exception as e:
        logger.error(f"个性化社区体验获取失败: {str(e)}")
        raise HTTPException(status_code=500, detail="个性化社区体验获取失败")


@router.get("/report/comprehensive", response_model=StandardResponse)
async def generate_comprehensive_report(
    child_id: str,
    report_period_days: int = 30,
    include_charts: bool = True,
    current_user = Depends(get_current_user)
):
    """生成综合报告"""
    try:
        report = await mental_health_platform.report_generator.generate_comprehensive_report(
            child_id=child_id,
            report_period_days=report_period_days,
            user_id=current_user.id,
            include_charts=include_charts
        )
        
        return StandardResponse(
            success=True,
            data=report,
            message="综合报告生成成功"
        )
        
    except Exception as e:
        logger.error(f"综合报告生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail="综合报告生成失败")
