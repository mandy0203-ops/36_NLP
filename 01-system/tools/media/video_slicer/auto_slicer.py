#!/usr/bin/env python3
"""
Auto Video Slicer - 自動化影片切片流水線
用途: 整合 轉錄 -> 分析 -> 切片 的完整流程
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parents[4]))

from clip_extractor import VideoSlicer

# Import STT tools
STT_TOOL_PATH = Path(__file__).parents[4] / "01-system/tools/stt/audio_transcribe"
sys.path.append(str(STT_TOOL_PATH))

try:
    from modules.stt_engine import STTEngine
    from modules.output_manager import OutputManager
except ImportError:
    print("❌ 錯誤: 找不到 STT 模組，請確認路徑是否正確")
    sys.exit(1)

def extract_audio(video_path, output_audio_path):
    """從影片提取音訊 (壓縮為 mp3 以節省流量)"""
    print(f"🔊 正在提取音訊: {video_path} -> {output_audio_path}")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn", "-ac", "1", "-ar", "16000", "-b:a", "32k", "-f", "mp3",
        output_audio_path,
        "-loglevel", "error", "-stats"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 音訊提取完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 音訊提取失敗: {e}")
        return False

def run_transcription(audio_path, config):
    """執行轉錄"""
    print("📝 開始轉錄...")
    
    stt_config_path = STT_TOOL_PATH / "config.yaml"
    stt_engine = STTEngine(stt_config_path)
    
    engine_name = config.get('transcription', {}).get('engine', 'elevenlabs')
    
    try:
        transcription = stt_engine.transcribe(audio_path, engine_name)
        print("✅ 轉錄完成")
        return transcription
    except Exception as e:
        print(f"❌ 轉錄失敗: {e}")
        return None

def save_srt(transcription, srt_path):
    """儲存 SRT 檔案"""
    from modules.formatter import Formatter
    
    # 使用 Formatter 產生標準 SRT
    formatter = Formatter(STT_TOOL_PATH / "formatting_rules.yaml", STT_TOOL_PATH / "custom_dict.yaml")
    formatted_srt = formatter.format_srt(transcription['segments'])
    
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write(formatted_srt)
    
    print(f"💾 字幕已儲存: {srt_path}")

def process_video(video_path, slicer, output_root):
    """處理單一影片"""
    video_path = Path(video_path)
    base_name = video_path.stem
    
    # 建立專屬輸出目錄
    video_output_dir = output_root / base_name
    video_output_dir.mkdir(parents=True, exist_ok=True)
    
    # 預覽影片目錄
    previews_dir = video_output_dir / "previews"
    
    print(f"\n🎬 處理影片: {base_name}")
    print(f"📂 輸出目錄: {video_output_dir}")
    
    # 1. 檢查/產生字幕
    srt_path = video_output_dir / f"{base_name}.srt"
    
    if not srt_path.exists():
        print("⚠️  找不到字幕，準備轉錄...")
        
        # 提取音訊
        audio_path = video_output_dir / f"{base_name}.mp3"
        if not extract_audio(str(video_path), str(audio_path)):
            return
            
        # 轉錄
        transcription = run_transcription(str(audio_path), slicer.config)
        if not transcription:
            return
            
        # 儲存 SRT
        save_srt(transcription, str(srt_path))
        
        # 清理暫存音訊 (可選)
        # os.remove(audio_path)
    else:
        print("✅ 發現現有字幕，跳過轉錄")
        
    # 2. AI 分析與切片
    print("🧠 開始 AI 分析...")
    transcript_text = slicer.parse_srt(str(srt_path))
    clips_info = slicer.analyze_transcript(transcript_text)
    
    print(f"🔍 AI 挑選了 {len(clips_info)} 個片段")
    
    # 3. 尋找時間碼並切割 (Proxy 模式)
    clips_with_time = slicer.find_timecodes(str(srt_path), clips_info)
    
    if clips_with_time:
        print(f"✂️  開始切割預覽影片 (Proxy Mode)...")
        slicer.slice_video(str(video_path), clips_with_time, str(previews_dir), mode="proxy")
        print(f"🎉 {base_name} 處理完成！")
        print(f"👉 預覽影片已儲存至: {previews_dir}")
        print(f"👉 剪輯資訊已儲存至: {previews_dir}/clips.json")
    else:
        print("❌ 無法提取任何片段")

def main():
    parser = argparse.ArgumentParser(description="Auto Video Slicer Pipeline")
    parser.add_argument("--input", required=True, help="影片檔案或目錄路徑")
    parser.add_argument("--output", default=None, help="輸出根目錄 (預設為 03-outputs/video_slicer)")
    args = parser.parse_args()
    
    # 設定輸出目錄
    if args.output:
        output_root = Path(args.output)
    else:
        output_root = Path(__file__).parents[4] / "03-outputs/video_slicer"
        
    if not output_root.exists():
        output_root.mkdir(parents=True)
        
    # 初始化 Slicer
    slicer = VideoSlicer()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        process_video(input_path, slicer, output_root)
    elif input_path.is_dir():
        video_extensions = {'.mp4', '.mov', '.mkv', '.avi'}
        files = [f for f in input_path.iterdir() if f.suffix.lower() in video_extensions]
        
        print(f"📦 掃描到 {len(files)} 個影片檔案")
        
        for f in files:
            process_video(f, slicer, output_root)
    else:
        print(f"❌ 錯誤: 無效的輸入路徑 {input_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
