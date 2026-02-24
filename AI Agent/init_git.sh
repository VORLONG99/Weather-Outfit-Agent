#!/bin/bash

# 初始化 Git 仓库并进行安全检查

echo "🔍 开始安全检查..."

# 检查 .gitignore 是否存在
if [ ! -f .gitignore ]; then
    echo "❌ 错误: .gitignore 文件不存在"
    exit 1
fi

# 检查 .env 是否在 .gitignore 中
if ! grep -q "^\.env$" .gitignore; then
    echo "❌ 错误: .env 未在 .gitignore 中"
    exit 1
fi

echo "✅ .gitignore 配置正确"

# 初始化 Git（如果尚未初始化）
if [ ! -d .git ]; then
    echo "📦 初始化 Git 仓库..."
    git init
else
    echo "✅ Git 仓库已存在"
fi

# 添加所有文件
echo "📝 添加文件到暂存区..."
git add .

# 检查 .env 是否会被提交
if git status --porcelain | grep -q "^[AM].*\.env$"; then
    echo "❌ 警告: .env 文件将被提交！请检查 .gitignore"
    git reset .env
    exit 1
fi

echo "✅ .env 文件已被正确忽略"

# 显示将要提交的文件
echo ""
echo "📋 将要提交的文件："
git status --short

echo ""
echo "✅ 安全检查通过！"
echo ""
echo "下一步："
echo "1. 检查上面的文件列表，确认没有敏感信息"
echo "2. 运行: git commit -m 'Initial commit: Daily outfit email agent'"
echo "3. 在 GitHub 创建新仓库"
echo "4. 运行: git remote add origin <你的仓库URL>"
echo "5. 运行: git push -u origin main"
