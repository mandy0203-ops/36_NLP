import os
import sys
import subprocess
import argparse
import glob
import time
import requests
import json

# Configuration
API_KEY_FILE = "01-system/configs/apis/API-Keys.md"
BASE_URL = "https://api.elevenlabs.io/v1/speech-to-text"

def get_api_key():
    """Retrieves API key from environment or config file."""
    api_key = os.environ.get("XI_API_KEY")
    if api_key:
        return api_key
    
    try:
        with open(API_KEY_FILE, "r") as f:
            for line in f:
                if line.startswith("XI_API_KEY="):
                    return line.split("=", 1)[1].strip()
    except FileNotFoundError:
        pass
    
    print(f"Error: XI_API_KEY not found in environment or {API_KEY_FILE}")
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
    if seconds is None:
        return "00:00:00,000"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_srt(words):
    """Generates SRT content from word-level timestamps."""
    # Scribe v1 returns words. We can group them into sentences or chunks for SRT.
    # For simplicity, we'll group by roughly 10 words or punctuation.
    # However, Scribe v1 output structure might differ. 
    # Based on docs, it returns 'words' list.
    
    srt_content = ""
    chunk = []
    chunk_start = None
    chunk_end = None
    counter = 1
    
    for word_obj in words:
        text = word_obj.get('text', '')
        start = word_obj.get('start')
        end = word_obj.get('end')
        
        if chunk_start is None:
            chunk_start = start
        
        chunk.append(text)
        chunk_end = end
        
        # Simple heuristic: split on punctuation or length
        if text.strip() in ['.', '?', '!', '。', '？', '！'] or len(chunk) > 10:
            srt_content += f"{counter}\n{format_timestamp(chunk_start)} --> {format_timestamp(chunk_end)}\n{' '.join(chunk)}\n\n"
            counter += 1
            chunk = []
            chunk_start = None
            chunk_end = None
            
    if chunk:
        srt_content += f"{counter}\n{format_timestamp(chunk_start)} --> {format_timestamp(chunk_end)}\n{' '.join(chunk)}\n\n"
        
    return srt_content

def transcribe_file(api_key, audio_path):
    """Transcribes a single audio file using ElevenLabs Scribe v1."""
    compressed_path = compress_audio(audio_path)
    
    print(f"Uploading {audio_path} to ElevenLabs Scribe v1...")
    
    headers = {
        "xi-api-key": api_key
    }
    
    try:
        with open(compressed_path, "rb") as file:
            files = {
                "file": (os.path.basename(compressed_path), file, "audio/mpeg")
            }
            data = {
                "model_id": "scribe_v1",
                "tag_audio_events": "true",
                "diarize": "true",
                "timestamps_granularity": "word"
            }
            
            response = requests.post(BASE_URL, headers=headers, files=files, data=data)
            
        if response.status_code != 200:
            print(f"Error submitting transcription: {response.status_code} - {response.text}")
            sys.exit(1)
            
        transcription_id = response.json().get("transcription_id")
        if not transcription_id:
             # Some versions might return result immediately if small? 
             # But docs say it returns transcription_id usually or we might need to poll?
             # Actually, the POST endpoint might return the result immediately for short files 
             # OR return an ID. The docs I found said "Asynchronous".
             # Let's assume we might need to poll if we get an ID, or we get the result.
             # If the response contains 'text', it's done.
             resp_json = response.json()
             if 'text' in resp_json:
                 return resp_json
             else:
                 print("No transcription_id or text returned.")
                 sys.exit(1)

        print(f"Transcription ID: {transcription_id}. Polling for results...")
        
        # Poll for results
        while True:
            poll_url = f"{BASE_URL}/transcripts/{transcription_id}"
            poll_response = requests.get(poll_url, headers=headers)
            
            if poll_response.status_code == 200:
                status_data = poll_response.json()
                # Check status - the API might return the full object when done.
                # If it has 'status' field, check it. If it looks like a result (has 'text'), it's done.
                if 'status' in status_data:
                     if status_data['status'] == 'completed':
                         return status_data
                     elif status_data['status'] == 'failed':
                         print("Transcription failed.")
                         sys.exit(1)
                     else:
                         print(f"Status: {status_data.get('status')}...")
                else:
                    # If no status field, assume it's the result
                    return status_data
            elif poll_response.status_code != 200:
                print(f"Error polling: {poll_response.status_code}")
            
            time.sleep(2)
            
    except Exception as e:
        print(f"Error transcribing file: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(compressed_path):
            os.remove(compressed_path)

def save_file(content, path):
    """Saves content to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved {path}")

def process_single_file(api_key, input_path):
    """Pipeline for a single file."""
    result = transcribe_file(api_key, input_path)
    
    base, _ = os.path.splitext(input_path)
    
    # Save TXT
    txt_path = f"{base}.txt"
    text = result.get('text', '')
    save_file(text, txt_path)
    
    # Save SRT
    # Scribe v1 returns 'words' list in the response
    words = result.get('words', [])
    if words:
        srt_path = f"{base}.srt"
        srt_content = generate_srt(words)
        save_file(srt_content, srt_path)
    
    return text

def process_project_folder(api_key, folder_path):
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
        text = process_single_file(api_key, audio_file)
        
        filename = os.path.basename(audio_file)
        combined_text += f"## {filename}\n\n{text}\n\n"
    
    # Save combined markdown
    md_path = os.path.join(folder_path, "project_compilation.md")
    save_file(combined_text, md_path)

def main():
    parser = argparse.ArgumentParser(description="ElevenLabs Scribe v1 Tool")
    parser.add_argument("--input", required=True, help="Input file or folder path")
    parser.add_argument("--mode", choices=["single", "project"], required=True, help="Mode: single file or project folder")
    
    args = parser.parse_args()
    
    api_key = get_api_key()
    
    if args.mode == "single":
        if os.path.isfile(args.input):
            process_single_file(api_key, args.input)
        else:
            print("Error: Input must be a file for single mode.")
    elif args.mode == "project":
        if os.path.isdir(args.input):
            process_project_folder(api_key, args.input)
        else:
            print("Error: Input must be a directory for project mode.")

if __name__ == "__main__":
    main()
