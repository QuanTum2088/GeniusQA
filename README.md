<div align="center">

# 🚀 GeniusQA 测试平台

<p align="center">
  <strong>AI驱动一体化测试管理平台</strong>
</p>

<p align="center">
  <a href="#主要特性">特性</a> •
  <a href="#技术栈">技术栈</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#部署指南">部署</a> •
  <a href="#功能说明">功能</a> •
  <a href="#常见问题">FAQ</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue-3.0+-brightgreen.svg" alt="Vue3">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

</div>

---

## 📖 项目简介

GeniusQA 是一个采用前后端分离架构的现代化测试管理平台，融合 **Python FastAPI** 后端框架和 **Vue3** 前端框架，提供一站式开箱即用的测试解决方案。

### 🎯 核心能力

- 🤖 **AI 智能生成** - 自动生成测试用例、接口测试脚本
- 📋 **需求管理** - 需求评审、拆分、自动生成用例
- 🔄 **多端测试** - 支持 API、UI、APP 自动化测试
- 🧠 **LLM 集成** - 支持多种大语言模型厂商配置
- 📊 **智能排版** - 测试报告智能生成与展示

---

## 🛠 技术栈

### 后端技术

| 技术 | 说明 |
|------|------|
| **FastAPI** | 高性能 Web 框架 |
| **Uvicorn** | ASGI 服务器 |
| **Pydantic 2.0** | 数据验证 |
| **Tortoise ORM** | 异步 ORM |
| **LangChain/LangGraph** | AI 编排框架 |

### 前端技术

| 技术 | 说明 |
|------|------|
| **Vue 3** | 渐进式框架 |
| **Vite** | 构建工具 |
| **TypeScript** | 类型安全 |
| **Element Plus** | UI 组件库 |

### AI 能力

- 🧠 **LLM 支持**: OpenAI、Azure OpenAI、Ollama 等
- 🔗 **MCP 协议**: FastMCP、MCP 工具集成
- 📚 **向量数据库**: 支持多种嵌入服务

### 数据库

- 🐬 **MySQL 8.0+**
- 🐘 **PostgreSQL 15+**
- 🔄 **一键切换**: 支持数据库类型动态切换

---

## ⚡ 快速开始

### 环境要求

```bash
Python 3.11+
MySQL 8.0+ / PostgreSQL 15+
Node.js 18+
Docker & Docker Compose (可选)
```

### 🐳 Docker 一键部署（推荐）

```bash
# Linux/Mac
./start-docker.sh

# Windows
start-docker.bat

# 或手动启动
docker-compose up -d
```

📘 详细说明请查看：[DOCKER.md](DOCKER.md)

### 💻 本地开发部署

#### 1️⃣ 后端部署

```bash
cd backend

# 一键部署（推荐新手）
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows
deploy.bat
```

**手动部署步骤：**

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接

# 初始化数据库
python -m aerich init -t app.configs.config.tortoise_orm_conf
python -m aerich init-db

# 启动服务
python main.py
```

#### 2️⃣ 前端部署

```bash
cd frontend

# 安装依赖
npm install
# 或使用国内镜像
npm install --registry=https://registry.npmmirror.com

# 开发环境
npm run dev

# 生产构建
npm run build
```

---

## 🔧 配置说明

### 数据库配置

编辑 `backend/.env` 文件：

```bash
# MySQL 配置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=test_platform

# PostgreSQL 配置
# DB_TYPE=postgresql
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_NAME=test_platform

# 后端服务配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8018
JOB_PORT=8019

# AI 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 安全配置
TOKEN_SECRET_KEY=your_secret_key
PASSWORD_SECRET_KEY=your_password_secret_key
```

### 数据库初始化

```bash
# 创建数据库
CREATE DATABASE test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 设置最大连接数
SET GLOBAL max_connections=16384;
```

### 🔄 数据库切换

```bash
# 使用切换脚本
python switch_database.py mysql       # 切换到 MySQL
python switch_database.py postgresql  # 切换到 PostgreSQL

# 应用迁移
python -m aerich upgrade
```

---

## 📚 部署指南

### 开发环境

```bash
# 启动主服务
python main.py

# 启动定时任务服务
python -m scheduledtask.job
```

### 生产环境

```bash
# 1. 给脚本执行权限
chmod 755 start.sh kill.sh

# 2. 启动服务
./start.sh

# 3. 停止服务
./kill.sh

# 使用 Gunicorn（推荐）
gunicorn main:app -c gunicorn_main.py
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8018;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 🎯 功能说明

### 1. MCP 配置管理

配置 Model Context Protocol 服务器：

1. 登录系统
2. 进入 **AI驱动管理模块** → **MCP 配置**
3. 点击 **新建配置**
4. 填写配置信息：
   - 配置名称: `测试 MCP 服务器`
   - 服务器 URL: `http://localhost:8765`
   - 传输协议: `streamable-http`
   - 认证头: `X-API-Key: your-key`（可选）
5. 测试连接并保存

### 2. LLM 配置管理

配置大语言模型：

1. 进入 **AI驱动管理模块** → **LLM 配置**
2. 点击 **新建配置**
3. 填写配置信息：
   - 配置名称: `OpenAI GPT-4`
   - 提供商: `openai`
   - 模型名称: `gpt-4`
   - API 密钥: `sk-your-key`
   - 基础 URL: `https://api.openai.com/v1`
4. 测试连接并保存

### 3. AI 测试用例生成

智能生成测试用例：

1. 创建项目并进入详情页
2. 点击 **AI 生成测试用例**
3. 选择生成方式：
   - 📴 **离线生成**: 基于模板生成
   - 🌐 **在线生成**: 调用 LLM 模型
4. 输入需求描述
5. 选择 LLM 配置
6. 生成并预览用例
7. 保存到对应模块或导出

### 4. 接口测试脚本生成

一键生成测试脚本：

- 支持框架: `pytest`、`unittest`、`TestNG`
- 自动生成断言
- 支持参数化
- 在线编辑和导出

### 5. 需求管理模块

智能需求管理：

- 📤 **文档上传**: 支持本地需求文档上传
- ✍️ **在线编辑**: 手动编写需求
- 🔍 **需求评审**: AI 辅助需求评审
- ✂️ **需求拆分**: 自动拆分功能点
- 🎯 **用例生成**: 基于拆分自动生成测试用例

---

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 **前端界面** | http://localhost:8016 | Web UI |
| 🔌 **后端 API** | http://localhost:8018 | REST API |
| 📖 **Swagger 文档** | http://localhost:8018/docs | API 文档 |
| 📘 **ReDoc 文档** | http://localhost:8018/redoc | API 文档 |
| ⏰ **定时任务** | http://localhost:8019 | Job 服务 |

### 默认账号

| 角色 | 账号 | 密码 | 权限 |
|------|------|------|------|
| 🔑 **管理员** | admin | 123456 | 所有权限 |
| 👤 **测试员** | tester | tester | 测试权限 |
| 👔 **负责人** | manager | manager | 管理权限 |

---

## ❓ 常见问题

<details>
<summary><b>1. 端口被占用</b></summary>

**错误**: `error while attempting to bind on address ('0.0.0.0', 8018)`

**解决方案**:

```bash
# Windows
netstat -ano | findstr :8018
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -ti:8018 | xargs kill -9
```
</details>

<details>
<summary><b>2. 数据库连接失败</b></summary>

**错误**: `Can't connect to MySQL server`

**解决方案**:
1. 确认 MySQL 服务正在运行
2. 确认数据库 `test_platform` 已创建
3. 检查 `.env` 文件中的数据库配置
4. 验证用户名和密码是否正确
</details>

<details>
<summary><b>3. Tortoise ORM 初始化失败</b></summary>

**错误**: `ConfigurationError: default_connection cannot be None`

**解决方案**:
- 确保使用 Tortoise ORM 0.25.3+
- 检查 `app/hooks/app_hook.py` 使用 `Tortoise.init`
- 验证数据库配置是否正确
</details>

<details>
<summary><b>4. 依赖包安装失败</b></summary>

**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:

```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用依赖安装工具
# Windows
install_deps.bat
# Linux/Mac
./install_deps.sh
```
</details>

<details>
<summary><b>5. UI 自动化浏览器驱动问题</b></summary>

**解决方案**:

1. 下载对应浏览器版本的驱动：[Selenium 驱动文档](https://www.selenium.dev/documentation/zh-cn/webdriver/driver_requirements/)
2. 将驱动放到 `browser_drivers` 目录
3. 给驱动添加执行权限：

```bash
chmod +x browser_drivers/chromedriver
```
</details>

---

## 🔄 数据库迁移

### 首次初始化

```bash
# 初始化 Aerich
python -m aerich init -t app.configs.config.tortoise_orm_conf

# 创建数据库表
python -m aerich init-db
```

### 模型变更后

```bash
# 生成迁移文件
python -m aerich migrate --name "描述变更内容"

# 应用迁移
python -m aerich upgrade

# 或使用数据库管理工具
python db_manager.py migrate
python db_manager.py upgrade
```

### 检查数据库状态

```bash
python db_manager.py status
```

---

## 🧪 测试 API

```bash
# 健康检查
curl http://localhost:8018/api/health

# 获取项目列表（需要登录）
curl -H "Authorization: Bearer <token>" \
     http://localhost:8018/api/aitestrebort/projects
```

---

## 📦 项目结构

```
GeniusQA/
├── backend/                 # 后端服务
│   ├── app/                # 应用核心
│   │   ├── configs/        # 配置文件
│   │   ├── models/         # 数据模型
│   │   ├── routers/        # 路由控制器
│   │   ├── schemas/        # 数据模式
│   │   ├── services/       # 业务逻辑
│   │   └── hooks/          # 钩子函数
│   ├── utils/              # 工具函数
│   ├── scheduledtask/      # 定时任务
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端服务
│   ├── src/               # 源代码
│   │   ├── api/           # API 接口
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── router/        # 路由
│   │   └── store/         # 状态管理
│   └── package.json       # Node 依赖
├── MCP/                   # MCP 工具服务
│   ├── GeniusQA_tools.py  # GeniusQA 工具
│   └── ms_mcp_api.py      # MS 工具
├── docker-compose.yml     # Docker 编排
└── README.md              # 项目文档
```

---

## 🤝 开发规范

### 代码风格

- **Python**: 遵循 PEP 8 规范，使用 Black 格式化
- **JavaScript/TypeScript**: 使用 ESLint + Prettier
- **提交信息**: 遵循 Conventional Commits 规范

### 分支管理

- `main`: 生产环境分支
- `develop`: 开发环境分支
- `feature/*`: 功能开发分支
- `bugfix/*`: 问题修复分支

---

<div align="center">

**[⬆ 回到顶部](#-geniusqa-测试平台)**

Made with ❤️ by GeniusQA Team

</div>
