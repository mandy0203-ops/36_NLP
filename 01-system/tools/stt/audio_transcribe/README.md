# Audio Transcription Tool

專業的語音轉錄工具，支援雙 STT 引擎、自訂詞典、智能格式化。

## 快速開始

```bash
# 基本使用
python transcribe.py --input "音檔.mp3"

# 指定引擎
python transcribe.py --input "音檔.mp3" --engine elevenlabs

# 批次處理
python transcribe.py --input "資料夾/" --batch
```

## 功能特色

- ✅ 雙 STT 引擎（ElevenLabs Scribe + Groq Whisper）
- ✅ 自訂詞典（記住您的慣用詞彙）
- ✅ 智能格式化（5 大規則）
- ✅ 專有名詞自動提取
- ✅ 組織化輸出（每集獨立資料夾）

## 詳細文件

請參閱：`01-system/docs/user/tools/audio_transcribe.md`
