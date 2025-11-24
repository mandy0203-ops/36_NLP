# 雙機同步方案

## 🎯 推薦方案:Git + 外接硬碟混合

### 為什麼選這個方案?
- ✅ **版本控制**: 可以追蹤所有變更歷史
- ✅ **選擇性同步**: 只同步程式碼,不同步大型輸出檔案
- ✅ **離線可用**: 不需要網路,使用外接硬碟即可
- ✅ **安全**: 輸出檔案和 API Keys 不會被同步到雲端

---

## 📋 初次設定 (只需做一次)

### 在 MacBook 上設定 Git

```bash
cd ~/Desktop/tars-001

# 初始化 Git repository
git init

# 設定 .gitignore (已經存在,但我們要加強)
cat >> .gitignore << 'EOF'

# 不要同步的內容
.venv/
venv/
03-outputs/
*.mp3
*.MP4
*.mp4
*.mov
*.MOV
__pycache__/
*.pyc
.DS_Store

# 保留 API Keys 在本地,不要上傳
01-system/configs/apis/API-Keys.md
EOF

# 第一次提交
git add .
git commit -m "Initial commit: Video to text workflow"
```

### 建立同步腳本

我會幫您建立兩個腳本:
1. **推送 (Push)**: 將變更同步到外接硬碟
2. **拉取 (Pull)**: 從外接硬碟同步變更

---

## 🔄 日常使用流程

### 情境 1: 在 MacBook 上做了更新,要同步到 Mac mini

**在 MacBook 上:**
```bash
cd ~/Desktop/tars-001
./scripts/sync-push.sh
```

**在 Mac mini 上:**
```bash
cd ~/Desktop/tars-001
./scripts/sync-pull.sh
```

### 情境 2: 在 Mac mini 上做了更新,要同步回 MacBook

**在 Mac mini 上:**
```bash
cd ~/Desktop/tars-001
./scripts/sync-push.sh
```

**在 MacBook 上:**
```bash
cd ~/Desktop/tars-001
./scripts/sync-pull.sh
```

---

## 📝 同步腳本說明

### sync-push.sh (推送變更)
- 自動提交所有變更
- 推送到外接硬碟的 Git repository
- 顯示同步狀態

### sync-pull.sh (拉取變更)
- 從外接硬碟拉取最新變更
- 自動合併
- 顯示更新內容

---

## 🎬 實際使用範例

### 範例 1: 修改了轉錄工具

**在 MacBook 上:**
```bash
# 1. 修改程式碼
nano 01-system/tools/stt/audio_transcribe/transcribe.py

# 2. 推送到外接硬碟
./scripts/sync-push.sh "修改轉錄工具的參數"
```

**在 Mac mini 上:**
```bash
# 拉取更新
./scripts/sync-pull.sh
```

### 範例 2: 新增了批次處理腳本

**在 Mac mini 上:**
```bash
# 1. 建立新腳本
nano scripts/new_batch_script.sh

# 2. 推送到外接硬碟
./scripts/sync-push.sh "新增批次處理腳本"
```

**在 MacBook 上:**
```bash
# 拉取更新
./scripts/sync-pull.sh
```

---

## 🔒 什麼會被同步?什麼不會?

### ✅ 會同步
- 所有程式碼和腳本
- 設定檔 (config.yaml, formatting_rules.yaml 等)
- 文件 (.md 檔案)
- 工作流程定義

### ❌ 不會同步
- 虛擬環境 (.venv/)
- 輸出檔案 (03-outputs/)
- 影片和音檔 (*.mp4, *.mp3)
- API Keys (保持本地)
- Python 快取檔案

---

## 💡 進階技巧

### 查看同步狀態
```bash
cd ~/Desktop/tars-001
git status
```

### 查看變更歷史
```bash
git log --oneline -10
```

### 復原到之前的版本
```bash
git log  # 找到想要的版本 ID
git checkout <版本ID>
```

---

## 🆘 常見問題

### Q: 如果兩邊都有修改怎麼辦?
A: Git 會自動合併。如果有衝突,腳本會提示您手動解決。

### Q: 可以不用 Git 嗎?
A: 可以,但不推薦。您可以用 rsync 直接同步,但會失去版本控制的好處。

### Q: 輸出檔案要怎麼同步?
A: 輸出檔案通常很大,建議:
- 方案 1: 直接在外接硬碟上工作
- 方案 2: 手動複製需要的檔案
- 方案 3: 使用雲端儲存 (iCloud, Dropbox)

---

## 🚀 快速開始

執行以下命令來設定同步:

```bash
cd ~/Desktop/tars-001
./scripts/setup-sync.sh
```

這會自動:
- 初始化 Git repository
- 建立同步腳本
- 設定 .gitignore
- 完成第一次提交

---

## 📊 同步方案比較

| 方案 | 優點 | 缺點 | 推薦度 |
|------|------|------|--------|
| **Git + 外接硬碟** | 版本控制、選擇性同步 | 需要學習 Git | ⭐⭐⭐⭐⭐ |
| rsync | 簡單直接 | 無版本控制 | ⭐⭐⭐ |
| iCloud/Dropbox | 自動同步 | 可能同步大檔案 | ⭐⭐ |
| 手動複製 | 完全控制 | 容易出錯 | ⭐ |

---

**建議**: 使用 Git + 外接硬碟方案,既有版本控制又不依賴網路!
