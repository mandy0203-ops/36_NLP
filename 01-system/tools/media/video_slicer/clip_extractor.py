#!/usr/bin/env python3
"""
AI Video Slicer - 智慧影片切片工具 (Class Version)
用途: 讀取字幕檔，利用 LLM 分析精彩片段，並自動切割影片。
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parents[4]))

class VideoSlicer:
    def __init__(self, config_path: str = None, api_key: str = None):
        self.base_dir = Path(__file__).parent
        
        if config_path:
            self.config = self._load_config(config_path)
        else:
            self.config = self._load_config(self.base_dir / "config.yaml")
            
        # Support multiple API keys for rotation
        if api_key:
            self.api_keys = [api_key] if isinstance(api_key, str) else api_key
        else:
            self.api_keys = self._load_api_key(self.config['llm']['provider'])
            
        # Load Style Guide
        self.style_guide = self._load_style_guide(self.base_dir / "style_guide.yaml")

    def _load_style_guide(self, path):
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _load_config(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_api_key(self, provider):
        """Load API keys (supports multiple keys for rotation)"""
        key_file = Path(__file__).parents[4] / "01-system/configs/apis/API-Keys.md"
        if not key_file.exists():
            raise FileNotFoundError(f"錯誤: 找不到 API Key 設定檔: {key_file}")
            
        keys = []
        with open(key_file, 'r', encoding='utf-8') as f:
            for line in f:
                if provider == "gemini" and line.startswith("GEMINI_API_KEY"):
                    key = line.split("=", 1)[1].strip()
                    if key and not key.startswith("sk-..."):  # Skip placeholder
                        keys.append(key)
                elif provider == "openai" and line.startswith("OPENAI_API_KEY"):
                    key = line.split("=", 1)[1].strip()
                    if key and not key.startswith("sk-..."):
                        keys.append(key)
                elif provider == "claude" and line.startswith("ANTHROPIC_API_KEY"):
                    key = line.split("=", 1)[1].strip()
                    if key and not key.startswith("sk-..."):
                        keys.append(key)
        
        if not keys:
            raise ValueError(f"錯誤: 在 {key_file} 中找不到有效的 {provider.upper()}_API_KEY")
        
        # Return all keys for rotation
        return keys

    def parse_srt(self, srt_path):
        """簡單解析 SRT 檔案，回傳純文字內容 (強制轉繁體)"""
        import opencc
        cc = opencc.OpenCC('s2t')  # 簡體轉繁體
        
        text_content = ""
        with open(srt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.isdigit(): continue
            if "-->" in line: continue
            
            # 轉繁體
            line = cc.convert(line)
            text_content += line + " "
            
        return text_content

    def analyze_transcript(self, text):
        """使用 LLM 分析字幕內容 - 主題式切分"""
        print("🤖 AI (內容分析師模式) 正在深度分析字幕...")
        
        provider = self.config['llm']['provider']
        
        if provider == "claude":
            return self._analyze_with_claude(text)
        elif provider == "gemini":
            return self._analyze_with_gemini(text)
        else:
            raise ValueError(f"不支援的 LLM provider: {provider}")
    
    def _analyze_with_claude(self, text):
        """使用 Claude API 分析"""
        from anthropic import Anthropic
        
        # Construct Prompt from Style Guide
        style = self.style_guide
        
        hooks_str = ""
        for hook in style.get('hooks', []):
            hooks_str += f"    *   **{hook['category']}**：\n"
            for ex in hook['examples']:
                hooks_str += f"        - {ex}\n"
                
        constraints_str = "\n".join([f"- {item}" for item in style.get('negative_constraints', {}).get('items', [])])
        positive_str = "\n".join([f"{i+1}. {item}" for i, item in enumerate(style.get('positive_examples', {}).get('items', []))])
        
        prompt = f"""
## 分析目標：行銷短影音素材（Teasers）

我們需要的是「販售課程」的行銷素材。風格參考「{style.get('marketing_strategy', {}).get('style_reference', '傑扣聊溝通')}」。
策略是**「{style.get('marketing_strategy', {}).get('goal', '')}」**。
請找出能引發觀眾「{style.get('marketing_strategy', {}).get('target_audience_feeling', '')}」的完整段落。

## 挑選標準（三要素）

請尋找包含以下任一（或多個）要素的段落：
1.  **痛點 (Pain Points)**：常見的溝通災難。
2.  **鉤子 (Hooks) - 參考爆款邏輯**：
{hooks_str}
3.  **情緒 (Emotion)**：能挑動情緒的段落。

## 關鍵要求：敘事完整性 (Narrative Completeness)

*   **最重要**：每個片段必須是**「有頭有尾的完整敘事」**。
*   **不限時長**：只要故事完整，長度不限（但通常建議在 30秒 到 3分鐘之間）。
*   **結構完整**：必須包含「情境/問題 -> 發展/轉折 -> 暫時的結論/懸念」。不要切在話講一半的地方。

**第二步：主題切分（{style.get('quality_control', {}).get('principle', '寧缺勿濫')}）**
請**最多**挑選 {self.config['clips']['count']} 個「絕對可用」的主題段落。

**核心原則：{style.get('quality_control', {}).get('principle', '寧缺勿濫')}**
*   如果找不到完美的片段，**請回傳較少的數量，甚至不回傳**。
*   不要為了湊數而選擇品質普通的段落。
*   不要選擇敘事不完整、或包含禁語的段落。

每個段落必須：
1. 有明確的開始和結束
2. 包含完整的論述（有前因後果）
3. 能獨立理解，不需要額外上下文
4. 至少 {self.config['clips']['min_topic_duration']} 秒

## 輸出格式

請務必回傳「純 JSON 格式」，格式如下：
[
    {{
        "topic_name": "主題名稱（吸睛標題）",
        "start_text": "片段開始的精確語句（⚠️ 必須完全符合逐字稿，連標點符號都不要改）",
        "end_text": "片段結束的精確語句（⚠️ 必須完全符合逐字稿，連標點符號都不要改）",
        "content_summary": "這段在講什麼？（2-3 句話，具體說明內容）",
        "key_point": "這段的核心重點是什麼？（1 句話）",
        "marketing_angle": "這段符合哪個行銷要素？（痛點/鉤子/情緒）",
        "narrative_check": "這段的故事是否完整？（是/否）",
        "why_selected": "為什麼這段適合做行銷素材？",
        "estimated_duration": 120
    }}
]

## 重要提醒

⚠️ **絕對禁止**：
1. 禁止捏造逐字稿中沒有的句子
2. 禁止修改原文
3. **禁止切到一半**（這是最嚴重的錯誤，務必確保語意結束）
4. 禁止選擇平淡無奇的過場

⛔️ **核心內容迴避（行銷用途，勿洩漏付費乾貨）**：
請避開包含以下「課程核心專有名詞」的段落，除非是純故事分享或引發好奇的提問：
{constraints_str}

✅ **優先選擇**：
{positive_str}

## 逐字稿內容

{text[:100000]}"""
        
        # Try each API key until one works
        for i, api_key in enumerate(self.api_keys, 1):
            try:
                client = Anthropic(api_key=api_key)
                print(f"   嘗試 API Key #{i}...")
                
                message = client.messages.create(
                    model=self.config['llm']['model'],
                    max_tokens=8192,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                json_str = message.content[0].text.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:-3]
                elif json_str.startswith("```"):
                    json_str = json_str[3:-3]
                    
                print(f"   ✅ API Key #{i} 成功")
                return json.loads(json_str)
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "rate_limit" in error_msg.lower():
                    print(f"   ⚠️  API Key #{i} 達到速率限制")
                    if i < len(self.api_keys):
                        print(f"   🔄 切換到下一個 Key...")
                        continue
                else:
                    print(f"   ❌ API Key #{i} 發生錯誤: {e}")
                    if i < len(self.api_keys):
                        continue
        
        print("❌ LLM 分析失敗: 所有 API Keys 都無法使用")
        return []
    
    def _analyze_with_gemini(self, text):
        """使用 Gemini API 分析"""
        import google.generativeai as genai
        
        model = genai.GenerativeModel(self.config['llm']['model'])
        
        # Construct Prompt from Style Guide
        style = self.style_guide
        
        hooks_str = ""
        for hook in style.get('hooks', []):
            hooks_str += f"    *   **{hook['category']}**：\n"
            for ex in hook['examples']:
                hooks_str += f"        - {ex}\n"
                
        constraints_str = "\n".join([f"- {item}" for item in style.get('negative_constraints', {}).get('items', [])])
        positive_str = "\n".join([f"{i+1}. {item}" for i, item in enumerate(style.get('positive_examples', {}).get('items', []))])
        
        prompt = f"""
        ## 分析目標：行銷短影音素材（Teasers）

        我們需要的是「販售課程」的行銷素材。風格參考「{style.get('marketing_strategy', {}).get('style_reference', '傑扣聊溝通')}」。
        策略是**「{style.get('marketing_strategy', {}).get('goal', '')}」**。
        請找出能引發觀眾「{style.get('marketing_strategy', {}).get('target_audience_feeling', '')}」的完整段落。

        ## 挑選標準（三要素）

        請尋找包含以下任一（或多個）要素的段落：
        1.  **痛點 (Pain Points)**：常見的溝通災難。
        2.  **鉤子 (Hooks) - 參考爆款邏輯**：
        {hooks_str}
        3.  **情緒 (Emotion)**：能挑動情緒的段落。

        ## 關鍵要求：敘事完整性 (Narrative Completeness)

        *   **最重要**：每個片段必須是**「有頭有尾的完整敘事」**。
        *   **不限時長**：只要故事完整，長度不限（但通常建議在 30秒 到 3分鐘之間）。
        *   **結構完整**：必須包含「情境/問題 -> 發展/轉折 -> 暫時的結論/懸念」。不要切在話講一半的地方。

        **第二步：主題切分（{style.get('quality_control', {}).get('principle', '寧缺勿濫')}）**
        請**最多**挑選 {self.config['clips']['count']} 個「絕對可用」的主題段落。

        **核心原則：{style.get('quality_control', {}).get('principle', '寧缺勿濫')}**
        *   如果找不到完美的片段，**請回傳較少的數量，甚至不回傳**。
        *   不要為了湊數而選擇品質普通的段落。
        *   不要選擇敘事不完整、或包含禁語的段落。

        每個段落必須：
        1. 有明確的開始和結束
        2. 包含完整的論述（有前因後果）
        3. 能獨立理解，不需要額外上下文
        4. 至少 {self.config['clips']['min_topic_duration']} 秒（避免過短的片段）

        ## 輸出格式

        請務必回傳「純 JSON 格式」（不要 markdown code block），格式如下：
        [
            {{
                "topic_name": "主題名稱（吸睛標題）",
                "start_text": "片段開始的精確語句（⚠️ 必須完全符合逐字稿，連標點符號都不要改）",
                "end_text": "片段結束的精確語句（⚠️ 必須完全符合逐字稿，連標點符號都不要改）",
                "content_summary": "這段在講什麼？（2-3 句話，具體說明內容）",
                "key_point": "這段的核心重點是什麼？（1 句話）",
                "marketing_angle": "這段符合哪個行銷要素？（痛點/鉤子/情緒）",
                "narrative_check": "這段的故事是否完整？（是/否）",
                "why_selected": "為什麼這段適合做行銷素材？",
                "estimated_duration": 120
            }}
        ]

        ## 重要提醒

        ⚠️ **絕對禁止**：
        1. 禁止捏造逐字稿中沒有的句子
        2. 禁止修改原文
        3. **禁止切到一半**（這是最嚴重的錯誤，務必確保語意結束）
        4. 禁止選擇平淡無奇的過場

        ⛔️ **核心內容迴避（行銷用途，勿洩漏付費乾貨）**：
        請避開包含以下「課程核心專有名詞」的段落，除非是純故事分享或引發好奇的提問：
        {constraints_str}

        ✅ **優先選擇**：
        {positive_str}

        ## 逐字稿內容

        {text[:40000]}
        """
        
        # Try each API key until one works
        for i, api_key in enumerate(self.api_keys, 1):
            try:
                genai.configure(api_key=api_key)
                print(f"   嘗試 API Key #{i}...")
                
                response = model.generate_content(prompt)
                json_str = response.text.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:-3]
                elif json_str.startswith("```"):
                    json_str = json_str[3:-3]
                    
                print(f"   ✅ API Key #{i} 成功")
                return json.loads(json_str)
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    print(f"   ⚠️  API Key #{i} 額度已滿")
                    if i < len(self.api_keys):
                        print(f"   🔄 切換到下一個 Key...")
                        continue
                    else:
                        print(f"   ❌ 所有 API Keys 都已達到額度上限")
                else:
                    print(f"   ❌ API Key #{i} 發生錯誤: {e}")
                    if i < len(self.api_keys):
                        continue
        
        print("❌ LLM 分析失敗: 所有 API Keys 都無法使用")
        return []

    def _normalize_text(self, text):
        """標準化文字以進行模糊比對"""
        import re
        text = re.sub(r'[^\w\s]', '', text)
        text = text.lower()
        return "".join(text.split())

    def find_timecodes(self, srt_path, clips):
        """在 SRT 中尋找對應的時間碼"""
        import re
        from datetime import datetime, timedelta
        
        def parse_time(t_str):
            t_str = t_str.replace(',', '.')
            return datetime.strptime(t_str, "%H:%M:%S.%f")
            
        def format_time(dt):
            # 格式化回 ffmpeg 可用的字串 (HH:MM:SS.mmm)
            return dt.strftime("%H:%M:%S.%f")[:-3]

        def time_diff_sec(t1_str, t2_str):
            t1 = parse_time(t1_str)
            t2 = parse_time(t2_str)
            return (t2 - t1).total_seconds()

        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import opencc
        cc = opencc.OpenCC('s2t')
        
        blocks = re.split(r'\n\n', content.strip())
        srt_data = []
        full_text_normalized = ""
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                time_line = lines[1]
                text = " ".join(lines[2:])
                try:
                    start, end = time_line.split(' --> ')
                    start = start.replace(',', '.')
                    end = end.replace(',', '.')
                except ValueError:
                    continue
                
                text = cc.convert(text)
                norm_text = self._normalize_text(text)
                start_idx = len(full_text_normalized)
                full_text_normalized += norm_text
                end_idx = len(full_text_normalized)
                
                srt_data.append({
                    'start': start, 
                    'end': end, 
                    'text': text,
                    'norm_text': norm_text,
                    'global_start_idx': start_idx,
                    'global_end_idx': end_idx
                })

        results = []
        padding = self.config['clips'].get('padding', 0)
        
        for clip in clips:
            topic_name = clip.get('topic_name', clip.get('topic', 'unknown'))
            print(f"🔍 尋找主題: {topic_name}")
            
            start_norm = self._normalize_text(clip['start_text'])
            end_norm = self._normalize_text(clip['end_text'])
            
            start_pos = full_text_normalized.find(start_norm)
            if start_pos == -1:
                start_pos = full_text_normalized.find(start_norm[:30])
            
            if start_pos == -1:
                print(f"   ⚠️  找不到開始語句: {clip['start_text'][:20]}...")
                continue
                
            end_pos = full_text_normalized.find(end_norm, start_pos)
            if end_pos == -1:
                end_pos = full_text_normalized.find(end_norm[-30:], start_pos)
                
            if end_pos == -1:
                print(f"   ⚠️  找不到結束語句: {clip['end_text'][-20:]}...")
                continue

            start_time_str = None
            end_time_str = None
            
            for item in srt_data:
                if start_time_str is None and item['global_end_idx'] > start_pos:
                    start_time_str = item['start']
                if item['global_start_idx'] <= end_pos + len(end_norm):
                    end_time_str = item['end']
            
            if start_time_str and end_time_str:
                # Apply Padding
                t1 = parse_time(start_time_str)
                t2 = parse_time(end_time_str)
                
                # Add padding
                t1 = t1 - timedelta(seconds=padding)
                t2 = t2 + timedelta(seconds=padding)
                
                # Ensure start is not negative (using arbitrary base date 1900-01-01)
                if t1.year < 1900: 
                    t1 = t1.replace(year=1900, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                
                duration = (t2 - t1).total_seconds()
                
                if duration < 5:
                    print(f"   ⚠️  片段過短 ({duration}s)，忽略")
                    continue
                
                final_start = format_time(t1)
                final_end = format_time(t2)
                    
                results.append({
                    'start': final_start,
                    'end': final_end,
                    'topic': clip.get('topic_name', clip.get('topic', 'unknown')),
                    'content_summary': clip.get('content_summary', ''),
                    'key_point': clip.get('key_point', ''),
                    'why_selected': clip.get('why_selected', clip.get('reason', '')),
                    'estimated_duration': clip.get('estimated_duration', duration)
                })
                print(f"   ✅ 鎖定時間: {final_start} - {final_end} ({duration:.1f}s, padding={padding}s)")
            else:
                print(f"   ⚠️  時間碼對應失敗")
                
        return results

    def slice_video(self, video_path, clips, output_dir, mode="proxy"):
        """使用 ffmpeg 切割影片 (支援 proxy/master 模式)"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        base_name = Path(video_path).stem
        
        # 儲存 metadata
        metadata_path = os.path.join(output_dir, "clips.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(clips, f, ensure_ascii=False, indent=2)
            
        print(f"💾 已儲存剪輯資訊: {metadata_path}")
        
        for i, clip in enumerate(clips, 1):
            output_filename = self.config['output']['filename_pattern'].format(
                original_name=base_name,
                index=i,
                topic=clip['topic']
            )
            output_path = os.path.join(output_dir, output_filename)
            
            print(f"✂️  正在切割片段 {i} ({mode}): {clip['topic']}")
            
            if mode == "proxy":
                # Proxy 模式：轉碼為 720p H.264，檔案小，適合預覽
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", clip['start'],
                    "-to", clip['end'],
                    "-i", video_path,
                    "-vf", "scale=-1:720",  # 縮放至 720p
                    "-c:v", "libx264",      # 使用 H.264 編碼
                    "-crf", "23",           # 平衡畫質與大小
                    "-preset", "fast",      # 快速編碼
                    "-c:a", "aac",          # 音訊轉碼
                    "-avoid_negative_ts", "1",
                    output_path
                ]
            else:
                # Master 模式：無損複製，畫質最高，檔案大
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", clip['start'],
                    "-to", clip['end'],
                    "-i", video_path,
                    "-c:v", "copy",         # 視訊無損複製
                    "-c:a", "copy",         # 音訊無損複製
                    "-avoid_negative_ts", "1",
                    output_path
                ]
            
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ 已儲存: {output_filename}")
            except subprocess.CalledProcessError as e:
                print(f"❌ 切割失敗: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Video Slicer")
    parser.add_argument("--video", required=True, help="影片檔案路徑")
    parser.add_argument("--srt", required=True, help="字幕檔案路徑")
    parser.add_argument("--output", default="highlights", help="輸出目錄")
    parser.add_argument("--mode", default="proxy", choices=["proxy", "master"], help="輸出模式")
    args = parser.parse_args()
    
    slicer = VideoSlicer()
    
    print(f"📖 讀取字幕: {args.srt}")
    transcript_text = slicer.parse_srt(args.srt)
    
    clips_info = slicer.analyze_transcript(transcript_text)
    print(f"🔍 AI 挑選了 {len(clips_info)} 個片段")
    
    clips_with_time = slicer.find_timecodes(args.srt, clips_info)
    
    if clips_with_time:
        print(f"🎬 開始切割影片 ({args.mode} 模式)...")
        slicer.slice_video(args.video, clips_with_time, args.output, mode=args.mode)
        print("🎉 全部完成！")
    else:
        print("❌ 無法提取任何片段")

if __name__ == "__main__":
    main()
