# Playbooks

Playbooks are short natural-language phrases or aliases that map to specific intents and workflows.
The agent must check this file first on every task to see if a known playbook exists for the user's request.
- "download youtube video":
    intent: Download a video from YouTube with subtitles.
    steps:
      - tool: youtube_downloader
        arguments:
          url: "{{url}}"
    outputs:
      - 03-outputs/下載存檔/

- "ytdlp":
    intent: Alias for downloading youtube video.
    steps:
      - tool: youtube_downloader
        arguments:
          url: "{{url}}"
    outputs:
      - 03-outputs/下載存檔/

## Format
- **Intent**: <Description of the goal>
  - **Trigger**: "<Phrase or pattern>"
  - **Steps**:
    1. <Step 1>
    2. <Step 2>
  - **Expected Output**: <Path to artifact>

## Active Playbooks

- "transcribe audio":
    intent: Transcribe a single audio file using Groq STT (Whisper).
    steps:
      - tool: audio_transcribe
        arguments:
          input: "{{file_path}}"
          engine: "groq"
    outputs:
      - 03-outputs/轉錄檔案/{{basename}}_{{timestamp}}/

- "project transcription":
    intent: Transcribe all audio in a folder and compile into a markdown file.
    steps:
      - command: .venv/bin/python 01-system/tools/stt/audio_transcribe/transcribe.py --input "{{folder_path}}" --engine groq --mode project
    outputs:
      - "{{folder_path}}/project_compilation.md"

- "transcribe audio with scribe":
    intent: Transcribe a single audio file using ElevenLabs Scribe v1.
    steps:
      - tool: audio_transcribe
        arguments:
          input: "{{file_path}}"
          engine: "elevenlabs"
    outputs:
      - 03-outputs/轉錄檔案/{{basename}}_{{timestamp}}/

- "project transcription with scribe":
    intent: Transcribe all audio in a folder using ElevenLabs Scribe v1 and compile into a markdown file.
    steps:
      - command: .venv/bin/python 01-system/tools/stt/audio_transcribe/transcribe.py --input "{{folder_path}}" --engine elevenlabs --mode project
    outputs:
      - "{{folder_path}}/project_compilation.md"

- "轉錄" / "transcribe":
    intent: 使用專業轉錄工具處理音檔（雙引擎、格式化、詞典）
    steps:
      - command: .venv/bin/python 01-system/tools/stt/audio_transcribe/transcribe.py --input "{{file_path}}"
    outputs:
      - 03-outputs/轉錄檔案/{{basename}}_{{timestamp}}/
    notes: 工具會詢問選擇 STT 引擎，並產生原始 + 格式化版本的 SRT 和 TXT

- "YouTube 轉字幕" / "yt2sub":
    intent: 一鍵下載 YouTube 音檔並轉錄為字幕
    steps:
      - command: .venv/bin/python scripts/youtube_to_subtitle.py --url "{{youtube_url}}"
    outputs:
      - 03-outputs/轉錄檔案/{{video_title}}_{{timestamp}}/
    notes: 自動下載 MP3 + 轉錄 + 格式化，完成後清理音檔


