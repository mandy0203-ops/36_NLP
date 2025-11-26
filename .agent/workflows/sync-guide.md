---
description: 在 MacBook 和 Mac mini 之間同步專案
---

# 雙機同步方案

## 🎯 推薦方案:Git + 外接硬碟

結合 Git 版本控制和外接硬碟備份,既安全又方便。

### 為什麼選這個方案?

- ✅ **版本控制**: 可以追蹤所有變更,隨時回溯
- ✅ **選擇性同步**: 只同步程式碼,不同步大型輸出檔案
- ✅ **離線工作**: 不需要網路,使用外接硬碟傳輸
- ✅ **備份安全**: Git repository 在外接硬碟上,不會遺失

## 📋 初始設定 (只需做一次)

### 在 MacBook 上初始化 Git

```bash
cd ~/Desktop/tars-001

# 初始化 Git repository
git init

# 設定 .gitignore (已經存在,但確認一下)
cat .gitignore
```

確保 `.gitignore` 包含:
```
.venv/
venv/
03-outputs/
__pycache__/
*.pyc
.DS_Store
```

### 建立外接硬碟上的 Git repository

```bash
# 在外接硬碟建立 bare repository (中央儲存庫)
git init --bare /Volumes/Samsung-T7/tars-001.git

# 在 MacBook 上設定 remote
cd ~/Desktop/tars-001
git remote add origin /Volumes/Samsung-T7/tars-001.git

# 第一次提交
git add .
git commit -m "Initial commit: 影片轉文字工作流程"
git push -u origin main
```

## 🔄 日常同步流程

### 從 MacBook 推送更新

當您在 MacBook 上修改了程式碼或腳本:

```bash
cd ~/Desktop/tars-001

# 查看變更
git status

# 加入變更
git add .

# 提交變更 (寫清楚改了什麼)
git commit -m "修復 ElevenLabs API 參數問題"

# 推送到外接硬碟
git push origin main
```

### 在 Mac mini 上拉取更新

```bash
cd ~/Desktop/tars-001

# 拉取最新變更
git pull origin main
```

## 📊 同步策略

### 需要同步的內容 (使用 Git)

- ✅ 程式碼 (`01-system/tools/`)
- ✅ 腳本 (`scripts/`)
- ✅ 設定檔 (`config.yaml`, `custom_dict.yaml` 等)
- ✅ 文件 (`.agent/workflows/`, `README.md` 等)
- ✅ API Keys (`01-system/configs/apis/API-Keys.md`)

### 不需要同步的內容 (排除在 Git 外)

- ❌ 虛擬環境 (`.venv/`)
- ❌ 輸出結果 (`03-outputs/`)
- ❌ 臨時檔案

### 大型檔案同步 (使用外接硬碟直接複製)

如果需要在兩台機器間傳輸轉錄結果:

```bash
# 從 MacBook 複製到外接硬碟
cp -r ~/Desktop/tars-001/03-outputs/audio_transcribe/C8575 \
  /Volumes/Samsung-T7/transcription-results/

# 在 Mac mini 上複製回來
cp -r /Volumes/Samsung-T7/transcription-results/C8575 \
  ~/Desktop/tars-001/03-outputs/audio_transcribe/
```

## 🚀 快速同步腳本

我已經建立了自動化腳本讓同步更簡單。

### MacBook 推送腳本

```bash
# 使用方式
./scripts/sync-push.sh "更新說明"
```

### Mac mini 拉取腳本

```bash
# 使用方式
./scripts/sync-pull.sh
```

## 📝 同步檢查清單

### 每次在 MacBook 上工作完成後:

- [ ] 執行 `git status` 檢查變更
- [ ] 執行 `git add .` 加入變更
- [ ] 執行 `git commit -m "說明"` 提交
- [ ] 執行 `git push origin main` 推送
- [ ] 確認推送成功

### 每次在 Mac mini 上開始工作前:

- [ ] 插入外接硬碟
- [ ] 執行 `git pull origin main` 拉取
- [ ] 確認拉取成功
- [ ] 開始工作

## 🔧 進階技巧

### 查看同步狀態

```bash
# 查看目前分支和遠端狀態
git status

# 查看提交歷史
git log --oneline -10

# 查看與遠端的差異
git diff origin/main
```

### 解決衝突

如果兩台機器都修改了同一個檔案:

```bash
# 拉取時會提示衝突
git pull origin main

# 手動編輯衝突檔案,解決衝突標記
# <<<<<<< HEAD
# 您的變更
# =======
# 遠端的變更
# >>>>>>> origin/main

# 解決後提交
git add .
git commit -m "解決衝突"
git push origin main
```

### 回溯到之前的版本

```bash
# 查看歷史
git log --oneline

# 回溯到特定版本
git checkout <commit-hash>

# 回到最新版本
git checkout main
```

## 🆘 故障排除

### 問題: 外接硬碟找不到 repository

```bash
# 檢查外接硬碟是否掛載
ls /Volumes/Samsung-T7/

# 重新設定 remote
git remote set-url origin /Volumes/Samsung-T7/tars-001.git
```

### 問題: 推送失敗

```bash
# 先拉取最新變更
git pull origin main

# 再推送
git push origin main
```

### 問題: 想要放棄本地變更

```bash
# 放棄所有未提交的變更
git reset --hard HEAD

# 拉取最新版本
git pull origin main
```

## 💡 最佳實踐

1. **經常提交**: 每次完成一個小功能就提交
2. **清楚的提交訊息**: 寫清楚改了什麼,為什麼改
3. **工作前先拉取**: 避免衝突
4. **工作後記得推送**: 確保變更已備份
5. **定期備份外接硬碟**: 將 `.git` 資料夾額外備份到雲端

## 📊 同步流程圖

```
MacBook                外接硬碟              Mac mini
   |                      |                     |
   |-- git push --------> |                     |
   |                      |                     |
   |                      | <---- git pull -----|
   |                      |                     |
   |                   [Git Repo]               |
   |                 (版本控制中心)              |
```

## 🎯 替代方案

如果您不想使用 Git,也可以:

### 方案 A: 純外接硬碟同步

```bash
# MacBook 推送
rsync -av --delete ~/Desktop/tars-001/ \
  /Volumes/Samsung-T7/tars-001-sync/

# Mac mini 拉取
rsync -av --delete /Volumes/Samsung-T7/tars-001-sync/ \
  ~/Desktop/tars-001/
```

### 方案 B: iCloud Drive (需要網路)

將專案放在 iCloud Drive,自動同步:
```bash
mv ~/Desktop/tars-001 ~/Library/Mobile\ Documents/com~apple~CloudDocs/tars-001
ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/tars-001 ~/Desktop/tars-001
```

## 📅 建議的工作流程

**情境 1: 主要在 MacBook 工作**
- MacBook: 開發和測試
- Mac mini: 批次處理大量影片
- 同步: 每天工作結束前推送一次

**情境 2: 兩台機器輪流使用**
- 每次切換機器前: 推送變更
- 每次開始工作前: 拉取最新版本
- 使用外接硬碟作為中轉站

---

**建議**: 使用 Git + 外接硬碟方案,最安全可靠! 🚀
