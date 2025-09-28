#!/usr/bin/env python3
"""
小雪宝AI助手 - 最小化API服务器
用于快速启动和测试
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="小雪宝AI助手 API",
    description="白血病儿童关爱AI助手 - 最小化版本",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None

class Article(ArticleBase):
    id: int
    author: str = "系统"
    created_at: str

# 模拟数据
articles = [
    {
        "id": 1,
        "title": "儿童急性淋巴细胞白血病 (ALL) 基础知识",
        "content": "急性淋巴细胞白血病（ALL）是儿童最常见的白血病类型，约占儿童白血病的75%。本文将介绍ALL的基本知识、症状、诊断和治疗方法。",
        "summary": "ALL是儿童最常见的白血病，治疗效果良好，5年生存率超过85%。",
        "author": "医学专家",
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": 2,
        "title": "白血病儿童的营养指导",
        "content": "白血病治疗期间，良好的营养支持对患儿的康复至关重要。本文提供详细的营养指导建议。",
        "summary": "合理的营养搭配有助于增强免疫力，减少感染风险。",
        "author": "营养师",
        "created_at": "2024-01-20T14:30:00Z"
    },
    {
        "id": 3,
        "title": "家庭心理支持指南",
        "content": "白血病诊断对整个家庭都是巨大的挑战。本指南帮助家长了解如何提供心理支持。",
        "summary": "积极的心理支持有助于患儿更好地配合治疗。",
        "author": "心理专家",
        "created_at": "2024-01-25T16:45:00Z"
    }
]

# API路由
@app.get("/", response_model=HealthResponse)
async def root():
    """根路径 - 服务状态"""
    return HealthResponse(
        status="running",
        message="欢迎使用小雪宝AI助手！🎈 专为白血病儿童和家庭提供支持",
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        message="服务运行正常",
        version="1.0.0"
    )

@app.get("/api/v1/articles", response_model=List[Article])
async def get_articles():
    """获取文章列表"""
    return articles

@app.get("/api/v1/articles/{article_id}", response_model=Article)
async def get_article(article_id: int):
    """获取单篇文章"""
    for article in articles:
        if article["id"] == article_id:
            return article
    raise HTTPException(status_code=404, detail="文章未找到")

@app.get("/api/v1/knowledge/search")
async def search_knowledge(q: str):
    """知识搜索"""
    results = []
    for article in articles:
        if q.lower() in article["title"].lower() or q.lower() in article["content"].lower():
            results.append(article)
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

@app.get("/api/v1/support/emergency")
async def emergency_contacts():
    """紧急联系方式"""
    return {
        "emergency_contacts": [
            {
                "name": "儿童医院急诊科",
                "phone": "120",
                "address": "当地儿童医院"
            },
            {
                "name": "白血病专科门诊",
                "phone": "400-xxxx-xxxx",
                "hours": "周一至周五 8:00-17:00"
            }
        ],
        "support_groups": [
            {
                "name": "小雪宝家长互助群",
                "type": "微信群",
                "description": "为白血病儿童家长提供经验分享和心理支持"
            }
        ]
    }

@app.get("/api/v1/demo/login")
async def demo_login():
    """演示登录"""
    return {
        "message": "演示账号登录成功",
        "user": {
            "id": 1,
            "username": "demo@example.com",
            "display_name": "演示用户",
            "role": "patient_family"
        },
        "token": "demo-token-123456",
        "expires_in": 3600
    }

if __name__ == "__main__":
    print("🚀 启动小雪宝AI助手最小化服务器...")
    print("📍 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔧 管理界面: http://localhost:8000/redoc")
    print("=" * 50)
    
    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
