# 語音轉錄工具

**類別**：STT (Speech-to-Text)  
**版本**：v1.0（更新日期：2025-11-23）

## 能力總覽

- ✅ 雙 STT 引擎支援（ElevenLabs Scribe + Groq Whisper）
- ✅ 互動式引擎選擇（顯示額度和優缺點）
- ✅ 智能音檔壓縮（根據檔案大小自動調整）
- ✅ 大檔案自動分割處理
- ✅ 5 大格式化規則（口水詞清洗、18 字斷句、風格統一等）
- ✅ 自訂詞典（記住您的慣用詞彙）
- ✅ 組織化輸出（每集獨立資料夾）
- ✅ 同時產生 SRT + TXT（原始 + 格式化）

## 參數說明

- `--input`：輸入音檔路徑（必填）
- `--engine`：指定 STT 引擎（`elevenlabs` 或 `groq`，可選）
- `--output-name`：自訂輸出資料夾名稱（可選）
- `--skip-format`：跳過格式化，只產生原始轉錄（可選）

## 常見用法（逐步）

### 基本使用

1. 準備音檔（支援 mp3, wav, m4a 等格式）
2. 執行工具：
   ```bash
   python 01-system/tools/stt/audio_transcribe/transcribe.py --input "音檔.mp3"
   ```
3. 選擇 STT 引擎（工具會顯示可用引擎和剩餘額度）
4. 等待轉錄完成
5. 檢查輸出資料夾

### 指定引擎

```bash
# 使用 ElevenLabs
python 01-system/tools/stt/audio_transcribe/transcribe.py --input "音檔.mp3" --engine elevenlabs

# 使用 Groq
python 01-system/tools/stt/audio_transcribe/transcribe.py --input "音檔.mp3" --engine groq
```

### 自訂輸出名稱

```bash
python 01-system/tools/stt/audio_transcribe/transcribe.py --input "音檔.mp3" --output-name "EP01_朋友邊界"
```

## 範例

**快速範例**：
```bash
python 01-system/tools/stt/audio_transcribe/transcribe.py --input "02-inputs/podcast.mp3"
```

產出於：`03-outputs/audio_transcribe/podcast_20251123_235959/`
- `podcast.mp3`（原始音檔）
- `podcast.srt`（原始字幕）
- `podcast.txt`（原始文字）
- `podcast_formatted.srt`（格式化字幕）⭐
- `podcast_formatted.txt`（格式化文字）⭐
- `_metadata.yaml`（轉錄資訊）

## 輸入 / 輸出路徑

- **輸入來源**：任何音檔路徑
- **產出位置**：`03-outputs/audio_transcribe/[檔名_時間戳]/`

## 自訂詞典

編輯 `01-system/tools/stt/audio_transcribe/custom_dict.yaml` 新增您的慣用詞彙：

```yaml
replacements:
  - wrong: ["人生解構", "人生解扣"]
    correct: "人生解扣方程式"
  
  - wrong: ["GPT", "G P T"]
    correct: "ChatGPT"
```

## 格式化規則

編輯 `01-system/tools/stt/audio_transcribe/formatting_rules.yaml` 調整：

- **口水詞清單**：新增要清除的詞彙
- **字幕限制**：調整每行字數（預設 18 字）
- **風格規則**：新增專有縮寫

## 風險與權限

- **ElevenLabs 免費版**：每月 150 分鐘，不可商用
- **Groq 免費版**：每小時 120 分鐘，可能遇到速率限制
- **大檔案處理**：會自動分割，可能需要較長時間

## 故障排除

### 錯誤：未安裝套件

```bash
# 安裝依賴
.venv/bin/pip install pyyaml elevenlabs groq
```

### 錯誤：API Key 未設定

檢查 `01-system/configs/apis/API-Keys.md` 是否包含：
- `ELEVENLABS_API_KEY=sk-...`
- `GROQ_API_KEY=gsk_...`

### 速率限制（429 錯誤）

- Groq：工具會自動重試，請耐心等待
- ElevenLabs：檢查是否超過每月額度

## 版本與更新紀錄

- **v1.0**（2025-11-23）：初版
  - 雙引擎支援
  - 智能格式化
  - 自訂詞典
  - 組織化輸出
