# 小雪宝 (LeukemiaPal) - 智能白血病AI关爱助手

[![GitHub license](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/blob/main/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/pulls)
[![GitHub stars](https://img.shields.io/github/stars/Handsome5201314/xiaoxuebao_AI_Project.svg)](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/stargazers)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![AI Powered](https://img.shields.io/badge/AI-Qwen3--8B-orange.svg)](https://cloud.siliconflow.cn/)

## 🎯 项目概述

**小雪宝 (LeukemiaPal)** 是一个基于先进AI技术的智能医疗助手平台，专注于为白血病患者、家属及医疗专业人员提供全方位的信息支持、心理健康干预和智能问答服务。

### 🌟 核心使命
- **🧠 AI驱动的智能问答**: 集成SiliconFlow Qwen3-8B模型，提供专业、温暖的医疗咨询
- **📚 专业知识库**: 构建涵盖白血病诊疗、心理健康、营养指导的权威知识体系
- **💝 儿童关爱特色**: 专注儿童白血病患者的心理健康干预和家庭支持
- **🔬 多模态分析**: 整合文本、语音、图像的情绪识别和心理评估
- **🌐 开源公益**: 完全免费开源，致力于用科技温暖每一个需要关爱的心灵

## 🚀 核心功能特性

### 🤖 AI智能问答系统
- **🧠 先进AI模型**: 集成SiliconFlow Qwen3-8B大语言模型
- **📖 知识库增强**: 基于专业医疗知识库的上下文增强回答
- **🎯 精准匹配**: 智能关键词匹配和相关性评分算法
- **💬 实时对话**: 毫秒级响应，支持连续对话和上下文理解
- **🔍 多维搜索**: 支持标题、内容、关键词的多维度知识检索

### � 专业知识库系统
- **🏥 疾病知识**: 白血病基础知识、症状表现、诊断要点
- **💊 治疗指导**: 化疗注意事项、感染预防、生活护理
- **🧘 心理健康**: 儿童心理支持、家长情绪管理、心理干预
- **🍎 营养指导**: 患儿营养管理、饮食安全、康复期指导
- **📊 智能分析**: 自动相关性评分、分类管理、实时搜索

### 💝 儿童心理健康干预平台
- **😊 多模态情绪识别**: 文本+语音+图像+生理数据融合分析
- **👤 个性化心理画像**: 基于大五人格模型的儿童适配版本
- **👨‍👩‍👧‍👦 家长协同支持**: 实时指导建议、教育资源推荐、危机干预
- **📈 数据可视化**: 情绪趋势分析、交互式图表、综合报告
- **🌐 社区支持网络**: 智能内容审核、个性化推荐、专家资源

### 🎨 现代化Web界面
- **� 响应式设计**: 基于Tailwind CSS的现代化界面
- **💬 聊天中心设计**: 突出AI问答功能的用户友好界面
- **🔍 集成搜索**: 无缝集成的知识库搜索功能
- **📱 移动优化**: 完美适配手机、平板等各种设备
- **✨ 动画效果**: 流畅的交互动画和视觉反馈

## �️ 技术架构

### 核心技术栈
- **🐍 后端框架**: FastAPI (高性能异步Python框架)
- **🧠 AI模型**: SiliconFlow Qwen3-8B (通义千问大语言模型)
- **💾 数据处理**: Pydantic v2, SQLAlchemy, httpx异步客户端
- **🎨 前端技术**: HTML5, Tailwind CSS, JavaScript ES6+
- **🔍 搜索引擎**: 自研多维度关键词匹配算法
- **📊 数据可视化**: Plotly交互式图表
- **🔒 安全加密**: Fernet对称加密, CORS跨域保护

### 系统架构图
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │────│   FastAPI Backend │────│  Knowledge Base │
│   (Tailwind)    │    │   (Python 3.8+)  │    │   (7 Categories)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Chat Interface│    │  SiliconFlow API │    │  Emotion Engine │
│   (Real-time)   │    │   (Qwen3-8B)     │    │  (Multi-modal)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 快速安装指南

### 系统要求
- **Python**: 3.8+ (推荐 3.9+)
- **内存**: 最低 4GB RAM (推荐 8GB+)
- **存储**: 至少 2GB 可用空间
- **网络**: 稳定的互联网连接 (用于AI API调用)

### 🚀 一键启动 (推荐)

```bash
# 克隆项目
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project/backend

# 安装依赖
pip install fastapi uvicorn pydantic sqlalchemy python-dotenv httpx structlog pydantic-settings

# 启动服务
python app_complete.py
```

### 📦 详细安装步骤

1. **环境准备**
```bash
# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

2. **安装核心依赖**
```bash
# 进入后端目录
cd backend

# 安装基础依赖
pip install -r requirements.txt

# 或手动安装核心包
pip install fastapi uvicorn pydantic sqlalchemy python-dotenv httpx structlog
```

3. **配置环境变量**
```bash
# 创建 .env 文件
cp .env.example .env

# 编辑配置 (可选)
# DATABASE_URL=sqlite:///./xiaoxuebao.db
# LOG_LEVEL=INFO
```

4. **启动应用**
```bash
# 方式1: 使用完整版启动脚本
python app_complete.py

# 方式2: 使用uvicorn直接启动
python -m uvicorn app_complete:app --host 0.0.0.0 --port 8000 --reload

# 方式3: 使用简化版 (用于测试)
python app_minimal.py
```

## 🎯 使用指南

### 🌐 Web界面访问

启动服务后，访问以下地址：

- **🏠 主页**: http://localhost:8000
- **📖 API文档**: http://localhost:8000/docs
- **📚 ReDoc文档**: http://localhost:8000/redoc
- **🧪 知识库测试**: http://localhost:8000/static/test_knowledge.html
- **� AI功能测试**: http://localhost:8000/static/test_ai.html

### 💬 AI问答使用

#### 对于患者和家属
1. **访问主页** - 点击"开始AI对话"进入聊天界面
2. **输入问题** - 例如：
   - "我的孩子确诊白血病后很焦虑，怎么办？"
   - "化疗期间需要注意什么？"
   - "如何帮助孩子建立治疗信心？"
3. **获取专业回答** - AI会基于知识库提供温暖、专业的指导
4. **使用快捷问题** - 点击预设问题快速开始对话

#### 知识库搜索功能
1. **点击"知识库搜索"** - 在聊天界面右上角
2. **输入关键词** - 如"白血病"、"化疗"、"营养"
3. **浏览搜索结果** - 查看相关度评分和详细内容
4. **一键提问** - 点击结果直接向AI提问

### 🔬 开发者使用

#### API接口调用
```python
import httpx
import asyncio

async def test_chat_api():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "message": "什么是白血病？",
                "context": "医疗咨询"
            }
        )
        result = response.json()
        print(f"AI回答: {result['answer']}")
        print(f"来源: {result['source']}")

# 运行测试
asyncio.run(test_chat_api())
```

#### 知识库搜索API
```python
async def test_knowledge_search():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/knowledge/search?q=化疗&limit=3"
        )
        result = response.json()
        for item in result['data']['results']:
            print(f"标题: {item['title']}")
            print(f"分类: {item['category']}")
            print(f"相关度: {item['relevance_score']}")
```

## 📊 API接口文档

### 🤖 核心API端点

| 端点 | 方法 | 描述 | 示例 |
|------|------|------|------|
| `/api/chat` | POST | AI智能问答 | 发送消息获取AI回复 |
| `/api/v1/knowledge/search` | GET | 知识库搜索 | 搜索相关医疗知识 |
| `/api/v1/knowledge/stats` | GET | 知识库统计 | 获取知识库概览信息 |
| `/api/v1/mental-health/emotion/analyze` | POST | 情绪分析 | 分析文本情绪状态 |
| `/api/v1/mental-health/parent/guidance` | POST | 家长指导 | 获取育儿建议 |

### 📝 API使用示例

#### 1. AI聊天接口
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "白血病的主要症状有哪些？",
    "context": "医疗咨询"
  }'
```

**响应示例:**
```json
{
  "answer": "白血病的主要症状包括：1. 发热：不明原因的持续发热...",
  "source": "小雪宝AI助手 (知识库增强)",
  "confidence": 0.95
}
```

#### 2. 知识库搜索接口
```bash
curl "http://localhost:8000/api/v1/knowledge/search?q=化疗&limit=3"
```

**响应示例:**
```json
{
  "success": true,
  "message": "找到 3 条相关信息",
  "data": {
    "query": "化疗",
    "total": 3,
    "search_time": 0.002,
    "results": [
      {
        "id": "kb_003",
        "title": "化疗期间的注意事项",
        "category": "治疗护理",
        "relevance_score": 3.0,
        "content": "化疗期间重要注意事项：感染预防、饮食管理..."
      }
    ]
  }
}
```

### 🔧 配置选项

#### 环境变量配置 (.env文件)
```bash
# 基础配置
APP_NAME=小雪宝AI助手
APP_VERSION=2.0.0
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置 (可选)
DATABASE_URL=sqlite:///./xiaoxuebao.db

# AI模型配置 (已内置SiliconFlow密钥)
SILICONFLOW_API_KEY=sk-hclwuosimfqpztfimjagookkkpbcqianfcihthgsvasynbrv
SILICONFLOW_MODEL=Qwen/Qwen3-8B

# 服务器配置
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

### 📚 知识库结构

项目内置专业医疗知识库，包含7个核心类别：

```
知识库分类:
├── 疾病知识 (3条)
│   ├── 白血病基础知识
│   ├── 症状表现诊断
│   └── 儿童白血病特点
├── 治疗护理 (2条)
│   ├── 化疗注意事项
│   └── 感染预防护理
├── 心理健康 (1条)
│   └── 儿童心理支持
├── 营养指导 (1条)
│   └── 患儿营养管理
├── 家长支持 (1条)
│   └── 家长情绪管理
└── 生活指导 (1条)
    └── 学习社交安排
```

#### 知识库特性
- **🎯 精准匹配**: 基于标题、关键词、内容的多维度搜索
- **📊 相关性评分**: 自动计算搜索结果相关度 (0-5分)
- **⚡ 高速检索**: 毫秒级搜索响应时间
- **🔄 实时更新**: 支持动态添加和更新知识条目

## 🎨 界面展示

### 🏠 主页面设计
- **💫 现代化设计**: 基于Tailwind CSS的渐变色彩和卡片布局
- **💬 聊天中心**: AI问答功能作为页面核心，突出显示
- **🔍 集成搜索**: 无缝集成的知识库搜索功能
- **📱 响应式布局**: 完美适配桌面、平板、手机等设备

### � AI聊天界面特性
- **实时对话**: 支持连续对话和上下文理解
- **思考指示**: 显示AI思考过程的动画效果
- **来源标识**: 清晰标识回答来源（知识库增强/AI模型）
- **快捷问题**: 预设常见问题，一键快速提问
- **消息历史**: 保存对话记录，支持清空功能

### 🔍 知识库搜索界面
- **智能搜索**: 支持关键词、分类、相关性搜索
- **结果展示**: 美观的卡片式搜索结果展示
- **一键使用**: 点击搜索结果直接向AI提问
- **实时反馈**: 显示搜索时间和结果数量

## 🤝 贡献指南

### 🎯 欢迎贡献的领域

| 领域 | 技能要求 | 贡献方式 |
|------|----------|----------|
| **🏥 医疗专业** | 医学背景 | 知识库内容审核、医学指导 |
| **🐍 后端开发** | Python, FastAPI | API开发、算法优化 |
| **🎨 前端开发** | HTML/CSS/JS | 界面优化、用户体验 |
| **🧠 AI算法** | 机器学习 | 情绪分析、模型优化 |
| **📝 内容运营** | 医学写作 | 知识库扩展、内容整理 |
| **🧪 测试质量** | 软件测试 | 功能测试、性能优化 |

### 📝 贡献流程

1. **🍴 Fork项目**
```bash
# Fork到你的GitHub账号
# 然后克隆到本地
git clone https://github.com/YOUR_USERNAME/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project
```

2. **🌿 创建分支**
```bash
# 创建功能分支
git checkout -b feature/your-feature-name
# 或修复分支
git checkout -b fix/your-fix-name
```

3. **💻 开发和测试**
```bash
# 进行开发
# 运行测试确保功能正常
python -m pytest tests/
```

4. **📤 提交代码**
```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-feature-name
```

5. **🔄 创建Pull Request**
- 在GitHub上创建PR
- 详细描述你的更改
- 等待代码审查和合并

### 📋 代码规范

#### Python代码规范
```python
# 遵循PEP 8规范
# 使用类型提示
def analyze_emotion(text: str, age: int) -> Dict[str, Any]:
    """分析情绪的函数

    Args:
        text: 要分析的文本
        age: 用户年龄

    Returns:
        包含情绪分析结果的字典
    """
    pass

# 使用docstring文档
# 适当的错误处理
```

#### 前端代码规范
```javascript
// 使用ES6+语法
// 清晰的函数命名
async function sendMessage() {
    try {
        // 适当的错误处理
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: userInput})
        });

        if (!response.ok) {
            throw new Error('请求失败');
        }

        const data = await response.json();
        displayMessage(data.answer);
    } catch (error) {
        console.error('发送消息失败:', error);
        showErrorMessage('发送失败，请重试');
    }
}
```

## 📊 项目发展路线图

### ✅ 已完成功能 (v2.0.0)
- [x] **AI智能问答系统** - 集成SiliconFlow Qwen3-8B模型
- [x] **专业知识库** - 7个核心医疗知识分类，智能搜索
- [x] **现代化Web界面** - 响应式设计，聊天中心布局
- [x] **多模态情绪分析** - 文本、语音、图像情绪识别
- [x] **心理健康干预** - 儿童心理支持、家长指导
- [x] **API接口体系** - RESTful API，完整文档
- [x] **知识库搜索** - 实时搜索，相关性评分

### 🚧 开发中功能 (v2.1.0)
- [ ] **用户认证系统** - 安全登录、权限管理
- [ ] **数据持久化** - 数据库集成、用户数据存储
- [ ] **高级情绪分析** - 更精准的多模态融合算法
- [ ] **社区功能** - 用户交流、专家问答
- [ ] **移动端适配** - PWA支持、移动端优化

### 🔮 规划中功能 (v3.0.0+)
- [ ] **垂直领域模型** - 专门的白血病知识模型训练
- [ ] **智能硬件集成** - 可穿戴设备数据接入
- [ ] **多语言支持** - 国际化，支持英文等多语言
- [ ] **高级分析** - 预测性分析、个性化推荐
- [ ] **医疗机构集成** - 与医院系统对接

### 📈 技术演进计划

#### 短期目标 (3个月内)
1. **性能优化** - 响应时间优化到100ms以内
2. **知识库扩展** - 扩展到50+专业知识条目
3. **用户体验** - 完善交互设计，提升易用性
4. **测试覆盖** - 单元测试覆盖率达到80%+

#### 中期目标 (6个月内)
1. **AI模型优化** - 集成更多AI服务提供商
2. **数据分析** - 用户行为分析，使用统计
3. **安全加固** - 数据加密，隐私保护
4. **部署优化** - Docker容器化，云原生部署

#### 长期目标 (1年内)
1. **生态建设** - 开发者社区，插件系统
2. **商业化探索** - 企业版功能，付费服务
3. **学术合作** - 与医疗机构、研究院所合作
4. **国际化** - 面向全球用户，多地区部署

## � 故障排除

### 常见问题解决

#### 1. 启动失败
```bash
# 检查Python版本
python --version  # 需要3.8+

# 检查依赖安装
pip list | grep fastapi

# 重新安装依赖
pip install --upgrade fastapi uvicorn pydantic
```

#### 2. AI API调用失败
```bash
# 检查网络连接
curl -I https://cloud.siliconflow.cn

# 检查API密钥配置
# 确保.env文件中的API密钥正确
```

#### 3. 知识库搜索无结果
- 检查搜索关键词是否正确
- 尝试使用更通用的关键词
- 查看知识库统计信息确认数据加载

#### 4. 前端页面无法访问
```bash
# 检查服务器状态
curl http://localhost:8000/health

# 检查端口占用
netstat -an | grep 8000
```

### �📞 获取帮助

#### 项目负责人
- **姓名**: 李帅帅
- **微信**: 13546777571
- **邮箱**: 13546777571@163.com
- **GitHub**: [@Handsome5201314](https://github.com/Handsome5201314)

#### 社区支持
- **🐛 Bug报告**: [GitHub Issues](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/issues)
- **💡 功能建议**: [GitHub Discussions](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/discussions)
- **📖 文档问题**: [Wiki页面](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/wiki)
- **💬 技术交流**: 微信群 (联系项目负责人获取邀请)

## ⚠️ 重要声明

### 🏥 医疗免责声明
**本项目提供的所有信息仅供参考和教育目的，不能替代专业医生的诊断和治疗建议。**

- ❌ 不能用于自我诊断或治疗决策
- ❌ 不能替代专业医疗咨询
- ❌ 不承担任何医疗责任
- ✅ 如有医疗问题，请务必咨询合格的医疗专业人员

### 🔒 隐私保护承诺
- **零主动收集**: 不主动收集用户个人信息
- **数据匿名化**: 所有数据都进行匿名化处理
- **本地优先**: 优先使用本地存储和处理
- **透明开源**: 所有代码开源，接受社区监督

### 📊 数据使用说明
- 聊天记录仅在浏览器本地存储
- 不会上传用户个人信息到服务器
- AI API调用不包含用户身份信息
- 知识库搜索记录不会被永久保存

## 📄 开源许可

本项目采用 **Apache License 2.0** 许可证，这意味着：

- ✅ **商业使用**: 可以用于商业目的
- ✅ **修改**: 可以修改源代码
- ✅ **分发**: 可以分发原始或修改版本
- ✅ **专利使用**: 授予专利使用权
- ⚠️ **责任**: 需要包含许可证和版权声明

详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢与鸣谢

### 核心贡献者
- **李帅帅** - 项目发起人、架构设计
- **AI技术团队** - 算法开发、模型集成
- **医疗专家顾问** - 知识库审核、专业指导
- **开源社区** - 代码贡献、测试反馈

### 技术支持
- **SiliconFlow** - 提供Qwen3-8B模型API服务
- **FastAPI社区** - 优秀的Python Web框架
- **Tailwind CSS** - 现代化的CSS框架
- **GitHub** - 代码托管和协作平台

### 特别感谢
- **"小胰宝"社区** - 项目灵感来源和技术指导
- **白血病患者家庭** - 需求反馈和使用建议
- **医疗机构** - 专业知识和临床指导
- **开源贡献者** - 无私的代码贡献和改进建议

---

## 🌟 项目愿景

> **"让科技温暖生命，用AI点亮希望"**

我们相信，通过先进的AI技术和温暖的人文关怀，能够为白血病患者及其家庭带来更多的希望和支持。每一行代码，每一个功能，都承载着我们对生命的敬畏和对未来的憧憬。

### 🎯 我们的使命
- 🏥 **医疗普惠**: 让专业医疗知识触手可及
- 💝 **关爱儿童**: 为患儿提供专业的心理健康支持
- 🤝 **家庭支持**: 帮助家长更好地陪伴和照护
- 🌐 **开源共享**: 让技术成果惠及更多人群

### 📈 项目数据 (截至2025年9月)
- **🔧 代码提交**: 200+ commits
- **📚 知识条目**: 7个核心分类
- **🤖 AI模型**: 集成Qwen3-8B
- **⭐ GitHub Stars**: 持续增长中
- **👥 贡献者**: 欢迎更多人加入

---

**📅 最后更新**: 2025年9月28日
**📦 当前版本**: v2.0.0
**🔄 更新频率**: 持续迭代，每周更新

*感谢您对小雪宝AI助手项目的关注和支持！* 🙏✨