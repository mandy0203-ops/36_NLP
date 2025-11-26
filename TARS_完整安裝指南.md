# TARS-001 完整安裝指南 (Mac mini 版)

> 📦 **同步日期**: 2025-11-25  
> 🎯 **目標**: 在 Mac mini 上完整部署 TARS-001 AI 工具集

---

## 📚 包含的工具清單

### 🎬 影片處理工具 (Media Tools)

#### 1. **挑片大師 (Video Slicer)**
- **路徑**: `01-system/tools/media/video_slicer/`
- **功能**: AI 智慧影片切片,自動挑選行銷素材
- **核心檔案**:
  - `clip_extractor.py` - 主程式
  - `config.yaml` - 系統配置
  - `style_guide.yaml` - AI 風格指南
  - `auto_slicer.py` - 自動化腳本
  - `render_master.py` - Master 版本渲染

#### 2. **YouTube 下載器**
- **路徑**: `01-system/tools/media/youtube_downloader/`
- **功能**: 下載 YouTube 影片(支援 8K)
- **核心檔案**: `youtube_downloader.py`

---

### 🎙️ 音訊轉錄工具 (STT Tools)

#### 3. **音訊轉錄系統 (Audio Transcribe)**
- **路徑**: `01-system/tools/stt/audio_transcribe/`
- **功能**: 
  - 支援雙引擎 STT (ElevenLabs + Groq)
  - 自動簡轉繁
  - 智慧音訊壓縮
  - 自訂字典替換
  - 短影音字幕格式化
- **核心檔案**:
  - `transcribe.py` - 主程式
  - `config.yaml` - 配置檔
  - `custom_dict.yaml` - 自訂字典
  - `formatting_rules.yaml` - 格式化規則
  - `modules/` - 核心模組

---

### 🛠️ 實用腳本 (Scripts)

#### 4. **批次處理腳本**
- `batch_video_to_text.sh` - 批次影片轉文字
- `groq_stt_tool.py` - Groq STT 工具
- `elevenlabs_scribe_tool.py` - ElevenLabs STT 工具
- `youtube_to_subtitle.py` - YouTube 字幕下載
- `merge_srt.py` - SRT 字幕合併
- `convert_to_mp4.py` - 影片格式轉換
- `organize_course.py` - 課程檔案整理
- `sync-push.sh` / `sync-pull.sh` - 專案同步腳本

---

## 🚀 Mac mini 安裝步驟

### Step 1: 複製檔案到 Mac mini

```bash
# 插入外接硬碟後
cp -r /Volumes/Samsung-T7/TARS-同步包 ~/Desktop/tars-001
cd ~/Desktop/tars-001
```

---

### Step 2: 安裝系統依賴

#### 安裝 Homebrew (如果還沒有)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 安裝 FFmpeg

```bash
brew install ffmpeg
```

#### 安裝 yt-dlp (YouTube 下載工具)

```bash
brew install yt-dlp
```

---

### Step 3: 安裝 Python 依賴

```bash
pip install opencc-python-reimplemented
pip install google-generativeai
pip install anthropic
pip install groq
pip install elevenlabs
pip install pyyaml
pip install pydub
```

或使用 requirements.txt (如果有):

```bash
pip install -r requirements.txt
```

---

### Step 4: 設定 API Keys

編輯 API Keys 檔案:

```bash
nano 01-system/configs/apis/API-Keys.md
```

加入你的 API Keys:

```
GEMINI_API_KEY=你的_Gemini_金鑰
ANTHROPIC_API_KEY=你的_Claude_金鑰
GROQ_API_KEY=你的_Groq_金鑰
ELEVENLABS_API_KEY=你的_ElevenLabs_金鑰
```

> 💡 **支援多 Key 輪替**: 可以設定多個相同類型的 Key,系統會自動輪替

---

### Step 5: 建立工作目錄

```bash
mkdir -p 02-inputs
mkdir -p 03-outputs
```

---

### Step 6: 測試各工具

#### 測試挑片大師

```bash
cd 01-system/tools/media/video_slicer
python clip_extractor.py \
  --video "測試影片.mp4" \
  --srt "測試字幕.srt" \
  --output "output/" \
  --mode proxy
```

#### 測試音訊轉錄

```bash
cd 01-system/tools/stt/audio_transcribe
python transcribe.py "測試音訊.mp3"
```

#### 測試 YouTube 下載

```bash
cd scripts
python youtube_to_subtitle.py "https://youtu.be/影片ID"
```

---

## 🎯 各工具詳細使用說明

### 1️⃣ 挑片大師 (Video Slicer)

#### 基本用法

```bash
python clip_extractor.py \
  --video "影片.mp4" \
  --srt "字幕.srt" \
  --output "highlights/" \
  --mode proxy
```

#### 參數說明

- `--mode proxy`: 720p 預覽版 (檔案小)
- `--mode master`: 原畫質無損版 (檔案大)

#### 配置調整

編輯 `config.yaml`:

```yaml
clips:
  min_topic_duration: 30  # 最短片段時長
  count: 8                # 最多挑選數量
  padding: 5              # 前後緩衝時間
```

---

### 2️⃣ 音訊轉錄系統

#### 基本用法

```bash
python transcribe.py "音訊檔案.mp3"
```

#### 選擇 STT 引擎

程式會自動詢問:
- **ElevenLabs**: 精準度高,有免費額度
- **Groq**: 速度快,免費額度大

#### 輸出檔案

```
03-outputs/transcriptions/音訊檔案_20251125_094500/
├── 音訊檔案_original.srt          # 原始字幕
├── 音訊檔案_original.txt          # 原始文字
├── 音訊檔案_formatted.srt         # 格式化字幕
├── 音訊檔案_formatted.txt         # 格式化文字
└── metadata.json                  # 轉錄資訊
```

#### 自訂字典

編輯 `custom_dict.yaml` 來替換專有名詞:

```yaml
replacements:
  "傑扣": "Jack"
  "溝通": "Communication"
```

---

### 3️⃣ YouTube 工具

#### 下載影片

```bash
python scripts/youtube_to_subtitle.py "https://youtu.be/影片ID"
```

#### 下載字幕

```bash
yt-dlp --write-subs --sub-lang zh-TW --skip-download "https://youtu.be/影片ID"
```

---

## 📁 專案目錄結構

```
tars-001/
├── 01-system/
│   ├── tools/
│   │   ├── media/
│   │   │   ├── video_slicer/      # 挑片大師
│   │   │   └── youtube_downloader/
│   │   └── stt/
│   │       └── audio_transcribe/   # 音訊轉錄
│   └── configs/
│       └── apis/
│           └── API-Keys.md         # API 金鑰
├── 02-inputs/                      # 輸入檔案
├── 03-outputs/                     # 輸出檔案
├── scripts/                        # 實用腳本
├── AGENTS.md                       # AI Agent 配置
└── requirements.txt                # Python 依賴
```

---

## 🔧 常見問題排解

### Q1: FFmpeg 找不到?

```bash
brew install ffmpeg
ffmpeg -version  # 確認安裝
```

### Q2: API Key 錯誤?

檢查 `01-system/configs/apis/API-Keys.md`:
- 確認格式正確 (KEY_NAME=value)
- 確認沒有多餘空格
- 確認 Key 有效且未過期

### Q3: 簡繁轉換失敗?

```bash
pip install opencc-python-reimplemented
```

### Q4: 音訊檔案過大?

系統會自動壓縮 >25MB 的檔案,但你也可以手動壓縮:

```bash
ffmpeg -i 大檔案.mp3 -ar 8000 -ab 24k 壓縮後.mp3
```

### Q5: 挑片大師沒有挑到片段?

- 檢查字幕檔是否為 SRT 格式
- 調低 `min_topic_duration` (在 config.yaml)
- 檢查 `style_guide.yaml` 的挑選標準是否太嚴格

---

## 🎓 進階技巧

### 多 API Key 輪替

在 `API-Keys.md` 中加入多個 Key:

```
GEMINI_API_KEY=key1
GEMINI_API_KEY=key2
GEMINI_API_KEY=key3
```

系統會自動輪替,避免額度限制。

### 批次處理影片

```bash
cd scripts
./batch_video_to_text.sh /path/to/videos/
```

### 自訂 STT 格式化規則

編輯 `formatting_rules.yaml`:

```yaml
rules:
  - name: "移除填充詞"
    pattern: "(嗯|啊|呃)"
    replacement: ""
```

---

## 📊 工具對照表

| 工具 | 用途 | 主要技術 | 免費額度 |
|------|------|----------|----------|
| 挑片大師 | 影片切片 | Gemini/Claude + FFmpeg | ✅ |
| 音訊轉錄 | 語音轉文字 | ElevenLabs/Groq | ✅ |
| YouTube 下載 | 影片下載 | yt-dlp | ✅ |

---

## 🔄 同步更新

### 從 MacBook 同步到 Mac mini

```bash
# 在 MacBook 上
./scripts/sync-push.sh

# 在 Mac mini 上
./scripts/sync-pull.sh
```

---

## 📝 重要提醒

1. **API Keys 安全**: 不要將 API-Keys.md 上傳到 GitHub
2. **大檔案處理**: 影片和音訊檔案放在 `02-inputs/`,不要提交到 Git
3. **繁體中文**: 所有字幕和文字輸出都會自動轉為繁體中文
4. **寧缺勿濫**: 挑片大師的核心原則,品質優於數量

---

## 🎉 安裝完成檢查清單

- [ ] FFmpeg 已安裝
- [ ] yt-dlp 已安裝
- [ ] Python 依賴已安裝
- [ ] API Keys 已設定
- [ ] 工作目錄已建立 (02-inputs, 03-outputs)
- [ ] 各工具測試通過

---

**完成以上步驟後,你的 Mac mini 就擁有完整的 TARS-001 AI 工具集了!** 🚀
