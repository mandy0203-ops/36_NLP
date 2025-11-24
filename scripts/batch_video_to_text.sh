#!/bin/bash
# 批次影片轉文字處理腳本
# 用途: 自動壓縮並轉錄多個影片檔案

set -e  # 遇到錯誤立即停止

# 設定路徑
SOURCE_DIR="/Volumes/Samsung-T7"
OUTPUT_DIR="/Users/xiangyun/Desktop"
WORK_DIR="/Users/xiangyun/Desktop/tars-001"
VENV_PYTHON="$WORK_DIR/.venv/bin/python"
TRANSCRIBE_TOOL="$WORK_DIR/01-system/tools/stt/audio_transcribe/transcribe.py"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "批次影片轉文字處理"
echo "=========================================="
echo ""

# 檢查來源目錄
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}錯誤: 找不到外接硬碟 $SOURCE_DIR${NC}"
    exit 1
fi

# 取得所有 C857*.MP4 檔案 (排除已處理的 C8573 和 C8574)
FILES=$(ls "$SOURCE_DIR"/C857[5-9].MP4 2>/dev/null || true)

if [ -z "$FILES" ]; then
    echo -e "${RED}錯誤: 找不到符合的影片檔案${NC}"
    exit 1
fi

# 計算檔案數量
FILE_COUNT=$(echo "$FILES" | wc -l | tr -d ' ')
echo -e "${GREEN}找到 $FILE_COUNT 個影片檔案待處理${NC}"
echo ""

CURRENT=0
TOTAL=$FILE_COUNT

# 處理每個檔案
for VIDEO_FILE in $FILES; do
    CURRENT=$((CURRENT + 1))
    BASENAME=$(basename "$VIDEO_FILE" .MP4)
    
    echo "=========================================="
    echo -e "${YELLOW}[$CURRENT/$TOTAL] 處理: $BASENAME${NC}"
    echo "=========================================="
    
    # 顯示檔案大小
    FILE_SIZE=$(ls -lh "$VIDEO_FILE" | awk '{print $5}')
    echo "檔案大小: $FILE_SIZE"
    
    # 步驟 1: 壓縮影片為音檔
    COMPRESSED_AUDIO="$OUTPUT_DIR/${BASENAME}_compressed.mp3"
    
    if [ -f "$COMPRESSED_AUDIO" ]; then
        echo -e "${YELLOW}⚠️  壓縮音檔已存在,跳過壓縮步驟${NC}"
    else
        echo -e "${GREEN}⚡ 步驟 1/2: 壓縮影片...${NC}"
        ffmpeg -i "$VIDEO_FILE" \
            -vn -ac 1 -ar 16000 -b:a 32k -f mp3 \
            "$COMPRESSED_AUDIO" \
            -y -loglevel error -stats
        
        COMPRESSED_SIZE=$(ls -lh "$COMPRESSED_AUDIO" | awk '{print $5}')
        echo -e "${GREEN}✅ 壓縮完成: $COMPRESSED_SIZE${NC}"
    fi
    
    # 步驟 2: 轉錄
    echo -e "${GREEN}⚡ 步驟 2/2: 轉錄音檔...${NC}"
    cd "$WORK_DIR"
    "$VENV_PYTHON" "$TRANSCRIBE_TOOL" \
        --input "$COMPRESSED_AUDIO" \
        --engine elevenlabs \
        --output-name "$BASENAME"
    
    echo -e "${GREEN}✅ $BASENAME 處理完成!${NC}"
    echo ""
done

echo "=========================================="
echo -e "${GREEN}🎉 所有檔案處理完成!${NC}"
echo "=========================================="
echo ""
echo "輸出位置: $WORK_DIR/03-outputs/audio_transcribe/"
echo ""
