#!/usr/bin/env python3
"""Generate per-scene voiceover audio from a video manifest.

Engines:
  edge  - edge-tts (fast, CPU-only, needs network)
  qwen3 - Qwen3-TTS-12Hz-1.7B-CustomVoice (best quality, needs GPU + model download)

Usage:
    python tts.py --manifest manifest.json --engine edge [--language en] [--voice en-US-ChristopherNeural]
    python tts.py --manifest manifest.json --engine qwen3 [--language en] [--speaker Ryan] [--device cuda]

Outputs:
    audio/scene-<id>.mp3  (one per scene with narration)
    audio/voiceover.mp3   (concatenated, requires ffmpeg)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_VOICES = {
    "en": "en-US-ChristopherNeural",
    "ja": "ja-JP-KeitaNeural",
    "zh": "zh-CN-YunxiNeural",
    "ko": "ko-KR-InJoonNeural",
}

DEFAULT_SPEAKERS = {
    "en": "Ryan",
    "zh": "Dylan",
    "ja": "Ono_Anna",
    "ko": "Sohee",
}


def find_ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def find_ffprobe() -> str | None:
    return shutil.which("ffprobe")


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def mp3_duration(path: Path) -> float | None:
    ffprobe = find_ffprobe()
    if not ffprobe:
        return None
    try:
        out = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return float(out.stdout.strip()) if out.stdout.strip() else None
    except (subprocess.SubprocessError, ValueError):
        return None


def concat_mp3s(paths: list[Path], output: Path) -> bool:
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("[WARN] ffmpeg not found; skipped concatenating voiceover.mp3", file=sys.stderr)
        return False
    if not paths:
        return False
    list_file = output.with_suffix(".txt")
    list_file.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in paths) + "\n",
        encoding="utf-8",
    )
    try:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c",
                "copy",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return output.exists() and output.stat().st_size > 0
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] concat failed: {exc.stderr[-800:]}", file=sys.stderr)
        return False
    finally:
        list_file.unlink(missing_ok=True)


def edge_synthesize(text: str, voice: str, output: Path) -> None:
    import edge_tts

    asyncio.run(edge_tts.Communicate(text, voice).save(str(output)))


def qwen3_synthesize(text: str, language: str, speaker: str, instruct: str | None,
                     device: str, output: Path, model) -> Path:
    import soundfile as sf
    import torch

    if model is None:
        raise RuntimeError("qwen3 model not loaded")
    wavs, sr = model.generate_custom_voice(
        text=text,
        language=language,
        speaker=speaker,
        instruct=instruct or "",
    )
    wav_path = output.with_suffix(".wav")
    sf.write(str(wav_path), wavs[0], sr)
    ffmpeg = find_ffmpeg()
    if ffmpeg:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(wav_path),
                "-codec:a",
                "libmp3lame",
                "-qscale:a",
                "2",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        wav_path.unlink(missing_ok=True)
        return output
    else:
        print("[WARN] ffmpeg not found; kept .wav instead of .mp3", file=sys.stderr)
        return wav_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--engine", required=True, choices=["edge", "qwen3"])
    parser.add_argument("--language", default=None, help="Default language (en/ja/zh/ko)")
    parser.add_argument("--voice", default=None, help="edge-tts voice name")
    parser.add_argument("--speaker", default=None, help="Qwen3 preset speaker")
    parser.add_argument("--device", default=None, help="Qwen3 device (cuda/cpu); defaults to CPU")
    parser.add_argument("--output-dir", default="audio", help="Output directory")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    manifest = load_manifest(args.manifest)
    meta = manifest.get("meta", {})
    default_lang = (args.language or meta.get("language", "en")).lower()
    engine = args.engine

    if engine == "edge":
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            print(
                "[ERROR] edge-tts is not installed. Run: python -m pip install edge-tts",
                file=sys.stderr,
            )
            return 1
    elif engine == "qwen3":
        try:
            from qwen_tts import Qwen3TTSModel  # noqa: F401
        except ImportError:
            print(
                "[ERROR] qwen-tts is not installed. Run: python -m pip install qwen-tts torch torchaudio soundfile",
                file=sys.stderr,
            )
            return 1

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = None
    if engine == "qwen3":
        import torch
        from qwen_tts import Qwen3TTSModel

        print(f"[INFO] loading Qwen3-TTS-12Hz-1.7B-CustomVoice on {args.device} ...")
        load_kwargs = {}
        if args.device:
            load_kwargs["device_map"] = args.device
            load_kwargs["dtype"] = torch.bfloat16
        else:
            load_kwargs["device_map"] = "cpu"
            load_kwargs["dtype"] = torch.float32
        model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
            **load_kwargs,
        )

    scene_paths: list[Path] = []
    for i, scene in enumerate(manifest.get("scenes", []), start=1):
        text = (scene.get("narration") or "").strip()
        if not text:
            continue
        lang = (scene.get("language") or default_lang).lower()
        scene_id = scene.get("id", f"{i:02d}")
        output = out_dir / f"scene-{scene_id}.mp3"

        if engine == "edge":
            voice = (
                args.voice
                or DEFAULT_VOICES.get(lang)
                or DEFAULT_VOICES["en"]
            )
            print(f"[edge] {scene_id}: {text[:60]}... -> {output}")
            edge_synthesize(text, voice, output)
            final_output = output
        else:
            speaker = args.speaker or scene.get("speaker") or DEFAULT_SPEAKERS.get(lang, "Ryan")
            instruct = scene.get("instruct")
            print(f"[qwen3] {scene_id}: {text[:60]}... -> {output}")
            final_output = qwen3_synthesize(
                text, lang, speaker, instruct, args.device, output, model
            )

        if final_output.exists():
            scene["audio"] = final_output.relative_to(out_dir.parent).as_posix()
            scene_paths.append(final_output)
            dur = mp3_duration(final_output)
            print(f"        duration: {dur if dur is not None else 'unknown'} s")
        else:
            print(f"[WARN] no output for {scene_id}", file=sys.stderr)

    if scene_paths:
        voiceover = out_dir / "voiceover.mp3"
        if concat_mp3s(scene_paths, voiceover):
            dur = mp3_duration(voiceover)
            print(f"[OK] voiceover: {voiceover} ({dur if dur is not None else 'unknown'} s)")
        manifest_path = Path(args.manifest)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[OK] updated {manifest_path} with per-scene audio paths")

    if not scene_paths:
        print("[WARN] no scenes had narration; nothing generated", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
