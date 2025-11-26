#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse

def download_video(url, output_dir):
    """
    Downloads a YouTube video using yt-dlp.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the command
    # -P: Set download path
    # -o: Output template
    # --write-subs: Download subtitles
    # --write-auto-subs: Download auto-generated subtitles if no manual ones
    # --sub-lang: Preferred subtitle languages (en, zh-Hant, zh-Hans)
    cmd = [
        "yt-dlp",
        "-P", output_dir,
        "-o", "%(title)s.%(ext)s",
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[ext=mp4]",
        "--merge-output-format", "mp4",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "en,zh-Hant,zh-Hans",
        url
    ]

    print(f"Starting download for: {url}")
    print(f"Output directory: {output_dir}")
    
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("Download completed successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error occurred during download:")
        print(e.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos and subtitles.")
    parser.add_argument("url", help="The YouTube video URL to download")
    args = parser.parse_args()

    # Define output directory relative to the workspace root
    # 03-outputs/youtube_downloader/downloads/
    # We assume the script is run from the workspace root or we find the root relative to this script
    # This script is in 01-system/tools/media/youtube_downloader/
    # So workspace root is ../../../../
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.abspath(os.path.join(script_dir, "../../../../"))
    output_dir = os.path.join(workspace_root, "03-outputs", "下載存檔")
    
    download_video(args.url, output_dir)

if __name__ == "__main__":
    main()
