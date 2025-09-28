"""
小雪宝AI助手 - 最小化启动版本
用于快速演示和测试
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
import os
from datetime import datetime

# 简化配置
class Settings:
    APP_NAME = "小雪宝AI助手"
    APP_VERSION = "1.0.0"
    DEBUG = True
    CORS_ORIGINS = ["*"]  # 开发环境允许所有源

settings = Settings()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于AI的儿童心理健康干预平台",
    debug=settings.DEBUG
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="./static"), name="static")

# 响应模型
class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime

# 根路由 - 重定向到静态页面
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

# 响应模型

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return StandardResponse(
        success=True,
        message="服务运行正常",
        data={
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION
        },
        timestamp=datetime.utcnow()
    )

# API版本信息
@app.get("/api/versions")
async def get_api_versions():
    """获取API版本信息"""
    return StandardResponse(
        success=True,
        message="API版本信息获取成功",
        data={
            "v1": {
                "version": "1.0.0",
                "status": "stable",
                "base_url": "/api/v1",
                "features": [
                    "心理健康评估",
                    "情绪分析",
                    "家长指导",
                    "社区支持"
                ]
            }
        },
        timestamp=datetime.utcnow()
    )

# 心理健康模块演示API
@app.get("/api/v1/mental-health/status")
async def get_mental_health_status():
    """获取心理健康平台状态"""
    return StandardResponse(
        success=True,
        message="心理健康平台状态获取成功",
        data={
            "platform_name": "小雪宝AI儿童心理健康干预平台",
            "is_initialized": True,
            "supported_features": [
                "多模态情绪识别",
                "个性化心理画像",
                "智能干预推荐",
                "家长协同支持",
                "家庭干预计划",
                "数据安全管理",
                "可视化报告",
                "社区支持网络",
                "危机干预机制",
                "专家资源对接"
            ],
            "active_modules": {
                "emotion_analysis": True,
                "psychological_profiling": True,
                "parent_support": True,
                "data_management": True,
                "community_platform": True
            }
        },
        timestamp=datetime.utcnow()
    )

# 情绪分析演示API
@app.post("/api/v1/mental-health/emotion/analyze")
async def analyze_emotion_demo(
    text_data: Optional[str] = None,
    child_age: Optional[int] = None
):
    """情绪分析演示"""
    
    if not text_data:
        raise HTTPException(status_code=400, detail="请提供文本数据")
    
    # 简单的情绪分析演示
    emotions = {
        "开心": {"emotion": "happy", "confidence": 0.85, "valence": 0.8},
        "难过": {"emotion": "sad", "confidence": 0.90, "valence": -0.7},
        "焦虑": {"emotion": "anxious", "confidence": 0.88, "valence": -0.5},
        "生气": {"emotion": "angry", "confidence": 0.82, "valence": -0.8},
        "平静": {"emotion": "calm", "confidence": 0.75, "valence": 0.3}
    }
    
    # 简单关键词匹配
    detected_emotion = "neutral"
    confidence = 0.5
    valence = 0.0
    
    for keyword, emotion_data in emotions.items():
        if keyword in text_data:
            detected_emotion = emotion_data["emotion"]
            confidence = emotion_data["confidence"]
            valence = emotion_data["valence"]
            break
    
    return StandardResponse(
        success=True,
        message="情绪分析完成",
        data={
            "primary_emotion": detected_emotion,
            "confidence": confidence,
            "intensity": confidence * 0.8,
            "valence": valence,
            "arousal": 0.6 if detected_emotion != "calm" else 0.3,
            "analysis_text": text_data,
            "child_age": child_age,
            "recommendations": [
                "建议关注孩子的情绪变化",
                "提供适当的情感支持",
                "如有需要，寻求专业帮助"
            ]
        },
        timestamp=datetime.utcnow()
    )

# 家长指导演示API
@app.post("/api/v1/mental-health/parent/guidance")
async def get_parent_guidance_demo(
    child_emotion_state: str,
    child_age: int,
    situation_context: Optional[str] = None
):
    """家长指导建议演示"""
    
    guidance_templates = {
        "happy": {
            "title": "孩子情绪积极时的指导",
            "actions": ["鼓励孩子分享快乐", "强化积极行为", "创造更多快乐时光"],
            "what_to_say": ["我很高兴看到你这么开心！", "你做得很棒！", "我们一起庆祝一下吧！"]
        },
        "sad": {
            "title": "孩子难过时的指导",
            "actions": ["倾听孩子的感受", "提供安慰和支持", "帮助孩子表达情绪"],
            "what_to_say": ["我理解你的感受", "有什么我可以帮助你的吗？", "我们一起面对这个问题"]
        },
        "anxious": {
            "title": "孩子焦虑时的指导",
            "actions": ["保持冷静", "教授放松技巧", "逐步解决问题"],
            "what_to_say": ["深呼吸，我们一起来", "你是安全的", "我们可以慢慢来"]
        }
    }
    
    guidance = guidance_templates.get(child_emotion_state, guidance_templates["sad"])
    
    return StandardResponse(
        success=True,
        message="家长指导建议生成成功",
        data={
            "guidance_id": f"guidance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "title": guidance["title"],
            "child_emotion_state": child_emotion_state,
            "child_age": child_age,
            "situation_context": situation_context,
            "specific_actions": guidance["actions"],
            "what_to_say": guidance["what_to_say"],
            "what_not_to_say": [
                "不要说'没关系'",
                "避免忽视孩子的感受",
                "不要急于给出解决方案"
            ],
            "follow_up_timeline": "24小时内观察情绪变化",
            "urgency_level": "normal"
        },
        timestamp=datetime.utcnow()
    )

# 社区功能演示API
@app.get("/api/v1/mental-health/community/personalized")
async def get_community_demo():
    """个性化社区体验演示"""
    
    return StandardResponse(
        success=True,
        message="个性化社区体验获取成功",
        data={
            "recommendations": {
                "posts": [
                    {
                        "post_id": "post_001",
                        "title": "如何帮助焦虑的孩子",
                        "category": "emotional_support",
                        "author_role": "expert"
                    },
                    {
                        "post_id": "post_002",
                        "title": "分享我家孩子克服社交恐惧的经历",
                        "category": "experience_sharing",
                        "author_role": "parent"
                    }
                ],
                "support_groups": [
                    {
                        "group_id": "group_001",
                        "name": "小学生家长互助群",
                        "description": "小学阶段儿童心理发展和学习支持",
                        "member_count": 156
                    }
                ],
                "educational_resources": [
                    {
                        "resource_id": "resource_001",
                        "title": "儿童心理发展基础知识",
                        "content_type": "article",
                        "difficulty_level": "beginner",
                        "rating": 4.8
                    }
                ]
            },
            "community_status": {
                "user_role": "parent",
                "reputation_score": 100,
                "community_contributions": 5,
                "support_connections": 3
            }
        },
        timestamp=datetime.utcnow()
    )

if __name__ == "__main__":
    print("🚀 启动小雪宝AI助手...")
    print("📍 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔧 管理界面: http://localhost:8000/redoc")
    
    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
