# 挑片大師 - Mac mini 安裝步驟

## 📦 這個資料夾包含什麼?

```
挑片大師/
├── video_slicer/              # 主程式資料夾
│   ├── clip_extractor.py      # 核心程式
│   ├── config.yaml            # 系統配置
│   ├── style_guide.yaml       # AI 風格指南
│   ├── auto_slicer.py         # 自動化腳本
│   └── render_master.py       # Master 渲染工具
├── configs/
│   └── API-Keys.md            # API 金鑰 (需要設定)
├── 挑片大師_設定指南.md        # 完整使用說明
└── README_安裝步驟.md         # 本檔案
```

---

## 🚀 在 Mac mini 上安裝步驟

### Step 1: 複製到 Mac mini

將整個 `挑片大師` 資料夾複製到 Mac mini 的任意位置,例如:

```bash
cp -r /Volumes/Samsung-T7/挑片大師 ~/Desktop/
```

或直接拖曳到桌面

---

### Step 2: 建立專案目錄結構

在 Mac mini 上建立相同的目錄結構:

```bash
# 假設你的專案在 ~/Desktop/tars-001
cd ~/Desktop/tars-001

# 建立目錄
mkdir -p 01-system/tools/media
mkdir -p 01-system/configs/apis

# 複製檔案
cp -r ~/Desktop/挑片大師/video_slicer 01-system/tools/media/
cp ~/Desktop/挑片大師/configs/API-Keys.md 01-system/configs/apis/
```

---

### Step 3: 安裝 Python 依賴套件

```bash
pip install opencc-python-reimplemented
pip install google-generativeai
pip install anthropic
pip install pyyaml
```

或使用 requirements.txt (如果有的話):

```bash
pip install -r requirements.txt
```

---

### Step 4: 設定 API Keys

編輯 `01-system/configs/apis/API-Keys.md`:

```bash
nano 01-system/configs/apis/API-Keys.md
```

加入你的 API Keys:

```
GEMINI_API_KEY=你的_Gemini_金鑰
ANTHROPIC_API_KEY=你的_Claude_金鑰
```

> 💡 可以設定多個 Key,系統會自動輪替

---

### Step 5: 確認 FFmpeg 已安裝

```bash
ffmpeg -version
```

如果沒有安裝,使用 Homebrew 安裝:

```bash
brew install ffmpeg
```

---

### Step 6: 測試運行

```bash
cd 01-system/tools/media/video_slicer

python clip_extractor.py \
  --video "測試影片.mp4" \
  --srt "測試字幕.srt" \
  --output "output/" \
  --mode proxy
```

---

## 📝 使用方式

### 快速開始

```bash
python clip_extractor.py \
  --video "影片路徑.mp4" \
  --srt "字幕路徑.srt" \
  --output "輸出資料夾" \
  --mode proxy
```

### 參數說明

- `--video`: 影片檔案路徑
- `--srt`: 字幕檔案路徑 (SRT 格式)
- `--output`: 輸出資料夾
- `--mode`: 
  - `proxy` = 720p 預覽版 (檔案小,適合快速分享)
  - `master` = 原畫質無損版 (檔案大,適合最終交付)

---

## ⚙️ 自訂設定

### 調整 AI 模型

編輯 `config.yaml`:

```yaml
llm:
  provider: "gemini"  # 或 "claude"
  model: "gemini-2.0-flash"
```

### 調整挑選參數

```yaml
clips:
  min_topic_duration: 30  # 最短片段時長 (秒)
  count: 8                # 最多挑選片段數
  padding: 5              # 前後緩衝時間 (秒)
```

### 自訂風格指南

編輯 `style_guide.yaml` 來調整:
- 行銷策略
- 鉤子範例
- 禁止內容清單

---

## 🔧 常見問題

### Q: API Key 錯誤?

確認 `01-system/configs/apis/API-Keys.md` 路徑正確,且格式為:

```
GEMINI_API_KEY=實際金鑰
```

### Q: 找不到 FFmpeg?

```bash
brew install ffmpeg
```

### Q: 簡繁轉換失敗?

```bash
pip install opencc-python-reimplemented
```

---

## 📚 完整文檔

詳細使用說明請參考: **挑片大師_設定指南.md**

---

**🎉 安裝完成後,就可以開始使用挑片大師了!**
