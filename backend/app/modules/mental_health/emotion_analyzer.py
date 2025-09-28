"""
多模态情绪识别与分析引擎
支持文字、语音、图像和生理数据的情感分析
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import cv2
import librosa
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from dataclasses import dataclass

from app.core.logging import get_logger
from app.core.cache import cached

logger = get_logger(__name__)


@dataclass
class EmotionResult:
    """情绪识别结果"""
    emotion: str
    confidence: float
    intensity: float
    valence: float  # 情绪效价 (-1到1)
    arousal: float  # 情绪唤醒度 (0到1)
    timestamp: datetime
    modality: str  # 识别模态
    raw_data: Dict[str, Any]


@dataclass
class MultiModalEmotionResult:
    """多模态情绪识别结果"""
    primary_emotion: str
    confidence: float
    intensity: float
    modality_results: Dict[str, EmotionResult]
    fusion_weights: Dict[str, float]
    context_factors: Dict[str, Any]
    timestamp: datetime


class TextEmotionAnalyzer:
    """文本情绪分析器"""
    
    def __init__(self):
        self.emotion_classifier = None
        self.tokenizer = None
        self.model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化模型"""
        try:
            # 使用预训练的中文情感分析模型
            self.emotion_classifier = pipeline(
                "text-classification",
                model="uer/roberta-base-finetuned-chinanews-chinese",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # 儿童语言特征模型
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
            self.model = AutoModel.from_pretrained("bert-base-chinese")
            
            logger.info("文本情绪分析模型初始化成功")
        except Exception as e:
            logger.error(f"文本情绪分析模型初始化失败: {str(e)}")
    
    async def analyze_text(self, text: str, child_age: int = None) -> EmotionResult:
        """分析文本情绪"""
        try:
            # 预处理文本
            processed_text = self._preprocess_text(text, child_age)
            
            # 基础情感分析
            emotion_result = self.emotion_classifier(processed_text)
            
            # 儿童特定情绪识别
            child_emotions = await self._analyze_child_specific_emotions(processed_text, child_age)
            
            # 情绪强度分析
            intensity = self._calculate_emotion_intensity(processed_text)
            
            # 情绪效价和唤醒度
            valence, arousal = self._calculate_valence_arousal(processed_text)
            
            return EmotionResult(
                emotion=emotion_result[0]['label'],
                confidence=emotion_result[0]['score'],
                intensity=intensity,
                valence=valence,
                arousal=arousal,
                timestamp=datetime.utcnow(),
                modality="text",
                raw_data={
                    "text": text,
                    "processed_text": processed_text,
                    "child_emotions": child_emotions,
                    "full_results": emotion_result
                }
            )
        except Exception as e:
            logger.error(f"文本情绪分析失败: {str(e)}")
            return self._create_default_result("text", text)
    
    def _preprocess_text(self, text: str, child_age: int = None) -> str:
        """预处理文本"""
        # 移除特殊字符
        import re
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        # 儿童语言特征处理
        if child_age and child_age < 12:
            # 处理儿童常用表达
            child_expressions = {
                "好开心": "非常高兴",
                "超级棒": "很好",
                "不想": "不愿意",
                "害怕": "恐惧"
            }
            for child_expr, standard_expr in child_expressions.items():
                text = text.replace(child_expr, standard_expr)
        
        return text.strip()
    
    async def _analyze_child_specific_emotions(self, text: str, child_age: int = None) -> Dict[str, float]:
        """分析儿童特定情绪"""
        child_emotion_keywords = {
            "兴奋": ["好玩", "有趣", "开心", "高兴", "棒"],
            "焦虑": ["担心", "害怕", "紧张", "不安"],
            "愤怒": ["生气", "讨厌", "烦", "气"],
            "悲伤": ["难过", "伤心", "哭", "不开心"],
            "困惑": ["不懂", "为什么", "奇怪", "不明白"],
            "孤独": ["一个人", "没朋友", "孤单", "寂寞"]
        }
        
        emotion_scores = {}
        for emotion, keywords in child_emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            emotion_scores[emotion] = min(score / len(keywords), 1.0)
        
        return emotion_scores
    
    def _calculate_emotion_intensity(self, text: str) -> float:
        """计算情绪强度"""
        intensity_indicators = {
            "很": 0.8, "非常": 0.9, "超级": 0.95, "特别": 0.85,
            "有点": 0.3, "稍微": 0.2, "一点": 0.25
        }
        
        max_intensity = 0.5  # 基础强度
        for indicator, intensity in intensity_indicators.items():
            if indicator in text:
                max_intensity = max(max_intensity, intensity)
        
        return max_intensity
    
    def _calculate_valence_arousal(self, text: str) -> Tuple[float, float]:
        """计算情绪效价和唤醒度"""
        positive_words = ["开心", "高兴", "喜欢", "好", "棒", "爱"]
        negative_words = ["难过", "生气", "害怕", "讨厌", "不好", "痛"]
        high_arousal_words = ["兴奋", "激动", "紧张", "害怕", "生气"]
        low_arousal_words = ["平静", "安静", "累", "困", "无聊"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        high_arousal_count = sum(1 for word in high_arousal_words if word in text)
        low_arousal_count = sum(1 for word in low_arousal_words if word in text)
        
        # 计算效价 (-1到1)
        total_valence_words = positive_count + negative_count
        if total_valence_words > 0:
            valence = (positive_count - negative_count) / total_valence_words
        else:
            valence = 0.0
        
        # 计算唤醒度 (0到1)
        total_arousal_words = high_arousal_count + low_arousal_count
        if total_arousal_words > 0:
            arousal = high_arousal_count / total_arousal_words
        else:
            arousal = 0.5
        
        return valence, arousal
    
    def _create_default_result(self, modality: str, raw_data: Any) -> EmotionResult:
        """创建默认结果"""
        return EmotionResult(
            emotion="neutral",
            confidence=0.5,
            intensity=0.5,
            valence=0.0,
            arousal=0.5,
            timestamp=datetime.utcnow(),
            modality=modality,
            raw_data={"error": "分析失败", "input": str(raw_data)}
        )


class AudioEmotionAnalyzer:
    """音频情绪分析器"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.feature_extractors = self._initialize_feature_extractors()
    
    def _initialize_feature_extractors(self):
        """初始化特征提取器"""
        return {
            "mfcc": True,
            "spectral": True,
            "prosodic": True
        }
    
    async def analyze_audio(self, audio_data: bytes, child_age: int = None) -> EmotionResult:
        """分析音频情绪"""
        try:
            # 音频预处理
            audio_features = await self._extract_audio_features(audio_data)
            
            # 儿童语音特征分析
            child_features = self._analyze_child_voice_features(audio_features, child_age)
            
            # 情绪识别
            emotion_scores = self._classify_audio_emotion(audio_features, child_features)
            
            # 获取主要情绪
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            # 计算强度和效价唤醒度
            intensity = self._calculate_audio_intensity(audio_features)
            valence, arousal = self._calculate_audio_valence_arousal(audio_features)
            
            return EmotionResult(
                emotion=primary_emotion[0],
                confidence=primary_emotion[1],
                intensity=intensity,
                valence=valence,
                arousal=arousal,
                timestamp=datetime.utcnow(),
                modality="audio",
                raw_data={
                    "audio_features": audio_features,
                    "child_features": child_features,
                    "emotion_scores": emotion_scores
                }
            )
        except Exception as e:
            logger.error(f"音频情绪分析失败: {str(e)}")
            return self._create_default_result("audio", "audio_data")
    
    async def _extract_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
        """提取音频特征"""
        try:
            # 将字节数据转换为numpy数组
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            features = {}
            
            # MFCC特征
            mfcc = librosa.feature.mfcc(y=audio_array, sr=self.sample_rate, n_mfcc=13)
            features['mfcc'] = {
                'mean': np.mean(mfcc, axis=1).tolist(),
                'std': np.std(mfcc, axis=1).tolist()
            }
            
            # 频谱特征
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_array, sr=self.sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_array, sr=self.sample_rate)
            features['spectral'] = {
                'centroid_mean': np.mean(spectral_centroids),
                'centroid_std': np.std(spectral_centroids),
                'rolloff_mean': np.mean(spectral_rolloff),
                'rolloff_std': np.std(spectral_rolloff)
            }
            
            # 韵律特征
            tempo, beats = librosa.beat.beat_track(y=audio_array, sr=self.sample_rate)
            features['prosodic'] = {
                'tempo': tempo,
                'rhythm_regularity': self._calculate_rhythm_regularity(beats)
            }
            
            return features
        except Exception as e:
            logger.error(f"音频特征提取失败: {str(e)}")
            return {}
    
    def _analyze_child_voice_features(self, audio_features: Dict[str, Any], child_age: int = None) -> Dict[str, Any]:
        """分析儿童语音特征"""
        child_features = {}
        
        if child_age and child_age < 12:
            # 儿童语音特征分析
            if 'spectral' in audio_features:
                # 儿童通常有更高的基频
                child_features['high_pitch_indicator'] = audio_features['spectral']['centroid_mean'] > 2000
                
            if 'prosodic' in audio_features:
                # 儿童语音节奏特征
                child_features['speech_rate'] = audio_features['prosodic']['tempo']
                child_features['rhythm_variability'] = audio_features['prosodic']['rhythm_regularity']
        
        return child_features
    
    def _classify_audio_emotion(self, audio_features: Dict[str, Any], child_features: Dict[str, Any]) -> Dict[str, float]:
        """音频情绪分类"""
        emotion_scores = {
            "happy": 0.0,
            "sad": 0.0,
            "angry": 0.0,
            "fear": 0.0,
            "neutral": 0.5
        }
        
        if 'spectral' in audio_features:
            centroid = audio_features['spectral']['centroid_mean']
            
            # 基于频谱质心的简单分类
            if centroid > 3000:
                emotion_scores["happy"] += 0.3
                emotion_scores["fear"] += 0.2
            elif centroid < 1500:
                emotion_scores["sad"] += 0.4
            
        if 'prosodic' in audio_features:
            tempo = audio_features['prosodic']['tempo']
            
            # 基于节奏的分类
            if tempo > 120:
                emotion_scores["happy"] += 0.2
                emotion_scores["angry"] += 0.3
            elif tempo < 80:
                emotion_scores["sad"] += 0.3
        
        # 归一化分数
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            emotion_scores = {k: v/total_score for k, v in emotion_scores.items()}
        
        return emotion_scores
    
    def _calculate_rhythm_regularity(self, beats: np.ndarray) -> float:
        """计算节奏规律性"""
        if len(beats) < 2:
            return 0.5
        
        intervals = np.diff(beats)
        if len(intervals) == 0:
            return 0.5
        
        regularity = 1.0 - (np.std(intervals) / np.mean(intervals))
        return max(0.0, min(1.0, regularity))
    
    def _calculate_audio_intensity(self, audio_features: Dict[str, Any]) -> float:
        """计算音频情绪强度"""
        intensity = 0.5
        
        if 'spectral' in audio_features:
            # 基于频谱变化计算强度
            centroid_std = audio_features['spectral']['centroid_std']
            intensity = min(1.0, centroid_std / 1000.0)
        
        return intensity
    
    def _calculate_audio_valence_arousal(self, audio_features: Dict[str, Any]) -> Tuple[float, float]:
        """计算音频效价和唤醒度"""
        valence = 0.0
        arousal = 0.5
        
        if 'spectral' in audio_features:
            centroid = audio_features['spectral']['centroid_mean']
            # 高频通常对应正面情绪
            valence = min(1.0, max(-1.0, (centroid - 2000) / 2000))
        
        if 'prosodic' in audio_features:
            tempo = audio_features['prosodic']['tempo']
            # 快节奏对应高唤醒度
            arousal = min(1.0, tempo / 150.0)
        
        return valence, arousal
    
    def _create_default_result(self, modality: str, raw_data: Any) -> EmotionResult:
        """创建默认结果"""
        return EmotionResult(
            emotion="neutral",
            confidence=0.5,
            intensity=0.5,
            valence=0.0,
            arousal=0.5,
            timestamp=datetime.utcnow(),
            modality=modality,
            raw_data={"error": "分析失败", "input": str(raw_data)}
        )


class VisualEmotionAnalyzer:
    """视觉情绪分析器"""

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.emotion_model = None
        self._initialize_models()

    def _initialize_models(self):
        """初始化视觉模型"""
        try:
            # 这里可以加载预训练的面部表情识别模型
            logger.info("视觉情绪分析模型初始化成功")
        except Exception as e:
            logger.error(f"视觉情绪分析模型初始化失败: {str(e)}")

    async def analyze_image(self, image_data: bytes, child_age: int = None) -> EmotionResult:
        """分析图像中的情绪"""
        try:
            # 图像预处理
            image = self._preprocess_image(image_data)

            # 人脸检测
            faces = self._detect_faces(image)

            if len(faces) == 0:
                return self._create_default_result("visual", "no_face_detected")

            # 选择最大的人脸
            main_face = self._select_main_face(faces, image)

            # 面部表情分析
            facial_emotions = self._analyze_facial_expression(main_face, child_age)

            # 身体语言分析
            body_language = self._analyze_body_language(image, child_age)

            # 综合分析
            emotion_result = self._combine_visual_analysis(facial_emotions, body_language)

            return EmotionResult(
                emotion=emotion_result['emotion'],
                confidence=emotion_result['confidence'],
                intensity=emotion_result['intensity'],
                valence=emotion_result['valence'],
                arousal=emotion_result['arousal'],
                timestamp=datetime.utcnow(),
                modality="visual",
                raw_data={
                    "faces_detected": len(faces),
                    "facial_emotions": facial_emotions,
                    "body_language": body_language,
                    "main_face_size": main_face.shape if main_face is not None else None
                }
            )
        except Exception as e:
            logger.error(f"视觉情绪分析失败: {str(e)}")
            return self._create_default_result("visual", "analysis_error")

    def _preprocess_image(self, image_data: bytes) -> np.ndarray:
        """预处理图像"""
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray

    def _detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """检测人脸"""
        faces = self.face_cascade.detectMultiScale(
            image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        return faces.tolist()

    def _select_main_face(self, faces: List[Tuple[int, int, int, int]], image: np.ndarray) -> Optional[np.ndarray]:
        """选择主要人脸"""
        if not faces:
            return None
        main_face_coords = max(faces, key=lambda face: face[2] * face[3])
        x, y, w, h = main_face_coords
        return image[y:y+h, x:x+w]

    def _analyze_facial_expression(self, face_image: np.ndarray, child_age: int = None) -> Dict[str, Any]:
        """分析面部表情"""
        if face_image is None:
            return {"emotion": "neutral", "confidence": 0.5}

        facial_features = self._extract_facial_features(face_image)

        if child_age and child_age < 12:
            facial_features = self._adjust_for_child_features(facial_features, child_age)

        emotion_scores = self._classify_facial_emotion(facial_features)

        return {
            "emotion_scores": emotion_scores,
            "primary_emotion": max(emotion_scores.items(), key=lambda x: x[1])[0],
            "confidence": max(emotion_scores.values()),
            "facial_features": facial_features
        }

    def _extract_facial_features(self, face_image: np.ndarray) -> Dict[str, float]:
        """提取面部特征"""
        features = {}
        features['brightness'] = np.mean(face_image)
        features['contrast'] = np.std(face_image)
        edges = cv2.Canny(face_image, 50, 150)
        features['edge_density'] = np.sum(edges > 0) / edges.size
        return features

    def _adjust_for_child_features(self, features: Dict[str, float], child_age: int) -> Dict[str, float]:
        """调整儿童面部特征"""
        adjusted_features = features.copy()
        if child_age < 8:
            adjusted_features['expression_intensity'] = features.get('edge_density', 0) * 1.2
        elif child_age < 12:
            adjusted_features['expression_intensity'] = features.get('edge_density', 0) * 1.1
        return adjusted_features

    def _classify_facial_emotion(self, features: Dict[str, float]) -> Dict[str, float]:
        """基于特征分类面部情绪"""
        emotion_scores = {
            "happy": 0.0, "sad": 0.0, "angry": 0.0,
            "fear": 0.0, "surprise": 0.0, "neutral": 0.5
        }

        brightness = features.get('brightness', 128)
        if brightness > 140:
            emotion_scores["happy"] += 0.3
        elif brightness < 100:
            emotion_scores["sad"] += 0.3

        contrast = features.get('contrast', 30)
        if contrast > 50:
            emotion_scores["surprise"] += 0.2
            emotion_scores["angry"] += 0.2

        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}

        return emotion_scores

    def _analyze_body_language(self, image: np.ndarray, child_age: int = None) -> Dict[str, Any]:
        """分析身体语言"""
        body_features = {
            "posture_confidence": 0.5,
            "gesture_intensity": 0.5,
            "overall_energy": 0.5
        }

        image_variance = np.var(image)
        if image_variance > 1000:
            body_features["gesture_intensity"] = 0.7
            body_features["overall_energy"] = 0.8

        return body_features

    def _combine_visual_analysis(self, facial_emotions: Dict[str, Any], body_language: Dict[str, Any]) -> Dict[str, Any]:
        """综合视觉分析结果"""
        primary_emotion = facial_emotions.get("primary_emotion", "neutral")
        confidence = facial_emotions.get("confidence", 0.5)

        body_energy = body_language.get("overall_energy", 0.5)
        adjusted_confidence = (confidence + body_energy) / 2

        gesture_intensity = body_language.get("gesture_intensity", 0.5)
        intensity = (confidence + gesture_intensity) / 2

        valence = self._calculate_visual_valence(primary_emotion)
        arousal = self._calculate_visual_arousal(primary_emotion, intensity)

        return {
            "emotion": primary_emotion,
            "confidence": adjusted_confidence,
            "intensity": intensity,
            "valence": valence,
            "arousal": arousal
        }

    def _calculate_visual_valence(self, emotion: str) -> float:
        """计算视觉效价"""
        valence_map = {
            "happy": 0.8, "surprise": 0.3, "neutral": 0.0,
            "fear": -0.6, "angry": -0.7, "sad": -0.8
        }
        return valence_map.get(emotion, 0.0)

    def _calculate_visual_arousal(self, emotion: str, intensity: float) -> float:
        """计算视觉唤醒度"""
        arousal_map = {
            "happy": 0.7, "surprise": 0.9, "angry": 0.8,
            "fear": 0.8, "sad": 0.3, "neutral": 0.5
        }
        base_arousal = arousal_map.get(emotion, 0.5)
        return min(1.0, base_arousal * intensity)

    def _create_default_result(self, modality: str, raw_data: Any) -> EmotionResult:
        """创建默认结果"""
        return EmotionResult(
            emotion="neutral",
            confidence=0.5,
            intensity=0.5,
            valence=0.0,
            arousal=0.5,
            timestamp=datetime.utcnow(),
            modality=modality,
            raw_data={"error": "分析失败", "input": str(raw_data)}
        )


class PhysiologicalEmotionAnalyzer:
    """生理数据情绪分析器"""

    def __init__(self):
        self.baseline_hr = 80  # 基础心率
        self.baseline_hrv = 50  # 基础心率变异性
        self.baseline_temp = 36.5  # 基础体温

    async def analyze_physiological_data(self, physio_data: Dict[str, Any], child_age: int = None) -> EmotionResult:
        """分析生理数据情绪"""
        try:
            # 调整儿童基础值
            if child_age:
                self._adjust_baselines_for_age(child_age)

            # 分析各项生理指标
            hr_analysis = self._analyze_heart_rate(physio_data.get('heart_rate', []))
            hrv_analysis = self._analyze_heart_rate_variability(physio_data.get('hrv', []))
            temp_analysis = self._analyze_temperature(physio_data.get('temperature', []))
            activity_analysis = self._analyze_activity_level(physio_data.get('activity', []))

            # 综合分析
            emotion_result = self._combine_physiological_analysis(
                hr_analysis, hrv_analysis, temp_analysis, activity_analysis
            )

            return EmotionResult(
                emotion=emotion_result['emotion'],
                confidence=emotion_result['confidence'],
                intensity=emotion_result['intensity'],
                valence=emotion_result['valence'],
                arousal=emotion_result['arousal'],
                timestamp=datetime.utcnow(),
                modality="physiological",
                raw_data={
                    "heart_rate_analysis": hr_analysis,
                    "hrv_analysis": hrv_analysis,
                    "temperature_analysis": temp_analysis,
                    "activity_analysis": activity_analysis,
                    "raw_data": physio_data
                }
            )
        except Exception as e:
            logger.error(f"生理数据情绪分析失败: {str(e)}")
            return self._create_default_result("physiological", physio_data)

    def _adjust_baselines_for_age(self, child_age: int):
        """根据年龄调整基础值"""
        if child_age < 5:
            self.baseline_hr = 100
            self.baseline_hrv = 40
        elif child_age < 10:
            self.baseline_hr = 90
            self.baseline_hrv = 45
        elif child_age < 15:
            self.baseline_hr = 85
            self.baseline_hrv = 48

    def _analyze_heart_rate(self, hr_data: List[float]) -> Dict[str, Any]:
        """分析心率数据"""
        if not hr_data:
            return {"status": "no_data", "emotion_indicators": {}}

        avg_hr = np.mean(hr_data)
        hr_variability = np.std(hr_data)

        # 心率情绪指标
        emotion_indicators = {}

        if avg_hr > self.baseline_hr * 1.2:
            emotion_indicators['high_arousal'] = 0.8
            emotion_indicators['stress'] = 0.7
        elif avg_hr > self.baseline_hr * 1.1:
            emotion_indicators['moderate_arousal'] = 0.6
            emotion_indicators['excitement'] = 0.5
        elif avg_hr < self.baseline_hr * 0.8:
            emotion_indicators['low_arousal'] = 0.7
            emotion_indicators['calm'] = 0.6

        if hr_variability > 15:
            emotion_indicators['anxiety'] = 0.6

        return {
            "average_hr": avg_hr,
            "variability": hr_variability,
            "baseline_ratio": avg_hr / self.baseline_hr,
            "emotion_indicators": emotion_indicators
        }

    def _analyze_heart_rate_variability(self, hrv_data: List[float]) -> Dict[str, Any]:
        """分析心率变异性"""
        if not hrv_data:
            return {"status": "no_data", "emotion_indicators": {}}

        avg_hrv = np.mean(hrv_data)

        emotion_indicators = {}

        if avg_hrv < self.baseline_hrv * 0.7:
            emotion_indicators['stress'] = 0.8
            emotion_indicators['fatigue'] = 0.6
        elif avg_hrv > self.baseline_hrv * 1.3:
            emotion_indicators['relaxed'] = 0.7
            emotion_indicators['positive'] = 0.5

        return {
            "average_hrv": avg_hrv,
            "baseline_ratio": avg_hrv / self.baseline_hrv,
            "emotion_indicators": emotion_indicators
        }

    def _analyze_temperature(self, temp_data: List[float]) -> Dict[str, Any]:
        """分析体温数据"""
        if not temp_data:
            return {"status": "no_data", "emotion_indicators": {}}

        avg_temp = np.mean(temp_data)

        emotion_indicators = {}

        if avg_temp > self.baseline_temp + 0.5:
            emotion_indicators['stress'] = 0.6
            emotion_indicators['anxiety'] = 0.5
        elif avg_temp < self.baseline_temp - 0.3:
            emotion_indicators['calm'] = 0.5

        return {
            "average_temperature": avg_temp,
            "baseline_difference": avg_temp - self.baseline_temp,
            "emotion_indicators": emotion_indicators
        }

    def _analyze_activity_level(self, activity_data: List[float]) -> Dict[str, Any]:
        """分析活动水平"""
        if not activity_data:
            return {"status": "no_data", "emotion_indicators": {}}

        avg_activity = np.mean(activity_data)
        activity_variance = np.var(activity_data)

        emotion_indicators = {}

        if avg_activity > 0.8:
            emotion_indicators['high_energy'] = 0.7
            emotion_indicators['excitement'] = 0.6
        elif avg_activity < 0.2:
            emotion_indicators['low_energy'] = 0.7
            emotion_indicators['sadness'] = 0.4

        if activity_variance > 0.3:
            emotion_indicators['restlessness'] = 0.6

        return {
            "average_activity": avg_activity,
            "variance": activity_variance,
            "emotion_indicators": emotion_indicators
        }

    def _combine_physiological_analysis(self, hr_analysis: Dict, hrv_analysis: Dict,
                                      temp_analysis: Dict, activity_analysis: Dict) -> Dict[str, Any]:
        """综合生理数据分析"""
        # 收集所有情绪指标
        all_indicators = {}

        for analysis in [hr_analysis, hrv_analysis, temp_analysis, activity_analysis]:
            indicators = analysis.get('emotion_indicators', {})
            for emotion, score in indicators.items():
                if emotion in all_indicators:
                    all_indicators[emotion] = max(all_indicators[emotion], score)
                else:
                    all_indicators[emotion] = score

        if not all_indicators:
            return {
                "emotion": "neutral",
                "confidence": 0.5,
                "intensity": 0.5,
                "valence": 0.0,
                "arousal": 0.5
            }

        # 找出主要情绪
        primary_emotion_indicator = max(all_indicators.items(), key=lambda x: x[1])

        # 映射到标准情绪
        emotion_mapping = {
            'stress': 'anxious',
            'anxiety': 'anxious',
            'excitement': 'happy',
            'calm': 'calm',
            'relaxed': 'calm',
            'high_energy': 'excited',
            'low_energy': 'sad',
            'restlessness': 'anxious',
            'fatigue': 'tired'
        }

        primary_emotion = emotion_mapping.get(primary_emotion_indicator[0], 'neutral')
        confidence = primary_emotion_indicator[1]

        # 计算强度
        intensity = np.mean(list(all_indicators.values()))

        # 计算效价和唤醒度
        valence = self._calculate_physio_valence(all_indicators)
        arousal = self._calculate_physio_arousal(all_indicators)

        return {
            "emotion": primary_emotion,
            "confidence": confidence,
            "intensity": intensity,
            "valence": valence,
            "arousal": arousal
        }

    def _calculate_physio_valence(self, indicators: Dict[str, float]) -> float:
        """计算生理数据效价"""
        positive_indicators = ['excitement', 'calm', 'relaxed', 'positive']
        negative_indicators = ['stress', 'anxiety', 'fatigue', 'sadness']

        positive_score = sum(indicators.get(ind, 0) for ind in positive_indicators)
        negative_score = sum(indicators.get(ind, 0) for ind in negative_indicators)

        total_score = positive_score + negative_score
        if total_score > 0:
            return (positive_score - negative_score) / total_score
        return 0.0

    def _calculate_physio_arousal(self, indicators: Dict[str, float]) -> float:
        """计算生理数据唤醒度"""
        high_arousal_indicators = ['stress', 'anxiety', 'excitement', 'high_energy', 'restlessness']
        low_arousal_indicators = ['calm', 'relaxed', 'low_energy', 'fatigue']

        high_arousal_score = sum(indicators.get(ind, 0) for ind in high_arousal_indicators)
        low_arousal_score = sum(indicators.get(ind, 0) for ind in low_arousal_indicators)

        total_score = high_arousal_score + low_arousal_score
        if total_score > 0:
            return high_arousal_score / total_score
        return 0.5

    def _create_default_result(self, modality: str, raw_data: Any) -> EmotionResult:
        """创建默认结果"""
        return EmotionResult(
            emotion="neutral",
            confidence=0.5,
            intensity=0.5,
            valence=0.0,
            arousal=0.5,
            timestamp=datetime.utcnow(),
            modality=modality,
            raw_data={"error": "分析失败", "input": str(raw_data)}
        )


class MultiModalEmotionAnalyzer:
    """多模态情绪分析器"""

    def __init__(self):
        self.text_analyzer = TextEmotionAnalyzer()
        self.audio_analyzer = AudioEmotionAnalyzer()
        self.visual_analyzer = VisualEmotionAnalyzer()
        self.physio_analyzer = PhysiologicalEmotionAnalyzer()

        # 模态权重配置
        self.modality_weights = {
            "text": 0.3,
            "audio": 0.25,
            "visual": 0.25,
            "physiological": 0.2
        }

        # 儿童年龄段权重调整
        self.age_weight_adjustments = {
            "0-5": {"visual": 0.4, "audio": 0.3, "text": 0.1, "physiological": 0.2},
            "6-8": {"visual": 0.35, "audio": 0.25, "text": 0.2, "physiological": 0.2},
            "9-12": {"text": 0.3, "visual": 0.3, "audio": 0.25, "physiological": 0.15},
            "13-17": {"text": 0.35, "audio": 0.25, "visual": 0.25, "physiological": 0.15}
        }

    async def analyze_multimodal_emotion(
        self,
        text_data: Optional[str] = None,
        audio_data: Optional[bytes] = None,
        image_data: Optional[bytes] = None,
        physio_data: Optional[Dict[str, Any]] = None,
        child_age: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> MultiModalEmotionResult:
        """多模态情绪分析"""

        try:
            # 并行分析各个模态
            analysis_tasks = []
            available_modalities = []

            if text_data:
                analysis_tasks.append(self.text_analyzer.analyze_text(text_data, child_age))
                available_modalities.append("text")

            if audio_data:
                analysis_tasks.append(self.audio_analyzer.analyze_audio(audio_data, child_age))
                available_modalities.append("audio")

            if image_data:
                analysis_tasks.append(self.visual_analyzer.analyze_image(image_data, child_age))
                available_modalities.append("visual")

            if physio_data:
                analysis_tasks.append(self.physio_analyzer.analyze_physiological_data(physio_data, child_age))
                available_modalities.append("physiological")

            if not analysis_tasks:
                return self._create_default_multimodal_result()

            # 执行并行分析
            modality_results = await asyncio.gather(*analysis_tasks)

            # 构建结果字典
            results_dict = {}
            for i, modality in enumerate(available_modalities):
                results_dict[modality] = modality_results[i]

            # 计算融合权重
            fusion_weights = self._calculate_fusion_weights(
                available_modalities, child_age, context
            )

            # 多模态融合
            fused_result = self._fuse_multimodal_results(
                results_dict, fusion_weights, context
            )

            return MultiModalEmotionResult(
                primary_emotion=fused_result['emotion'],
                confidence=fused_result['confidence'],
                intensity=fused_result['intensity'],
                modality_results=results_dict,
                fusion_weights=fusion_weights,
                context_factors=context or {},
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"多模态情绪分析失败: {str(e)}")
            return self._create_default_multimodal_result()

    def _calculate_fusion_weights(
        self,
        available_modalities: List[str],
        child_age: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """计算融合权重"""

        # 基础权重
        weights = {}
        for modality in available_modalities:
            weights[modality] = self.modality_weights.get(modality, 0.25)

        # 根据儿童年龄调整权重
        if child_age:
            age_group = self._get_age_group(child_age)
            age_adjustments = self.age_weight_adjustments.get(age_group, {})

            for modality in available_modalities:
                if modality in age_adjustments:
                    weights[modality] = age_adjustments[modality]

        # 根据上下文调整权重
        if context:
            weights = self._adjust_weights_by_context(weights, context)

        # 根据可用模态数量调整权重
        weights = self._adjust_weights_by_availability(weights, available_modalities)

        # 归一化权重
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}

        return weights

    def _get_age_group(self, age: int) -> str:
        """获取年龄组"""
        if age <= 5:
            return "0-5"
        elif age <= 8:
            return "6-8"
        elif age <= 12:
            return "9-12"
        else:
            return "13-17"

    def _adjust_weights_by_context(
        self,
        weights: Dict[str, float],
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """根据上下文调整权重"""

        # 环境因素调整
        environment = context.get('environment', '')
        if environment == 'noisy':
            # 嘈杂环境降低音频权重
            if 'audio' in weights:
                weights['audio'] *= 0.7
        elif environment == 'dark':
            # 黑暗环境降低视觉权重
            if 'visual' in weights:
                weights['visual'] *= 0.5

        # 活动类型调整
        activity = context.get('activity', '')
        if activity == 'reading':
            # 阅读时提高文本权重
            if 'text' in weights:
                weights['text'] *= 1.3
        elif activity == 'playing':
            # 游戏时提高视觉和音频权重
            if 'visual' in weights:
                weights['visual'] *= 1.2
            if 'audio' in weights:
                weights['audio'] *= 1.2

        # 设备类型调整
        device = context.get('device', '')
        if device == 'wearable':
            # 可穿戴设备提高生理数据权重
            if 'physiological' in weights:
                weights['physiological'] *= 1.5

        return weights

    def _adjust_weights_by_availability(
        self,
        weights: Dict[str, float],
        available_modalities: List[str]
    ) -> Dict[str, float]:
        """根据可用模态调整权重"""

        # 如果只有一个模态，权重为1
        if len(available_modalities) == 1:
            return {available_modalities[0]: 1.0}

        # 如果缺少关键模态，提高其他模态权重
        if 'text' not in available_modalities and 'audio' not in available_modalities:
            # 没有语言信息，提高视觉权重
            if 'visual' in weights:
                weights['visual'] *= 1.5

        if 'visual' not in available_modalities:
            # 没有视觉信息，提高其他模态权重
            for modality in weights:
                if modality != 'visual':
                    weights[modality] *= 1.2

        return weights

    def _fuse_multimodal_results(
        self,
        results: Dict[str, EmotionResult],
        weights: Dict[str, float],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """融合多模态结果"""

        # 收集所有情绪和分数
        emotion_scores = {}
        total_confidence = 0
        total_intensity = 0
        total_valence = 0
        total_arousal = 0

        for modality, result in results.items():
            weight = weights.get(modality, 0)

            # 累积情绪分数
            if result.emotion not in emotion_scores:
                emotion_scores[result.emotion] = 0
            emotion_scores[result.emotion] += result.confidence * weight

            # 累积其他指标
            total_confidence += result.confidence * weight
            total_intensity += result.intensity * weight
            total_valence += result.valence * weight
            total_arousal += result.arousal * weight

        # 确定主要情绪
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            emotion_confidence = emotion_scores[primary_emotion]
        else:
            primary_emotion = "neutral"
            emotion_confidence = 0.5

        # 一致性检查
        consistency_bonus = self._calculate_consistency_bonus(results)
        final_confidence = min(1.0, total_confidence + consistency_bonus)

        # 上下文调整
        if context:
            primary_emotion, final_confidence = self._adjust_by_context(
                primary_emotion, final_confidence, context
            )

        return {
            "emotion": primary_emotion,
            "confidence": final_confidence,
            "intensity": total_intensity,
            "valence": total_valence,
            "arousal": total_arousal,
            "emotion_scores": emotion_scores
        }

    def _calculate_consistency_bonus(self, results: Dict[str, EmotionResult]) -> float:
        """计算一致性奖励"""
        if len(results) < 2:
            return 0

        emotions = [result.emotion for result in results.values()]
        valences = [result.valence for result in results.values()]
        arousals = [result.arousal for result in results.values()]

        # 情绪一致性
        emotion_consistency = len(set(emotions)) / len(emotions)

        # 效价一致性
        valence_std = np.std(valences) if len(valences) > 1 else 0
        valence_consistency = max(0, 1 - valence_std)

        # 唤醒度一致性
        arousal_std = np.std(arousals) if len(arousals) > 1 else 0
        arousal_consistency = max(0, 1 - arousal_std)

        # 综合一致性奖励
        consistency = (emotion_consistency + valence_consistency + arousal_consistency) / 3
        return consistency * 0.2  # 最大20%的置信度奖励

    def _adjust_by_context(
        self,
        emotion: str,
        confidence: float,
        context: Dict[str, Any]
    ) -> Tuple[str, float]:
        """根据上下文调整结果"""

        # 时间因素
        time_of_day = context.get('time_of_day', '')
        if time_of_day == 'bedtime' and emotion == 'excited':
            # 睡前兴奋可能是焦虑
            emotion = 'anxious'
            confidence *= 0.9

        # 社交情境
        social_context = context.get('social_context', '')
        if social_context == 'alone' and emotion == 'happy':
            # 独处时的快乐置信度稍低
            confidence *= 0.9
        elif social_context == 'with_friends' and emotion == 'sad':
            # 和朋友在一起时的悲伤需要更高关注
            confidence *= 1.1

        # 活动情境
        activity = context.get('activity', '')
        if activity == 'homework' and emotion == 'frustrated':
            # 做作业时的挫败感很常见
            confidence *= 1.1

        return emotion, min(1.0, confidence)

    def _create_default_multimodal_result(self) -> MultiModalEmotionResult:
        """创建默认多模态结果"""
        return MultiModalEmotionResult(
            primary_emotion="neutral",
            confidence=0.5,
            intensity=0.5,
            modality_results={},
            fusion_weights={},
            context_factors={},
            timestamp=datetime.utcnow()
        )
