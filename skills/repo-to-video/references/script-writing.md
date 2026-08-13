# Script Writing and Manifest Schema

## Structure (target 60-180 s)

| Beat         | Time        | Content                                                        |
| ------------ | ----------- | -------------------------------------------------------------- |
| title        | 3-5 s       | Repo name + one-line value proposition                         |
| hook         | 8-15 s      | Surprising fact or question that makes the viewer stay         |
| what it is   | 10-20 s     | One-sentence pitch + the problem it solves                     |
| how it works | 35-80 s     | 3-6 scenes walking real architecture/flow/demo, one idea each  |
| insights     | 10-25 s     | 2-4 numbers or design insights from analysis/report.json       |
| outro        | 5-10 s      | Repo link, stars/license, call to action                       |

## Pacing

- English: 150-160 words per minute. 60 s ~= 155 words, 120 s ~= 310 words,
  180 s ~= 465 words.
- Japanese/Chinese: ~2.8-3.5 characters per second. 120 s ~= 350-420 chars.
- Each scene 5-20 s; a 5 s scene carries 12-20 English words.

## Rules

- Show, don't tell: narration explains what the on-screen visual demonstrates.
- No filler words ("um", "basically", "really"); no unverified claims.
- Ground the script in artifacts: file names, function names, real numbers
  (stars, LOC, modules, commits, benchmarks) from analysis/report.json.
- One idea per scene; each scene has exactly one primary visual.
- Match language to the user's request (default English).

## Manifest schema

```json
{
  "repo": {
    "name": "my-project", "url": "https://github.com/o/my-project",
    "stars": 12300, "license": "MIT", "language": "Python"
  },
  "meta": {
    "language": "en", "engine": "remotion", "fps": 30,
    "width": 1920, "height": 1080
  },
  "scenes": [
    {
      "id": "01-title",
      "type": "title",
      "title": "My Project: scale without the ops",
      "narration": "My Project turns a thousand servers into a single Python object.",
      "duration_s": 8,
      "visuals": [
        {"kind": "diagram", "src": "diagrams/architecture.png", "caption": "One control plane, many workers"}
      ],
      "points": [],
      "speaker": "Ryan",
      "instruct": "enthusiastic, clear"
    }
  ],
  "voiceover": {"engine": "edge", "file": "audio/voiceover.mp3"},
  "render": {"output": "video/out.mp4"}
}
```

Scene types: `title`, `hook`, `architecture`, `datamodel`, `flow`, `demo`,
`code`, `insight`, `outro`.

Visual kinds: `image` (generic full-bleed image), `diagram`, `screenshot`,
`code` (renders `visual.code` as a monospace block, or `visual.src` as an
image if no inline code).

Optional per-scene fields:

- `points`: bullet list rendered for `hook`/`insight`/`flow` scenes.
- `speaker` / `instruct`: TTS speaker and emotion hint (Qwen3 only).
- `audio`: per-scene audio path (default `audio/scene-<id>.mp3`, computed by
  tts.py).

Validate with:

```bash
python <skill>/scripts/estimate_duration.py --manifest manifest.json
```
