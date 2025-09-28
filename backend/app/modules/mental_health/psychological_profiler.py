"""
个性化心理画像系统
基于AI的儿童心理特征分析和个性化干预方案生成
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.core.logging import get_logger
from app.models.mental_health import Child, EmotionRecord, PsychologicalProfile
from app.modules.mental_health.emotion_analyzer import MultiModalEmotionResult

logger = get_logger(__name__)


@dataclass
class PersonalityTrait:
    """性格特征"""
    name: str
    score: float  # 0-1
    confidence: float
    description: str
    development_stage: str


@dataclass
class PsychologicalPattern:
    """心理模式"""
    pattern_type: str
    frequency: float
    intensity: float
    triggers: List[str]
    contexts: List[str]
    trend: str  # increasing, decreasing, stable


@dataclass
class InterventionRecommendation:
    """干预建议"""
    intervention_type: str
    priority: str  # high, medium, low
    description: str
    activities: List[Dict[str, Any]]
    expected_outcome: str
    duration_weeks: int
    success_metrics: List[str]


@dataclass
class PsychologicalProfileResult:
    """心理画像结果"""
    child_id: str
    personality_traits: List[PersonalityTrait]
    emotional_patterns: List[PsychologicalPattern]
    stress_triggers: List[str]
    coping_mechanisms: List[str]
    developmental_stage: str
    risk_assessment: Dict[str, Any]
    intervention_recommendations: List[InterventionRecommendation]
    confidence_score: float
    last_updated: datetime


class PersonalityAnalyzer:
    """性格分析器"""
    
    def __init__(self):
        # 大五人格模型适配儿童版本
        self.personality_dimensions = {
            "openness": "开放性",
            "conscientiousness": "责任心", 
            "extraversion": "外向性",
            "agreeableness": "宜人性",
            "neuroticism": "神经质"
        }
        
        # 儿童特定性格特征
        self.child_traits = {
            "curiosity": "好奇心",
            "resilience": "韧性",
            "social_confidence": "社交自信",
            "emotional_regulation": "情绪调节",
            "creativity": "创造力",
            "empathy": "共情能力"
        }
    
    async def analyze_personality(
        self, 
        emotion_history: List[EmotionRecord],
        child_age: int,
        behavioral_data: Dict[str, Any] = None
    ) -> List[PersonalityTrait]:
        """分析性格特征"""
        
        try:
            # 分析情绪数据中的性格指标
            emotion_traits = self._analyze_emotion_based_traits(emotion_history, child_age)
            
            # 分析行为数据中的性格指标
            behavioral_traits = self._analyze_behavioral_traits(behavioral_data, child_age)
            
            # 综合分析
            combined_traits = self._combine_trait_analysis(emotion_traits, behavioral_traits)
            
            # 年龄适配调整
            adjusted_traits = self._adjust_for_developmental_stage(combined_traits, child_age)
            
            return adjusted_traits
            
        except Exception as e:
            logger.error(f"性格分析失败: {str(e)}")
            return self._create_default_traits(child_age)
    
    def _analyze_emotion_based_traits(
        self, 
        emotion_history: List[EmotionRecord], 
        child_age: int
    ) -> Dict[str, float]:
        """基于情绪历史分析性格特征"""
        
        if not emotion_history:
            return {}
        
        traits = {}
        
        # 分析情绪稳定性 (神经质的反向)
        emotion_variability = self._calculate_emotion_variability(emotion_history)
        traits["emotional_stability"] = max(0, 1 - emotion_variability)
        
        # 分析外向性
        positive_emotions = ["happy", "excited", "joyful"]
        social_emotions = ["proud", "confident"]
        
        positive_ratio = self._calculate_emotion_ratio(emotion_history, positive_emotions)
        social_ratio = self._calculate_emotion_ratio(emotion_history, social_emotions)
        traits["extraversion"] = (positive_ratio + social_ratio) / 2
        
        # 分析开放性 (好奇心、创造力)
        curious_emotions = ["surprised", "interested", "excited"]
        curious_ratio = self._calculate_emotion_ratio(emotion_history, curious_emotions)
        traits["openness"] = curious_ratio
        
        # 分析宜人性 (合作、友善)
        cooperative_emotions = ["content", "peaceful", "loving"]
        cooperative_ratio = self._calculate_emotion_ratio(emotion_history, cooperative_emotions)
        traits["agreeableness"] = cooperative_ratio
        
        # 分析责任心 (通过情绪调节能力推断)
        regulation_score = self._analyze_emotion_regulation(emotion_history)
        traits["conscientiousness"] = regulation_score
        
        return traits
    
    def _calculate_emotion_variability(self, emotion_history: List[EmotionRecord]) -> float:
        """计算情绪变异性"""
        if len(emotion_history) < 2:
            return 0.5
        
        intensities = [record.intensity for record in emotion_history]
        return min(1.0, np.std(intensities))
    
    def _calculate_emotion_ratio(
        self, 
        emotion_history: List[EmotionRecord], 
        target_emotions: List[str]
    ) -> float:
        """计算特定情绪的比例"""
        if not emotion_history:
            return 0.5
        
        target_count = sum(1 for record in emotion_history 
                          if record.emotion_type in target_emotions)
        return target_count / len(emotion_history)
    
    def _analyze_emotion_regulation(self, emotion_history: List[EmotionRecord]) -> float:
        """分析情绪调节能力"""
        if len(emotion_history) < 3:
            return 0.5
        
        # 分析情绪恢复速度
        negative_emotions = ["sad", "angry", "anxious", "frustrated"]
        regulation_scores = []
        
        for i in range(len(emotion_history) - 2):
            current = emotion_history[i]
            next_emotion = emotion_history[i + 1]
            
            if (current.emotion_type in negative_emotions and 
                current.intensity > 0.6):
                # 检查后续情绪是否有所改善
                if next_emotion.intensity < current.intensity:
                    regulation_scores.append(1.0)
                else:
                    regulation_scores.append(0.0)
        
        return np.mean(regulation_scores) if regulation_scores else 0.5
    
    def _analyze_behavioral_traits(
        self, 
        behavioral_data: Dict[str, Any], 
        child_age: int
    ) -> Dict[str, float]:
        """分析行为数据中的性格特征"""
        
        if not behavioral_data:
            return {}
        
        traits = {}
        
        # 分析活动偏好
        activity_preferences = behavioral_data.get('activity_preferences', {})
        
        # 社交活动偏好 -> 外向性
        social_activities = activity_preferences.get('social', 0)
        traits["extraversion"] = min(1.0, social_activities / 10)
        
        # 创造性活动偏好 -> 开放性
        creative_activities = activity_preferences.get('creative', 0)
        traits["openness"] = min(1.0, creative_activities / 10)
        
        # 规律性行为 -> 责任心
        routine_adherence = behavioral_data.get('routine_adherence', 0.5)
        traits["conscientiousness"] = routine_adherence
        
        # 合作行为 -> 宜人性
        cooperation_score = behavioral_data.get('cooperation_score', 0.5)
        traits["agreeableness"] = cooperation_score
        
        return traits
    
    def _combine_trait_analysis(
        self, 
        emotion_traits: Dict[str, float], 
        behavioral_traits: Dict[str, float]
    ) -> Dict[str, float]:
        """综合特征分析"""
        
        combined = {}
        all_traits = set(emotion_traits.keys()) | set(behavioral_traits.keys())
        
        for trait in all_traits:
            emotion_score = emotion_traits.get(trait, 0.5)
            behavioral_score = behavioral_traits.get(trait, 0.5)
            
            # 加权平均，情绪数据权重稍高
            combined[trait] = emotion_score * 0.6 + behavioral_score * 0.4
        
        return combined
    
    def _adjust_for_developmental_stage(
        self, 
        traits: Dict[str, float], 
        child_age: int
    ) -> List[PersonalityTrait]:
        """根据发展阶段调整特征"""
        
        developmental_stage = self._get_developmental_stage(child_age)
        adjusted_traits = []
        
        for trait_name, score in traits.items():
            # 根据年龄调整特征表现
            adjusted_score = self._age_adjust_trait(trait_name, score, child_age)
            
            # 计算置信度
            confidence = self._calculate_trait_confidence(trait_name, child_age)
            
            # 获取描述
            description = self._get_trait_description(trait_name, adjusted_score, child_age)
            
            adjusted_traits.append(PersonalityTrait(
                name=trait_name,
                score=adjusted_score,
                confidence=confidence,
                description=description,
                development_stage=developmental_stage
            ))
        
        return adjusted_traits
    
    def _get_developmental_stage(self, age: int) -> str:
        """获取发展阶段"""
        if age <= 5:
            return "学前期"
        elif age <= 8:
            return "学龄早期"
        elif age <= 12:
            return "学龄期"
        elif age <= 15:
            return "青春早期"
        else:
            return "青春期"
    
    def _age_adjust_trait(self, trait_name: str, score: float, age: int) -> float:
        """年龄调整特征分数"""
        
        # 不同特征在不同年龄段的表现差异
        age_adjustments = {
            "extraversion": {
                "0-5": 1.1,    # 幼儿通常更外向
                "6-8": 1.0,
                "9-12": 0.9,   # 学龄期可能更内敛
                "13-17": 1.0
            },
            "openness": {
                "0-5": 1.2,    # 幼儿好奇心强
                "6-8": 1.1,
                "9-12": 1.0,
                "13-17": 0.9   # 青春期可能更保守
            },
            "conscientiousness": {
                "0-5": 0.7,    # 幼儿责任心发展不完全
                "6-8": 0.8,
                "9-12": 1.0,
                "13-17": 1.1   # 青春期责任心增强
            }
        }
        
        age_group = self._get_age_group_key(age)
        adjustment = age_adjustments.get(trait_name, {}).get(age_group, 1.0)
        
        return min(1.0, max(0.0, score * adjustment))
    
    def _get_age_group_key(self, age: int) -> str:
        """获取年龄组键"""
        if age <= 5:
            return "0-5"
        elif age <= 8:
            return "6-8"
        elif age <= 12:
            return "9-12"
        else:
            return "13-17"
    
    def _calculate_trait_confidence(self, trait_name: str, age: int) -> float:
        """计算特征置信度"""
        
        # 基础置信度
        base_confidence = 0.7
        
        # 年龄因素：年龄越大，性格越稳定
        age_factor = min(1.0, age / 15.0)
        
        # 特征稳定性因素
        trait_stability = {
            "extraversion": 0.8,
            "openness": 0.7,
            "conscientiousness": 0.6,  # 随年龄变化较大
            "agreeableness": 0.8,
            "emotional_stability": 0.7
        }
        
        stability = trait_stability.get(trait_name, 0.7)
        
        return base_confidence * age_factor * stability
    
    def _get_trait_description(self, trait_name: str, score: float, age: int) -> str:
        """获取特征描述"""
        
        descriptions = {
            "extraversion": {
                "high": "活泼外向，喜欢与人交往，表达能力强",
                "medium": "社交能力适中，在熟悉环境中表现活跃",
                "low": "较为内向，喜欢安静活动，需要时间适应新环境"
            },
            "openness": {
                "high": "好奇心强，富有想象力，喜欢探索新事物",
                "medium": "对新事物有一定兴趣，学习能力良好",
                "low": "偏好熟悉的活动，需要引导培养探索精神"
            },
            "conscientiousness": {
                "high": "自律性强，做事有条理，能够坚持完成任务",
                "medium": "基本能够遵守规则，需要适当督促",
                "low": "自控能力有待提高，需要更多结构化指导"
            }
        }
        
        level = "high" if score > 0.7 else "medium" if score > 0.4 else "low"
        return descriptions.get(trait_name, {}).get(level, "特征表现正常")
    
    def _create_default_traits(self, age: int) -> List[PersonalityTrait]:
        """创建默认特征"""
        
        default_traits = ["extraversion", "openness", "conscientiousness", "agreeableness"]
        traits = []
        
        for trait_name in default_traits:
            traits.append(PersonalityTrait(
                name=trait_name,
                score=0.5,
                confidence=0.5,
                description="数据不足，需要更多观察",
                development_stage=self._get_developmental_stage(age)
            ))
        
        return traits


class EmotionalPatternAnalyzer:
    """情绪模式分析器"""

    def __init__(self):
        self.pattern_types = [
            "daily_rhythm",      # 日常节律
            "stress_response",   # 压力反应
            "social_interaction", # 社交互动
            "learning_emotion",  # 学习情绪
            "family_dynamics"    # 家庭动态
        ]

    async def analyze_emotional_patterns(
        self,
        emotion_history: List[EmotionRecord],
        child_age: int,
        time_window_days: int = 30
    ) -> List[PsychologicalPattern]:
        """分析情绪模式"""

        try:
            patterns = []

            # 过滤时间窗口内的数据
            recent_emotions = self._filter_recent_emotions(emotion_history, time_window_days)

            if not recent_emotions:
                return []

            # 分析各种模式
            daily_patterns = await self._analyze_daily_patterns(recent_emotions)
            stress_patterns = await self._analyze_stress_patterns(recent_emotions)
            social_patterns = await self._analyze_social_patterns(recent_emotions)
            learning_patterns = await self._analyze_learning_patterns(recent_emotions)

            patterns.extend(daily_patterns)
            patterns.extend(stress_patterns)
            patterns.extend(social_patterns)
            patterns.extend(learning_patterns)

            return patterns

        except Exception as e:
            logger.error(f"情绪模式分析失败: {str(e)}")
            return []

    def _filter_recent_emotions(
        self,
        emotion_history: List[EmotionRecord],
        days: int
    ) -> List[EmotionRecord]:
        """过滤最近的情绪记录"""

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [record for record in emotion_history
                if record.recorded_at >= cutoff_date]

    async def _analyze_daily_patterns(
        self,
        emotions: List[EmotionRecord]
    ) -> List[PsychologicalPattern]:
        """分析日常情绪节律"""

        patterns = []

        # 按小时分组分析
        hourly_emotions = {}
        for emotion in emotions:
            hour = emotion.recorded_at.hour
            if hour not in hourly_emotions:
                hourly_emotions[hour] = []
            hourly_emotions[hour].append(emotion)

        # 识别情绪高峰和低谷
        hourly_intensities = {}
        for hour, emotion_list in hourly_emotions.items():
            avg_intensity = np.mean([e.intensity for e in emotion_list])
            hourly_intensities[hour] = avg_intensity

        if hourly_intensities:
            # 找出情绪高峰时段
            mean_intensity = np.mean(list(hourly_intensities.values()))
            std_intensity = np.std(list(hourly_intensities.values()))

            peak_hours = [hour for hour, intensity in hourly_intensities.items()
                         if intensity > mean_intensity + std_intensity]

            # 找出情绪低谷时段
            low_hours = [hour for hour, intensity in hourly_intensities.items()
                        if intensity < mean_intensity - std_intensity]

            if peak_hours:
                patterns.append(PsychologicalPattern(
                    pattern_type="daily_peak",
                    frequency=len(peak_hours) / 24,
                    intensity=max(hourly_intensities[h] for h in peak_hours),
                    triggers=[f"{h}:00时段" for h in peak_hours],
                    contexts=["日常作息"],
                    trend="stable"
                ))

            if low_hours:
                patterns.append(PsychologicalPattern(
                    pattern_type="daily_low",
                    frequency=len(low_hours) / 24,
                    intensity=min(hourly_intensities[h] for h in low_hours),
                    triggers=[f"{h}:00时段" for h in low_hours],
                    contexts=["日常作息"],
                    trend="stable"
                ))

        return patterns

    async def _analyze_stress_patterns(
        self,
        emotions: List[EmotionRecord]
    ) -> List[PsychologicalPattern]:
        """分析压力反应模式"""

        patterns = []
        stress_emotions = ["anxious", "frustrated", "overwhelmed", "angry"]

        # 识别压力事件
        stress_events = [e for e in emotions if e.emotion_type in stress_emotions and e.intensity > 0.6]

        if not stress_events:
            return patterns

        # 分析压力触发因素
        stress_triggers = []
        stress_contexts = []

        for event in stress_events:
            if event.trigger_events:
                stress_triggers.extend(event.trigger_events)
            if event.context:
                context_info = event.context.get('situation', '')
                if context_info:
                    stress_contexts.append(context_info)

        # 统计最常见的触发因素
        trigger_counts = {}
        for trigger in stress_triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

        common_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        if common_triggers:
            patterns.append(PsychologicalPattern(
                pattern_type="stress_response",
                frequency=len(stress_events) / len(emotions),
                intensity=np.mean([e.intensity for e in stress_events]),
                triggers=[trigger for trigger, _ in common_triggers],
                contexts=list(set(stress_contexts)),
                trend=self._calculate_trend([e.intensity for e in stress_events])
            ))

        return patterns

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 3:
            return "stable"

        # 简单线性趋势分析
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"


class PsychologicalProfiler:
    """心理画像生成器"""

    def __init__(self):
        self.personality_analyzer = PersonalityAnalyzer()
        self.pattern_analyzer = EmotionalPatternAnalyzer()
        self.risk_assessor = RiskAssessment()
        self.intervention_engine = InterventionEngine()

    async def generate_psychological_profile(
        self,
        child_id: str,
        emotion_history: List[EmotionRecord],
        child_age: int,
        behavioral_data: Dict[str, Any] = None,
        family_context: Dict[str, Any] = None
    ) -> PsychologicalProfileResult:
        """生成完整的心理画像"""

        try:
            # 并行分析各个维度
            personality_task = self.personality_analyzer.analyze_personality(
                emotion_history, child_age, behavioral_data
            )

            patterns_task = self.pattern_analyzer.analyze_emotional_patterns(
                emotion_history, child_age
            )

            # 等待分析完成
            personality_traits, emotional_patterns = await asyncio.gather(
                personality_task, patterns_task
            )

            # 风险评估
            risk_assessment = await self.risk_assessor.assess_risks(
                personality_traits, emotional_patterns, child_age, family_context
            )

            # 生成干预建议
            interventions = await self.intervention_engine.generate_intervention_recommendations(
                personality_traits, emotional_patterns, child_age, risk_assessment.get('risk_factors', [])
            )

            # 计算整体置信度
            confidence_score = self._calculate_overall_confidence(
                personality_traits, emotional_patterns, len(emotion_history)
            )

            return PsychologicalProfileResult(
                child_id=child_id,
                personality_traits=personality_traits,
                emotional_patterns=emotional_patterns,
                stress_triggers=self._extract_stress_triggers(emotional_patterns),
                coping_mechanisms=self._identify_coping_mechanisms(emotion_history),
                developmental_stage=self._determine_developmental_stage(child_age),
                risk_assessment=risk_assessment,
                intervention_recommendations=interventions,
                confidence_score=confidence_score,
                last_updated=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"心理画像生成失败: {str(e)}")
            return self._create_default_profile(child_id, child_age)

    def _extract_stress_triggers(self, patterns: List[PsychologicalPattern]) -> List[str]:
        """提取压力触发因素"""
        triggers = []
        for pattern in patterns:
            if pattern.pattern_type == "stress_response":
                triggers.extend(pattern.triggers)
        return list(set(triggers))

    def _identify_coping_mechanisms(self, emotion_history: List[EmotionRecord]) -> List[str]:
        """识别应对机制"""
        mechanisms = []

        # 分析情绪恢复模式
        for i in range(len(emotion_history) - 1):
            current = emotion_history[i]
            next_emotion = emotion_history[i + 1]

            if current.intensity > 0.7 and next_emotion.intensity < current.intensity - 0.3:
                # 情绪快速恢复，可能有有效的应对机制
                if current.context:
                    activity = current.context.get('recovery_activity', '')
                    if activity:
                        mechanisms.append(activity)

        # 添加常见的健康应对机制
        if not mechanisms:
            mechanisms = ["需要观察和培养", "建议引导积极应对方式"]

        return list(set(mechanisms))

    def _determine_developmental_stage(self, age: int) -> str:
        """确定发展阶段"""
        if age <= 5:
            return "学前期 - 基础情绪认知发展"
        elif age <= 8:
            return "学龄早期 - 社交技能建立"
        elif age <= 12:
            return "学龄期 - 自我概念形成"
        elif age <= 15:
            return "青春早期 - 身份探索"
        else:
            return "青春期 - 独立性发展"

    def _calculate_overall_confidence(
        self,
        traits: List[PersonalityTrait],
        patterns: List[PsychologicalPattern],
        data_points: int
    ) -> float:
        """计算整体置信度"""

        # 基于数据量的置信度
        data_confidence = min(1.0, data_points / 100.0)

        # 基于特征置信度的平均值
        trait_confidence = np.mean([t.confidence for t in traits]) if traits else 0.5

        # 基于模式数量的置信度
        pattern_confidence = min(1.0, len(patterns) / 5.0)

        # 综合置信度
        overall_confidence = (data_confidence * 0.4 + trait_confidence * 0.4 + pattern_confidence * 0.2)

        return round(overall_confidence, 2)

    def _create_default_profile(self, child_id: str, child_age: int) -> PsychologicalProfileResult:
        """创建默认画像"""
        return PsychologicalProfileResult(
            child_id=child_id,
            personality_traits=[],
            emotional_patterns=[],
            stress_triggers=[],
            coping_mechanisms=["需要更多观察"],
            developmental_stage=self._determine_developmental_stage(child_age),
            risk_assessment={"overall_risk": "unknown", "risk_factors": []},
            intervention_recommendations=[],
            confidence_score=0.3,
            last_updated=datetime.utcnow()
        )


class RiskAssessment:
    """风险评估器"""

    def __init__(self):
        self.risk_indicators = {
            "depression": {
                "emotional_patterns": ["persistent_sadness", "low_energy", "withdrawal"],
                "personality_traits": ["low_extraversion", "high_neuroticism"],
                "threshold": 0.6
            },
            "anxiety": {
                "emotional_patterns": ["stress_response", "social_anxiety"],
                "personality_traits": ["high_neuroticism", "low_emotional_stability"],
                "threshold": 0.7
            },
            "behavioral_issues": {
                "emotional_patterns": ["anger_outbursts", "defiance"],
                "personality_traits": ["low_conscientiousness", "low_agreeableness"],
                "threshold": 0.6
            },
            "social_difficulties": {
                "emotional_patterns": ["social_anxiety", "isolation"],
                "personality_traits": ["low_extraversion", "low_social_confidence"],
                "threshold": 0.5
            }
        }

    async def assess_risks(
        self,
        personality_traits: List[PersonalityTrait],
        emotional_patterns: List[PsychologicalPattern],
        child_age: int,
        family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """评估心理健康风险"""

        try:
            risk_scores = {}
            risk_factors = []
            protective_factors = []

            # 评估各类风险
            for risk_type, indicators in self.risk_indicators.items():
                score = self._calculate_risk_score(
                    risk_type, indicators, personality_traits, emotional_patterns
                )
                risk_scores[risk_type] = score

                if score > indicators["threshold"]:
                    risk_factors.append(risk_type)

            # 识别保护因素
            protective_factors = self._identify_protective_factors(
                personality_traits, family_context
            )

            # 计算整体风险等级
            overall_risk = self._calculate_overall_risk(risk_scores, protective_factors)

            # 生成风险报告
            risk_report = self._generate_risk_report(
                risk_scores, risk_factors, protective_factors, child_age
            )

            return {
                "overall_risk": overall_risk,
                "risk_scores": risk_scores,
                "risk_factors": risk_factors,
                "protective_factors": protective_factors,
                "risk_report": risk_report,
                "recommendations": self._generate_risk_recommendations(risk_factors, child_age)
            }

        except Exception as e:
            logger.error(f"风险评估失败: {str(e)}")
            return {"overall_risk": "unknown", "risk_factors": [], "protective_factors": []}

    def _calculate_risk_score(
        self,
        risk_type: str,
        indicators: Dict[str, Any],
        traits: List[PersonalityTrait],
        patterns: List[PsychologicalPattern]
    ) -> float:
        """计算特定风险的分数"""

        score = 0.0
        total_indicators = 0

        # 检查情绪模式指标
        pattern_indicators = indicators.get("emotional_patterns", [])
        for pattern in patterns:
            if pattern.pattern_type in pattern_indicators:
                score += pattern.intensity * pattern.frequency
                total_indicators += 1

        # 检查性格特征指标
        trait_indicators = indicators.get("personality_traits", [])
        trait_dict = {t.name: t for t in traits}

        for trait_indicator in trait_indicators:
            if trait_indicator.startswith("low_"):
                trait_name = trait_indicator[4:]
                if trait_name in trait_dict:
                    # 低分特征作为风险因素
                    score += (1 - trait_dict[trait_name].score) * trait_dict[trait_name].confidence
                    total_indicators += 1
            elif trait_indicator.startswith("high_"):
                trait_name = trait_indicator[5:]
                if trait_name in trait_dict:
                    # 高分特征作为风险因素
                    score += trait_dict[trait_name].score * trait_dict[trait_name].confidence
                    total_indicators += 1

        return score / total_indicators if total_indicators > 0 else 0.0

    def _identify_protective_factors(
        self,
        traits: List[PersonalityTrait],
        family_context: Dict[str, Any] = None
    ) -> List[str]:
        """识别保护因素"""

        protective_factors = []

        # 基于性格特征的保护因素
        trait_dict = {t.name: t for t in traits}

        if "emotional_stability" in trait_dict and trait_dict["emotional_stability"].score > 0.7:
            protective_factors.append("情绪稳定性强")

        if "extraversion" in trait_dict and trait_dict["extraversion"].score > 0.6:
            protective_factors.append("社交能力良好")

        if "conscientiousness" in trait_dict and trait_dict["conscientiousness"].score > 0.7:
            protective_factors.append("自律性强")

        # 基于家庭环境的保护因素
        if family_context:
            if family_context.get("family_support", 0) > 0.7:
                protective_factors.append("家庭支持充分")

            if family_context.get("stable_environment", False):
                protective_factors.append("环境稳定")

        return protective_factors

    def _calculate_overall_risk(
        self,
        risk_scores: Dict[str, float],
        protective_factors: List[str]
    ) -> str:
        """计算整体风险等级"""

        # 计算平均风险分数
        avg_risk = np.mean(list(risk_scores.values())) if risk_scores else 0.0

        # 保护因素调整
        protection_adjustment = len(protective_factors) * 0.1
        adjusted_risk = max(0.0, avg_risk - protection_adjustment)

        if adjusted_risk < 0.3:
            return "low"
        elif adjusted_risk < 0.6:
            return "medium"
        else:
            return "high"

    def _generate_risk_report(
        self,
        risk_scores: Dict[str, float],
        risk_factors: List[str],
        protective_factors: List[str],
        child_age: int
    ) -> str:
        """生成风险报告"""

        report = f"年龄{child_age}岁儿童心理健康风险评估报告：\n\n"

        if risk_factors:
            report += "识别的风险因素：\n"
            for factor in risk_factors:
                score = risk_scores.get(factor, 0)
                report += f"- {factor}: 风险程度 {score:.2f}\n"
        else:
            report += "未发现显著风险因素。\n"

        if protective_factors:
            report += "\n保护因素：\n"
            for factor in protective_factors:
                report += f"- {factor}\n"

        return report

    def _generate_risk_recommendations(
        self,
        risk_factors: List[str],
        child_age: int
    ) -> List[str]:
        """生成风险管理建议"""

        recommendations = []

        if "depression" in risk_factors:
            recommendations.append("建议寻求专业心理咨询师帮助")
            recommendations.append("增加积极活动和社交互动")

        if "anxiety" in risk_factors:
            recommendations.append("学习放松技巧和应对策略")
            recommendations.append("创造安全稳定的环境")

        if "behavioral_issues" in risk_factors:
            recommendations.append("建立清晰的行为规则和后果")
            recommendations.append("使用正面强化策略")

        if "social_difficulties" in risk_factors:
            recommendations.append("提供社交技能训练")
            recommendations.append("创造安全的社交练习机会")

        if not recommendations:
            recommendations.append("继续保持良好的心理健康状态")
            recommendations.append("定期进行心理健康检查")

        return recommendations


class InterventionEngine:
    """干预推荐引擎"""

    def __init__(self):
        self.intervention_database = {
            "emotional_regulation": {
                "name": "情绪调节训练",
                "description": "帮助儿童学习识别、理解和管理情绪",
                "activities": ["深呼吸练习", "情绪日记", "正念冥想"],
                "duration_weeks": 6,
                "success_metrics": ["情绪稳定性提升", "自我调节能力增强"]
            },
            "social_skills": {
                "name": "社交技能训练",
                "description": "提升儿童的人际交往和沟通能力",
                "activities": ["角色扮演", "社交游戏", "沟通练习"],
                "duration_weeks": 8,
                "success_metrics": ["社交自信提升", "友谊质量改善"]
            },
            "anxiety_management": {
                "name": "焦虑管理",
                "description": "学习应对焦虑的有效策略",
                "activities": ["渐进式肌肉放松", "认知重构", "暴露疗法"],
                "duration_weeks": 10,
                "success_metrics": ["焦虑水平降低", "应对能力提升"]
            }
        }

    async def generate_intervention_recommendations(
        self,
        personality_traits: List[PersonalityTrait],
        emotional_patterns: List[PsychologicalPattern],
        child_age: int,
        risk_factors: List[str] = None
    ) -> List[InterventionRecommendation]:
        """生成干预建议"""

        recommendations = []

        # 基于风险因素生成建议
        if risk_factors:
            for risk in risk_factors:
                if risk == "anxiety":
                    recommendations.append(self._create_anxiety_intervention(child_age))
                elif risk == "depression":
                    recommendations.append(self._create_mood_intervention(child_age))
                elif risk == "social_difficulties":
                    recommendations.append(self._create_social_intervention(child_age))

        # 基于情绪模式生成建议
        for pattern in emotional_patterns:
            if pattern.pattern_type == "stress_response" and pattern.intensity > 0.7:
                recommendations.append(self._create_stress_management_intervention(child_age))

        # 去重并排序
        unique_recommendations = []
        seen_types = set()

        for rec in recommendations:
            if rec.intervention_type not in seen_types:
                unique_recommendations.append(rec)
                seen_types.add(rec.intervention_type)

        return unique_recommendations[:3]  # 返回前3个建议

    def _create_anxiety_intervention(self, child_age: int) -> InterventionRecommendation:
        """创建焦虑干预建议"""
        return InterventionRecommendation(
            intervention_type="anxiety_management",
            priority="high",
            description="针对焦虑情绪的专门干预训练",
            activities=[
                {"name": "深呼吸练习", "frequency": "每日2次", "duration": "5分钟"},
                {"name": "渐进式肌肉放松", "frequency": "每日1次", "duration": "15分钟"},
                {"name": "正念冥想", "frequency": "每周3次", "duration": "10分钟"}
            ],
            expected_outcome="焦虑水平显著降低，应对能力提升",
            duration_weeks=8,
            success_metrics=["焦虑评分降低30%", "睡眠质量改善", "学校表现提升"]
        )

    def _create_mood_intervention(self, child_age: int) -> InterventionRecommendation:
        """创建情绪提升干预建议"""
        return InterventionRecommendation(
            intervention_type="mood_enhancement",
            priority="high",
            description="提升积极情绪和心理韧性",
            activities=[
                {"name": "感恩日记", "frequency": "每日", "duration": "10分钟"},
                {"name": "积极活动安排", "frequency": "每周3次", "duration": "30分钟"},
                {"name": "成就庆祝", "frequency": "每周", "duration": "不限"}
            ],
            expected_outcome="情绪状态改善，积极性提升",
            duration_weeks=6,
            success_metrics=["积极情绪增加", "活动参与度提升", "自信心增强"]
        )

    def _create_social_intervention(self, child_age: int) -> InterventionRecommendation:
        """创建社交技能干预建议"""
        return InterventionRecommendation(
            intervention_type="social_skills",
            priority="medium",
            description="提升社交能力和人际关系质量",
            activities=[
                {"name": "角色扮演游戏", "frequency": "每周2次", "duration": "20分钟"},
                {"name": "社交故事练习", "frequency": "每周1次", "duration": "15分钟"},
                {"name": "小组活动参与", "frequency": "每周1次", "duration": "60分钟"}
            ],
            expected_outcome="社交自信提升，友谊关系改善",
            duration_weeks=10,
            success_metrics=["社交互动增加", "友谊数量提升", "社交焦虑减少"]
        )

    def _create_stress_management_intervention(self, child_age: int) -> InterventionRecommendation:
        """创建压力管理干预建议"""
        return InterventionRecommendation(
            intervention_type="stress_management",
            priority="medium",
            description="学习有效的压力应对策略",
            activities=[
                {"name": "压力识别训练", "frequency": "每周1次", "duration": "20分钟"},
                {"name": "应对策略练习", "frequency": "每周2次", "duration": "15分钟"},
                {"name": "放松技巧训练", "frequency": "每日", "duration": "10分钟"}
            ],
            expected_outcome="压力应对能力提升，情绪调节改善",
            duration_weeks=6,
            success_metrics=["压力反应强度降低", "恢复时间缩短", "应对策略多样化"]
        )
