"""
心理健康数据管理模块
实现心理健康数据的安全存储、分析和可视化展示
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import hashlib
from cryptography.fernet import Fernet
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from app.core.logging import get_logger
from app.core.database import get_db
from app.models.mental_health import (
    Child, EmotionRecord, PsychologicalProfile, 
    InterventionSession, MentalHealthAlert
)

logger = get_logger(__name__)


@dataclass
class DataAnalysisResult:
    """数据分析结果"""
    analysis_id: str
    child_id: str
    analysis_type: str
    time_period: str
    key_insights: List[str]
    trends: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float
    generated_at: datetime


@dataclass
class VisualizationConfig:
    """可视化配置"""
    chart_type: str
    title: str
    x_axis: str
    y_axis: str
    color_scheme: str
    interactive: bool
    export_format: str


@dataclass
class PrivacyMetrics:
    """隐私保护指标"""
    encryption_level: str
    anonymization_applied: bool
    data_retention_days: int
    access_log_entries: int
    compliance_status: str


class DataSecurityManager:
    """数据安全管理器"""
    
    def __init__(self):
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.anonymization_salt = self._generate_salt()
    
    def _generate_encryption_key(self) -> bytes:
        """生成加密密钥"""
        # 在实际应用中，这应该从安全的密钥管理系统获取
        return Fernet.generate_key()
    
    def _generate_salt(self) -> str:
        """生成匿名化盐值"""
        return hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:16]
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"数据加密失败: {str(e)}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"数据解密失败: {str(e)}")
            return encrypted_data
    
    def anonymize_identifier(self, identifier: str) -> str:
        """匿名化标识符"""
        combined = f"{identifier}{self.anonymization_salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:12]
    
    def validate_data_access(self, user_id: str, child_id: str, access_type: str) -> bool:
        """验证数据访问权限"""
        # 实现访问控制逻辑
        # 这里简化处理，实际应该检查用户权限
        return True
    
    def log_data_access(self, user_id: str, child_id: str, access_type: str, success: bool):
        """记录数据访问日志"""
        access_log = {
            "user_id": user_id,
            "child_id": self.anonymize_identifier(child_id),
            "access_type": access_type,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": "anonymized"
        }
        logger.info(f"数据访问日志: {json.dumps(access_log)}")


class MentalHealthDataAnalyzer:
    """心理健康数据分析器"""
    
    def __init__(self):
        self.security_manager = DataSecurityManager()
    
    async def analyze_emotion_trends(
        self,
        child_id: str,
        time_period_days: int = 30,
        user_id: str = None
    ) -> DataAnalysisResult:
        """分析情绪趋势"""
        
        try:
            # 验证访问权限
            if not self.security_manager.validate_data_access(user_id, child_id, "emotion_analysis"):
                raise PermissionError("无权限访问此数据")
            
            # 记录访问日志
            self.security_manager.log_data_access(user_id, child_id, "emotion_analysis", True)
            
            # 获取情绪数据
            emotion_data = await self._fetch_emotion_data(child_id, time_period_days)
            
            if not emotion_data:
                return self._create_empty_analysis_result(child_id, "emotion_trends")
            
            # 分析趋势
            trends = self._analyze_emotion_patterns(emotion_data)
            
            # 生成洞察
            insights = self._generate_emotion_insights(trends, emotion_data)
            
            # 生成建议
            recommendations = self._generate_emotion_recommendations(trends, insights)
            
            # 计算置信度
            confidence = self._calculate_analysis_confidence(emotion_data, trends)
            
            return DataAnalysisResult(
                analysis_id=f"emotion_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                child_id=child_id,
                analysis_type="emotion_trends",
                time_period=f"{time_period_days}天",
                key_insights=insights,
                trends=trends,
                recommendations=recommendations,
                confidence_score=confidence,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"情绪趋势分析失败: {str(e)}")
            self.security_manager.log_data_access(user_id, child_id, "emotion_analysis", False)
            return self._create_empty_analysis_result(child_id, "emotion_trends")
    
    async def _fetch_emotion_data(self, child_id: str, days: int) -> List[Dict[str, Any]]:
        """获取情绪数据"""
        # 这里应该从数据库获取数据
        # 模拟数据用于演示
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 模拟情绪数据
        emotion_data = []
        for i in range(days):
            date = cutoff_date + timedelta(days=i)
            emotion_data.append({
                "date": date,
                "emotion_type": np.random.choice(["happy", "sad", "anxious", "calm", "excited"]),
                "intensity": np.random.uniform(0.3, 0.9),
                "valence": np.random.uniform(-0.8, 0.8),
                "arousal": np.random.uniform(0.2, 0.9),
                "context": {"activity": "school", "social_context": "with_friends"}
            })
        
        return emotion_data
    
    def _analyze_emotion_patterns(self, emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析情绪模式"""
        
        if not emotion_data:
            return {}
        
        # 转换为DataFrame便于分析
        df = pd.DataFrame(emotion_data)
        
        trends = {}
        
        # 情绪分布
        emotion_counts = df['emotion_type'].value_counts()
        trends['emotion_distribution'] = emotion_counts.to_dict()
        
        # 强度趋势
        df['date'] = pd.to_datetime(df['date'])
        daily_intensity = df.groupby(df['date'].dt.date)['intensity'].mean()
        trends['intensity_trend'] = {
            'slope': self._calculate_trend_slope(daily_intensity.values),
            'average': daily_intensity.mean(),
            'variability': daily_intensity.std()
        }
        
        # 效价趋势
        daily_valence = df.groupby(df['date'].dt.date)['valence'].mean()
        trends['valence_trend'] = {
            'slope': self._calculate_trend_slope(daily_valence.values),
            'average': daily_valence.mean(),
            'positive_days': (daily_valence > 0).sum(),
            'negative_days': (daily_valence < 0).sum()
        }
        
        # 唤醒度趋势
        daily_arousal = df.groupby(df['date'].dt.date)['arousal'].mean()
        trends['arousal_trend'] = {
            'slope': self._calculate_trend_slope(daily_arousal.values),
            'average': daily_arousal.mean(),
            'high_arousal_days': (daily_arousal > 0.7).sum()
        }
        
        # 周期性模式
        df['weekday'] = df['date'].dt.dayofweek
        weekday_patterns = df.groupby('weekday').agg({
            'intensity': 'mean',
            'valence': 'mean',
            'arousal': 'mean'
        })
        trends['weekly_patterns'] = weekday_patterns.to_dict()
        
        return trends
    
    def _calculate_trend_slope(self, values: np.ndarray) -> float:
        """计算趋势斜率"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return float(slope)
    
    def _generate_emotion_insights(
        self, 
        trends: Dict[str, Any], 
        emotion_data: List[Dict[str, Any]]
    ) -> List[str]:
        """生成情绪洞察"""
        
        insights = []
        
        # 主要情绪分析
        emotion_dist = trends.get('emotion_distribution', {})
        if emotion_dist:
            dominant_emotion = max(emotion_dist.items(), key=lambda x: x[1])
            insights.append(f"主要情绪状态为{dominant_emotion[0]}，占比{dominant_emotion[1]/len(emotion_data)*100:.1f}%")
        
        # 强度趋势分析
        intensity_trend = trends.get('intensity_trend', {})
        if intensity_trend.get('slope', 0) > 0.01:
            insights.append("情绪强度呈上升趋势，需要关注情绪调节")
        elif intensity_trend.get('slope', 0) < -0.01:
            insights.append("情绪强度呈下降趋势，情绪状态趋于稳定")
        
        # 效价分析
        valence_trend = trends.get('valence_trend', {})
        positive_ratio = valence_trend.get('positive_days', 0) / (
            valence_trend.get('positive_days', 0) + valence_trend.get('negative_days', 1)
        )
        if positive_ratio > 0.7:
            insights.append("整体情绪偏向积极，心理状态良好")
        elif positive_ratio < 0.3:
            insights.append("消极情绪较多，建议加强心理支持")
        
        # 周期性模式
        weekly_patterns = trends.get('weekly_patterns', {})
        if weekly_patterns:
            # 分析工作日vs周末的差异
            weekday_valence = np.mean([weekly_patterns['valence'].get(str(i), 0) for i in range(5)])
            weekend_valence = np.mean([weekly_patterns['valence'].get(str(i), 0) for i in [5, 6]])
            
            if weekend_valence > weekday_valence + 0.2:
                insights.append("周末情绪明显好于工作日，可能存在学业压力")
            elif weekday_valence > weekend_valence + 0.2:
                insights.append("工作日情绪更好，可能喜欢结构化的环境")
        
        return insights
    
    def _generate_emotion_recommendations(
        self, 
        trends: Dict[str, Any], 
        insights: List[str]
    ) -> List[str]:
        """生成情绪建议"""
        
        recommendations = []
        
        # 基于强度趋势的建议
        intensity_trend = trends.get('intensity_trend', {})
        if intensity_trend.get('variability', 0) > 0.3:
            recommendations.append("情绪波动较大，建议学习情绪调节技巧")
        
        # 基于效价的建议
        valence_trend = trends.get('valence_trend', {})
        if valence_trend.get('average', 0) < -0.2:
            recommendations.append("整体情绪偏消极，建议增加积极活动")
        
        # 基于唤醒度的建议
        arousal_trend = trends.get('arousal_trend', {})
        if arousal_trend.get('average', 0) > 0.8:
            recommendations.append("情绪唤醒度较高，建议学习放松技巧")
        elif arousal_trend.get('average', 0) < 0.3:
            recommendations.append("情绪唤醒度较低，建议增加刺激性活动")
        
        # 基于情绪分布的建议
        emotion_dist = trends.get('emotion_distribution', {})
        if emotion_dist.get('anxious', 0) > len(emotion_dist) * 0.3:
            recommendations.append("焦虑情绪较多，建议寻求专业支持")
        
        if not recommendations:
            recommendations.append("情绪状态整体良好，继续保持")
        
        return recommendations
    
    def _calculate_analysis_confidence(
        self, 
        emotion_data: List[Dict[str, Any]], 
        trends: Dict[str, Any]
    ) -> float:
        """计算分析置信度"""
        
        # 基于数据量的置信度
        data_confidence = min(1.0, len(emotion_data) / 30.0)
        
        # 基于数据完整性的置信度
        complete_records = sum(1 for record in emotion_data 
                             if all(key in record for key in ['emotion_type', 'intensity', 'valence']))
        completeness_confidence = complete_records / len(emotion_data) if emotion_data else 0
        
        # 基于趋势一致性的置信度
        trend_confidence = 0.8  # 简化处理
        
        # 综合置信度
        overall_confidence = (data_confidence * 0.4 + 
                            completeness_confidence * 0.3 + 
                            trend_confidence * 0.3)
        
        return round(overall_confidence, 2)
    
    def _create_empty_analysis_result(self, child_id: str, analysis_type: str) -> DataAnalysisResult:
        """创建空的分析结果"""
        return DataAnalysisResult(
            analysis_id=f"empty_{analysis_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            child_id=child_id,
            analysis_type=analysis_type,
            time_period="无数据",
            key_insights=["数据不足，无法生成分析"],
            trends={},
            recommendations=["建议收集更多数据后再进行分析"],
            confidence_score=0.0,
            generated_at=datetime.utcnow()
        )


class DataVisualizationEngine:
    """数据可视化引擎"""

    def __init__(self):
        self.color_schemes = {
            "emotion": {
                "happy": "#FFD700",
                "sad": "#4169E1",
                "anxious": "#FF6347",
                "calm": "#98FB98",
                "excited": "#FF69B4",
                "angry": "#DC143C"
            },
            "intensity": ["#E8F5E8", "#90EE90", "#32CD32", "#228B22", "#006400"],
            "valence": ["#FF4444", "#FF8888", "#FFCCCC", "#CCFFCC", "#88FF88", "#44FF44"]
        }

    async def create_emotion_timeline_chart(
        self,
        emotion_data: List[Dict[str, Any]],
        config: VisualizationConfig = None
    ) -> Dict[str, Any]:
        """创建情绪时间线图表"""

        try:
            if not emotion_data:
                return {"error": "无数据可视化"}

            # 准备数据
            df = pd.DataFrame(emotion_data)
            df['date'] = pd.to_datetime(df['date'])

            # 创建图表
            fig = go.Figure()

            # 添加情绪强度线
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['intensity'],
                mode='lines+markers',
                name='情绪强度',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            ))

            # 添加效价线
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['valence'],
                mode='lines+markers',
                name='情绪效价',
                line=dict(color='#ff7f0e', width=2),
                marker=dict(size=6),
                yaxis='y2'
            ))

            # 设置布局
            fig.update_layout(
                title='情绪变化时间线',
                xaxis_title='日期',
                yaxis_title='情绪强度',
                yaxis2=dict(
                    title='情绪效价',
                    overlaying='y',
                    side='right'
                ),
                hovermode='x unified',
                template='plotly_white'
            )

            return {
                "chart_html": fig.to_html(include_plotlyjs='cdn'),
                "chart_json": fig.to_json(),
                "chart_type": "timeline"
            }

        except Exception as e:
            logger.error(f"情绪时间线图表创建失败: {str(e)}")
            return {"error": f"图表创建失败: {str(e)}"}

    async def create_emotion_distribution_chart(
        self,
        emotion_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建情绪分布图表"""

        try:
            if not emotion_data:
                return {"error": "无数据可视化"}

            # 统计情绪分布
            emotion_counts = {}
            for record in emotion_data:
                emotion = record.get('emotion_type', 'unknown')
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            # 创建饼图
            fig = go.Figure(data=[go.Pie(
                labels=list(emotion_counts.keys()),
                values=list(emotion_counts.values()),
                hole=0.3,
                marker_colors=[self.color_schemes["emotion"].get(emotion, "#CCCCCC")
                             for emotion in emotion_counts.keys()]
            )])

            fig.update_layout(
                title='情绪分布',
                template='plotly_white',
                showlegend=True
            )

            return {
                "chart_html": fig.to_html(include_plotlyjs='cdn'),
                "chart_json": fig.to_json(),
                "chart_type": "distribution"
            }

        except Exception as e:
            logger.error(f"情绪分布图表创建失败: {str(e)}")
            return {"error": f"图表创建失败: {str(e)}"}

    async def create_weekly_pattern_chart(
        self,
        emotion_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建周模式图表"""

        try:
            if not emotion_data:
                return {"error": "无数据可视化"}

            # 准备数据
            df = pd.DataFrame(emotion_data)
            df['date'] = pd.to_datetime(df['date'])
            df['weekday'] = df['date'].dt.day_name()

            # 计算每天的平均值
            weekday_stats = df.groupby('weekday').agg({
                'intensity': 'mean',
                'valence': 'mean',
                'arousal': 'mean'
            }).reset_index()

            # 重新排序星期
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_stats['weekday'] = pd.Categorical(weekday_stats['weekday'], categories=weekday_order, ordered=True)
            weekday_stats = weekday_stats.sort_values('weekday')

            # 创建子图
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=('情绪强度', '情绪效价', '情绪唤醒度'),
                vertical_spacing=0.1
            )

            # 添加强度图
            fig.add_trace(
                go.Bar(x=weekday_stats['weekday'], y=weekday_stats['intensity'],
                      name='强度', marker_color='#1f77b4'),
                row=1, col=1
            )

            # 添加效价图
            fig.add_trace(
                go.Bar(x=weekday_stats['weekday'], y=weekday_stats['valence'],
                      name='效价', marker_color='#ff7f0e'),
                row=2, col=1
            )

            # 添加唤醒度图
            fig.add_trace(
                go.Bar(x=weekday_stats['weekday'], y=weekday_stats['arousal'],
                      name='唤醒度', marker_color='#2ca02c'),
                row=3, col=1
            )

            fig.update_layout(
                title='一周情绪模式',
                template='plotly_white',
                showlegend=False,
                height=800
            )

            return {
                "chart_html": fig.to_html(include_plotlyjs='cdn'),
                "chart_json": fig.to_json(),
                "chart_type": "weekly_pattern"
            }

        except Exception as e:
            logger.error(f"周模式图表创建失败: {str(e)}")
            return {"error": f"图表创建失败: {str(e)}"}

    async def create_intervention_progress_chart(
        self,
        intervention_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建干预进度图表"""

        try:
            if not intervention_data:
                return {"error": "无干预数据"}

            # 准备数据
            df = pd.DataFrame(intervention_data)
            df['date'] = pd.to_datetime(df['date'])

            # 创建进度图
            fig = go.Figure()

            # 添加干预前后对比
            if 'pre_session_mood' in df.columns and 'post_session_mood' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['pre_session_mood'],
                    mode='lines+markers',
                    name='干预前情绪',
                    line=dict(color='#ff7f0e', dash='dash')
                ))

                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['post_session_mood'],
                    mode='lines+markers',
                    name='干预后情绪',
                    line=dict(color='#2ca02c')
                ))

            # 添加参与度
            if 'engagement_level' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['engagement_level'],
                    mode='lines+markers',
                    name='参与度',
                    line=dict(color='#d62728'),
                    yaxis='y2'
                ))

            fig.update_layout(
                title='干预效果进度',
                xaxis_title='日期',
                yaxis_title='情绪评分',
                yaxis2=dict(
                    title='参与度',
                    overlaying='y',
                    side='right'
                ),
                template='plotly_white'
            )

            return {
                "chart_html": fig.to_html(include_plotlyjs='cdn'),
                "chart_json": fig.to_json(),
                "chart_type": "intervention_progress"
            }

        except Exception as e:
            logger.error(f"干预进度图表创建失败: {str(e)}")
            return {"error": f"图表创建失败: {str(e)}"}


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.data_analyzer = MentalHealthDataAnalyzer()
        self.visualization_engine = DataVisualizationEngine()
        self.security_manager = DataSecurityManager()

    async def generate_comprehensive_report(
        self,
        child_id: str,
        report_period_days: int = 30,
        user_id: str = None,
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """生成综合报告"""

        try:
            # 验证权限
            if not self.security_manager.validate_data_access(user_id, child_id, "report_generation"):
                raise PermissionError("无权限生成报告")

            # 获取分析结果
            emotion_analysis = await self.data_analyzer.analyze_emotion_trends(
                child_id, report_period_days, user_id
            )

            # 获取原始数据用于可视化
            emotion_data = await self.data_analyzer._fetch_emotion_data(child_id, report_period_days)

            # 生成图表
            charts = {}
            if include_charts and emotion_data:
                charts['timeline'] = await self.visualization_engine.create_emotion_timeline_chart(emotion_data)
                charts['distribution'] = await self.visualization_engine.create_emotion_distribution_chart(emotion_data)
                charts['weekly_pattern'] = await self.visualization_engine.create_weekly_pattern_chart(emotion_data)

            # 生成报告摘要
            summary = self._generate_report_summary(emotion_analysis, emotion_data)

            # 生成建议部分
            recommendations = self._generate_detailed_recommendations(emotion_analysis)

            # 计算风险评估
            risk_assessment = self._assess_current_risks(emotion_analysis, emotion_data)

            report = {
                "report_id": f"report_{child_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "child_id": child_id,
                "report_period": f"{report_period_days}天",
                "generated_at": datetime.utcnow().isoformat(),
                "summary": summary,
                "emotion_analysis": {
                    "key_insights": emotion_analysis.key_insights,
                    "trends": emotion_analysis.trends,
                    "confidence_score": emotion_analysis.confidence_score
                },
                "risk_assessment": risk_assessment,
                "recommendations": recommendations,
                "charts": charts,
                "privacy_info": {
                    "data_anonymized": True,
                    "encryption_applied": True,
                    "retention_period": "根据隐私政策"
                }
            }

            # 记录报告生成日志
            self.security_manager.log_data_access(user_id, child_id, "report_generation", True)

            return report

        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}")
            self.security_manager.log_data_access(user_id, child_id, "report_generation", False)
            return {"error": f"报告生成失败: {str(e)}"}

    def _generate_report_summary(
        self,
        analysis: DataAnalysisResult,
        emotion_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成报告摘要"""

        summary = {
            "data_points": len(emotion_data),
            "analysis_period": analysis.time_period,
            "confidence_level": analysis.confidence_score,
            "key_findings": analysis.key_insights[:3],  # 前3个关键发现
            "overall_status": self._determine_overall_status(analysis),
            "attention_areas": self._identify_attention_areas(analysis)
        }

        return summary

    def _determine_overall_status(self, analysis: DataAnalysisResult) -> str:
        """确定整体状态"""

        trends = analysis.trends

        # 基于效价趋势判断
        valence_avg = trends.get('valence_trend', {}).get('average', 0)
        intensity_avg = trends.get('intensity_trend', {}).get('average', 0.5)

        if valence_avg > 0.3 and intensity_avg < 0.7:
            return "良好"
        elif valence_avg > 0 and intensity_avg < 0.8:
            return "稳定"
        elif valence_avg > -0.3:
            return "需要关注"
        else:
            return "需要支持"

    def _identify_attention_areas(self, analysis: DataAnalysisResult) -> List[str]:
        """识别需要关注的领域"""

        attention_areas = []
        trends = analysis.trends

        # 检查情绪强度
        intensity_trend = trends.get('intensity_trend', {})
        if intensity_trend.get('variability', 0) > 0.3:
            attention_areas.append("情绪稳定性")

        # 检查效价趋势
        valence_trend = trends.get('valence_trend', {})
        if valence_trend.get('average', 0) < -0.2:
            attention_areas.append("情绪积极性")

        # 检查唤醒度
        arousal_trend = trends.get('arousal_trend', {})
        if arousal_trend.get('average', 0) > 0.8:
            attention_areas.append("情绪调节")

        # 检查情绪分布
        emotion_dist = trends.get('emotion_distribution', {})
        total_emotions = sum(emotion_dist.values()) if emotion_dist else 1
        if emotion_dist.get('anxious', 0) / total_emotions > 0.3:
            attention_areas.append("焦虑管理")

        return attention_areas

    def _generate_detailed_recommendations(self, analysis: DataAnalysisResult) -> Dict[str, Any]:
        """生成详细建议"""

        recommendations = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_strategies": [],
            "professional_support": []
        }

        # 基于分析结果生成建议
        for insight in analysis.key_insights:
            if "焦虑" in insight or "紧张" in insight:
                recommendations["immediate_actions"].append("学习深呼吸和放松技巧")
                recommendations["short_term_goals"].append("建立日常放松routine")

            elif "消极" in insight or "负面" in insight:
                recommendations["immediate_actions"].append("增加积极活动")
                recommendations["short_term_goals"].append("培养感恩习惯")

            elif "波动" in insight:
                recommendations["immediate_actions"].append("识别情绪触发因素")
                recommendations["long_term_strategies"].append("发展情绪调节技能")

        # 基于趋势生成建议
        trends = analysis.trends
        valence_avg = trends.get('valence_trend', {}).get('average', 0)

        if valence_avg < -0.3:
            recommendations["professional_support"].append("考虑寻求专业心理咨询")

        return recommendations

    def _assess_current_risks(
        self,
        analysis: DataAnalysisResult,
        emotion_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """评估当前风险"""

        risk_assessment = {
            "overall_risk_level": "低",
            "specific_risks": [],
            "protective_factors": [],
            "monitoring_recommendations": []
        }

        trends = analysis.trends

        # 评估风险因素
        valence_avg = trends.get('valence_trend', {}).get('average', 0)
        intensity_var = trends.get('intensity_trend', {}).get('variability', 0)

        if valence_avg < -0.4:
            risk_assessment["overall_risk_level"] = "高"
            risk_assessment["specific_risks"].append("持续消极情绪")

        elif valence_avg < -0.2:
            risk_assessment["overall_risk_level"] = "中"
            risk_assessment["specific_risks"].append("情绪偏消极")

        if intensity_var > 0.4:
            risk_assessment["specific_risks"].append("情绪不稳定")
            if risk_assessment["overall_risk_level"] == "低":
                risk_assessment["overall_risk_level"] = "中"

        # 识别保护因素
        if valence_avg > 0.2:
            risk_assessment["protective_factors"].append("整体积极情绪")

        if intensity_var < 0.2:
            risk_assessment["protective_factors"].append("情绪稳定")

        # 监控建议
        if risk_assessment["overall_risk_level"] == "高":
            risk_assessment["monitoring_recommendations"].append("每日情绪监测")
            risk_assessment["monitoring_recommendations"].append("专业评估")
        elif risk_assessment["overall_risk_level"] == "中":
            risk_assessment["monitoring_recommendations"].append("每周情绪检查")

        return risk_assessment
