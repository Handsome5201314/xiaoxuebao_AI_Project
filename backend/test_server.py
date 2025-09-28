#!/usr/bin/env python3
"""
简单的测试服务器 - 用于诊断启动问题
"""

import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

print(f"Python版本: {sys.version}")
print(f"当前工作目录: {sys.path[0]}")

try:
    app = FastAPI(title="测试服务器", version="1.0.0")
    
    @app.get("/")
    async def root():
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>小雪宝AI助手 - 测试页面</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>🎉 服务器运行正常！</h1>
            <p>这是一个测试页面，用于验证服务器是否正常启动。</p>
            <ul>
                <li><a href="/docs">API文档</a></li>
                <li><a href="/health">健康检查</a></li>
            </ul>
        </body>
        </html>
        """)
    
    @app.get("/health")
    async def health():
        return {"status": "ok", "message": "服务器运行正常"}
    
    @app.get("/test")
    async def test():
        return {"message": "测试成功", "python_version": sys.version}
    
    print("✅ FastAPI应用创建成功")
    
    if __name__ == "__main__":
        print("🚀 启动测试服务器...")
        print("📍 访问地址: http://localhost:8002")
        uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")
        
except Exception as e:
    print(f"❌ 启动失败: {e}")
    traceback.print_exc()
