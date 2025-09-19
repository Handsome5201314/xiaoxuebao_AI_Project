#!/bin/bash

# 启动脚本
echo "启动小雪宝知识库服务..."

# 等待Elasticsearch就绪
echo "等待Elasticsearch连接..."
python -c "
import time
import requests
import os

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        response = requests.get(f'http://{os.getenv(\"ELASTICSEARCH_HOST\", \"elasticsearch\")}:{os.getenv(\"ELASTICSEARCH_PORT\", \"9200\")}/_cluster/health', timeout=5)
        if response.status_code == 200:
            print('Elasticsearch连接成功')
            break
    except Exception as e:
        retry_count += 1
        print(f'Elasticsearch连接失败，重试 {retry_count}/{max_retries}: {e}')
        time.sleep(2)

if retry_count >= max_retries:
    print('Elasticsearch连接超时，继续启动...')
"

# 启动应用
echo "启动FastAPI应用..."
exec uvicorn main:app --host 0.0.0.0 --port 8001 --workers 2
