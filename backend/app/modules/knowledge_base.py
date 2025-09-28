"""
白血病知识库管理模块
提供专业的医疗知识检索和问答支持
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class KnowledgeItem:
    """知识库条目"""
    id: str
    title: str
    content: str
    category: str
    keywords: List[str]
    relevance_score: float = 0.0
    source: str = "小雪宝知识库"
    last_updated: datetime = None


@dataclass
class KnowledgeSearchResult:
    """知识库搜索结果"""
    query: str
    total_results: int
    items: List[KnowledgeItem]
    search_time: float
    timestamp: datetime


class WhiteBloodKnowledgeBase:
    """白血病专业知识库"""
    
    def __init__(self):
        self.knowledge_data = self._initialize_knowledge_base()
        self.api_url = "https://cloud.siliconflow.cn/api/v1/chat/completions"
        self.api_key = "sk-hclwuosimfqpztfimjagookkkpbcqianfcihthgsvasynbrv"
        self.model = "Qwen/Qwen3-8B"
    
    def _initialize_knowledge_base(self) -> Dict[str, KnowledgeItem]:
        """初始化知识库数据"""
        
        knowledge_items = [
            # 疾病基础知识
            KnowledgeItem(
                id="kb_001",
                title="什么是白血病",
                content="""白血病是一种血液系统的恶性肿瘤，主要特征是骨髓中异常白血病细胞的克隆性增殖。

主要类型：
1. 急性淋巴细胞白血病(ALL) - 儿童最常见
2. 急性髓系白血病(AML) 
3. 慢性淋巴细胞白血病(CLL)
4. 慢性髓系白血病(CML)

儿童白血病特点：
- 80%为急性淋巴细胞白血病
- 发病年龄多在2-10岁
- 治愈率较成人高，可达80-90%
- 早期诊断和规范治疗是关键""",
                category="疾病知识",
                keywords=["白血病", "血液肿瘤", "儿童白血病", "ALL", "AML", "诊断"]
            ),
            
            KnowledgeItem(
                id="kb_002", 
                title="白血病的症状表现",
                content="""儿童白血病常见症状：

早期症状：
- 发热：不明原因的持续发热
- 贫血：面色苍白、乏力、气促
- 出血：皮肤瘀点瘀斑、鼻出血、牙龈出血
- 淋巴结肿大：颈部、腋下、腹股沟

进展期症状：
- 肝脾肿大
- 骨关节疼痛
- 感染反复发作
- 体重下降

注意事项：
- 出现上述症状应及时就医
- 早期症状可能不典型
- 需要专业医生诊断
- 不要自行判断病情""",
                category="症状诊断",
                keywords=["症状", "发热", "贫血", "出血", "淋巴结", "诊断"]
            ),
            
            KnowledgeItem(
                id="kb_003",
                title="化疗期间的注意事项",
                content="""化疗期间重要注意事项：

感染预防：
- 避免到人群密集场所
- 勤洗手，戴口罩
- 保持居住环境清洁
- 监测体温变化

饮食管理：
- 高蛋白、高维生素饮食
- 避免生冷、未煮熟食物
- 多饮水，促进药物代谢
- 少食多餐，减轻胃肠反应

生活护理：
- 充足休息，避免过度劳累
- 保持口腔清洁
- 皮肤护理，预防破损
- 定期复查血常规

心理支持：
- 保持积极乐观心态
- 家人陪伴和鼓励
- 适当的娱乐活动
- 必要时寻求心理咨询""",
                category="治疗护理",
                keywords=["化疗", "护理", "感染预防", "饮食", "注意事项"]
            ),
            
            KnowledgeItem(
                id="kb_004",
                title="儿童白血病的心理支持",
                content="""儿童白血病心理支持指南：

儿童心理特点：
- 对疾病理解有限
- 容易产生恐惧和焦虑
- 需要安全感和陪伴
- 表达方式可能不直接

家长支持策略：
- 用适合年龄的语言解释病情
- 保持日常生活的规律性
- 鼓励表达情感和担忧
- 提供持续的爱和支持

心理干预方法：
- 游戏治疗和艺术治疗
- 音乐治疗和故事治疗
- 同伴支持和病友交流
- 专业心理咨询

注意事项：
- 不要隐瞒病情，但要适度
- 关注情绪变化
- 维护孩子的自尊心
- 寻求专业心理帮助""",
                category="心理健康",
                keywords=["心理支持", "儿童心理", "焦虑", "恐惧", "家长指导"]
            ),
            
            KnowledgeItem(
                id="kb_005",
                title="白血病患儿的营养指导",
                content="""白血病患儿营养管理：

营养原则：
- 高蛋白：促进组织修复
- 高维生素：增强免疫力
- 适量脂肪：提供能量
- 充足水分：促进代谢

推荐食物：
- 优质蛋白：瘦肉、鱼类、蛋类、豆制品
- 新鲜蔬果：富含维生素和矿物质
- 全谷物：提供B族维生素
- 奶制品：补充钙质和蛋白质

避免食物：
- 生冷食物：生鱼片、生菜等
- 未充分加热的食物
- 过期变质食品
- 刺激性食物

特殊情况：
- 恶心呕吐时：少量多餐，清淡饮食
- 口腔溃疡时：软食、温凉食物
- 腹泻时：补充电解质
- 食欲不振时：增加食物色香味""",
                category="营养指导",
                keywords=["营养", "饮食", "蛋白质", "维生素", "食物安全"]
            ),
            
            KnowledgeItem(
                id="kb_006",
                title="家长情绪管理和支持",
                content="""家长情绪管理指南：

常见情绪反应：
- 震惊和否认
- 愤怒和自责
- 焦虑和恐惧
- 抑郁和绝望

应对策略：
- 接受和表达情绪
- 寻求专业帮助
- 建立支持网络
- 学习疾病知识

自我照顾：
- 保证充足睡眠
- 适当运动和放松
- 维持社交关系
- 寻找意义和希望

支持资源：
- 医疗团队的专业指导
- 病友家庭的经验分享
- 心理咨询师的专业帮助
- 社会组织的支持服务

注意事项：
- 家长的情绪会影响孩子
- 不要独自承担所有压力
- 及时寻求帮助
- 保持希望和信心""",
                category="家长支持",
                keywords=["家长", "情绪管理", "焦虑", "支持", "自我照顾"]
            ),
            
            KnowledgeItem(
                id="kb_007",
                title="治疗期间的学习和社交",
                content="""治疗期间学习社交指导：

学习安排：
- 根据身体状况调整学习强度
- 利用网络教育资源
- 与学校保持沟通
- 制定个性化学习计划

社交维护：
- 保持与同学朋友的联系
- 参加适合的社交活动
- 避免过度隔离
- 建立新的友谊

注意事项：
- 避免人群密集场所
- 注意个人防护
- 选择合适的活动时间
- 监测身体状况

心理建议：
- 不要因病情而自卑
- 保持正常的社交需求
- 培养新的兴趣爱好
- 建立积极的生活态度""",
                category="生活指导",
                keywords=["学习", "社交", "教育", "友谊", "生活质量"]
            )
        ]
        
        # 转换为字典格式
        return {item.id: item for item in knowledge_items}
    
    async def search_knowledge(self, query: str, limit: int = 5, category: str = None, min_score: float = 0.0) -> KnowledgeSearchResult:
        """增强版知识库搜索

        Args:
            query: 搜索查询词
            limit: 返回结果数量限制
            category: 指定搜索分类
            min_score: 最低相关性分数阈值
        """

        start_time = datetime.utcnow()
        query_lower = query.lower().strip()
        results = []

        # 预处理查询词
        query_words = [word for word in query_lower.split() if len(word) > 1]

        # 遍历知识库进行匹配
        for item in self.knowledge_data.values():
            # 分类过滤
            if category and item.category != category:
                continue

            score = 0.0

            # 1. 精确标题匹配（权重最高）
            if query_lower == item.title.lower():
                score += 5.0
            elif query_lower in item.title.lower():
                score += 3.0

            # 2. 关键词匹配（高权重）
            for keyword in item.keywords:
                keyword_lower = keyword.lower()
                if query_lower == keyword_lower:
                    score += 4.0  # 精确匹配
                elif keyword_lower in query_lower or query_lower in keyword_lower:
                    score += 2.5
                # 部分匹配
                for word in query_words:
                    if word in keyword_lower:
                        score += 1.5

            # 3. 内容匹配（中等权重）
            content_lower = item.content.lower()
            if query_lower in content_lower:
                # 计算匹配次数，增加权重
                match_count = content_lower.count(query_lower)
                score += min(match_count * 1.0, 3.0)  # 最多3分

            # 4. 分词匹配（低权重）
            for word in query_words:
                if word in item.title.lower():
                    score += 0.8
                if word in content_lower:
                    score += 0.3
                # 关键词部分匹配
                for keyword in item.keywords:
                    if word in keyword.lower():
                        score += 0.6

            # 5. 语义相关性加分
            semantic_bonus = self._calculate_semantic_bonus(query_lower, item)
            score += semantic_bonus

            # 6. 分类相关性加分
            if category and item.category == category:
                score += 0.5

            # 应用最低分数阈值
            if score >= min_score:
                item.relevance_score = round(score, 2)
                results.append(item)

        # 按相关性排序
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        results = results[:limit]

        search_time = (datetime.utcnow() - start_time).total_seconds()

        return KnowledgeSearchResult(
            query=query,
            total_results=len(results),
            items=results,
            search_time=search_time,
            timestamp=datetime.utcnow()
        )

    def _calculate_semantic_bonus(self, query: str, item: KnowledgeItem) -> float:
        """计算语义相关性加分"""

        # 医疗相关词汇映射
        medical_synonyms = {
            "白血病": ["血癌", "血液肿瘤", "造血系统肿瘤"],
            "化疗": ["化学治疗", "药物治疗", "抗癌治疗"],
            "心理": ["情绪", "精神", "心理健康", "心态"],
            "营养": ["饮食", "食物", "膳食", "营养素"],
            "症状": ["表现", "征象", "临床表现"],
            "治疗": ["医治", "诊疗", "康复", "疗法"],
            "家长": ["父母", "监护人", "家属"],
            "儿童": ["孩子", "小孩", "患儿", "宝宝"]
        }

        bonus = 0.0
        item_text = (item.title + " " + item.content + " " + " ".join(item.keywords)).lower()

        for main_word, synonyms in medical_synonyms.items():
            if main_word in query:
                for synonym in synonyms:
                    if synonym in item_text:
                        bonus += 0.3
                        break
            elif any(synonym in query for synonym in synonyms):
                if main_word in item_text:
                    bonus += 0.3

        return min(bonus, 1.0)  # 最多1分语义加分

    async def search_by_category(self, category: str, limit: int = 10) -> KnowledgeSearchResult:
        """按分类搜索知识库"""

        start_time = datetime.utcnow()
        results = []

        for item in self.knowledge_data.values():
            if item.category == category:
                item.relevance_score = 1.0  # 分类匹配基础分
                results.append(item)

        # 按ID排序（保持一致性）
        results.sort(key=lambda x: x.id)
        results = results[:limit]

        search_time = (datetime.utcnow() - start_time).total_seconds()

        return KnowledgeSearchResult(
            query=f"分类:{category}",
            total_results=len(results),
            items=results,
            search_time=search_time,
            timestamp=datetime.utcnow()
        )

    async def get_all_categories(self) -> Dict[str, int]:
        """获取所有分类及其文档数量"""

        categories = {}
        for item in self.knowledge_data.values():
            if item.category not in categories:
                categories[item.category] = 0
            categories[item.category] += 1

        return categories

    async def get_popular_keywords(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取热门关键词"""

        keyword_count = {}
        for item in self.knowledge_data.values():
            for keyword in item.keywords:
                if keyword not in keyword_count:
                    keyword_count[keyword] = 0
                keyword_count[keyword] += 1

        # 按使用频率排序
        popular_keywords = sorted(
            keyword_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {
                "keyword": keyword,
                "count": count,
                "category": self._get_keyword_primary_category(keyword)
            }
            for keyword, count in popular_keywords
        ]

    def _get_keyword_primary_category(self, keyword: str) -> str:
        """获取关键词的主要分类"""

        category_count = {}
        for item in self.knowledge_data.values():
            if keyword in item.keywords:
                if item.category not in category_count:
                    category_count[item.category] = 0
                category_count[item.category] += 1

        if category_count:
            return max(category_count.items(), key=lambda x: x[1])[0]
        return "未分类"

    async def smart_search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """智能搜索 - 综合多种搜索策略"""

        start_time = datetime.utcnow()

        # 1. 常规搜索
        regular_results = await self.search_knowledge(query, limit)

        # 2. 如果结果不足，尝试语义扩展搜索
        if len(regular_results.items) < limit:
            expanded_query = self._expand_query(query)
            if expanded_query != query:
                expanded_results = await self.search_knowledge(expanded_query, limit - len(regular_results.items))
                # 合并结果，避免重复
                existing_ids = {item.id for item in regular_results.items}
                for item in expanded_results.items:
                    if item.id not in existing_ids:
                        regular_results.items.append(item)

        # 3. 生成搜索建议
        suggestions = self._generate_search_suggestions(query)

        # 4. 相关分类推荐
        related_categories = self._get_related_categories(query)

        search_time = (datetime.utcnow() - start_time).total_seconds()

        return {
            "query": query,
            "results": regular_results.items,
            "total_results": len(regular_results.items),
            "search_time": search_time,
            "suggestions": suggestions,
            "related_categories": related_categories,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _expand_query(self, query: str) -> str:
        """扩展查询词"""

        expansions = {
            "白血病": "白血病 血癌 血液肿瘤",
            "化疗": "化疗 化学治疗 药物治疗",
            "心理": "心理 情绪 精神 心态",
            "营养": "营养 饮食 食物 膳食",
            "症状": "症状 表现 征象",
            "治疗": "治疗 医治 诊疗 康复",
            "家长": "家长 父母 家属",
            "儿童": "儿童 孩子 患儿"
        }

        query_lower = query.lower()
        for key, expansion in expansions.items():
            if key in query_lower:
                return expansion

        return query

    def _generate_search_suggestions(self, query: str) -> List[str]:
        """生成搜索建议"""

        suggestions = []
        query_lower = query.lower()

        # 基于关键词的建议
        all_keywords = set()
        for item in self.knowledge_data.values():
            all_keywords.update(item.keywords)

        # 找到相关关键词
        related_keywords = []
        for keyword in all_keywords:
            if query_lower in keyword.lower() or keyword.lower() in query_lower:
                related_keywords.append(keyword)

        # 生成建议
        if "白血病" in query_lower:
            suggestions.extend(["白血病症状", "白血病治疗", "儿童白血病"])
        if "化疗" in query_lower:
            suggestions.extend(["化疗注意事项", "化疗副作用", "化疗期间饮食"])
        if "心理" in query_lower:
            suggestions.extend(["心理支持", "情绪管理", "家长心理"])
        if "营养" in query_lower:
            suggestions.extend(["营养指导", "饮食管理", "营养补充"])

        # 添加相关关键词建议
        suggestions.extend(related_keywords[:3])

        return list(set(suggestions))[:5]  # 去重并限制数量

    def _get_related_categories(self, query: str) -> List[Dict[str, Any]]:
        """获取相关分类"""

        category_scores = {}
        query_lower = query.lower()

        for item in self.knowledge_data.values():
            score = 0
            if query_lower in item.title.lower():
                score += 2
            if query_lower in item.content.lower():
                score += 1
            for keyword in item.keywords:
                if query_lower in keyword.lower():
                    score += 1

            if score > 0:
                if item.category not in category_scores:
                    category_scores[item.category] = 0
                category_scores[item.category] += score

        # 排序并返回前3个相关分类
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        return [
            {
                "category": category,
                "relevance_score": score,
                "item_count": sum(1 for item in self.knowledge_data.values() if item.category == category)
            }
            for category, score in sorted_categories
        ]
    
    async def get_ai_enhanced_answer(self, question: str, knowledge_context: str = "") -> str:
        """使用AI增强回答，结合知识库内容"""
        
        try:
            # 构建包含知识库信息的提示
            system_prompt = f"""你是小雪宝AI助手，专注于白血病知识解答和儿童心理健康支持。

知识库信息：
{knowledge_context}

请基于以上知识库信息回答用户问题。要求：
1. 优先使用知识库中的专业信息
2. 用温暖、通俗易懂的语言回答
3. 如果涉及医疗建议，提醒用户咨询专业医生
4. 关注儿童和家长的心理需求
5. 提供实用的建议和指导"""

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
                            {"role": "user", "content": question}
                        ],
                        "max_tokens": 1024,
                        "temperature": 0.7,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return ai_response
                    
        except Exception as e:
            logger.error(f"AI增强回答失败: {e}")
        
        return ""
    
    async def answer_question(self, question: str) -> Dict[str, Any]:
        """回答问题，结合知识库和AI"""
        
        # 搜索相关知识
        search_result = await self.search_knowledge(question, limit=3)
        
        # 构建知识库上下文
        knowledge_context = ""
        if search_result.items:
            knowledge_context = "\n\n".join([
                f"【{item.title}】\n{item.content}"
                for item in search_result.items
            ])
        
        # 获取AI增强回答
        ai_answer = await self.get_ai_enhanced_answer(question, knowledge_context)
        
        # 如果AI回答失败，使用知识库直接回答
        if not ai_answer and search_result.items:
            best_match = search_result.items[0]
            ai_answer = f"根据知识库信息：\n\n{best_match.content}\n\n如需更详细的信息，建议咨询专业医生。"
        
        # 构建最终回答
        final_answer = ai_answer or "抱歉，我暂时无法找到相关信息。建议您咨询专业医生获取准确的医疗建议。"
        
        return {
            "answer": final_answer,
            "source": "小雪宝AI助手 (知识库增强)",
            "confidence": 0.95 if ai_answer else 0.7,
            "knowledge_items": [
                {
                    "title": item.title,
                    "category": item.category,
                    "relevance_score": item.relevance_score
                }
                for item in search_result.items
            ],
            "search_time": search_result.search_time,
            "has_knowledge_base": len(search_result.items) > 0
        }


# 创建全局知识库实例
knowledge_base = WhiteBloodKnowledgeBase()
