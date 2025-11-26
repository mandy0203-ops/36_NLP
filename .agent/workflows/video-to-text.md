# 🎥 影片轉文字黃金工作流 (Video to Text Gold Workflow)

這是一套經過驗證、最高效的影片轉文字標準作業程序 (SOP)。適用於 Mac mini 和 MacBook。

## 核心策略：先壓縮，再轉錄 (Compress First, Transcribe Later)

> [!IMPORTANT]
> **永遠不要直接上傳大影片檔！**
> 10GB 的影片壓縮後通常不到 20MB。這能節省 99% 的上傳時間和 API 處理時間。

## 🛠️ 準備工作

1.  **確認環境**：確保已執行 `./scripts/setup.sh` 安裝所有工具。
2.  **設定 API Keys**：在 `01-system/configs/apis/API-Keys.md` 中填入 Key。
    *   **💡 技巧**：支援多組 Key！填寫多行 `ELEVENLABS_API_KEY=...`，系統會自動輪替使用，突破每日額度限制。

## 🚀 執行步驟

### 情境 A：單一影片處理 (手動)

適合處理單個檔案，想精確控制時。

1.  **壓縮影片 (提取音訊)**
    ```bash
    ffmpeg -i "影片檔名.MP4" -vn -ac 1 -ar 16000 -b:a 32k -f mp3 "影片_compressed.mp3"
    ```

2.  **執行轉錄**
    ```bash
    .venv/bin/python 01-system/tools/stt/audio_transcribe/transcribe.py \
      --input "影片_compressed.mp3" \
      --engine elevenlabs
    ```

### 情境 B：批次自動化處理 (推薦 ⭐)

適合處理整個資料夾、外接硬碟中的大量影片。

1.  **編輯腳本設定**
    打開 `scripts/batch_video_to_text.sh`，修改 `SOURCE_DIR`：
    ```bash
    SOURCE_DIR="/Volumes/Samsung-T7/我的影片資料夾"
    ```

2.  **執行腳本**
    ```bash
    ./scripts/batch_video_to_text.sh
    ```
    *   腳本會自動掃描、壓縮、轉錄，並跳過已處理的檔案。

## 📂 輸出結果

所有檔案會自動儲存在：`03-outputs/audio_transcribe/[影片檔名]/`

包含：
*   `_formatted.srt`：**字幕檔** (已優化時間軸，可直接用於 YouTube)
*   `_formatted.txt`：**文字稿** (已去除口語贅字，適合閱讀)
*   `_metadata.yaml`：處理資訊

## 💡 常見問題與技巧

*   **多帳號切換**：不用手動換！只要在 `API-Keys.md` 填入多組 Key，程式遇到額度不足會自動切換下一組。
*   **超長錄音 (3小時+)**：ElevenLabs 支援度很好。如果想省錢用 Groq，工具也內建了自動切割功能，不用擔心檔案太大。
*   **Mac mini 同步**：使用外接硬碟的 `scripts/setup.sh` 一鍵更新環境。
