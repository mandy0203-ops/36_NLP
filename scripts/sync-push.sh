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
