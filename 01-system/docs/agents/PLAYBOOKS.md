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
      - 03-outputs/youtube_downloader/downloads/

- "ytdlp":
    intent: Alias for downloading youtube video.
    steps:
      - tool: youtube_downloader
        arguments:
          url: "{{url}}"
    outputs:
      - 03-outputs/youtube_downloader/downloads/

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
      - command: ./venv/bin/python scripts/groq_stt_tool.py --input "{{file_path}}" --mode single
    outputs:
      - "{{file_path}}.txt"
      - "{{file_path}}.srt"

- "project transcription":
    intent: Transcribe all audio in a folder and compile into a markdown file.
    steps:
      - command: ./venv/bin/python scripts/groq_stt_tool.py --input "{{folder_path}}" --mode project
    outputs:
      - "{{folder_path}}/project_compilation.md"
