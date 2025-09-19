#!/bin/bash

# 启动脚本
echo "启动小雪宝API网关..."

# 等待数据库就绪
echo "等待数据库连接..."
python -c "
import time
import psycopg2
import os

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'xiaoxuebao'),
            user=os.getenv('POSTGRES_USER', 'xiaoxuebao'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )
        conn.close()
        print('数据库连接成功')
        break
    except Exception as e:
        retry_count += 1
        print(f'数据库连接失败，重试 {retry_count}/{max_retries}: {e}')
        time.sleep(2)

if retry_count >= max_retries:
    print('数据库连接超时，退出')
    exit(1)
"

# 启动应用
echo "启动FastAPI应用..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
