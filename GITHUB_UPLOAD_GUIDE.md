# 📤 GitHub 上传完整指南

本指南将帮助你将 GeniusQA 项目上传到 GitHub。

---

## 🚀 快速上传（推荐）

### Windows 用户

```bash
# 双击运行或在命令行执行
upload-to-github.bat
```

### Linux/Mac 用户

```bash
# 添加执行权限
chmod +x upload-to-github.sh

# 运行脚本
./upload-to-github.sh
```

---

## 📋 手动上传步骤

### 前置准备

#### 1. 安装 Git

**Windows:**
- 下载：https://git-scm.com/download/win
- 运行安装程序，使用默认设置
- 重启命令行

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install git

# CentOS/RHEL
sudo yum install git
```

**Mac:**
```bash
# 使用 Homebrew
brew install git
```

#### 2. 配置 Git

```bash
# 设置用户名
git config --global user.name "你的GitHub用户名"

# 设置邮箱
git config --global user.email "your-email@example.com"

# 验证配置
git config --list
```

#### 3. 创建 GitHub 仓库

1. 登录 GitHub: https://github.com
2. 点击右上角 **+** → **New repository**
3. 填写信息：
   - Repository name: `GeniusQA`
   - Description: `AI驱动的一体化测试管理平台`
   - 选择 Public 或 Private
   - ⚠️ **不要勾选** "Initialize this repository with a README"
4. 点击 **Create repository**
5. 复制仓库地址（HTTPS 或 SSH）

---

## 📦 上传项目

### 方法一：HTTPS 方式（推荐新手）

```bash
# 1. 进入项目目录
cd C:\Users\Administrator\Desktop\GeniusQA

# 2. 初始化 Git 仓库
git init

# 3. 添加所有文件
git add .

# 4. 提交到本地仓库
git commit -m "Initial commit: GeniusQA AI-driven testing platform"

# 5. 设置主分支为 main
git branch -M main

# 6. 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/GeniusQA.git

# 7. 推送到 GitHub
git push -u origin main
```

### 方法二：SSH 方式（推荐熟练用户）

#### 配置 SSH 密钥

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your-email@example.com"

# 2. 启动 ssh-agent
eval "$(ssh-agent -s)"

# 3. 添加私钥
ssh-add ~/.ssh/id_ed25519

# 4. 复制公钥
cat ~/.ssh/id_ed25519.pub
```

#### 添加 SSH 密钥到 GitHub

1. 登录 GitHub
2. 点击头像 → **Settings**
3. 左侧菜单 → **SSH and GPG keys**
4. 点击 **New SSH key**
5. 粘贴公钥内容
6. 点击 **Add SSH key**

#### 使用 SSH 上传

```bash
# 1-5 步骤同 HTTPS 方式

# 6. 添加远程仓库（SSH 地址）
git remote add origin git@github.com:你的用户名/GeniusQA.git

# 7. 推送到 GitHub
git push -u origin main
```

---

## 🔐 GitHub 认证方式

### Personal Access Token (推荐)

从 2021 年 8 月起，GitHub 不再支持密码认证，需要使用 Personal Access Token。

#### 创建 Token

1. 登录 GitHub
2. 点击头像 → **Settings**
3. 左侧菜单 → **Developer settings**
4. 点击 **Personal access tokens** → **Tokens (classic)**
5. 点击 **Generate new token** → **Generate new token (classic)**
6. 填写信息：
   - Note: `GeniusQA Upload`
   - Expiration: 选择过期时间
   - 勾选权限：
     - ✅ `repo` (完整仓库访问权限)
7. 点击 **Generate token**
8. ⚠️ **立即复制 Token**（只显示一次）

#### 使用 Token

推送时输入：
- Username: 你的 GitHub 用户名
- Password: 粘贴刚才复制的 Token

#### 保存凭据（避免重复输入）

```bash
# Windows
git config --global credential.helper wincred

# Linux/Mac
git config --global credential.helper store
```

---

## 🔄 后续更新代码

### 日常提交流程

```bash
# 1. 查看修改状态
git status

# 2. 添加修改的文件
git add .
# 或添加特定文件
git add backend/main.py

# 3. 提交到本地
git commit -m "描述你的修改内容"

# 4. 推送到 GitHub
git push
```

### 提交信息规范

使用清晰的提交信息：

```bash
# 功能开发
git commit -m "feat: 添加AI用例生成功能"

# Bug 修复
git commit -m "fix: 修复数据库连接超时问题"

# 文档更新
git commit -m "docs: 更新README部署说明"

# 代码重构
git commit -m "refactor: 优化API接口性能"

# 样式调整
git commit -m "style: 统一代码格式"

# 测试相关
git commit -m "test: 添加单元测试"
```

---

## ❓ 常见问题

### 1. 推送失败：认证错误

**错误信息:**
```
remote: Support for password authentication was removed
fatal: Authentication failed
```

**解决方案:**
使用 Personal Access Token 代替密码（见上文）

### 2. 推送失败：远程仓库有更新

**错误信息:**
```
! [rejected] main -> main (fetch first)
```

**解决方案:**
```bash
# 拉取远程更新
git pull origin main --rebase

# 再次推送
git push origin main
```

### 3. 文件太大无法上传

**错误信息:**
```
remote: error: File xxx is 100.00 MB; this exceeds GitHub's file size limit
```

**解决方案:**
```bash
# 1. 将大文件添加到 .gitignore
echo "large-file.zip" >> .gitignore

# 2. 从 Git 历史中移除
git rm --cached large-file.zip

# 3. 重新提交
git commit -m "Remove large file"
git push
```

### 4. 忘记添加 .gitignore

**解决方案:**
```bash
# 1. 创建 .gitignore 文件（已提供）

# 2. 清除已跟踪的文件
git rm -r --cached .

# 3. 重新添加文件
git add .

# 4. 提交
git commit -m "Update .gitignore"
git push
```

### 5. 网络连接问题

**解决方案:**

```bash
# 使用代理（如果有）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy https://127.0.0.1:7890

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy

# 增加超时时间
git config --global http.postBuffer 524288000
```

---

## 📁 推荐的 .gitignore 配置

项目已包含 `.gitignore` 文件，主要排除：

- ✅ Python 缓存文件 (`__pycache__`, `*.pyc`)
- ✅ 虚拟环境 (`.venv/`, `venv/`)
- ✅ 环境变量文件 (`.env`)
- ✅ 日志文件 (`logs/`, `*.log`)
- ✅ 数据库文件 (`*.db`, `*.sqlite`)
- ✅ Node 模块 (`node_modules/`)
- ✅ 构建文件 (`dist/`, `build/`)
- ✅ IDE 配置 (`.vscode/`, `.idea/`)
- ✅ 上传文件 (`uploads/`)
- ✅ 浏览器驱动 (`browser_drivers/`)

---

## 🌿 分支管理

### 创建开发分支

```bash
# 创建并切换到开发分支
git checkout -b develop

# 推送开发分支
git push -u origin develop
```

### 功能开发流程

```bash
# 1. 从 develop 创建功能分支
git checkout -b feature/ai-test-generation

# 2. 开发并提交
git add .
git commit -m "feat: 实现AI测试用例生成"

# 3. 推送功能分支
git push -u origin feature/ai-test-generation

# 4. 在 GitHub 创建 Pull Request
# 5. 代码审查后合并到 develop
```

---

## 🔒 安全建议

### 敏感信息保护

1. ✅ **永远不要提交**：
   - `.env` 文件
   - 数据库密码
   - API 密钥
   - SSH 私钥
   - 访问令牌

2. ✅ **使用环境变量**：
   - 提供 `.env.example` 模板
   - 在 README 中说明配置方法

3. ✅ **检查提交历史**：
   ```bash
   # 查看提交内容
   git log --oneline
   git show <commit-id>
   ```

4. ✅ **如果不小心提交了敏感信息**：
   ```bash
   # 从历史中完全删除
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/sensitive-file" \
     --prune-empty --tag-name-filter cat -- --all
   
   # 强制推送
   git push origin --force --all
   ```

---

## 📊 查看仓库状态

```bash
# 查看当前状态
git status

# 查看提交历史
git log --oneline --graph --all

# 查看远程仓库
git remote -v

# 查看分支
git branch -a
```

---

## 🎯 完成检查清单

上传前确认：

- [ ] 已安装 Git
- [ ] 已配置 Git 用户信息
- [ ] 已创建 GitHub 仓库
- [ ] 已创建 `.gitignore` 文件
- [ ] 已删除敏感信息
- [ ] README.md 内容完整
- [ ] 项目可以正常运行

---

## 📞 获取帮助

- Git 官方文档: https://git-scm.com/doc
- GitHub 帮助: https://docs.github.com
- Git 教程: https://www.atlassian.com/git/tutorials

---

**祝你上传顺利！🎉**
