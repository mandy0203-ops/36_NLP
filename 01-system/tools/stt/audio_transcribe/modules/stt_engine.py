"""
STT Engine Module - 雙引擎支援 (ElevenLabs + Groq)
"""
import os
import sys
import subprocess
import glob
import json
from datetime import datetime
from pathlib import Path

class STTEngine:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.api_keys = self._load_api_keys()
        
    def _load_config(self, path):
        import yaml
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_api_keys(self):
        """從 API-Keys.md 讀取 API Keys"""
        keys_file = Path(__file__).parents[4] / "configs/apis/API-Keys.md"
        keys = {}
        
        with open(keys_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    keys['groq'] = line.split("=", 1)[1].strip()
                elif line.startswith("ELEVENLABS_API_KEY="):
                    keys['elevenlabs'] = line.split("=", 1)[1].strip()
        
        return keys
    
    def get_available_engines(self):
        """取得可用引擎及其狀態"""
        engines = {}
        
        # ElevenLabs
        engines['elevenlabs'] = {
            'name': 'ElevenLabs Scribe v1',
            'available': 'elevenlabs' in self.api_keys,
            'quota': self.config['engines']['elevenlabs']['monthly_quota'],
            'pros': ['更準確', '支援大檔案', '無需分割'],
            'cons': ['免費版不可商用', f"每月限制 {self.config['engines']['elevenlabs']['monthly_quota']} 分鐘"]
        }
        
        # Groq
        engines['groq'] = {
            'name': 'Groq Whisper-large-v3',
            'available': 'groq' in self.api_keys,
            'quota': self.config['engines']['groq']['hourly_quota'],
            'pros': ['速度快', '可商用'],
            'cons': ['大檔案需分割', '可能遇到速率限制']
        }
        
        return engines
    
    def compress_audio(self, input_path, aggressive=False):
        """壓縮音檔"""
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed.mp3"
        
        # 根據檔案大小選擇壓縮參數
        file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        
        if file_size_mb >= 20 or aggressive:
            # 大檔案：激進壓縮
            params = self.config['compression']['large_file']
        else:
            # 小檔案：標準壓縮
            params = self.config['compression']['small_file']
        
        print(f"壓縮中... ({file_size_mb:.1f} MB)")
        
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-map", "0:a", "-ac", str(params['channels']),
            "-ar", str(params['sample_rate']), "-b:a", params['bitrate'],
            output_path
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    
    def transcribe_elevenlabs(self, audio_path):
        """使用 ElevenLabs Scribe 轉錄"""
        try:
            from elevenlabs import ElevenLabs
        except ImportError:
            print("錯誤：未安裝 elevenlabs 套件")
            print("請執行：pip install elevenlabs")
            sys.exit(1)
        
        client = ElevenLabs(api_key=self.api_keys['elevenlabs'])
        
        print(f"使用 ElevenLabs Scribe 轉錄中...")
        
        with open(audio_path, "rb") as f:
            response = client.speech_to_text.convert(
                file=f,
                model_id="scribe_v1",
                language_code="zh",  # 繁體中文
                diarize=True,  # 啟用說話者識別
                timestamps_granularity="word"  # 詞級時間戳
            )
        
        # 轉換為統一格式
        result = {
            'text': response.text,
            'segments': []
        }
        
        # 處理 segments
        if hasattr(response, 'words'):
            current_segment = {'start': 0, 'end': 0, 'text': ''}
            for word in response.words:
                if word.start is not None:
                    current_segment['start'] = word.start
                if word.end is not None:
                    current_segment['end'] = word.end
                current_segment['text'] += word.text
                
                # 每 10 個詞或遇到停頓就分段
                if len(current_segment['text'].split()) >= 10:
                    result['segments'].append(current_segment.copy())
                    current_segment = {'start': word.end or 0, 'end': word.end or 0, 'text': ''}
            
            if current_segment['text']:
                result['segments'].append(current_segment)
        
        return result
    
    def transcribe_groq(self, audio_path):
        """使用 Groq Whisper 轉錄（支援大檔案分割）"""
        try:
            from groq import Groq
        except ImportError:
            print("錯誤：未安裝 groq 套件")
            print("請執行：pip install groq")
            sys.exit(1)
        
        client = Groq(api_key=self.api_keys['groq'])
        compressed_path = self.compress_audio(audio_path)
        
        file_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
        
        if file_size_mb < 24:
            # 小檔案：直接轉錄
            print(f"使用 Groq Whisper 轉錄中... ({file_size_mb:.1f} MB)")
            result = self._transcribe_groq_single(client, compressed_path)
            os.remove(compressed_path)
            return result
        else:
            # 大檔案：分割轉錄
            print(f"檔案較大 ({file_size_mb:.1f} MB)，分割處理中...")
            result = self._transcribe_groq_chunked(client, compressed_path)
            os.remove(compressed_path)
            return result
    
    def _transcribe_groq_single(self, client, audio_path):
        """Groq 單檔轉錄"""
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), file.read()),
                model="whisper-large-v3",
                prompt="繁體中文",
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        return {
            'text': transcription.text,
            'segments': transcription.segments
        }
    
    def _transcribe_groq_chunked(self, client, audio_path):
        """Groq 分割轉錄"""
        chunks = self._split_audio(audio_path)
        
        full_text = ""
        all_segments = []
        time_offset = 0.0
        
        for i, chunk in enumerate(chunks, 1):
            print(f"轉錄片段 {i}/{len(chunks)}...")
            
            # 重試邏輯
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
                    break
                except Exception as e:
                    if "429" in str(e):
                        import time
                        wait_time = 60 * (attempt + 1)
                        print(f"速率限制，等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                    else:
                        raise
            
            full_text += transcription.text + " "
            
            # 調整時間戳
            for segment in transcription.segments:
                segment['start'] += time_offset
                segment['end'] += time_offset
                all_segments.append(segment)
            
            duration = self._get_duration(chunk)
            time_offset += duration
            os.remove(chunk)
        
        return {
            'text': full_text.strip(),
            'segments': all_segments
        }
    
    def _split_audio(self, input_path):
        """分割音檔"""
        base, ext = os.path.splitext(input_path)
        output_pattern = f"{base}_part%03d{ext}"
        segment_time = self.config['engines']['groq']['chunk_duration']
        
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-f", "segment", "-segment_time", str(segment_time),
            "-c", "copy", output_pattern
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return sorted(glob.glob(f"{base}_part*{ext}"))
    
    def _get_duration(self, file_path):
        """取得音檔長度"""
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    
    def transcribe(self, audio_path, engine):
        """統一的轉錄介面"""
        if engine == "elevenlabs":
            return self.transcribe_elevenlabs(audio_path)
        elif engine == "groq":
            return self.transcribe_groq(audio_path)
        else:
            raise ValueError(f"未知的引擎: {engine}")
