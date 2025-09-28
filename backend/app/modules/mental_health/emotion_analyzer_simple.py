"""
简化版情绪分析器 (无AI依赖)
用于快速启动和测试
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from dataclasses import dataclass
import random

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EmotionResult:
    """情绪分析结果"""
    emotion: str
    confidence: float
    intensity: float
    valence: float  # 效价 (-1到1, 负面到正面)
    arousal: float  # 唤醒度 (0到1, 平静到兴奋)
    timestamp: datetime


@dataclass
class MultiModalEmotionResult:
    """多模态情绪分析结果"""
    primary_emotion: str
    confidence: float
    intensity: float
    modality_results: Dict[str, EmotionResult]
    fusion_weights: Dict[str, float]
    timestamp: datetime


class SimpleTextEmotionAnalyzer:
    """简化文本情绪分析器"""
    
    def __init__(self):
        # 简单的关键词映射
        self.emotion_keywords = {
            "happy": ["开心", "高兴", "快乐", "愉快", "兴奋", "满意"],
            "sad": ["难过", "伤心", "沮丧", "失落", "悲伤", "痛苦"],
            "anxious": ["焦虑", "紧张", "担心", "害怕", "恐惧", "不安"],
            "angry": ["生气", "愤怒", "恼火", "烦躁", "气愤", "愤恨"],
            "calm": ["平静", "安静", "放松", "舒适", "宁静", "淡定"],
            "excited": ["兴奋", "激动", "热情", "活跃", "精神", "振奋"]
        }
    
    async def analyze_emotion(self, text: str) -> EmotionResult:
        """分析文本情绪"""
        try:
            if not text:
                return EmotionResult(
                    emotion="neutral",
                    confidence=0.5,
                    intensity=0.3,
                    valence=0.0,
                    arousal=0.3,
                    timestamp=datetime.utcnow()
                )
            
            text_lower = text.lower()
            emotion_scores = {}
            
            # 基于关键词计算情绪分数
            for emotion, keywords in self.emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    emotion_scores[emotion] = score / len(keywords)
            
            if not emotion_scores:
                # 如果没有匹配的关键词，返回中性情绪
                primary_emotion = "neutral"
                confidence = 0.5
                intensity = 0.3
                valence = 0.0
                arousal = 0.3
            else:
                # 选择得分最高的情绪
                primary_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = min(emotion_scores[primary_emotion] * 2, 1.0)
                
                # 根据情绪类型设置强度、效价和唤醒度
                emotion_properties = {
                    "happy": {"intensity": 0.7, "valence": 0.8, "arousal": 0.6},
                    "sad": {"intensity": 0.6, "valence": -0.7, "arousal": 0.3},
                    "anxious": {"intensity": 0.8, "valence": -0.5, "arousal": 0.9},
                    "angry": {"intensity": 0.9, "valence": -0.8, "arousal": 0.8},
                    "calm": {"intensity": 0.4, "valence": 0.3, "arousal": 0.2},
                    "excited": {"intensity": 0.8, "valence": 0.6, "arousal": 0.9}
                }
                
                props = emotion_properties.get(primary_emotion, {"intensity": 0.5, "valence": 0.0, "arousal": 0.5})
                intensity = props["intensity"] * confidence
                valence = props["valence"]
                arousal = props["arousal"]
            
            return EmotionResult(
                emotion=primary_emotion,
                confidence=confidence,
                intensity=intensity,
                valence=valence,
                arousal=arousal,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"文本情绪分析失败: {str(e)}")
            return EmotionResult(
                emotion="unknown",
                confidence=0.0,
                intensity=0.0,
                valence=0.0,
                arousal=0.0,
                timestamp=datetime.utcnow()
            )


class SimpleAudioEmotionAnalyzer:
    """简化音频情绪分析器"""
    
    async def analyze_emotion(self, audio_data: bytes) -> EmotionResult:
        """分析音频情绪 (模拟实现)"""
        try:
            # 模拟音频分析
            emotions = ["happy", "sad", "anxious", "calm", "excited", "angry"]
            emotion = random.choice(emotions)
            confidence = random.uniform(0.6, 0.9)
            
            # 根据情绪设置属性
            emotion_properties = {
                "happy": {"intensity": 0.7, "valence": 0.8, "arousal": 0.6},
                "sad": {"intensity": 0.6, "valence": -0.7, "arousal": 0.3},
                "anxious": {"intensity": 0.8, "valence": -0.5, "arousal": 0.9},
                "angry": {"intensity": 0.9, "valence": -0.8, "arousal": 0.8},
                "calm": {"intensity": 0.4, "valence": 0.3, "arousal": 0.2},
                "excited": {"intensity": 0.8, "valence": 0.6, "arousal": 0.9}
            }
            
            props = emotion_properties[emotion]
            
            return EmotionResult(
                emotion=emotion,
                confidence=confidence,
                intensity=props["intensity"],
                valence=props["valence"],
                arousal=props["arousal"],
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"音频情绪分析失败: {str(e)}")
            return EmotionResult(
                emotion="unknown",
                confidence=0.0,
                intensity=0.0,
                valence=0.0,
                arousal=0.0,
                timestamp=datetime.utcnow()
            )


class SimpleVisualEmotionAnalyzer:
    """简化视觉情绪分析器"""
    
    async def analyze_emotion(self, image_data: bytes) -> EmotionResult:
        """分析图像情绪 (模拟实现)"""
        try:
            # 模拟图像分析
            emotions = ["happy", "sad", "anxious", "calm", "excited", "angry"]
            emotion = random.choice(emotions)
            confidence = random.uniform(0.5, 0.8)
            
            # 根据情绪设置属性
            emotion_properties = {
                "happy": {"intensity": 0.7, "valence": 0.8, "arousal": 0.6},
                "sad": {"intensity": 0.6, "valence": -0.7, "arousal": 0.3},
                "anxious": {"intensity": 0.8, "valence": -0.5, "arousal": 0.9},
                "angry": {"intensity": 0.9, "valence": -0.8, "arousal": 0.8},
                "calm": {"intensity": 0.4, "valence": 0.3, "arousal": 0.2},
                "excited": {"intensity": 0.8, "valence": 0.6, "arousal": 0.9}
            }
            
            props = emotion_properties[emotion]
            
            return EmotionResult(
                emotion=emotion,
                confidence=confidence,
                intensity=props["intensity"],
                valence=props["valence"],
                arousal=props["arousal"],
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"视觉情绪分析失败: {str(e)}")
            return EmotionResult(
                emotion="unknown",
                confidence=0.0,
                intensity=0.0,
                valence=0.0,
                arousal=0.0,
                timestamp=datetime.utcnow()
            )


class SimpleMultiModalEmotionAnalyzer:
    """简化多模态情绪分析器"""
    
    def __init__(self):
        self.text_analyzer = SimpleTextEmotionAnalyzer()
        self.audio_analyzer = SimpleAudioEmotionAnalyzer()
        self.visual_analyzer = SimpleVisualEmotionAnalyzer()
    
    async def analyze_multimodal_emotion(
        self,
        text_data: Optional[str] = None,
        audio_data: Optional[bytes] = None,
        image_data: Optional[bytes] = None,
        child_age: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> MultiModalEmotionResult:
        """多模态情绪分析"""
        
        try:
            modality_results = {}
            fusion_weights = {}
            
            # 分析各个模态
            if text_data:
                text_result = await self.text_analyzer.analyze_emotion(text_data)
                modality_results["text"] = text_result
                fusion_weights["text"] = 0.4
            
            if audio_data:
                audio_result = await self.audio_analyzer.analyze_emotion(audio_data)
                modality_results["audio"] = audio_result
                fusion_weights["audio"] = 0.3
            
            if image_data:
                visual_result = await self.visual_analyzer.analyze_emotion(image_data)
                modality_results["visual"] = visual_result
                fusion_weights["visual"] = 0.3
            
            if not modality_results:
                # 如果没有输入数据，返回中性结果
                return MultiModalEmotionResult(
                    primary_emotion="neutral",
                    confidence=0.5,
                    intensity=0.3,
                    modality_results={},
                    fusion_weights={},
                    timestamp=datetime.utcnow()
                )
            
            # 归一化权重
            total_weight = sum(fusion_weights.values())
            fusion_weights = {k: v/total_weight for k, v in fusion_weights.items()}
            
            # 融合结果
            emotion_scores = {}
            for modality, result in modality_results.items():
                weight = fusion_weights[modality]
                emotion = result.emotion
                score = result.confidence * weight
                
                if emotion in emotion_scores:
                    emotion_scores[emotion] += score
                else:
                    emotion_scores[emotion] = score
            
            # 选择最高分的情绪
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[primary_emotion]
            
            # 计算平均强度
            intensity = sum(result.intensity * fusion_weights[modality] 
                          for modality, result in modality_results.items())
            
            return MultiModalEmotionResult(
                primary_emotion=primary_emotion,
                confidence=confidence,
                intensity=intensity,
                modality_results=modality_results,
                fusion_weights=fusion_weights,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"多模态情绪分析失败: {str(e)}")
            return MultiModalEmotionResult(
                primary_emotion="unknown",
                confidence=0.0,
                intensity=0.0,
                modality_results={},
                fusion_weights={},
                timestamp=datetime.utcnow()
            )
