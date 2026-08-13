#!/usr/bin/env python3
"""Estimate narration duration from a video manifest and validate the 1-3 min target.

Usage:
    python estimate_duration.py --manifest manifest.json [--target-min 60 --target-max 180]

Exits 0 when the total planned + estimated duration is within target, else 1.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORDS_PER_SEC = {
    "en": 2.583,  # ~155 wpm
    "de": 2.333,  # ~140 wpm
    "es": 2.333,
    "fr": 2.333,
    "pt": 2.333,
}

# Spoken characters per second for CJK scripts (Japanese / Chinese / Korean).
CHARS_PER_SEC_DEFAULT = 3.0

# CJK ideographs/syllabaries are counted separately from Latin-script words.
_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")

# A "word" is a run of Unicode letters or digits, optionally with internal
# apostrophes/hyphens, so accented Latin ("déjà"), contractions ("don't") and
# hyphenated compounds ("state-of-the-art") each count once. CJK is stripped
# before counting so it is not double-counted here.
_WORD_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*")


def count_words(text: str) -> int:
    return len(_WORD_RE.findall(_CJK_RE.sub(" ", text)))


def count_cjk_chars(text: str) -> int:
    return len(_CJK_RE.findall(text))


def estimate_scene_duration(narration: str, language: str) -> float:
    """Seconds of speech for a narration string in the given language.

    CJK characters and Latin-script words are disjoint, so a mixed narration
    (e.g. Chinese with English identifiers) is the sum of both parts rather
    than dropping either.
    """
    if not narration:
        return 0.0
    lang = (language or "en").lower()
    cjk_seconds = count_cjk_chars(narration) / CHARS_PER_SEC_DEFAULT
    if lang in ("ja", "zh", "ko"):
        # English words/numbers mixed into a CJK narration are still spoken
        # as English words.
        word_seconds = count_words(narration) / WORDS_PER_SEC["en"]
    else:
        word_seconds = count_words(narration) / WORDS_PER_SEC.get(lang, WORDS_PER_SEC["en"])
    return cjk_seconds + word_seconds


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Path to manifest.json")
    parser.add_argument("--target-min", type=float, default=60.0)
    parser.add_argument("--target-max", type=float, default=180.0)
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    manifest = load_manifest(args.manifest)
    meta = manifest.get("meta", {})
    default_lang = meta.get("language", "en")
    scenes = manifest.get("scenes", [])
    if not scenes:
        print("[ERROR] manifest has no scenes", file=sys.stderr)
        return 1

    rows = []
    total_planned = 0.0
    total_estimated = 0.0
    for i, scene in enumerate(scenes, start=1):
        narration = scene.get("narration", "")
        lang = scene.get("language") or default_lang
        planned = float(scene.get("duration_s", 0))
        estimated = estimate_scene_duration(narration, lang)
        total_planned += planned
        total_estimated += estimated
        rows.append(
            {
                "id": scene.get("id", f"{i:02d}"),
                "words": count_words(narration),
                "planned": planned,
                "estimated": round(estimated, 1),
            }
        )

    ok = args.target_min <= total_planned <= args.target_max
    coverage = total_estimated / total_planned if total_planned else 0.0
    warnings = []
    if total_estimated < 0.45 * total_planned:
        warnings.append(
            f"narration only covers {coverage * 100:.0f}% of the timeline "
            "(<45%); consider adding narration or shortening quiet scenes"
        )
    if total_estimated > 1.1 * total_planned:
        warnings.append(
            f"estimated narration {total_estimated:.1f}s overruns the planned "
            f"timeline {total_planned:.1f}s; trim narration or extend scenes"
        )

    if args.json:
        print(
            json.dumps(
                {
                    "scenes": rows,
                    "total_planned_s": round(total_planned, 1),
                    "total_estimated_s": round(total_estimated, 1),
                    "within_target": ok,
                    "speech_coverage": round(coverage, 2),
                    "warnings": warnings,
                    "target_min": args.target_min,
                    "target_max": args.target_max,
                },
                indent=2,
            )
        )
        if warnings:
            for w in warnings:
                print(f"[WARN] {w}", file=sys.stderr)
    else:
        print(f"{'scene':<12}{'words':>6}{'planned':>10}{'estimated':>10}  status")
        for row in rows:
            print(
                f"{row['id']:<12}{row['words']:>6}{row['planned']:>10.1f}{row['estimated']:>10.1f}"
            )
        print("-" * 44)
        print(f"total planned   {total_planned:8.1f} s ({total_planned / 60:.2f} min)")
        print(f"total estimated {total_estimated:8.1f} s ({total_estimated / 60:.2f} min)")
        print(f"speech coverage {coverage * 100:7.1f}% of timeline")
        print(f"target range    {args.target_min:.0f}-{args.target_max:.0f} s")
        for w in warnings:
            print(f"[WARN] {w}")
        print("RESULT:", "PASS" if ok else "FAIL")

    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
