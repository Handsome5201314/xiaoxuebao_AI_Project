#!/usr/bin/env python3
"""
小雪宝AI助手 - 完整版API服务器
包含AI聊天代理功能
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
import httpx
import json
import asyncio
from datetime import datetime

# 导入AI情绪分析器和知识库
try:
    from app.modules.mental_health.ai_emotion_analyzer import ai_emotion_analyzer
    AI_EMOTION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI情绪分析器导入失败: {e}")
    AI_EMOTION_AVAILABLE = False

try:
    from app.modules.knowledge_base import knowledge_base
    KNOWLEDGE_BASE_AVAILABLE = True
    print("✅ 知识库模块导入成功")
except ImportError as e:
    print(f"⚠️ 知识库导入失败: {e}")
    KNOWLEDGE_BASE_AVAILABLE = False

# 创建FastAPI应用
app = FastAPI(
    title="小雪宝AI助手",
    description="基于AI的儿童心理健康干预平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    source: str = "小雪宝AI助手"
    confidence: float = 0.9

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime

# 根路由 - 返回新的主页面
@app.get("/")
async def root():
    """返回主页"""
    return FileResponse("static/index_new.html")

# 旧版主页面（备用）
@app.get("/old")
async def old_page():
    """返回旧版主页面"""
    return FileResponse("static/index.html")

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return StandardResponse(
        success=True,
        message="服务运行正常",
        data={
            "status": "healthy",
            "app_name": "小雪宝AI助手",
            "version": "1.0.0"
        },
        timestamp=datetime.utcnow()
    )

# AI聊天代理API
@app.post("/api/chat")
async def chat_proxy(chat_message: ChatMessage):
    """AI聊天代理 - 集成知识库的智能问答"""

    try:
        # 优先使用知识库增强的AI回答
        if KNOWLEDGE_BASE_AVAILABLE:
            try:
                kb_result = await knowledge_base.answer_question(chat_message.message)

                if kb_result["answer"]:
                    return ChatResponse(
                        answer=kb_result["answer"],
                        source=kb_result["source"],
                        confidence=kb_result["confidence"]
                    )

            except Exception as kb_error:
                logger.warning(f"知识库查询失败，尝试直接AI调用: {kb_error}")

        # 备用：直接调用AI API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://cloud.siliconflow.cn/api/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer sk-hclwuosimfqpztfimjagookkkpbcqianfcihthgsvasynbrv"
                    },
                    json={
                        "model": "Qwen/Qwen3-8B",
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是小雪宝AI助手，专注于白血病知识解答和儿童心理健康支持。请用温暖、专业、通俗易懂的语言回答用户问题。如果涉及医疗建议，请提醒用户咨询专业医生。重点关注：1）白血病相关知识 2）儿童心理健康 3）家长支持指导 4）康复期间的生活建议。"
                            },
                            {
                                "role": "user",
                                "content": chat_message.message
                            }
                        ],
                        "max_tokens": 1024,
                        "temperature": 0.7,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                    if ai_response:
                        return ChatResponse(
                            answer=ai_response,
                            source="小雪宝AI助手 (Qwen3-8B)",
                            confidence=0.95
                        )

        except Exception as api_error:
            logger.warning(f"AI API调用失败，使用备用响应: {api_error}")

        # 备用响应系统
        message = chat_message.message.lower()

        # 基于关键词的智能响应系统
        responses = {
            "你好": "您好！我是小雪宝AI助手，专门为白血病患儿及家属提供心理健康支持。有什么我可以帮助您的吗？",
            "心理": "心理健康对于白血病患儿的康复非常重要。我们提供情绪识别、心理疏导和家庭支持等服务。您想了解哪个方面？",
            "焦虑": "面对疾病，感到焦虑是很正常的。建议您：1）深呼吸放松 2）与家人朋友交流 3）保持规律作息 4）如需要可寻求专业心理咨询。",
            "治疗": "白血病的治疗需要专业医生指导。在治疗过程中，保持积极心态很重要。我们可以为您提供心理支持和康复指导。",
            "家长": "作为家长，您的情绪状态会影响孩子。建议：1）保持冷静和乐观 2）学习疾病相关知识 3）与医护团队密切配合 4）关注自己的心理健康。",
            "孩子": "每个孩子都是独特的。在治疗期间，给予孩子足够的关爱和陪伴，帮助他们表达情感，保持与同龄人的适当交流。",
            "饮食": "营养对康复很重要。建议遵循医生的饮食指导，保证营养均衡，避免生冷食物，注意食品安全。",
            "运动": "适当的运动有助于康复，但需要根据病情和医生建议进行。可以选择散步、轻柔的伸展运动等。"
        }

        # 查找匹配的关键词
        response_text = "感谢您的提问。作为小雪宝AI助手，我致力于为白血病患儿及家属提供专业的心理健康支持。如果您有具体的问题，请详细描述，我会尽力为您提供帮助。同时，请记住，对于医疗问题，一定要咨询专业医生。"

        for keyword, response in responses.items():
            if keyword in message:
                response_text = response
                break

        return ChatResponse(
            answer=response_text,
            source="小雪宝AI助手 (备用模式)",
            confidence=0.8
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天服务暂时不可用: {str(e)}")

# 心理健康评估API
@app.post("/api/v1/mental-health/emotion/analyze")
async def analyze_emotion(
    text_data: Optional[str] = None,
    child_age: Optional[int] = None
):
    """AI驱动的情绪分析"""

    if not text_data:
        raise HTTPException(status_code=400, detail="请提供文本数据")

    try:
        # 使用AI情绪分析器
        if AI_EMOTION_AVAILABLE:
            if child_age:
                emotion_result = await ai_emotion_analyzer.analyze_child_emotion_with_age(
                    text_data, child_age, "白血病患儿心理健康评估"
                )
            else:
                emotion_result = await ai_emotion_analyzer.analyze_text_emotion(
                    text_data, "心理健康评估"
                )

            return StandardResponse(
                success=True,
                message="AI情绪分析完成",
                data={
                    "primary_emotion": emotion_result.primary_emotion,
                    "confidence": emotion_result.confidence,
                    "intensity": emotion_result.intensity,
                    "sentiment_score": emotion_result.sentiment_score,
                    "emotions_detected": emotion_result.emotions_detected,
                    "emotional_keywords": emotion_result.emotional_keywords,
                    "analysis_text": text_data,
                    "child_age": child_age,
                    "ai_model": emotion_result.ai_model,
                    "recommendations": emotion_result.suggestions,
                    "analysis_timestamp": emotion_result.timestamp.isoformat()
                },
                timestamp=datetime.utcnow()
            )

        # 备用简单分析
        emotions = {
            "开心": {"emotion": "happy", "confidence": 0.85, "valence": 0.8},
            "高兴": {"emotion": "happy", "confidence": 0.85, "valence": 0.8},
            "快乐": {"emotion": "happy", "confidence": 0.85, "valence": 0.8},
            "难过": {"emotion": "sad", "confidence": 0.90, "valence": -0.7},
            "伤心": {"emotion": "sad", "confidence": 0.90, "valence": -0.7},
            "焦虑": {"emotion": "anxious", "confidence": 0.88, "valence": -0.5},
            "紧张": {"emotion": "anxious", "confidence": 0.88, "valence": -0.5},
            "担心": {"emotion": "anxious", "confidence": 0.88, "valence": -0.5},
            "生气": {"emotion": "angry", "confidence": 0.82, "valence": -0.8},
            "愤怒": {"emotion": "angry", "confidence": 0.82, "valence": -0.8},
            "平静": {"emotion": "calm", "confidence": 0.75, "valence": 0.3},
            "放松": {"emotion": "calm", "confidence": 0.75, "valence": 0.3}
        }

        # 关键词匹配
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
            message="情绪分析完成（备用模式）",
            data={
                "primary_emotion": detected_emotion,
                "confidence": confidence,
                "intensity": confidence * 0.8,
                "sentiment_score": valence,
                "analysis_text": text_data,
                "child_age": child_age,
                "ai_model": "备用分析器",
                "recommendations": [
                    "建议关注孩子的情绪变化",
                    "提供适当的情感支持",
                    "如有需要，寻求专业帮助"
                ]
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情绪分析服务暂时不可用: {str(e)}")

# 家长指导API
@app.post("/api/v1/mental-health/parent/guidance")
async def get_parent_guidance(
    child_emotion_state: str,
    child_age: int,
    situation_context: Optional[str] = None
):
    """家长指导建议"""
    
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
        },
        "angry": {
            "title": "孩子生气时的指导",
            "actions": ["保持冷静", "给孩子时间冷静", "帮助识别愤怒原因"],
            "what_to_say": ["我看到你很生气", "我们来谈谈发生了什么", "愤怒是正常的感受"]
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

# 知识库搜索API
@app.get("/api/v1/knowledge/search")
async def search_knowledge(q: str, limit: int = 5, category: str = None, min_score: float = 0.0):
    """专业知识库搜索

    Args:
        q: 搜索查询词
        limit: 返回结果数量限制
        category: 指定搜索分类
        min_score: 最低相关性分数阈值
    """

    try:
        if KNOWLEDGE_BASE_AVAILABLE:
            # 使用增强版知识库搜索
            search_result = await knowledge_base.search_knowledge(q, limit, category, min_score)

            results = []
            for item in search_result.items:
                results.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                    "full_content": item.content,
                    "category": item.category,
                    "keywords": item.keywords,
                    "relevance_score": round(item.relevance_score, 2),
                    "source": item.source
                })

            return StandardResponse(
                success=True,
                message=f"找到 {search_result.total_results} 条相关信息",
                data={
                    "query": q,
                    "total": search_result.total_results,
                    "search_time": round(search_result.search_time, 3),
                    "results": results,
                    "filters": {
                        "category": category,
                        "min_score": min_score
                    },
                    "timestamp": search_result.timestamp.isoformat()
                },
                timestamp=datetime.utcnow()
            )

        # 备用搜索逻辑
        fallback_results = [{
            "id": "fallback_001",
            "title": "搜索结果",
            "content": f"关于'{q}'的信息正在整理中，请咨询专业医生获取准确信息。",
            "category": "一般信息",
            "relevance_score": 0.5,
            "source": "系统提示"
        }]

        return StandardResponse(
            success=True,
            message="搜索完成（备用模式）",
            data={
                "query": q,
                "total": len(fallback_results),
                "results": fallback_results
            },
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识库搜索失败: {str(e)}")

# 获取知识库统计信息
@app.get("/api/v1/knowledge/stats")
async def get_knowledge_stats():
    """获取知识库统计信息"""

    try:
        if KNOWLEDGE_BASE_AVAILABLE:
            total_items = len(knowledge_base.knowledge_data)
            categories = {}

            for item in knowledge_base.knowledge_data.values():
                if item.category not in categories:
                    categories[item.category] = 0
                categories[item.category] += 1

            return StandardResponse(
                success=True,
                message="知识库统计信息获取成功",
                data={
                    "total_items": total_items,
                    "categories": categories,
                    "last_updated": datetime.utcnow().isoformat(),
                    "status": "active"
                },
                timestamp=datetime.utcnow()
            )

        return StandardResponse(
            success=False,
            message="知识库暂时不可用",
            data={"status": "unavailable"},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库统计失败: {str(e)}")

# 智能搜索API
@app.get("/api/v1/knowledge/smart-search")
async def smart_search_knowledge(q: str, limit: int = 5):
    """智能知识库搜索 - 包含搜索建议和相关分类"""

    try:
        if KNOWLEDGE_BASE_AVAILABLE:
            result = await knowledge_base.smart_search(q, limit)

            # 格式化结果
            formatted_results = []
            for item in result["results"]:
                formatted_results.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                    "full_content": item.content,
                    "category": item.category,
                    "keywords": item.keywords,
                    "relevance_score": round(item.relevance_score, 2),
                    "source": item.source
                })

            return StandardResponse(
                success=True,
                message=f"智能搜索完成，找到 {result['total_results']} 条结果",
                data={
                    "query": result["query"],
                    "results": formatted_results,
                    "total_results": result["total_results"],
                    "search_time": round(result["search_time"], 3),
                    "suggestions": result["suggestions"],
                    "related_categories": result["related_categories"],
                    "timestamp": result["timestamp"]
                },
                timestamp=datetime.utcnow()
            )

        return StandardResponse(
            success=False,
            message="知识库暂时不可用",
            data={"status": "unavailable"},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能搜索失败: {str(e)}")

# 分类搜索API
@app.get("/api/v1/knowledge/category/{category}")
async def search_by_category(category: str, limit: int = 10):
    """按分类搜索知识库"""

    try:
        if KNOWLEDGE_BASE_AVAILABLE:
            search_result = await knowledge_base.search_by_category(category, limit)

            results = []
            for item in search_result.items:
                results.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                    "full_content": item.content,
                    "category": item.category,
                    "keywords": item.keywords,
                    "source": item.source
                })

            return StandardResponse(
                success=True,
                message=f"分类 '{category}' 下找到 {search_result.total_results} 条信息",
                data={
                    "category": category,
                    "results": results,
                    "total": search_result.total_results,
                    "search_time": round(search_result.search_time, 3),
                    "timestamp": search_result.timestamp.isoformat()
                },
                timestamp=datetime.utcnow()
            )

        return StandardResponse(
            success=False,
            message="知识库暂时不可用",
            data={"status": "unavailable"},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分类搜索失败: {str(e)}")

# 获取所有分类API
@app.get("/api/v1/knowledge/categories")
async def get_all_categories():
    """获取所有知识库分类"""

    try:
        if KNOWLEDGE_BASE_AVAILABLE:
            categories = await knowledge_base.get_all_categories()

            return StandardResponse(
                success=True,
                message="获取分类信息成功",
                data={
                    "categories": categories,
                    "total_categories": len(categories),
                    "total_items": sum(categories.values())
                },
                timestamp=datetime.utcnow()
            )

        return StandardResponse(
            success=False,
            message="知识库暂时不可用",
            data={"status": "unavailable"},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")

# 获取热门关键词API
@app.get("/api/v1/knowledge/keywords")
async def get_popular_keywords(limit: int = 20):
    """获取热门关键词"""

    try:
        if KNOWLEDGE_BASE_AVAILABLE:
            keywords = await knowledge_base.get_popular_keywords(limit)

            return StandardResponse(
                success=True,
                message=f"获取前 {len(keywords)} 个热门关键词",
                data={
                    "keywords": keywords,
                    "total": len(keywords)
                },
                timestamp=datetime.utcnow()
            )

        return StandardResponse(
            success=False,
            message="知识库暂时不可用",
            data={"status": "unavailable"},
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关键词失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 启动小雪宝AI助手完整版...")
    print("📍 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🏠 主页: http://localhost:8000")
    
    uvicorn.run(
        "app_complete:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
