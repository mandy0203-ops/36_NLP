#!/bin/bash
# 自動執行所有影片的 AI 切片分析

echo "🎬 開始批次切片處理..."
echo ""

# 影片目錄
VIDEO_DIR="/Volumes/SP PC60/1116"
OUTPUT_DIR="03-outputs/1116_highlights"
SLICER="01-system/tools/media/video_slicer/clip_extractor.py"

# 建立輸出目錄
mkdir -p "$OUTPUT_DIR"

# 處理計數
total=0
success=0
failed=0

# 逐一處理每個 SRT 檔案
for srt in 03-outputs/audio_transcribe/*/C*_formatted.srt; do
    # 提取檔案名稱 (例如: C8681_audio)
    basename=$(basename "$srt" _formatted.srt)
    # 移除 _audio 後綴得到影片名稱 (例如: C8681)
    video_name="${basename%_audio}"
    video_file="$VIDEO_DIR/${video_name}.MP4"
    
    # 檢查影片檔案是否存在
    if [ ! -f "$video_file" ]; then
        echo "⚠️  跳過: 找不到影片 $video_file"
        continue
    fi
    
    total=$((total + 1))
    echo "============================================================"
    echo "📊 進度: $total | 處理: $video_name"
    echo "============================================================"
    echo "   影片: $video_file"
    echo "   字幕: $srt"
    echo ""
    
    # 執行挑片大師
    output_subdir="$OUTPUT_DIR/${video_name}"
    mkdir -p "$output_subdir"
    
    python3 "$SLICER" \
        --video "$video_file" \
        --srt "$srt" \
        --output "$output_subdir" \
        --mode master
    
    if [ $? -eq 0 ]; then
        success=$((success + 1))
        echo "✅ $video_name 切片完成"
    else
        failed=$((failed + 1))
        echo "❌ $video_name 切片失敗"
    fi
    echo ""
done

echo "============================================================"
echo "🎉 批次切片處理完成!"
echo "============================================================"
echo "✅ 成功: $success 個"
echo "❌ 失敗: $failed 個"
echo "📁 輸出目錄: $OUTPUT_DIR"
