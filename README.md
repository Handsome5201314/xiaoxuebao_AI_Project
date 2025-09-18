# 小雪宝 (LeukemiaPal) - 白血病AI关爱助手

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/blob/main/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/pulls)
[![GitHub stars](https://img.shields.io/github/stars/Handsome5201314/xiaoxuebao_AI_Project.svg)](https://github.com/Handsome5201314/xiaoxuebao_AI_Project/stargazers)

## 🎯 项目概述

**小雪宝 (LeukemiaPal)** 是一个社区驱动、医生主导的公益AI项目，旨在为白血病患者、家属及临床医生提供智能、可靠、富有同理心的信息支持与自我管理平台。

### 🌟 核心价值
- **消除信息鸿沟**: 提供权威、个性化的白血病相关知识问答
- **儿童白血病关爱**: 特别关注儿童患者，提供适龄的科普和心理支持
- **医生辅助工具**: 为临床医生提供高效的文献查询与知识检索工具
- **公益性质**: 完全免费开源，致力于服务白血病患者群体

## 🚀 主要功能

### 🤖 智能问答系统
- 基于权威指南（NCCN, CSCO）的精准医疗知识问答
- 支持多种白血病亚型（ALL, AML, CLL, CML等）
- 回答内容可溯源至具体指南和文献

### 👶 儿童关爱模块
- 绘本风格和动画形式的儿童科普内容
- 家长心理支持和护理指导
- 患儿情绪管理和康复辅助工具

### 🏥 医生专业工具
- 精细化医疗知识检索
- 最新研究文献查询功能
- 诊疗指南快速参考

### 📊 个性化管理
- 匿名用户画像系统（基于治疗阶段、疾病类型等标签）
- 个性化内容推荐和健康提醒
- 严格的隐私保护设计

## 📋 安装指南

### 环境要求
- Python 3.8+
- Node.js 16+ (前端)
- Docker (可选，用于容器化部署)

### 快速开始

1. **克隆仓库**
```bash
git clone https://github.com/Handsome5201314/xiaoxuebao_AI_Project.git
cd xiaoxuebao_AI_Project
```

2. **安装依赖**
```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend && npm install
```

3. **启动开发服务器**
```bash
# 启动后端API
python app/main.py

# 启动前端开发服务器
cd frontend && npm run dev
```

## 🛠️ 使用说明

### 对于患者和家属
1. 访问项目网站或打开应用
2. 在问答界面输入您的问题（如："化疗后恶心怎么办？"）
3. 获取基于权威指南的个性化回答
4. 浏览儿童专属内容或心理支持资源

### 对于临床医生
1. 使用专业查询模式
2. 输入具体的医学问题（如："FLT3-ITD突变AML的二线治疗方案"）
3. 获取指南推荐和文献参考
4. 使用文献检索功能查找最新研究

### 对于开发者
1. 参考项目文档了解架构设计
2. 参与知识库建设和维护
3. 贡献代码或提出改进建议

## ⚙️ 配置选项

### 环境变量配置
```bash
# 数据库配置
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url

# AI模型配置
LLM_API_KEY=your_llm_api_key
EMBEDDING_MODEL=text-embedding-ada-002

# 知识库配置
KNOWLEDGE_BASE_PATH=./knowledge_base
```

### 知识库管理
项目使用模块化的知识库结构：
```
knowledge_base/
├── guidelines/          # 诊疗指南
├── medications/         # 药品知识
├── terminology/        # 医学术语
├── pediatric/          # 儿童专属内容
└── literature/         # 研究文献
```

## 🤝 贡献指南

我们热烈欢迎各种形式的贡献！以下是参与方式：

### 🎯 急需贡献领域
1. **医疗专家**: 知识库审核和医学指导
2. **前端开发**: Vue.js/React 界面开发
3. **后端开发**: Python RAG架构优化
4. **知识库运营**: 内容整理和结构化

### 📝 贡献流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 📋 代码规范
- 遵循PEP 8 (Python)和ESLint (JavaScript)规范
- 编写清晰的注释和文档
- 添加适当的测试用例

## 📊 项目阶段规划

### 阶段一: MVP验证 (2025.09-2025.10)
- [ ] 核心团队组建和知识库初建
- [ ] 低代码平台Demo开发
- [ ] 社区招募和宣传

### 阶段二: 开源化 (2025.11-2026.01)
- [ ] 迁移至Python RAG技术栈
- [ ] 上线个性化管理功能
- [ ] 发布V1.0正式版

### 阶段三: 智能化演进 (2026.02+)
- [ ] 垂直模型训练
- [ ] 智能硬件集成
- [ ] 高级AI功能开发

## 📞 联系我们

### 项目负责人
- **姓名**: 李帅帅
- **微信**: [您的微信号]
- **邮箱**: [您的邮箱地址]

### 加入社区
- **微信群**: [群二维码或群号]
- **GitHub Discussions**: [项目讨论区]
- **在线报名表**: [报名链接]

## ⚠️ 重要声明

**医疗免责声明**: 本项目提供的所有信息仅供参考和教育目的，不能替代专业医生的诊断和治疗建议。如有医疗问题，请务必咨询合格的医疗专业人员。

**隐私保护**: 我们严格遵守"零主动数据收集"原则，所有用户数据都进行匿名化处理。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为这个项目做出贡献的医疗专家、开发者和志愿者！特别感谢"小胰宝"社区的技术支持和指导。

---

*让科技温暖生命，用AI点亮希望* ✨

*最后更新: 2025年9月19日*