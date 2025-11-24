# 部署到其他機器指南

本指南說明如何將影片轉文字工作流程部署到其他 Mac 電腦 (例如 Mac mini)。

## 📋 前置需求

在目標機器上需要安裝:
- macOS
- Homebrew
- Git (可選,用於版本控制)

## 🚀 快速部署步驟

### 方法一: 使用 USB 隨身碟或外接硬碟複製

#### 1. 在原機器上準備檔案

```bash
# 進入專案目錄
cd /Users/xiangyun/Desktop/tars-001

# 複製整個專案到外接硬碟 (例如 Samsung-T7)
cp -r /Users/xiangyun/Desktop/tars-001 /Volumes/Samsung-T7/tars-001-backup
```

#### 2. 在目標機器 (Mac mini) 上

```bash
# 從外接硬碟複製到目標機器
cp -r /Volumes/Samsung-T7/tars-001-backup ~/Desktop/tars-001

# 進入專案目錄
cd ~/Desktop/tars-001
```

### 方法二: 使用 AirDrop (適合小型專案)

1. 在原機器上壓縮專案資料夾
2. 使用 AirDrop 傳送到 Mac mini
3. 在 Mac mini 上解壓縮

### 方法三: 使用網路共享

1. 在原機器上開啟檔案共享
2. 從 Mac mini 連接到原機器
3. 複製專案資料夾

## 🔧 環境設定

### 1. 安裝 Homebrew (如果尚未安裝)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安裝 ffmpeg

```bash
brew install ffmpeg
```

### 3. 安裝 Python 3 (如果尚未安裝)

```bash
brew install python@3
```

### 4. 建立 Python 虛擬環境

```bash
cd ~/Desktop/tars-001

# 刪除舊的虛擬環境 (如果存在)
rm -rf .venv

# 建立新的虛擬環境
python3 -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate

# 安裝必要套件
pip install pyyaml elevenlabs groq pydub
```

### 5. 設定 API Keys

編輯 `01-system/configs/apis/API-Keys.md`,確保包含您的 API Keys:

```markdown
ELEVENLABS_API_KEY=sk-your-key-here
GROQ_API_KEY=gsk_your-key-here
```

> [!WARNING]
> **重要:** API Keys 是敏感資訊,請勿分享或上傳到公開的 Git repository!

## ✅ 驗證安裝

### 測試 ffmpeg

```bash
ffmpeg -version
```

應該顯示 ffmpeg 版本資訊。

### 測試 Python 環境

```bash
cd ~/Desktop/tars-001
.venv/bin/python --version
```

應該顯示 Python 3.x 版本。

### 測試轉錄工具

使用一個小型測試檔案:

```bash
# 下載測試音檔 (或使用您自己的小型影片)
.venv/bin/python 01-system/tools/stt/audio_transcribe/transcribe.py \
  --input "測試音檔.mp3" \
  --engine elevenlabs
```

## 📝 使用工作流程

### 單一檔案轉錄

```bash
cd ~/Desktop/tars-001

# 1. 壓縮影片
ffmpeg -i "/path/to/video.MP4" \
  -vn -ac 1 -ar 16000 -b:a 32k -f mp3 \
  "/path/to/output_compressed.mp3"

# 2. 轉錄
.venv/bin/python 01-system/tools/stt/audio_transcribe/transcribe.py \
  --input "/path/to/output_compressed.mp3" \
  --engine elevenlabs
```

### 批次處理

```bash
cd ~/Desktop/tars-001

# 編輯批次處理腳本,修改路徑
# SOURCE_DIR="/Volumes/Samsung-T7"  # 改為您的影片來源路徑
# OUTPUT_DIR="/Users/您的使用者名稱/Desktop"

# 執行批次處理
./scripts/batch_video_to_text.sh
```

## 🔄 同步更新

如果您在原機器上更新了工具或腳本,可以只複製特定檔案:

### 只複製工具檔案

```bash
# 在原機器上
cp -r 01-system/tools/stt /Volumes/Samsung-T7/tools-backup/

# 在 Mac mini 上
cp -r /Volumes/Samsung-T7/tools-backup/stt ~/Desktop/tars-001/01-system/tools/
```

### 只複製腳本

```bash
# 在原機器上
cp scripts/batch_video_to_text.sh /Volumes/Samsung-T7/

# 在 Mac mini 上
cp /Volumes/Samsung-T7/batch_video_to_text.sh ~/Desktop/tars-001/scripts/
chmod +x ~/Desktop/tars-001/scripts/batch_video_to_text.sh
```

## 📂 最小化部署 (只複製必要檔案)

如果您只想複製必要的檔案,不包含輸出結果:

```bash
# 在原機器上建立乾淨的副本
mkdir -p /Volumes/Samsung-T7/tars-001-clean

# 複製必要的目錄和檔案
cp -r 01-system /Volumes/Samsung-T7/tars-001-clean/
cp -r scripts /Volumes/Samsung-T7/tars-001-clean/
cp -r .agent /Volumes/Samsung-T7/tars-001-clean/
cp requirements.txt /Volumes/Samsung-T7/tars-001-clean/

# 在 Mac mini 上
cp -r /Volumes/Samsung-T7/tars-001-clean ~/Desktop/tars-001
cd ~/Desktop/tars-001

# 建立必要的目錄
mkdir -p 02-inputs
mkdir -p 03-outputs/audio_transcribe

# 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml elevenlabs groq pydub
```

## 🐛 常見問題排除

### 問題: 找不到 python3

```bash
# 安裝 Python
brew install python@3

# 或使用系統 Python
which python3
```

### 問題: ffmpeg 未安裝

```bash
brew install ffmpeg
```

### 問題: 權限錯誤

```bash
# 確保腳本有執行權限
chmod +x scripts/batch_video_to_text.sh
```

### 問題: API Key 錯誤

檢查 `01-system/configs/apis/API-Keys.md` 檔案,確保:
- API Keys 格式正確
- 沒有多餘的空格
- 使用正確的 Key (不是過期的)

### 問題: 虛擬環境路徑錯誤

如果使用者名稱不同,需要修改批次處理腳本中的路徑:

```bash
# 編輯 scripts/batch_video_to_text.sh
# 將 /Users/xiangyun/ 改為 /Users/您的使用者名稱/
```

## 💡 建議

1. **使用相同的使用者名稱:** 如果可能,在兩台機器上使用相同的使用者名稱,可以避免路徑問題
2. **定期備份:** 定期將專案備份到外接硬碟
3. **版本控制:** 考慮使用 Git 來管理專案,方便同步更新
4. **測試先行:** 在新機器上先用小檔案測試,確認一切正常後再處理大檔案

## 📋 檢查清單

部署完成後,請確認:

- [ ] ffmpeg 已安裝且可執行
- [ ] Python 3 已安裝
- [ ] 虛擬環境已建立
- [ ] 必要套件已安裝 (pyyaml, elevenlabs, groq, pydub)
- [ ] API Keys 已設定
- [ ] 測試檔案轉錄成功
- [ ] 批次處理腳本可執行
- [ ] 輸出目錄已建立

完成以上檢查後,您就可以在 Mac mini 上使用完整的影片轉文字工作流程了! 🎉
