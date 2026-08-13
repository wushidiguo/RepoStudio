# TTS Voiceover

## Engine selection

| Engine | Quality | Requirements | Notes                              |
| ------ | ------- | ------------ | ----------------------------------- |
| qwen3  | Best    | Python 3.9+, GPU (CUDA), ~3.5 GB model download | Qwen3-TTS-12Hz-1.7B-CustomVoice, 9 preset speakers, instruction control |
| edge   | Good    | Python 3.8+, network | edge-tts, fast, CPU-only, no API key |

## Qwen3-TTS (preferred)

Install:

```bash
python -m pip install qwen-tts torch torchaudio soundfile
```

`flash-attn` is optional (slower without it). The model downloads from
HuggingFace on first use; in restricted networks use ModelScope:

```bash
python -m pip install modelscope
modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --local_dir ./models
```

Preset speakers: Vivian, Serena, Uncle_Fu, Dylan, Eric (Chinese); Ryan, Aiden
(English); Ono_Anna (Japanese); Sohee (Korean). The `instruct` field steers
emotion, e.g. "very happy and enthusiastic" or "calm and professional".

## edge-tts (fallback)

```bash
python -m pip install edge-tts
```

Default voices by language (override with `--voice`):

| Language | Voice                        |
| -------- | ---------------------------- |
| en       | en-US-ChristopherNeural      |
| ja       | ja-JP-KeitaNeural            |
| zh       | zh-CN-YunxiNeural            |
| ko       | ko-KR-InJoonNeural           |

## Generate

```bash
python <skill>/scripts/tts.py --manifest manifest.json --engine qwen3 --language en --speaker Ryan
python <skill>/scripts/tts.py --manifest manifest.json --engine edge --language en
```

Outputs `audio/scene-<NN>.mp3` per scene plus concatenated
`audio/voiceover.mp3` (ffmpeg required for concatenation). The script prints
actual per-scene durations.

The edge engine splits long narrations into sentences and inserts a short
silence between them for more natural pacing (tune with `--pause-ms`, default
220). The concatenated `voiceover.mp3` is then loudness-normalized to EBU R128
(`-16 LUFS`) so volume stays consistent across scenes and engines.

## Timing check

If a scene's TTS duration exceeds its planned `duration_s` by more than 20%,
trim the narration or extend the scene duration in manifest.json, then re-run
`<skill>/scripts/estimate_duration.py` and `<skill>/scripts/tts.py`. Per-scene audio is mounted at the
cumulative offset, so scene durations and audio stay in sync automatically.
