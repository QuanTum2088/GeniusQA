#!/bin/bash

echo "================================"
echo "  GeniusQA 上传到 GitHub"
echo "================================"
echo ""

# 检查是否已安装 Git
if ! command -v git &> /dev/null; then
    echo "[错误] Git 未安装"
    echo "请先安装 Git: https://git-scm.com/downloads"
    exit 1
fi

echo "[1/7] 初始化 Git 仓库..."
git init
if [ $? -ne 0 ]; then
    echo "[错误] Git 初始化失败"
    exit 1
fi
echo "[成功] Git 仓库初始化完成"

echo ""
echo "[2/7] 添加所有文件到暂存区..."
git add .
if [ $? -ne 0 ]; then
    echo "[错误] 添加文件失败"
    exit 1
fi
echo "[成功] 文件添加完成"

echo ""
echo "[3/7] 提交到本地仓库..."
git commit -m "Initial commit: GeniusQA AI-driven testing platform"
if [ $? -ne 0 ]; then
    echo "[警告] 提交失败，可能没有文件变更"
fi
echo "[成功] 本地提交完成"

echo ""
echo "[4/7] 设置主分支为 main..."
git branch -M main
echo "[成功] 分支设置完成"

echo ""
echo "================================"
echo "  请输入你的 GitHub 仓库地址"
echo "================================"
echo ""
echo "格式示例: https://github.com/username/GeniusQA.git"
echo "或: git@github.com:username/GeniusQA.git"
echo ""
read -p "请输入仓库地址: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "[错误] 仓库地址不能为空"
    exit 1
fi

echo ""
echo "[5/7] 添加远程仓库..."
git remote add origin "$REPO_URL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[警告] 远程仓库可能已存在，尝试更新..."
    git remote set-url origin "$REPO_URL"
fi
echo "[成功] 远程仓库配置完成"

echo ""
echo "[6/7] 推送到 GitHub..."
echo "注意: 首次推送可能需要输入 GitHub 用户名和密码"
echo ""
git push -u origin main
if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 推送失败"
    echo ""
    echo "可能的原因:"
    echo "  1. 网络连接问题"
    echo "  2. 认证失败 - 需要配置 GitHub 访问令牌"
    echo "  3. 远程仓库地址错误"
    echo ""
    echo "解决方案:"
    echo "  1. 检查网络连接"
    echo "  2. 配置 GitHub Personal Access Token"
    echo "  3. 验证仓库地址是否正确"
    echo ""
    exit 1
fi

echo ""
echo "================================"
echo "  🎉 上传成功！"
echo "================================"
echo ""
echo "你的项目已成功上传到 GitHub"
echo "仓库地址: $REPO_URL"
echo ""
echo "后续更新代码使用:"
echo "  git add ."
echo "  git commit -m \"更新说明\""
echo "  git push"
echo ""
