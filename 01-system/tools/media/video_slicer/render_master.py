#!/usr/bin/env python3
"""
Render Master - 輸出無損原畫質影片
用途: 讀取 Proxy 階段產生的 clips.json，輸出 Master 級無損影片
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parents[4]))

from clip_extractor import VideoSlicer

def load_clips(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_original_video(video_name, search_paths):
    """嘗試尋找原始影片檔案"""
    extensions = ['.mp4', '.MP4', '.mov', '.MOV', '.mkv', '.MKV']
    
    for path in search_paths:
        path = Path(path)
        if not path.exists(): continue
        
        # 直接檢查檔名
        for ext in extensions:
            video_file = path / f"{video_name}{ext}"
            if video_file.exists():
                return str(video_file)
        
        # 遞迴搜尋 (如果 path 是資料夾)
        if path.is_dir():
            for ext in extensions:
                results = list(path.rglob(f"{video_name}{ext}"))
                if results:
                    return str(results[0])
                    
    return None

def main():
    parser = argparse.ArgumentParser(description="Render Master Clips")
    parser.add_argument("--input", required=True, help="輸入目錄 (包含 clips.json 的資料夾)")
    parser.add_argument("--indices", help="指定要輸出的片段編號 (例如: 1,3,5)，預設為全部")
    parser.add_argument("--video-dir", default="/Users/xiangyun/Desktop", help="原始影片搜尋目錄")
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    json_path = input_dir / "clips.json"
    
    if not json_path.exists():
        print(f"❌ 錯誤: 找不到 {json_path}")
        sys.exit(1)
        
    print(f"📖 讀取剪輯資訊: {json_path}")
    clips = load_clips(json_path)
    
    # 篩選片段
    if args.indices:
        indices = [int(i.strip()) for i in args.indices.split(',')]
        selected_clips = [c for i, c in enumerate(clips, 1) if i in indices]
        print(f"🎯 已選擇 {len(selected_clips)} 個片段 (編號: {args.indices})")
    else:
        selected_clips = clips
        print(f"🎯 選擇全部 {len(selected_clips)} 個片段")
        
    # 尋找原始影片
    # 假設 input_dir 是 .../video_name/previews/
    # 則 video_name 是 input_dir.parent.name
    video_name = input_dir.parent.name
    
    print(f"🔍 正在尋找原始影片: {video_name}...")
    original_video = find_original_video(video_name, [args.video_dir, "/Volumes/Samsung-T7"])
    
    if not original_video:
        # 嘗試從 input_dir 往上找
        original_video = find_original_video(video_name, [input_dir.parents[2]])
        
    if not original_video:
        print(f"❌ 錯誤: 找不到原始影片 {video_name}")
        print(f"請使用 --video-dir 指定原始影片所在目錄")
        sys.exit(1)
        
    print(f"✅ 找到原始影片: {original_video}")
    
    # 準備輸出目錄
    master_dir = input_dir.parent / "masters"
    master_dir.mkdir(exist_ok=True)
    
    # 開始輸出
    slicer = VideoSlicer()
    print(f"🚀 開始輸出 Master 影片...")
    slicer.slice_video(original_video, selected_clips, str(master_dir), mode="master")
    
    print(f"🎉 輸出完成！檔案位於: {master_dir}")

if __name__ == "__main__":
    main()
