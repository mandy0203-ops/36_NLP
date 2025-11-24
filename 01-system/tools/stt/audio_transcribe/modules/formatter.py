"""
Formatter Module - 實作 5 大格式化規則
"""
import re
import yaml
from pathlib import Path

class Formatter:
    def __init__(self, rules_path="formatting_rules.yaml", dict_path="custom_dict.yaml"):
        self.rules = self._load_rules(rules_path)
        self.custom_dict = self._load_dict(dict_path)
    
    def _load_rules(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_dict(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('replacements', [])
    
    def format_text(self, text):
        """套用所有格式化規則"""
        # 規則 1: 清洗口水詞
        text = self.clean_fillers(text)
        
        # 規則 2: 停頓替換
        text = self.apply_pause_spacing(text)
        
        # 規則 5: 風格統一
        text = self.unify_style(text)
        
        # 套用自訂詞典
        text = self.apply_custom_dict(text)
        
        return text
    
    def clean_fillers(self, text):
        """規則 1: 清洗口水詞"""
        for filler in self.rules['filler_words']:
            # 移除獨立的口水詞
            text = re.sub(rf'\b{re.escape(filler)}\b', '', text)
            # 移除句尾的口水詞（如「所以呢」中的「呢」）
            text = re.sub(rf'{re.escape(filler)}(?=[，。！？、])', '', text)
        
        return text
    
    def apply_pause_spacing(self, text):
        """規則 2: 用雙空格替換停頓"""
        pause = self.rules['pause_replacement']
        
        # 移除所有標點（除了書名號）
        text = re.sub(r'[，。！？、：；]', pause, text)
        
        # 清理多餘空格
        text = re.sub(r' {3,}', pause, text)
        
        return text.strip()
    
    def smart_break_sentences(self, text, max_chars=18):
        """規則 3+4: 智能斷句（18字限制）"""
        sentences = []
        current = ""
        
        # 按雙空格分割
        parts = text.split('  ')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 如果加上這部分會超過限制
            if len(current) + len(part) > max_chars:
                if current:
                    sentences.append(current.strip())
                current = part
            else:
                current += "  " + part if current else part
        
        if current:
            sentences.append(current.strip())
        
        return sentences
    
    def unify_style(self, text):
        """規則 5: 風格統一"""
        # 英文縮寫大寫
        for acronym in self.rules['style_rules']['acronyms']:
            text = re.sub(rf'\b{re.escape(acronym.lower())}\b', acronym, text, flags=re.IGNORECASE)
        
        # 數字轉阿拉伯數字（這裡簡化處理）
        # 實際應用可能需要更複雜的中文數字轉換
        
        return text
    
    def apply_custom_dict(self, text):
        """套用自訂詞典"""
        for entry in self.custom_dict:
            wrong_list = entry.get('wrong', [])
            correct = entry.get('correct', '')
            
            for wrong in wrong_list:
                text = text.replace(wrong, correct)
        
        return text
    
    def format_srt(self, segments):
        """將 segments 格式化為 SRT"""
        srt_content = ""
        
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment['start'])
            end = self._format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            # 格式化文字
            text = self.format_text(text)
            
            # 斷句
            lines = self.smart_break_sentences(text)
            
            # 每個斷句成為一個字幕條目
            for line in lines:
                srt_content += f"{i}\n{start} --> {end}\n{line}\n\n"
        
        return srt_content
    
    def _format_timestamp(self, seconds):
        """格式化時間戳為 SRT 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
