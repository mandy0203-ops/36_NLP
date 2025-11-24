#!/usr/bin/env python3
"""
YouTube to Subtitle Tool - 一鍵整合
下載 YouTube 音檔並自動轉錄為字幕
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def download_audio(url, output_dir="02-inputs"):
    """下載 YouTube 音檔為 MP3"""
    print("📥 步驟 1/2：下載 YouTube 音檔")
    print("-" * 60)
    
    output_template = f"{output_dir}/%(title)s.%(ext)s"
    
    cmd = [
        "yt-dlp",
        "-x",  # 只下載音檔
        "--audio-format", "mp3",
        "--audio-quality", "0",  # 最佳音質
        "-o", output_template,
        url
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # 從輸出中提取檔案名稱
        for line in result.stdout.split('\n'):
            if 'Destination:' in line or 'ExtractAudio' in line:
                # 提取檔案路徑
                if '.mp3' in line:
                    parts = line.split()
                    for part in parts:
                        if part.endswith('.mp3'):
                            return part
        
        # 備用方法：列出最新的 mp3 檔案
        mp3_files = list(Path(output_dir).glob("*.mp3"))
        if mp3_files:
            latest_file = max(mp3_files, key=lambda p: p.stat().st_mtime)
            return str(latest_file)
        
        print("❌ 無法找到下載的檔案")
        sys.exit(1)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 下載失敗：{e}")
        print(e.stderr)
        sys.exit(1)

def transcribe_audio(audio_path, engine=None, output_name=None):
    """呼叫轉錄工具"""
    print("\n📝 步驟 2/2：轉錄為字幕")
    print("-" * 60)
    
    transcribe_script = "01-system/tools/stt/audio_transcribe/transcribe.py"
    
    cmd = [
        ".venv/bin/python",
        transcribe_script,
        "--input", audio_path
    ]
    
    if engine:
        cmd.extend(["--engine", engine])
    
    if output_name:
        cmd.extend(["--output-name", output_name])
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 轉錄失敗：{e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="YouTube 轉字幕一鍵工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s --url "https://youtu.be/xxxxx"
  %(prog)s --url "https://youtu.be/xxxxx" --engine elevenlabs
  %(prog)s --url "https://youtu.be/xxxxx" --output-name "EP01"
        """
    )
    
    parser.add_argument('--url', required=True, help='YouTube 影片網址')
    parser.add_argument('--engine', choices=['elevenlabs', 'groq'], help='指定 STT 引擎')
    parser.add_argument('--output-name', help='自訂輸出資料夾名稱')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎬 YouTube 轉字幕工具")
    print("=" * 60)
    print()
    
    # 步驟 1：下載音檔
    audio_path = download_audio(args.url)
    print(f"✅ 下載完成：{audio_path}")
    print()
    
    # 步驟 2：轉錄
    transcribe_audio(audio_path, args.engine, args.output_name)
    
    # 自動清理音檔
    try:
        os.remove(audio_path)
        print(f"\n🗑️  已清理臨時音檔：{audio_path}")
    except Exception as e:
        print(f"\n⚠️  清理音檔時發生錯誤：{e}")
    
    print("\n" + "=" * 60)
    print("🎉 完成！字幕已產生，臨時檔案已清理")
    print("=" * 60)

if __name__ == "__main__":
    main()
