#!/bin/bash
# 一鍵部署腳本 - 在目標機器上執行
# 用途: 自動設定環境並安裝所有必要套件
# 特點: 智能檢查,避免重複安裝,支援部分已安裝的環境

set -e

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "影片轉文字工作流程 - 智能部署"
echo "=========================================="
echo ""

# 檢查是否在正確的目錄
if [ ! -f "01-system/tools/stt/audio_transcribe/transcribe.py" ]; then
    echo -e "${RED}❌ 錯誤: 請在 tars-001 專案目錄中執行此腳本${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 專案目錄確認${NC}"
echo ""

# ============================================
# 檢查並安裝 Homebrew
# ============================================
echo -e "${BLUE}[1/4] 檢查 Homebrew...${NC}"
if command -v brew &> /dev/null; then
    BREW_VERSION=$(brew --version | head -n1)
    echo -e "${GREEN}✅ Homebrew 已安裝 ($BREW_VERSION)${NC}"
else
    echo -e "${YELLOW}⚠️  Homebrew 未安裝${NC}"
    echo "正在安裝 Homebrew (這可能需要幾分鐘)..."
    
    # 非互動式安裝 Homebrew
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 設定 PATH (針對 Apple Silicon Mac)
    if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    echo -e "${GREEN}✅ Homebrew 安裝完成${NC}"
fi
echo ""

# ============================================
# 檢查並安裝 ffmpeg
# ============================================
echo -e "${BLUE}[2/4] 檢查 ffmpeg...${NC}"
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | awk '{print $3}')
    echo -e "${GREEN}✅ ffmpeg 已安裝 (版本 $FFMPEG_VERSION)${NC}"
else
    echo -e "${YELLOW}⚠️  ffmpeg 未安裝${NC}"
    echo "正在安裝 ffmpeg..."
    
    # 靜默安裝,不顯示過多輸出
    brew install ffmpeg > /dev/null 2>&1 || {
        echo -e "${YELLOW}使用詳細模式重試...${NC}"
        brew install ffmpeg
    }
    
    echo -e "${GREEN}✅ ffmpeg 安裝完成${NC}"
fi
echo ""

# ============================================
# 檢查並安裝 Python 3
# ============================================
echo -e "${BLUE}[3/4] 檢查 Python 3...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✅ Python 3 已安裝 (版本 $PYTHON_VERSION)${NC}"
else
    echo -e "${YELLOW}⚠️  Python 3 未安裝${NC}"
    echo "正在安裝 Python 3..."
    
    brew install python@3 > /dev/null 2>&1 || {
        echo -e "${YELLOW}使用詳細模式重試...${NC}"
        brew install python@3
    }
    
    echo -e "${GREEN}✅ Python 3 安裝完成${NC}"
fi
echo ""

# ============================================
# 建立 Python 虛擬環境
# ============================================
echo -e "${BLUE}[4/4] 設定 Python 環境...${NC}"

if [ -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  虛擬環境已存在${NC}"
    read -p "是否重新建立? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "移除舊的虛擬環境..."
        rm -rf .venv
        echo "建立新的虛擬環境..."
        python3 -m venv .venv
    else
        echo "保留現有虛擬環境"
    fi
else
    echo "建立 Python 虛擬環境..."
    python3 -m venv .venv
fi

echo ""
echo "安裝 Python 套件..."
echo -e "${YELLOW}(這可能需要 1-2 分鐘)${NC}"

# 升級 pip (靜默模式)
.venv/bin/pip install --upgrade pip --quiet

# 檢查並安裝套件
PACKAGES="pyyaml elevenlabs groq pydub"
for package in $PACKAGES; do
    if .venv/bin/pip show $package &> /dev/null; then
        echo -e "${GREEN}  ✓ $package 已安裝${NC}"
    else
        echo -e "${YELLOW}  ⬇ 安裝 $package...${NC}"
        .venv/bin/pip install $package --quiet
        echo -e "${GREEN}  ✓ $package 安裝完成${NC}"
    fi
done

echo ""

# ============================================
# 建立必要的目錄
# ============================================
echo "建立必要的目錄結構..."
mkdir -p 02-inputs
mkdir -p 03-outputs/audio_transcribe
echo -e "${GREEN}✅ 目錄結構已建立${NC}"
echo ""

# ============================================
# 設定腳本執行權限
# ============================================
echo "設定腳本執行權限..."
chmod +x scripts/*.sh 2>/dev/null || true
echo -e "${GREEN}✅ 腳本權限已設定${NC}"
echo ""

# ============================================
# 檢查 API Keys
# ============================================
echo "檢查 API Keys..."
if [ ! -f "01-system/configs/apis/API-Keys.md" ]; then
    echo -e "${RED}❌ 警告: API-Keys.md 檔案不存在${NC}"
    echo ""
    echo "請建立此檔案並加入您的 API Keys:"
    echo "  nano 01-system/configs/apis/API-Keys.md"
    echo ""
    echo "內容格式:"
    echo "  ELEVENLABS_API_KEY=sk-..."
    echo "  GROQ_API_KEY=gsk_..."
    echo ""
else
    # 檢查 API Keys 是否有內容
    if grep -q "ELEVENLABS_API_KEY=sk-" "01-system/configs/apis/API-Keys.md" && \
       grep -q "GROQ_API_KEY=gsk_" "01-system/configs/apis/API-Keys.md"; then
        echo -e "${GREEN}✅ API Keys 已設定${NC}"
    else
        echo -e "${YELLOW}⚠️  API Keys 檔案存在但可能未正確設定${NC}"
        echo "請確認檔案包含:"
        echo "  ELEVENLABS_API_KEY=sk-..."
        echo "  GROQ_API_KEY=gsk_..."
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 部署完成!${NC}"
echo "=========================================="
echo ""
echo "📋 安裝摘要:"
echo "  • Homebrew: $(command -v brew &> /dev/null && echo '✓' || echo '✗')"
echo "  • ffmpeg: $(command -v ffmpeg &> /dev/null && echo '✓' || echo '✗')"
echo "  • Python 3: $(command -v python3 &> /dev/null && echo '✓' || echo '✗')"
echo "  • 虛擬環境: $([ -d .venv ] && echo '✓' || echo '✗')"
echo "  • Python 套件: $([ -f .venv/bin/pip ] && .venv/bin/pip list | grep -q elevenlabs && echo '✓' || echo '✗')"
echo ""
echo "🚀 下一步:"
echo ""
echo "1. 測試單一檔案轉錄:"
echo "   ${BLUE}.venv/bin/python 01-system/tools/stt/audio_transcribe/transcribe.py --help${NC}"
echo ""
echo "2. 使用批次處理:"
echo "   ${BLUE}./scripts/batch_video_to_text.sh${NC}"
echo ""
echo "3. 查看工作流程文件:"
echo "   ${BLUE}cat .agent/workflows/video-to-text.md${NC}"
echo ""
