"""
小雪宝知识库服务
负责知识库管理、RAG问答、文档处理等功能
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import structlog
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime

# 配置日志
logger = structlog.get_logger()

# 知识库配置
KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "/app/knowledge_base")
CHUNK_SIZE = int(os.getenv("KNOWLEDGE_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("KNOWLEDGE_CHUNK_OVERLAP", "200"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("知识库服务启动中...")
    
    # 确保知识库目录存在
    os.makedirs(KNOWLEDGE_BASE_PATH, exist_ok=True)
    
    # 初始化知识库
    await initialize_knowledge_base()
    
    yield
    
    logger.info("知识库服务关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="小雪宝知识库服务",
    description="白血病知识库管理和RAG问答服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 知识库存储
knowledge_base = {}

async def initialize_knowledge_base():
    """初始化知识库"""
    logger.info("初始化知识库...")
    
    # 创建基础知识库结构
    base_structure = {
        "guidelines": {
            "name": "诊疗指南",
            "description": "NCCN、CSCO等权威诊疗指南",
            "documents": []
        },
        "medications": {
            "name": "药品知识",
            "description": "白血病相关药物信息",
            "documents": []
        },
        "terminology": {
            "name": "医学术语",
            "description": "白血病相关医学术语解释",
            "documents": []
        },
        "pediatric": {
            "name": "儿童关爱",
            "description": "儿童白血病特殊内容",
            "documents": []
        },
        "psychology": {
            "name": "心理支持",
            "description": "患者及家属心理支持内容",
            "documents": []
        }
    }
    
    # 保存知识库结构
    knowledge_base.update(base_structure)
    
    # 加载现有文档
    await load_existing_documents()
    
    logger.info("知识库初始化完成")

async def load_existing_documents():
    """加载现有文档"""
    for category, info in knowledge_base.items():
        category_path = os.path.join(KNOWLEDGE_BASE_PATH, category)
        if os.path.exists(category_path):
            for filename in os.listdir(category_path):
                if filename.endswith(('.md', '.txt', '.pdf')):
                    doc_path = os.path.join(category_path, filename)
                    await add_document_to_knowledge_base(category, filename, doc_path)

async def add_document_to_knowledge_base(category: str, filename: str, file_path: str):
    """添加文档到知识库"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        document = {
            "id": f"{category}_{filename}",
            "filename": filename,
            "content": content,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        knowledge_base[category]["documents"].append(document)
        logger.info(f"加载文档: {filename}")
        
    except Exception as e:
        logger.error(f"加载文档失败: {filename}, 错误: {e}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "knowledge-service",
        "version": "1.0.0",
        "knowledge_base_categories": len(knowledge_base)
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "小雪宝知识库服务",
        "version": "1.0.0",
        "categories": list(knowledge_base.keys())
    }

@app.get("/categories")
async def get_categories():
    """获取知识库分类"""
    return {
        "categories": [
            {
                "id": category_id,
                "name": info["name"],
                "description": info["description"],
                "document_count": len(info["documents"])
            }
            for category_id, info in knowledge_base.items()
        ]
    }

@app.get("/categories/{category_id}/documents")
async def get_documents(category_id: str):
    """获取指定分类的文档列表"""
    if category_id not in knowledge_base:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    return {
        "category": category_id,
        "documents": knowledge_base[category_id]["documents"]
    }

@app.get("/categories/{category_id}/documents/{document_id}")
async def get_document(category_id: str, document_id: str):
    """获取指定文档内容"""
    if category_id not in knowledge_base:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    documents = knowledge_base[category_id]["documents"]
    document = next((doc for doc in documents if doc["id"] == document_id), None)
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return document

@app.post("/categories/{category_id}/documents")
async def upload_document(
    category_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = None
):
    """上传文档到指定分类"""
    if category_id not in knowledge_base:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查文件类型
    allowed_extensions = ['.md', '.txt', '.pdf']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    try:
        # 读取文件内容
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 创建文档对象
        document_id = f"{category_id}_{file.filename}"
        document = {
            "id": document_id,
            "filename": file.filename,
            "title": title or file.filename,
            "content": content_str,
            "category": category_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 添加到知识库
        knowledge_base[category_id]["documents"].append(document)
        
        # 保存到文件系统
        category_path = os.path.join(KNOWLEDGE_BASE_PATH, category_id)
        os.makedirs(category_path, exist_ok=True)
        
        file_path = os.path.join(category_path, file.filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_str)
        
        logger.info(f"文档上传成功: {file.filename}")
        
        return {
            "message": "文档上传成功",
            "document_id": document_id,
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"文档上传失败: {e}")
        raise HTTPException(status_code=500, detail="文档上传失败")

@app.post("/search")
async def search_knowledge(
    query: str,
    category: Optional[str] = None,
    limit: int = 10
):
    """搜索知识库"""
    results = []
    
    # 简单的文本搜索实现
    # 在实际应用中，这里应该使用向量搜索或Elasticsearch
    for cat_id, cat_info in knowledge_base.items():
        if category and cat_id != category:
            continue
            
        for doc in cat_info["documents"]:
            if query.lower() in doc["content"].lower():
                results.append({
                    "document_id": doc["id"],
                    "category": cat_id,
                    "title": doc.get("title", doc["filename"]),
                    "content_preview": doc["content"][:200] + "...",
                    "relevance_score": 0.8  # 简单的相关性评分
                })
    
    # 按相关性排序
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "query": query,
        "results": results[:limit],
        "total": len(results)
    }

@app.post("/ask")
async def ask_question(question: str, context: Optional[str] = None):
    """RAG问答功能"""
    # 这里应该实现真正的RAG逻辑
    # 包括文档检索、向量搜索、LLM生成等
    
    # 简单的示例回答
    answer = f"关于您的问题「{question}」，我为您找到了相关信息。"
    
    # 搜索相关文档
    search_results = await search_knowledge(question, limit=3)
    
    return {
        "question": question,
        "answer": answer,
        "sources": search_results["results"],
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/categories/{category_id}/documents/{document_id}")
async def delete_document(category_id: str, document_id: str):
    """删除文档"""
    if category_id not in knowledge_base:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    documents = knowledge_base[category_id]["documents"]
    document = next((doc for doc in documents if doc["id"] == document_id), None)
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 从知识库中移除
    knowledge_base[category_id]["documents"] = [
        doc for doc in documents if doc["id"] != document_id
    ]
    
    # 删除文件
    file_path = os.path.join(KNOWLEDGE_BASE_PATH, category_id, document["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    logger.info(f"文档删除成功: {document_id}")
    
    return {"message": "文档删除成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
