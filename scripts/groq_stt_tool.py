import os
import sys
import subprocess
import argparse
import glob
import json
from groq import Groq

# Configuration
API_KEY_FILE = "01-system/configs/apis/API-Keys.md"

def get_api_key():
    """Retrieves API key from environment or config file."""
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return api_key
    
    try:
        with open(API_KEY_FILE, "r") as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    return line.split("=", 1)[1].strip()
    except FileNotFoundError:
        pass
    
    print(f"Error: GROQ_API_KEY not found in environment or {API_KEY_FILE}")
    sys.exit(1)

def compress_audio(input_path):
    """Compresses audio to 16kHz mono mp3 using ffmpeg."""
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_compressed.mp3"
    
    print(f"Compressing {input_path} to {output_path}...")
    
    # ffmpeg command: convert to mp3, 1 channel (mono), 16000 Hz sample rate, 64k bitrate
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-map", "0:a", "-ac", "1", "-ar", "16000", "-b:a", "64k",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error compressing audio: {e}")
        sys.exit(1)

def format_timestamp(seconds):
    """Formats seconds into SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_srt(segments):
    """Generates SRT content from segments."""
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
    return srt_content

def transcribe_file(client, audio_path):
    """Transcribes a single audio file."""
    compressed_path = compress_audio(audio_path)
    
    print(f"Transcribing {audio_path}...")
    try:
        with open(compressed_path, "rb") as file:
            # Request verbose_json to get both text and segments
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(compressed_path), file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
                timestamp_granularities=["segment"] # Required for segments
            )
        
        # Cleanup compressed file
        os.remove(compressed_path)
        
        return transcription
    except Exception as e:
        print(f"Error transcribing file: {e}")
        if os.path.exists(compressed_path):
            os.remove(compressed_path)
        sys.exit(1)

def save_file(content, path):
    """Saves content to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved {path}")

def process_single_file(client, input_path):
    """Pipeline for a single file."""
    transcription = transcribe_file(client, input_path)
    
    base, _ = os.path.splitext(input_path)
    
    # Save TXT
    txt_path = f"{base}.txt"
    save_file(transcription.text, txt_path)
    
    # Save SRT
    srt_path = f"{base}.srt"
    srt_content = generate_srt(transcription.segments)
    save_file(srt_content, srt_path)
    
    return transcription.text

def process_project_folder(client, folder_path):
    """Pipeline for a project folder."""
    # Find all audio files
    extensions = ['*.mp3', '*.wav', '*.m4a', '*.mp4', '*.mov', '*.ogg', '*.flac']
    audio_files = []
    for ext in extensions:
        audio_files.extend(glob.glob(os.path.join(folder_path, ext)))
    
    # Sort by filename to ensure order
    audio_files.sort()
    
    if not audio_files:
        print("No audio files found in folder.")
        return

    combined_text = "# Project Transcription\n\n"
    
    for audio_file in audio_files:
        print(f"Processing {audio_file}...")
        text = process_single_file(client, audio_file)
        
        filename = os.path.basename(audio_file)
        combined_text += f"## {filename}\n\n{text}\n\n"
    
    # Save combined markdown
    md_path = os.path.join(folder_path, "project_compilation.md")
    save_file(combined_text, md_path)

def main():
    parser = argparse.ArgumentParser(description="Groq STT Tool")
    parser.add_argument("--input", required=True, help="Input file or folder path")
    parser.add_argument("--mode", choices=["single", "project"], required=True, help="Mode: single file or project folder")
    
    args = parser.parse_args()
    
    api_key = get_api_key()
    client = Groq(api_key=api_key)
    
    if args.mode == "single":
        if os.path.isfile(args.input):
            process_single_file(client, args.input)
        else:
            print("Error: Input must be a file for single mode.")
    elif args.mode == "project":
        if os.path.isdir(args.input):
            process_project_folder(client, args.input)
        else:
            print("Error: Input must be a directory for project mode.")

if __name__ == "__main__":
    main()
