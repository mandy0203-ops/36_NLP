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

