#!/usr/bin/env python3
"""
批次課程影片處理器
功能: 自動提取音訊 → STT 轉錄 → AI 切片
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class CourseVideoProcessor:
    def __init__(self, input_dir, output_dir, stt_engine="groq", slice_mode="proxy"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.stt_engine = stt_engine
        self.slice_mode = slice_mode
        
        # 工作目錄
        self.audio_dir = Path("02-inputs/1116_audio")
        self.transcripts_dir = Path("03-outputs/transcriptions")
        self.highlights_dir = Path(output_dir)
        
        # 創建目錄
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.highlights_dir.mkdir(parents=True, exist_ok=True)
        
        # 工具路徑
        self.project_root = Path.cwd()
        self.stt_tool = self.project_root / "01-system/tools/stt/audio_transcribe/transcribe.py"
        self.slicer_tool = self.project_root / "01-system/tools/media/video_slicer/clip_extractor.py"
        
        # 進度追蹤
        self.progress_file = self.output_dir / "processing_progress.json"
        self.load_progress()
    
    def load_progress(self):
        """載入處理進度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "completed": [],
                "failed": [],
                "current": None,
                "started_at": datetime.now().isoformat()
            }
    
    def save_progress(self):
        """儲存處理進度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def get_video_files(self):
        """取得所有影片檔案"""
        videos = sorted(self.input_dir.glob("*.MP4"))
        print(f"📹 找到 {len(videos)} 個影片檔案")
        for i, video in enumerate(videos, 1):
            size_gb = video.stat().st_size / (1024**3)
            print(f"   {i}. {video.name} ({size_gb:.1f}GB)")
        return videos
    
    def extract_audio(self, video_path):
        """提取並壓縮音訊"""
        audio_path = self.audio_dir / f"{video_path.stem}_audio.mp3"
        
        if audio_path.exists():
            print(f"   ✅ 音訊已存在: {audio_path.name}")
            return audio_path
        
        print(f"   🎵 提取音訊: {video_path.name}")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",  # 不要視訊
            "-acodec", "libmp3lame",
            "-ar", "16000",  # 16kHz 採樣率
            "-ab", "64k",    # 64kbps 位元率
            str(audio_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            size_mb = audio_path.stat().st_size / (1024**2)
            print(f"   ✅ 音訊提取完成: {audio_path.name} ({size_mb:.1f}MB)")
            return audio_path
        except subprocess.CalledProcessError as e:
            print(f"   ❌ 音訊提取失敗: {e}")
            return None
    
    def transcribe_audio(self, audio_path):
        """使用 STT 轉錄音訊"""
        print(f"   🎙️  開始轉錄: {audio_path.name}")
        
        # 執行轉錄工具
        cmd = [
            "python3", str(self.stt_tool),
            "--input", str(audio_path),
            "--engine", self.stt_engine
        ]
        
        try:
            # 使用 Popen 來即時顯示輸出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 即時顯示輸出
            for line in process.stdout:
                print(f"      {line.rstrip()}")
            
            process.wait()
            
            if process.returncode == 0:
                # 找到生成的 SRT 檔案 - 搜尋整個 03-outputs 目錄
                output_base = Path("03-outputs")
                srt_files = list(output_base.glob(f"**/*{audio_path.stem}*.srt"))
                
                # 優先使用 formatted.srt,否則使用 original.srt
                formatted_srt = [f for f in srt_files if "formatted" in f.name]
                original_srt = [f for f in srt_files if "original" in f.name or "formatted" not in f.name]
                
                if formatted_srt:
                    srt_path = formatted_srt[0]
                    print(f"   ✅ 轉錄完成: {srt_path}")
                    return srt_path
                elif original_srt:
                    srt_path = original_srt[0]
                    print(f"   ✅ 轉錄完成: {srt_path}")
                    return srt_path
                else:
                    print(f"   ⚠️  找不到 SRT 檔案")
                    print(f"   搜尋路徑: {output_base}/**/*{audio_path.stem}*.srt")
                    return None
            else:
                print(f"   ❌ 轉錄失敗 (exit code: {process.returncode})")
                return None
                
        except Exception as e:
            print(f"   ❌ 轉錄失敗: {e}")
            return None
    
    def slice_video(self, video_path, srt_path):
        """使用挑片大師切片"""
        print(f"   ✂️  開始切片: {video_path.name}")
        
        output_subdir = self.highlights_dir / video_path.stem
        output_subdir.mkdir(exist_ok=True)
        
        cmd = [
            "python3", str(self.slicer_tool),
            "--video", str(video_path),
            "--srt", str(srt_path),
            "--output", str(output_subdir),
            "--mode", self.slice_mode
        ]
        
        try:
            # 使用 Popen 來即時顯示輸出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 即時顯示輸出
            for line in process.stdout:
                print(f"      {line.rstrip()}")
            
            process.wait()
            
            if process.returncode == 0:
                # 統計切片數量
                clips = list(output_subdir.glob("*.mp4"))
                print(f"   ✅ 切片完成: 產生 {len(clips)} 個片段")
                return True
            else:
                print(f"   ❌ 切片失敗 (exit code: {process.returncode})")
                return False
                
        except Exception as e:
            print(f"   ❌ 切片失敗: {e}")
            return False
    
    def process_video(self, video_path):
        """處理單一影片的完整流程"""
        video_name = video_path.name
        
        # 檢查是否已處理
        if video_name in self.progress["completed"]:
            print(f"⏭️  跳過已完成: {video_name}")
            return True
        
        print(f"\n{'='*60}")
        print(f"🎬 處理影片: {video_name}")
        print(f"{'='*60}")
        
        self.progress["current"] = video_name
        self.save_progress()
        
        # Step 1: 提取音訊
        audio_path = self.extract_audio(video_path)
        if not audio_path:
            self.progress["failed"].append({
                "video": video_name,
                "stage": "audio_extraction",
                "time": datetime.now().isoformat()
            })
            self.save_progress()
            return False
        
        # Step 2: STT 轉錄
        srt_path = self.transcribe_audio(audio_path)
        if not srt_path:
            self.progress["failed"].append({
                "video": video_name,
                "stage": "transcription",
                "time": datetime.now().isoformat()
            })
            self.save_progress()
            return False
        
        # Step 3: AI 切片
        success = self.slice_video(video_path, srt_path)
        if success:
            self.progress["completed"].append(video_name)
            print(f"✅ {video_name} 處理完成!")
        else:
            self.progress["failed"].append({
                "video": video_name,
                "stage": "slicing",
                "time": datetime.now().isoformat()
            })
        
        self.progress["current"] = None
        self.save_progress()
        return success
    
    def process_all(self):
        """處理所有影片"""
        videos = self.get_video_files()
        total = len(videos)
        
        print(f"\n🚀 開始批次處理 {total} 個影片")
        print(f"   STT 引擎: {self.stt_engine}")
        print(f"   切片模式: {self.slice_mode}")
        print(f"   輸出目錄: {self.highlights_dir}\n")
        
        for i, video in enumerate(videos, 1):
            print(f"\n📊 進度: {i}/{total}")
            self.process_video(video)
        
        # 最終報告
        print(f"\n{'='*60}")
        print(f"🎉 批次處理完成!")
        print(f"{'='*60}")
        print(f"✅ 成功: {len(self.progress['completed'])} 個")
        print(f"❌ 失敗: {len(self.progress['failed'])} 個")
        
        if self.progress['failed']:
            print(f"\n失敗清單:")
            for fail in self.progress['failed']:
                print(f"   - {fail['video']} (階段: {fail['stage']})")
        
        print(f"\n📁 所有切片已儲存至: {self.highlights_dir}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="批次處理課程影片")
    parser.add_argument("--input", required=True, help="影片資料夾路徑")
    parser.add_argument("--output", default="03-outputs/1116_highlights", help="輸出資料夾")
    parser.add_argument("--stt", default="groq", choices=["groq", "elevenlabs"], help="STT 引擎")
    parser.add_argument("--mode", default="proxy", choices=["proxy", "master"], help="切片模式")
    args = parser.parse_args()
    
    processor = CourseVideoProcessor(
        input_dir=args.input,
        output_dir=args.output,
        stt_engine=args.stt,
        slice_mode=args.mode
    )
    
    processor.process_all()

if __name__ == "__main__":
    main()
