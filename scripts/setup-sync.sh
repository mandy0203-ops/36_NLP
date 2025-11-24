#!/bin/bash
# 同步設定腳本 - 初始化 Git 和建立同步腳本

set -e

echo "=========================================="
echo "設定雙機同步環境"
echo "=========================================="
echo ""

# 檢查是否在正確的目錄
if [ ! -f "01-system/tools/stt/audio_transcribe/transcribe.py" ]; then
    echo "❌ 錯誤: 請在 tars-001 專案目錄中執行此腳本"
    exit 1
fi

# 初始化 Git (如果尚未初始化)
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git repository..."
    git init
    echo "✅ Git repository 已初始化"
else
    echo "✅ Git repository 已存在"
fi

# 更新 .gitignore
echo "📝 更新 .gitignore..."
cat >> .gitignore << 'EOF'

# 同步排除項目
.venv/
venv/
03-outputs/
*.mp3
*.MP4
*.mp4
*.mov
*.MOV
__pycache__/
*.pyc
.DS_Store

# API Keys 保持本地
01-system/configs/apis/API-Keys.md
EOF

echo "✅ .gitignore 已更新"

# 建立 sync-push.sh
echo "📝 建立 sync-push.sh..."
cat > scripts/sync-push.sh << 'PUSHEOF'
#!/bin/bash
# 推送變更到外接硬碟

set -e

COMMIT_MSG="${1:-Update: $(date +'%Y-%m-%d %H:%M:%S')}"
REMOTE_PATH="/Volumes/Samsung-T7/tars-001-git-repo"

echo "=========================================="
echo "推送變更到外接硬碟"
echo "=========================================="

# 檢查外接硬碟
if [ ! -d "/Volumes/Samsung-T7" ]; then
    echo "❌ 錯誤: 找不到 Samsung-T7 外接硬碟"
    exit 1
fi

# 顯示變更
echo ""
echo "📝 變更內容:"
git status --short

# 提交變更
echo ""
echo "💾 提交變更..."
git add .
git commit -m "$COMMIT_MSG" || echo "⚠️  沒有新的變更需要提交"

# 設定遠端 repository (如果不存在)
if [ ! -d "$REMOTE_PATH" ]; then
    echo "📦 建立遠端 repository..."
    mkdir -p "$REMOTE_PATH"
    cd "$REMOTE_PATH"
    git init --bare
    cd -
fi

# 設定 remote (如果不存在)
if ! git remote | grep -q "usb"; then
    git remote add usb "$REMOTE_PATH"
fi

# 推送
echo ""
echo "⬆️  推送到外接硬碟..."
git push usb main 2>/dev/null || git push usb master 2>/dev/null || {
    # 第一次推送
    BRANCH=$(git branch --show-current)
    git push -u usb $BRANCH
}

echo ""
echo "✅ 同步完成!"
echo "=========================================="
PUSHEOF

chmod +x scripts/sync-push.sh
echo "✅ sync-push.sh 已建立"

# 建立 sync-pull.sh
echo "📝 建立 sync-pull.sh..."
cat > scripts/sync-pull.sh << 'PULLEOF'
#!/bin/bash
# 從外接硬碟拉取變更

set -e

REMOTE_PATH="/Volumes/Samsung-T7/tars-001-git-repo"

echo "=========================================="
echo "從外接硬碟拉取變更"
echo "=========================================="

# 檢查外接硬碟
if [ ! -d "/Volumes/Samsung-T7" ]; then
    echo "❌ 錯誤: 找不到 Samsung-T7 外接硬碟"
    exit 1
fi

# 檢查遠端 repository
if [ ! -d "$REMOTE_PATH" ]; then
    echo "❌ 錯誤: 找不到遠端 repository"
    echo "   請先在另一台機器上執行 sync-push.sh"
    exit 1
fi

# 設定 remote (如果不存在)
if ! git remote | grep -q "usb"; then
    git remote add usb "$REMOTE_PATH"
fi

# 拉取變更
echo ""
echo "⬇️  拉取變更..."
BRANCH=$(git branch --show-current)
git pull usb $BRANCH || {
    echo "⚠️  第一次拉取,設定追蹤分支..."
    git branch --set-upstream-to=usb/$BRANCH $BRANCH
    git pull
}

echo ""
echo "📝 更新內容:"
git log -1 --oneline

echo ""
echo "✅ 同步完成!"
echo "=========================================="
PULLEOF

chmod +x scripts/sync-pull.sh
echo "✅ sync-pull.sh 已建立"

# 第一次提交
echo ""
echo "💾 建立初始提交..."
git add .
git commit -m "Initial commit: Video to text workflow with sync setup" || echo "⚠️  已有提交記錄"

echo ""
echo "=========================================="
echo "🎉 同步環境設定完成!"
echo "=========================================="
echo ""
echo "使用方式:"
echo ""
echo "推送變更到外接硬碟:"
echo "  ./scripts/sync-push.sh \"您的提交訊息\""
echo ""
echo "從外接硬碟拉取變更:"
echo "  ./scripts/sync-pull.sh"
echo ""
echo "查看詳細說明:"
echo "  cat .agent/workflows/sync-guide.md"
echo ""
