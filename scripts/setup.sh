#!/bin/bash
# 一鍵部署腳本 - 在目標機器上執行
# 用途: 自動設定環境並安裝所有必要套件

set -e

echo "=========================================="
echo "影片轉文字工作流程 - 一鍵部署"
echo "=========================================="
echo ""

# 檢查是否在正確的目錄
if [ ! -f "01-system/tools/stt/audio_transcribe/transcribe.py" ]; then
    echo "❌ 錯誤: 請在 tars-001 專案目錄中執行此腳本"
    exit 1
fi

echo "✅ 專案目錄確認"

# 檢查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "⚠️  Homebrew 未安裝,正在安裝..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew 已安裝"
fi

# 檢查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg 未安裝,正在安裝..."
    brew install ffmpeg
else
    echo "✅ ffmpeg 已安裝"
fi

# 檢查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python 3 未安裝,正在安裝..."
    brew install python@3
else
    echo "✅ Python 3 已安裝"
fi

# 建立虛擬環境
if [ -d ".venv" ]; then
    echo "⚠️  虛擬環境已存在,將重新建立..."
    rm -rf .venv
fi

echo "📦 建立 Python 虛擬環境..."
python3 -m venv .venv

echo "📦 安裝 Python 套件..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install pyyaml elevenlabs groq pydub

# 建立必要的目錄
mkdir -p 02-inputs
mkdir -p 03-outputs/audio_transcribe

echo "✅ 目錄結構已建立"

# 設定腳本執行權限
if [ -f "scripts/batch_video_to_text.sh" ]; then
    chmod +x scripts/batch_video_to_text.sh
    echo "✅ 批次處理腳本權限已設定"
fi

# 檢查 API Keys
if [ ! -f "01-system/configs/apis/API-Keys.md" ]; then
    echo "⚠️  警告: API-Keys.md 檔案不存在"
    echo "   請建立此檔案並加入您的 API Keys:"
    echo "   ELEVENLABS_API_KEY=sk-..."
    echo "   GROQ_API_KEY=gsk_..."
else
    echo "✅ API Keys 檔案存在"
fi

echo ""
echo "=========================================="
echo "🎉 部署完成!"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 確認 API Keys 已設定在 01-system/configs/apis/API-Keys.md"
echo "2. 測試單一檔案轉錄:"
echo "   .venv/bin/python 01-system/tools/stt/audio_transcribe/transcribe.py --input 測試檔案.mp3"
echo ""
echo "3. 使用批次處理:"
echo "   ./scripts/batch_video_to_text.sh"
echo ""
