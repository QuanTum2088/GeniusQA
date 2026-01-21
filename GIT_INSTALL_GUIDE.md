# 📥 Git 安装详细教程（Windows）

## 🎯 安装步骤

### 第一步：下载 Git

**方式一：官方网站（推荐）**
- 访问：https://git-scm.com/download/win
- 页面会自动开始下载最新版本
- 文件名类似：`Git-2.43.0-64-bit.exe`

**方式二：国内镜像（下载更快）**
- 访问：https://registry.npmmirror.com/binary.html?path=git-for-windows/
- 选择最新版本文件夹
- 下载 `Git-x.xx.x-64-bit.exe`

**方式三：直接下载链接**
- 64位系统：https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe

---

### 第二步：安装 Git

1. **双击下载的安装包**
   - 文件名：`Git-x.xx.x-64-bit.exe`

2. **安装向导 - 按以下选择**

   #### 📄 许可协议
   - 点击 **Next**

   #### 📁 选择安装位置
   - 默认：`C:\Program Files\Git`
   - 可以修改，但建议使用默认
   - 点击 **Next**

   #### ☑️ 选择组件
   - 保持默认勾选即可
   - 建议勾选：
     - ✅ Windows Explorer integration（右键菜单集成）
     - ✅ Git Bash Here
     - ✅ Git GUI Here
     - ✅ Associate .git* configuration files
     - ✅ Associate .sh files to be run with Bash
   - 点击 **Next**

   #### 📋 开始菜单文件夹
   - 默认：`Git`
   - 点击 **Next**

   #### 📝 选择默认编辑器
   - 推荐选择：**Use Vim** 或 **Use Notepad++**
   - 如果不熟悉，选择 **Use Notepad**
   - 点击 **Next**

   #### 🌿 调整初始分支名称
   - 选择：**Let Git decide**（让 Git 决定）
   - 或选择：**Override the default branch name for new repositories** 并输入 `main`
   - 点击 **Next**

   #### 🔧 调整 PATH 环境变量
   - ⭐ **重要：选择第二项**
   - ✅ **Git from the command line and also from 3rd-party software**
   - 这样可以在 CMD 和 PowerShell 中使用 Git
   - 点击 **Next**

   #### 🔐 选择 SSH 可执行文件
   - 选择：**Use bundled OpenSSH**
   - 点击 **Next**

   #### 🔒 选择 HTTPS 传输后端
   - 选择：**Use the OpenSSL library**
   - 点击 **Next**

   #### 📄 配置行尾转换
   - Windows 系统选择：**Checkout Windows-style, commit Unix-style line endings**
   - 点击 **Next**

   #### 💻 配置终端模拟器
   - 选择：**Use MinTTY (the default terminal of MSYS2)**
   - 点击 **Next**

   #### 🔄 配置 git pull 行为
   - 选择：**Default (fast-forward or merge)**
   - 点击 **Next**

   #### 🔑 选择凭据助手
   - 选择：**Git Credential Manager**
   - 这样可以保存 GitHub 凭据，不用每次输入
   - 点击 **Next**

   #### ⚙️ 配置额外选项
   - 保持默认勾选：
     - ✅ Enable file system caching
     - ✅ Enable symbolic links
   - 点击 **Next**

   #### 🧪 配置实验性功能
   - 不勾选任何选项
   - 点击 **Install**

3. **等待安装完成**
   - 安装过程约 1-2 分钟
   - 完成后点击 **Finish**

---

### 第三步：验证安装

1. **打开新的命令行窗口**
   - 按 `Win + R`
   - 输入 `cmd`
   - 按回车

2. **检查 Git 版本**
   ```bash
   git --version
   ```
   
   **成功显示：**
   ```
   git version 2.43.0.windows.1
   ```

3. **如果显示 "git 不是内部或外部命令"**
   - 关闭命令行窗口
   - 重新打开新的命令行窗口
   - 再次尝试

---

### 第四步：配置 Git

安装成功后，需要配置用户信息：

```bash
# 设置用户名（替换为你的 GitHub 用户名）
git config --global user.name "YourGitHubUsername"

# 设置邮箱（替换为你的 GitHub 邮箱）
git config --global user.email "your-email@example.com"

# 验证配置
git config --list
```

**应该看到：**
```
user.name=YourGitHubUsername
user.email=your-email@example.com
...
```

---

## 🎨 Git 工具介绍

安装完成后，你会有以下工具：

### 1. Git Bash
- 类 Unix 命令行环境
- 推荐使用
- 右键文件夹 → **Git Bash Here**

### 2. Git CMD
- Windows 命令行集成
- 在 CMD 中直接使用 `git` 命令

### 3. Git GUI
- 图形界面工具
- 适合不熟悉命令行的用户

---

## 🔧 常用 Git 配置

### 配置中文显示

```bash
# 解决中文乱码
git config --global core.quotepath false
git config --global gui.encoding utf-8
git config --global i18n.commit.encoding utf-8
git config --global i18n.logoutputencoding utf-8
```

### 配置凭据保存

```bash
# Windows 凭据管理器（推荐）
git config --global credential.helper wincred

# 或使用 Git Credential Manager
git config --global credential.helper manager
```

### 配置默认分支名

```bash
# 设置默认分支为 main
git config --global init.defaultBranch main
```

### 配置代理（如果需要）

```bash
# HTTP 代理
git config --global http.proxy http://127.0.0.1:7890

# HTTPS 代理
git config --global https.proxy https://127.0.0.1:7890

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

## ❓ 常见问题

### 问题1：安装后命令行找不到 git

**原因：** 环境变量未生效

**解决方案：**
1. 关闭所有命令行窗口
2. 重新打开新的命令行窗口
3. 如果还不行，重启电脑

### 问题2：中文文件名显示乱码

**解决方案：**
```bash
git config --global core.quotepath false
```

### 问题3：每次都要输入用户名密码

**解决方案：**
```bash
git config --global credential.helper wincred
```

### 问题4：SSL 证书错误

**解决方案：**
```bash
git config --global http.sslVerify false
```

---

## 🎯 下一步

Git 安装完成后，你可以：

1. ✅ 配置 Git 用户信息
2. ✅ 在 GitHub 创建仓库
3. ✅ 上传 GeniusQA 项目

---

## 📚 学习资源

- Git 官方文档：https://git-scm.com/doc
- Git 中文教程：https://www.liaoxuefeng.com/wiki/896043488029600
- GitHub 帮助：https://docs.github.com

---

**安装完成后，告诉我，我会指导你下一步！**
