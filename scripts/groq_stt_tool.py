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

def get_duration(file_path):
    """Gets audio duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 0

def split_audio(input_path, segment_time=600):
    """Splits audio into chunks using ffmpeg."""
    base, ext = os.path.splitext(input_path)
    output_pattern = f"{base}_part%03d{ext}"
    
    print(f"Splitting {input_path} into {segment_time}s chunks...")
    
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-f", "segment", "-segment_time", str(segment_time),
        "-c", "copy", output_pattern
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return sorted(glob.glob(f"{base}_part*{ext}"))
    except subprocess.CalledProcessError as e:
        print(f"Error splitting audio: {e}")
        sys.exit(1)

def transcribe_file(client, audio_path):
    """Transcribes a single audio file, handling large files by splitting."""
    compressed_path = compress_audio(audio_path)
    
    # Check file size (Groq limit is ~25MB)
    file_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
    
    if file_size_mb < 24:
        # Process normally
        print(f"Transcribing {audio_path} ({file_size_mb:.2f} MB)...")
        try:
            with open(compressed_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(compressed_path), file.read()),
                    model="whisper-large-v3",
                    prompt="繁體中文",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            os.remove(compressed_path)
            return transcription
        except Exception as e:
            print(f"Error transcribing file: {e}")
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
            sys.exit(1)
    
    else:
        # Split and process
        print(f"File too large ({file_size_mb:.2f} MB). Splitting...")
        chunks = split_audio(compressed_path, segment_time=600) # 10 min chunks
        
        full_text = ""
        all_segments = []
        time_offset = 0.0
        
        for chunk in chunks:
            print(f"Transcribing chunk {chunk}...")
            
            max_retries = 10
            for attempt in range(max_retries):
                try:
                    with open(chunk, "rb") as file:
                        transcription = client.audio.transcriptions.create(
                            file=(os.path.basename(chunk), file.read()),
                            model="whisper-large-v3",
                            prompt="繁體中文",
                            response_format="verbose_json",
                            timestamp_granularities=["segment"]
                        )
                    break # Success, exit retry loop
                except Exception as e:
                    if "429" in str(e):
                        wait_time = 60 * (attempt + 1)
                        print(f"Rate limit hit (429). Waiting {wait_time}s before retry {attempt+1}/{max_retries}...")
                        import time
                        time.sleep(wait_time)
                    else:
                        print(f"Error transcribing chunk {chunk}: {e}")
                        # Cleanup remaining chunks
                        for c in chunks:
                            if os.path.exists(c):
                                os.remove(c)
                        if os.path.exists(compressed_path):
                            os.remove(compressed_path)
                        sys.exit(1)
            else:
                # Failed after retries
                print(f"Failed to transcribe chunk {chunk} after {max_retries} retries.")
                sys.exit(1)
                
            full_text += transcription.text + " "
            
            # Adjust timestamps
            for segment in transcription.segments:
                segment['start'] += time_offset
                segment['end'] += time_offset
                all_segments.append(segment)
            
            # Update offset
            duration = get_duration(chunk)
            time_offset += duration
            
            os.remove(chunk)
        
        os.remove(compressed_path)
        
        # Create a mock object to match the expected return structure
        class TranscriptionResult:
            def __init__(self, text, segments):
                self.text = text
                self.segments = segments
        
        return TranscriptionResult(full_text.strip(), all_segments)

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
