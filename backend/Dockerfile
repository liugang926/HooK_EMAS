# Django 后端 Dockerfile
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements 并安装 Python 依赖
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制项目代码
COPY . .

# 创建静态文件目录
RUN mkdir -p /app/staticfiles /app/media && chmod -R 755 /app/staticfiles /app/media

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
