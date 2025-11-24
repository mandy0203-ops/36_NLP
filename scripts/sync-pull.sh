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
