# System Memory

Canonical log of all major agent activities and state changes.
Format: `YYYY-MM-DD — Title :: change | impact | artifacts`

2025-11-23 — Bootstrap Workspace :: Scaffolding and spec migration | Initialized workspace structure and canonical docs | `AGENTS.md`, `01-system/`
2025-11-23 — YouTube 8K Download :: Downloaded video in 8K resolution | User requested 8K video download | `Youtube Download/Japan in 8K ULTRA HD - Land of The Rising Sun (60 FPS).mp4`
2025-11-23 — Audio to SRT Conversion :: Converted audio to SRT with Traditional Chinese | Added `prompt="繁體中文"` to Groq STT tool | `02-inputs/EP49_Friends_Boundaries.srt`, `02-inputs/EP49_Friends_Boundaries.txt`
2025-11-23 — AGENTS.md Update :: Added Traditional Chinese subtitle requirement | Enforced繁體中文 for all generated subtitles | `AGENTS.md`
2025-11-23 — SRT Merge Tool :: Created tool to merge teaser and corrected subtitles | Merged preamble with reference file | `scripts/merge_srt.py`, `02-inputs/EP49_Friends_Boundaries.srt`
2025-11-23 — STT Tool Enhancement :: Added chunking and retry logic for large files | Handles files > 25MB and rate limits | `scripts/groq_stt_tool.py`
2025-11-23 — STT Improvement Plan :: Documented smart compression strategy | Future: auto-compress large files before transcription (8kHz, 24k bitrate for files > 20MB) | Pending implementation
2025-11-24 — Refactor AGENTS.md :: extracted templates and simplified rules | improved readability and agent efficiency | `AGENTS.md`, `01-system/docs/templates/`
2025-11-25 — Video Download Preference :: Enforced 1080p MP4 default | User requested strict 1080p MP4 format for all downloads | `AGENTS.md`, `STATE.md`
2025-11-26 — Language Protocol Update :: Enforced Chinese Filenames | User requested file names be in Traditional Chinese where possible | `AGENTS.md`
2025-11-26 — Documentation Update :: Created User Manual | Compiled TARS-001 User Manual in Traditional Chinese | `01-system/docs/TARS_使用說明書.md`
2025-11-26 — Workspace Reorganization :: Sinicized Directory Structure | Renamed user-facing folders to Traditional Chinese and updated tool configs | `02-inputs/`, `03-outputs/`, `PLAYBOOKS.md`, `registry.yaml`
2025-11-26 — Course Download :: Claude Code Course (Partial) | Downloaded 3 videos and notes. Failed to access lessons 4+ due to site errors. | `03-outputs/下載存檔/Claude_Code_Gemini_CLI_入門/`
2025-11-26 — Course Download :: Claude Code Course (Batch 2) | Successfully downloaded lessons 4 & 5 using anti-bot navigation strategy. | `03-outputs/下載存檔/Claude_Code_Gemini_CLI_入門/`
2025-11-26 — Course Download :: Claude Code Course (Batch 3) | Downloaded Codex CLI lessons (7-9). Windows section skipped due to access issues. | `03-outputs/下載存檔/Claude_Code_Gemini_CLI_入門/`
2025-11-26 — Task Completed :: Claude Code Course Backup | User confirmed completion. Windows section skipped. Final cleanup performed. | `03-outputs/下載存檔/Claude_Code_Gemini_CLI_入門/`
