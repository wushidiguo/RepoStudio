# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-13

### Added

- Ken Burns pan/zoom on screenshots, count-up animation for insight numbers,
  and word-by-word burn-in captions in the Remotion template.
- `.srt` subtitle export via `scripts/export_srt.py`.
- EBU R128 loudness normalization and sentence-level pacing in `tts.py`.
- Python project metadata (`pyproject.toml`) with `uv` support and a locked
  `uv.lock` for reproducible environments.
- Unit tests for duration estimation, capture name slugging, and TTS manifest
  metadata, plus a `pytest`/`ruff` setup.
- GitHub Actions CI (Python lint/test + Remotion TypeScript typecheck).
- Open-source community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, issue/PR templates, and `.gitattributes`.
- Deterministic fonts in the Remotion template via `@remotion/google-fonts`.

### Fixed

- Word counting now handles accented Latin text ("déjà" no longer splits).
- Mixed CJK/English narration is estimated as the sum of both parts instead of
  dropping the English words.
- Capture route names are slugified into safe filenames.
- `edge-tts` synthesis retries with exponential backoff on network errors.
- `tts.py` writes the top-level `voiceover` field back into `manifest.json`.
- The Remotion template no longer silently drops a third (or later) visual.
- Total duration is computed in one place (`duration.ts`) instead of two.

## [0.1.0] - 2026-08-13

Initial release: the `repo-to-video` Codex skill, installer, bundled Remotion
template, and reference playbooks.
