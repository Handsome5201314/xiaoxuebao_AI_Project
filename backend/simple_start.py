#!/usr/bin/env python3
"""
简化版启动脚本
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# 创建FastAPI应用
app = FastAPI(
    title="小雪宝AI助手",
    description="智能白血病关爱平台",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """主页"""
    if os.path.exists("static/index_new.html"):
        return FileResponse("static/index_new.html")
    else:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>小雪宝AI助手</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; }
                .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 20px 0; }
                h1 { font-size: 2.5em; margin-bottom: 20px; }
                .status { color: #4CAF50; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌟 小雪宝AI助手</h1>
                <div class="card">
                    <h2>✅ 服务器运行正常</h2>
                    <p class="status">状态: 在线</p>
                    <p>智能白血病关爱平台已启动</p>
                </div>
                <div class="card">
                    <h3>🔗 快速链接</h3>
                    <p><a href="/docs" style="color: #FFD700;">📖 API文档</a></p>
                    <p><a href="/health" style="color: #FFD700;">🏥 健康检查</a></p>
                    <p><a href="/static/test_knowledge.html" style="color: #FFD700;">🧪 功能测试</a></p>
                </div>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "小雪宝AI助手运行正常",
        "version": "2.0.0",
        "services": {
            "api": "online",
            "knowledge_base": "available"
        }
    }

@app.get("/test")
async def test():
    """测试接口"""
    return {
        "message": "测试成功",
        "timestamp": "2025-09-28",
        "features": [
            "AI智能问答",
            "专业知识库",
            "心理健康支持"
        ]
    }

if __name__ == "__main__":
    print("🚀 启动小雪宝AI助手简化版...")
    print("📍 访问地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🏥 健康检查: http://localhost:8000/health")
    
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
