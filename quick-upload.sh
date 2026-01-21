#!/bin/bash

echo "================================"
echo "  🚀 GeniusQA 快速上传到 GitHub"
echo "================================"
echo ""
echo "当前用户: QuanTum2088"
echo "当前邮箱: quantum2088@gmail.com"
echo ""

# 进入项目目录
cd /c/Users/Administrator/Desktop/GeniusQA

echo "📁 当前目录: $(pwd)"
echo ""

# 检查是否已经初始化
if [ -d ".git" ]; then
    echo "⚠️  Git 仓库已存在"
    read -p "是否重新初始化？(y/n): " reinit
    if [ "$reinit" = "y" ]; then
        rm -rf .git
        echo "✅ 已删除旧的 Git 仓库"
    fi
fi

echo ""
echo "================================"
echo "  第一步：初始化 Git 仓库"
echo "================================"
git init
if [ $? -eq 0 ]; then
    echo "✅ Git 仓库初始化成功"
else
    echo "❌ 初始化失败"
    exit 1
fi

echo ""
echo "================================"
echo "  第二步：添加文件到暂存区"
echo "================================"
git add .
if [ $? -eq 0 ]; then
    echo "✅ 文件添加成功"
else
    echo "❌ 添加文件失败"
    exit 1
fi

echo ""
echo "================================"
echo "  第三步：提交到本地仓库"
echo "================================"
git commit -m "Initial commit: GeniusQA AI-driven testing platform"
if [ $? -eq 0 ]; then
    echo "✅ 本地提交成功"
else
    echo "⚠️  提交失败（可能没有文件变更）"
fi

echo ""
echo "================================"
echo "  第四步：设置主分支"
echo "================================"
git branch -M main
echo "✅ 主分支设置为 main"

echo ""
echo "================================"
echo "  第五步：添加远程仓库"
echo "================================"
echo ""
echo "请输入你的 GitHub 仓库地址"
echo "格式: https://github.com/QuanTum2088/GeniusQA.git"
echo ""
read -p "仓库地址: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ 仓库地址不能为空"
    exit 1
fi

# 检查远程仓库是否已存在
if git remote | grep -q "origin"; then
    echo "⚠️  远程仓库已存在，正在更新..."
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi
echo "✅ 远程仓库配置完成"

echo ""
echo "================================"
echo "  第六步：推送到 GitHub"
echo "================================"
echo ""
echo "⚠️  注意："
echo "  - 用户名: QuanTum2088"
echo "  - 密码: 使用你的 Personal Access Token（不是密码）"
echo ""
echo "正在推送..."
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "  🎉 上传成功！"
    echo "================================"
    echo ""
    echo "你的项目已成功上传到 GitHub"
    echo "仓库地址: $REPO_URL"
    echo ""
    echo "访问你的项目："
    echo "${REPO_URL%.git}"
    echo ""
    echo "后续更新代码使用："
    echo "  git add ."
    echo "  git commit -m \"更新说明\""
    echo "  git push"
    echo ""
else
    echo ""
    echo "================================"
    echo "  ❌ 推送失败"
    echo "================================"
    echo ""
    echo "可能的原因："
    echo "  1. 网络连接问题"
    echo "  2. 认证失败 - 确保使用 Token 而不是密码"
    echo "  3. 仓库地址错误"
    echo "  4. 没有权限"
    echo ""
    echo "解决方案："
    echo "  1. 检查网络连接"
    echo "  2. 确认使用的是 Personal Access Token"
    echo "  3. 验证仓库地址是否正确"
    echo "  4. 确认 Token 有 repo 权限"
    echo ""
    exit 1
fi
