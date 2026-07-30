# 使用官方 Python 运行时作为父镜像
FROM python:3.11-slim

# 安装 uv（更快的依赖安装）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    UV_LINK_MODE=copy

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖清单，利用 Docker 层缓存
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖（生产环境，不含 dev 组）
RUN uv sync --frozen --no-dev

# 复制项目文件
COPY . .

# 使用 uv 创建的虚拟环境
ENV PATH="/app/.venv/bin:$PATH"

# 暴露端口
EXPOSE 8100

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8100/api/health/health')"

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
