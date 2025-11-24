"""
Output Manager Module - 管理輸出資料夾和檔案
"""
import os
import shutil
import yaml
from datetime import datetime
from pathlib import Path

class OutputManager:
    def __init__(self, config):
        self.config = config
        self.base_dir = Path(config['output']['base_dir'])
    
    def create_output_folder(self, audio_name, custom_name=None):
        """創建輸出資料夾"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 決定資料夾名稱
        if custom_name:
            folder_name = custom_name
        elif self.config['output']['folder_naming'] == 'filename_timestamp':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{audio_name}_{timestamp}"
        else:
            folder_name = audio_name
        
        folder_path = self.base_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return folder_path
    
    def handle_audio(self, audio_path, output_folder):
        """處理原始音檔（複製/移動/連結）"""
        mode = self.config['output']['audio_handling']
        audio_name = Path(audio_path).name
        dest_path = output_folder / audio_name
        
        if mode == 'copy':
            shutil.copy2(audio_path, dest_path)
        elif mode == 'move':
            shutil.move(audio_path, dest_path)
        elif mode == 'link':
            # 只記錄路徑，不複製檔案
            return audio_path
        
        return dest_path
    
    def save_transcription(self, folder, basename, transcription, formatted_text=None):
        """儲存轉錄結果"""
        files = {}
        
        # 原始 TXT
        txt_path = folder / f"{basename}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(transcription['text'])
        files['txt_original'] = txt_path
        
        # 原始 SRT
        srt_path = folder / f"{basename}.srt"
        srt_content = self._generate_srt(transcription['segments'])
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        files['srt_original'] = srt_path
        
        # 格式化版本（如果有）
        if formatted_text:
            txt_formatted_path = folder / f"{basename}_formatted.txt"
            with open(txt_formatted_path, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            files['txt_formatted'] = txt_formatted_path
        
        return files
    
    def save_formatted_srt(self, folder, basename, formatted_srt):
        """儲存格式化的 SRT"""
        srt_formatted_path = folder / f"{basename}_formatted.srt"
        with open(srt_formatted_path, 'w', encoding='utf-8') as f:
            f.write(formatted_srt)
        return srt_formatted_path
    
    def generate_metadata(self, folder, info):
        """生成 metadata.yaml"""
        metadata_path = folder / "_metadata.yaml"
        
        metadata = {
            'transcription': {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'engine': info.get('engine'),
                'model': info.get('model'),
            },
            'source': {
                'original_file': str(info.get('original_file')),
                'file_size': info.get('file_size'),
                'duration': info.get('duration'),
            },
            'processing': {
                'compression': info.get('compression'),
                'formatting_applied': info.get('formatting_applied', False),
                'custom_dict_used': info.get('custom_dict_used', False),
            },
            'output': info.get('output_files', {})
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, allow_unicode=True, default_flow_style=False)
        
        return metadata_path
    
    def _generate_srt(self, segments):
        """生成基本 SRT（未格式化）"""
        srt_content = ""
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment['start'])
            end = self._format_timestamp(segment['end'])
            text = segment['text'].strip()
            srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
        return srt_content
    
    def _format_timestamp(self, seconds):
        """格式化時間戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
