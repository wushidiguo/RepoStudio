# AGENTS.md

Orientation for AI coding agents working in this repository. Read this before
making changes; it captures the invariants and commands so you don't have to
re-discover them.

## What this is

**RepoStudio** is a [Codex](https://openai.com/codex/) skill that turns any
GitHub repository into a 1–3 minute narrated explainer video. The pipeline is:
clone → deep analysis → screenshots → diagrams → timed narration script →
TTS voiceover → render MP4.

There are two independent runtimes, plus prose playbooks that wire them
together:

- **Python scripts** — `skills/repo-to-video/scripts/` (analysis helpers,
  duration estimation, screenshot capture, TTS, SRT export).
- **Remotion template** — `skills/repo-to-video/assets/remotion-template/`
  (a TypeScript/React renderer driven by `manifest.json`).
- **Playbooks** — `skills/repo-to-video/SKILL.md` (7-phase workflow + quality
  gates) and `skills/repo-to-video/references/*.md` (per-phase detail).

Two render engines are supported: **Remotion** (default, deterministic) and
**HyperFrames** (optional, when the environment provides it).

## Core invariant: `manifest.json` is the single source of truth

The pipeline contract is `manifest.json` (schema documented in
`references/script-writing.md`). It drives every downstream stage:

- `estimate_duration.py` — validates the 60–180 s target.
- `tts.py` — generates per-scene audio + concatenated voiceover.
- `export_srt.py` — derives an `.srt` subtitle file.
- the Remotion template — `src/types.ts`, `src/Video.tsx`, `src/Root.tsx`.

**If you change the manifest schema, update ALL of these together:**
`references/script-writing.md`, `src/types.ts`, `tts.py`, `export_srt.py`,
and the tests under `tests/`.

Scene types: `title`, `hook`, `architecture`, `datamodel`, `flow`, `demo`,
`code`, `insight`, `outro`. Visual kinds: `image`, `diagram`, `screenshot`,
`code` (inline `visual.code`) plus optional `visual.src`/`visual.caption`.

Per-job workspace layout (see SKILL.md "Workspace contract"):
`repo/ analysis/ captures/ diagrams/ script.md manifest.json audio/ video/`.
All skill scripts run from the workspace root (the dir containing
`manifest.json`).

## Commands

### Python (uv)

```bash
uv sync --extra dev    # create .venv with edge-tts, playwright, pytest, ruff
uv run pytest          # run the test suite
uv run ruff check .    # lint
uv run ruff format .   # format
```

`.python-version` pins Python 3.12 and `uv.lock` is committed (reproducible
env). Plain-pip fallback: `pip install -r requirements.txt -r requirements-dev.txt`.

### Remotion template

```bash
cd skills/repo-to-video/assets/remotion-template
npm install
npm run build           # tsc --noEmit (typecheck)
npm run dev             # remotion studio
npx remotion render src/index.ts Explainer out.mp4
```

`package-lock.json` is committed; Node >= 18.

### Skill scripts (from a job workspace root)

```bash
python <skill>/scripts/estimate_duration.py --manifest manifest.json
python <skill>/scripts/tts.py --manifest manifest.json --engine edge [--pause-ms 220]
python <skill>/scripts/capture_screens.py --config captures.json
python <skill>/scripts/export_srt.py --manifest manifest.json
```

`estimate_duration.py` exits non-zero when outside the 60–180 s target;
`tts.py` chooses `edge` (CPU, network) or `qwen3` (GPU).

## Where things live

- `skills/repo-to-video/SKILL.md` — entry point: workflow + quality gates.
- `skills/repo-to-video/references/` — analysis, screenshots, diagrams,
  script-writing, tts, rendering playbooks.
- `skills/repo-to-video/scripts/` — `estimate_duration.py`, `tts.py`,
  `capture_screens.py`, `export_srt.py`.
- `skills/repo-to-video/assets/remotion-template/` — the renderer.
- `skills/repo-to-video/agents/openai.yaml` — Codex UI metadata.
- `tests/` — pytest suite; `conftest.py` adds the scripts dir to `sys.path`.
- `install.ps1` / `install.sh` — copy the skill into `$CODEX_HOME/skills`,
  optionally install prerequisites.
- Root docs: `README.md` (English, default), `README.zh-CN.md`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`,
  `AGENTS.md` (this file).

## Remotion template internals

- `src/types.ts` — `Visual` / `Scene` / `Manifest` types.
- `src/duration.ts` — `getFps`, `getSceneDurationFrames`,
  `getTotalDurationFrames`. **The single place for duration math** — never
  re-implement it in `Root.tsx` or `Video.tsx`.
- `src/fonts.ts` — loads Inter + JetBrains Mono via `@remotion/google-fonts`
  (deterministic regardless of machine fonts).
- `src/Root.tsx` — registers the `Explainer` Composition; imports
  `../public/manifest.json`.
- `src/Video.tsx` — renders scenes as `Sequence`s with per-scene audio.
- `src/scenes.tsx` — `SceneCard` + `FadeIn`, `KenBurnsImage`, `VisualItem`/
  `VisualBlock`, `PointsCard`, `CountUp`, `NarrationCaption`, `Caption`, `Chip`.

## Testing & CI

- GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR:
  - Python job: `uv run ruff check .`, `uv run ruff format --check .`,
    `uv run pytest`.
  - Remotion job: `npm ci` + `npm run build` (`tsc --noEmit`).
- Keep ruff green; first-party modules are configured in `pyproject.toml`
  (`estimate_duration`, `capture_screens`, `export_srt`, `tts`).
- When touching `scripts/`, add a test under `tests/`.

## Gotchas (learned the hard way)

- On Windows, `python`/`python3` may be the Microsoft Store stub (prints
  nothing). Use `uv` (`uv run python ...`), or `py`.
- Per-scene audio mounts at cumulative offsets; if a scene's narration is
  longer than its `duration_s`, it bleeds into the next scene. `tts.py`
  prints real durations — trim narration or extend the scene if overrun.
- The first Remotion render downloads a headless Chrome; `@remotion/google-fonts`
  fetches fonts at bundle/render time (cached after the first run).
- `edge-tts` needs network (tts.py retries with exponential backoff and inserts
  inter-sentence pauses); `qwen3` needs a GPU + model download.
- The concatenated `voiceover.mp3` is loudness-normalized to EBU R128
  (`-16 LUFS`).
- Lockfiles (`uv.lock`, `package-lock.json`) are committed. Gitignored:
  `.venv/`, `node_modules/`, `video/`, `out.mp4`, `renders/`, caches.
- `sample-output.mp4` (~4.9 MB) is committed intentionally (already in
  history). Prefer GitHub Releases for future large assets.
- Quality gates (SKILL.md) must pass before delivery: 60–180 s total, non-empty
  voiceover, ≥1 screenshot and ≥1 diagram used, every referenced visual exists,
  `ffprobe` confirms 60–180 s.

## Change checklist

- Manifest schema → `script-writing.md` + `src/types.ts` + `tts.py` +
  `export_srt.py` + tests.
- New scene layout / motion → `src/scenes.tsx`, then verify with a smoke render.
- Script behavior → `scripts/*.py` + `tests/` + the matching `references/*.md`.
- User-facing docs → keep `README.zh-CN.md` in sync with `README.md`, and add a
  `CHANGELOG.md` entry.
