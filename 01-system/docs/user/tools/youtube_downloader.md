# YouTube 下載器 (YTDLP)
**類別**：media
**版本**：v0.1 （更新日期：2025-11-23）

## 能力總覽
- 下載 YouTube 影片（最高畫質）。
- 自動下載字幕（支援繁體中文、簡體中文、英文）。
- 支援 Playbook 快速指令。

## 參數說明
- `url`：YouTube 影片網址（必填）。

## 常見用法（逐步）
1. 確保已安裝 `yt-dlp`（本工具依賴此套件）。
2. 使用 Playbook 指令或直接呼叫工具。

## 範例
- **快速範例**：
  - "download youtube video https://youtu.be/..."
  - "ytdlp https://youtu.be/..."
  
  產出於 `03-outputs/youtube_downloader/downloads/`

## 輸入 / 輸出路徑
- 輸入來源：無（直接使用網址）。
- 產出位置：`03-outputs/youtube_downloader/downloads/`

## 風險與權限
- 需網路連線。
- 請遵守 YouTube 使用條款與版權規範。

## 故障排除
- 若下載失敗，請確認網址是否正確。
- 若無字幕，可能是該影片未提供指定語言的字幕。

## 版本與更新紀錄
- v0.1（2025-11-23）：初版建立。
