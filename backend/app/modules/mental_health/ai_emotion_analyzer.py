"""
基于AI的情绪分析模块
集成SiliconFlow API进行高级情绪识别
"""

import asyncio
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AIEmotionResult:
    """AI情绪识别结果"""
    primary_emotion: str
    confidence: float
    intensity: float
    emotions_detected: Dict[str, float]
    sentiment_score: float  # -1 到 1
    emotional_keywords: List[str]
    suggestions: List[str]
    timestamp: datetime
    ai_model: str


class SiliconFlowEmotionAnalyzer:
    """基于SiliconFlow API的情绪分析器"""
    
    def __init__(self):
        self.api_url = "https://cloud.siliconflow.cn/api/v1/chat/completions"
        self.api_key = "sk-hclwuosimfqpztfimjagookkkpbcqianfcihthgsvasynbrv"
        self.model = "Qwen/Qwen3-8B"
        
        # 情绪映射
        self.emotion_mapping = {
            "开心": {"en": "happy", "valence": 0.8, "arousal": 0.7},
            "快乐": {"en": "happy", "valence": 0.8, "arousal": 0.7},
            "高兴": {"en": "happy", "valence": 0.8, "arousal": 0.7},
            "难过": {"en": "sad", "valence": -0.7, "arousal": 0.3},
            "伤心": {"en": "sad", "valence": -0.7, "arousal": 0.3},
            "悲伤": {"en": "sad", "valence": -0.7, "arousal": 0.3},
            "焦虑": {"en": "anxious", "valence": -0.5, "arousal": 0.8},
            "紧张": {"en": "anxious", "valence": -0.5, "arousal": 0.8},
            "担心": {"en": "worried", "valence": -0.4, "arousal": 0.6},
            "生气": {"en": "angry", "valence": -0.8, "arousal": 0.9},
            "愤怒": {"en": "angry", "valence": -0.8, "arousal": 0.9},
            "平静": {"en": "calm", "valence": 0.3, "arousal": 0.2},
            "放松": {"en": "relaxed", "valence": 0.5, "arousal": 0.1},
            "恐惧": {"en": "fear", "valence": -0.8, "arousal": 0.8},
            "害怕": {"en": "fear", "valence": -0.8, "arousal": 0.8},
            "惊讶": {"en": "surprised", "valence": 0.0, "arousal": 0.8},
            "厌恶": {"en": "disgust", "valence": -0.6, "arousal": 0.5}
        }
    
    async def analyze_text_emotion(self, text: str, context: Optional[str] = None) -> AIEmotionResult:
        """分析文本情绪"""
        
        try:
            # 构建专门的情绪分析提示
            system_prompt = """你是一个专业的儿童心理情绪分析师。请分析给定文本中的情绪状态，特别关注儿童和青少年的情绪表达特点。

请按照以下JSON格式返回分析结果：
{
    "primary_emotion": "主要情绪（如：开心、难过、焦虑、生气、平静等）",
    "confidence": 0.85,
    "intensity": 0.7,
    "emotions_detected": {
        "开心": 0.2,
        "焦虑": 0.8,
        "担心": 0.6
    },
    "sentiment_score": -0.3,
    "emotional_keywords": ["担心", "紧张", "害怕"],
    "suggestions": [
        "建议给予孩子更多的安全感",
        "可以尝试深呼吸放松练习",
        "建议家长耐心倾听孩子的感受"
    ]
}

注意：
1. confidence表示识别置信度(0-1)
2. intensity表示情绪强度(0-1)
3. sentiment_score表示情绪倾向(-1到1，负数表示消极，正数表示积极)
4. suggestions要针对儿童心理健康给出具体建议"""

            user_prompt = f"请分析以下文本的情绪：\n\n文本内容：{text}"
            if context:
                user_prompt += f"\n\n背景信息：{context}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": 1024,
                        "temperature": 0.3,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # 尝试解析JSON响应
                    try:
                        # 提取JSON部分
                        json_start = ai_response.find('{')
                        json_end = ai_response.rfind('}') + 1
                        if json_start != -1 and json_end != -1:
                            json_str = ai_response[json_start:json_end]
                            emotion_data = json.loads(json_str)
                            
                            return AIEmotionResult(
                                primary_emotion=emotion_data.get("primary_emotion", "中性"),
                                confidence=emotion_data.get("confidence", 0.5),
                                intensity=emotion_data.get("intensity", 0.5),
                                emotions_detected=emotion_data.get("emotions_detected", {}),
                                sentiment_score=emotion_data.get("sentiment_score", 0.0),
                                emotional_keywords=emotion_data.get("emotional_keywords", []),
                                suggestions=emotion_data.get("suggestions", []),
                                timestamp=datetime.utcnow(),
                                ai_model=self.model
                            )
                    except json.JSONDecodeError:
                        logger.warning("AI响应JSON解析失败，使用备用分析")
                
        except Exception as e:
            logger.error(f"AI情绪分析失败: {e}")
        
        # 备用分析方法
        return await self._fallback_emotion_analysis(text)
    
    async def _fallback_emotion_analysis(self, text: str) -> AIEmotionResult:
        """备用情绪分析方法"""
        
        text_lower = text.lower()
        detected_emotions = {}
        emotional_keywords = []
        
        # 关键词匹配
        for emotion_cn, emotion_data in self.emotion_mapping.items():
            if emotion_cn in text:
                detected_emotions[emotion_cn] = 0.8
                emotional_keywords.append(emotion_cn)
        
        # 确定主要情绪
        if detected_emotions:
            primary_emotion = max(detected_emotions.keys(), key=lambda k: detected_emotions[k])
            confidence = detected_emotions[primary_emotion]
        else:
            primary_emotion = "中性"
            confidence = 0.5
            detected_emotions = {"中性": 0.5}
        
        # 计算情绪倾向
        sentiment_score = 0.0
        if primary_emotion in self.emotion_mapping:
            sentiment_score = self.emotion_mapping[primary_emotion]["valence"]
        
        # 生成建议
        suggestions = self._generate_suggestions(primary_emotion)
        
        return AIEmotionResult(
            primary_emotion=primary_emotion,
            confidence=confidence,
            intensity=confidence * 0.8,
            emotions_detected=detected_emotions,
            sentiment_score=sentiment_score,
            emotional_keywords=emotional_keywords,
            suggestions=suggestions,
            timestamp=datetime.utcnow(),
            ai_model="备用分析器"
        )
    
    def _generate_suggestions(self, emotion: str) -> List[str]:
        """根据情绪生成建议"""
        
        suggestions_map = {
            "开心": [
                "鼓励孩子分享快乐的原因",
                "可以记录下这个美好时刻",
                "适当给予表扬和肯定"
            ],
            "难过": [
                "给予孩子足够的理解和陪伴",
                "鼓励孩子表达内心感受",
                "提供温暖的拥抱和安慰"
            ],
            "焦虑": [
                "教授孩子深呼吸放松技巧",
                "帮助孩子识别焦虑的具体原因",
                "建立安全感和信任感"
            ],
            "生气": [
                "保持冷静，不要与孩子对抗",
                "帮助孩子学会表达愤怒的健康方式",
                "给孩子一些冷静的时间和空间"
            ],
            "平静": [
                "维持当前的良好状态",
                "可以进行一些有益的活动",
                "继续提供稳定的环境支持"
            ]
        }
        
        return suggestions_map.get(emotion, [
            "关注孩子的情绪变化",
            "提供适当的情感支持",
            "如有需要，寻求专业帮助"
        ])
    
    async def analyze_child_emotion_with_age(self, text: str, age: int, context: Optional[str] = None) -> AIEmotionResult:
        """根据儿童年龄分析情绪"""
        
        # 添加年龄相关的上下文
        age_context = f"这是一个{age}岁儿童的表达。"
        
        if age <= 6:
            age_context += "请考虑学龄前儿童的情绪表达特点，他们可能用更直接、简单的方式表达情绪。"
        elif age <= 12:
            age_context += "请考虑学龄儿童的情绪表达特点，他们开始学会更复杂的情绪表达。"
        else:
            age_context += "请考虑青少年的情绪表达特点，他们的情绪可能更加复杂和多变。"
        
        full_context = age_context
        if context:
            full_context += f" 额外背景：{context}"
        
        return await self.analyze_text_emotion(text, full_context)


# 创建全局实例
ai_emotion_analyzer = SiliconFlowEmotionAnalyzer()
