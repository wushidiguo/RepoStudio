#!/usr/bin/env python3
"""Export an SRT subtitle file from a video manifest.

Usage:
    python export_srt.py --manifest manifest.json [--output subtitles.srt]

Cues are derived from each scene's narration and planned duration, so timing
matches the manifest even before audio is generated. Long sentences stay as a
single cue; the skill's pacing rules keep sentences short by design.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tts import split_sentences


def format_timestamp(seconds: float) -> str:
    """Format seconds as an SRT timestamp (HH:MM:SS,mmm)."""
    if seconds < 0:
        seconds = 0.0
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(manifest: dict) -> str:
    """Build SRT text from a manifest, one cue per narration sentence."""
    scenes = manifest.get("scenes", [])
    cues: list[str] = []
    cursor = 0.0
    index = 1
    for scene in scenes:
        duration = float(scene.get("duration_s", 0) or 0)
        narration = (scene.get("narration") or "").strip()
        if narration and duration > 0:
            sentences = split_sentences(narration) or [narration]
            total_chars = sum(len(sentence) for sentence in sentences) or 1
            for sentence in sentences:
                sentence_duration = duration * (len(sentence) / total_chars)
                end = cursor + sentence_duration
                cues.append(
                    f"{index}\n{format_timestamp(cursor)} --> {format_timestamp(end)}\n{sentence}"
                )
                index += 1
                cursor = end
        else:
            cursor += duration
    return "\n\n".join(cues) + ("\n" if cues else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=None, help="Output .srt path")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    srt = build_srt(manifest)
    if not srt.strip():
        print("[WARN] no narration found; nothing exported", file=sys.stderr)
        return 2

    output = args.output or (args.manifest.parent / "subtitles.srt")
    output.write_text(srt, encoding="utf-8")
    print(f"[OK] wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
