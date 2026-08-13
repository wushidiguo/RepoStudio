---
name: repo-to-video
description: >
  Turn any GitHub repository into a 1-3 minute narrated explainer video.
  Use when the user wants a video, explainer, demo, or walkthrough of a GitHub
  project or codebase, or asks to make/render/produce a video from a repo URL.
  The pipeline clones the repo, performs deep codebase analysis (codebase-memory-mcp
  or ripgrep-based fallback), captures screenshots, generates diagrams, writes a
  timed narration script, synthesizes a voiceover (Qwen3-TTS or edge-tts), and
  renders the final MP4 with Remotion or HyperFrames.
---

# Repo to Video

Turn any GitHub repository into a 1-3 minute narrated explainer video. The whole
pipeline runs from a single user request: `Use $repo-to-video to make an explainer
video of <repo-url>`.

## Workflow at a glance

1. Clone the repository.
2. Analyze the codebase deeply (not just the README).
3. Capture key screens (web pages, CLI sessions, or code).
4. Draw 2-4 explanatory diagrams.
5. Write a timed 1-3 minute narration script (manifest.json).
6. Synthesize the voiceover with TTS.
7. Render the final video with Remotion or HyperFrames.

## Workspace contract

Create one output directory per job and keep this layout (paths below are
relative to it):

```text
<repo-slug>/
├── repo/                  # shallow clone of the target repository
├── analysis/              # analysis/report.json + supporting notes
├── captures/              # screenshot PNGs (1920x1080)
├── diagrams/              # diagram HTML + exported PNGs (1920x1080)
├── script.md              # narration script (human-readable)
├── manifest.json          # single source of truth for the video
├── audio/                 # per-scene MP3s + voiceover.mp3
└── video/                 # render project (Remotion or HyperFrames) + final MP4
```

`manifest.json` is the contract between every phase. Write it after the script
phase, then let TTS and rendering read it. Schema: see
[references/script-writing.md](references/script-writing.md#manifest-schema).

## Phase 1 - Clone

Clone into `repo/`:

- GitHub URL, gh authenticated: `gh repo clone <owner/repo> repo -- --depth 1`
  (or `gh repo clone <url> repo -- --depth 1`).
- Otherwise: `git clone --depth 1 <url> repo`.
- If the user already has the repository locally, copy/symlink it instead and
  skip the network.

Note the checked-out commit, default branch, and whether the clone is shallow.
Prefer the default branch unless the user asks for a tag/branch.

## Environment note

- Commands below assume a working Python 3.9+ on PATH. If `python` is a
  non-functional Windows Store stub (prints nothing), try `py`, `python3`, or
  the Codex desktop bundled runtime (`codex_app.load_workspace_dependencies`)
  and use that interpreter consistently.
- All commands run from the workspace root (the directory containing
  `repo/`, `manifest.json`, etc.) so relative paths resolve.

## Phase 2 - Deep analysis

Produce `analysis/report.json` with: tech stack, entry points, module map, data
flow, key files, metrics, and 3-8 "insight candidates" (facts a viewer would
find surprising or valuable). Base every insight on code you actually read, not
just README claims.

Read [references/analysis.md](references/analysis.md) before analyzing. It
covers the codebase-memory-mcp workflow (index + 15 graph tools), and a
ripgrep/cloc/git fallback when the MCP is unavailable.

Minimum analysis depth:

- README + docs/ folder.
- Package manifests (package.json, pyproject.toml, go.mod, Cargo.toml, etc.).
- Entry points and the call/data flow from entry to core logic.
- 5-15 highest-signal files (highest LOC, most imports, most commits).
- Git history signals: initial commit message, release cadence, contributor
  count, notable milestones.

## Phase 3 - Capture key screens

Capture 3-8 visuals that show the repository in action. Choose the capture
strategy by project type (see
[references/screenshots.md](references/screenshots.md)):

- Web app: run the dev server, then screenshot key routes at 1920x1080 with the
  Playwright helper: `python <skill>/scripts/capture_screens.py --config captures.json`.
- CLI tool: run `--help` and a realistic example, and render the terminal
  session as a styled PNG.
- Library/SDK: run a small example program and capture its output.
- Static/infra: capture the rendered README/docs, key config, or architecture
  files as code cards.

Every capture must be 1920x1080 (or scaled to that) and stored in `captures/`
with a stable slug name.

## Phase 4 - Diagrams

Create 2-4 diagrams that explain the parts screenshots cannot: architecture,
data flow, data model, sequence, timeline, or layer stack. One message per
diagram, at most ~7-12 nodes each.

Preferred tool: the diagram-design skill
(cathrynlavery/diagram-design, 27 editorial HTML+SVG types). If it is not
installed, install it once with:

```bash
codex plugin marketplace add cathrynlavery/diagram-design
codex plugin add diagram-design@diagram-design
```

Fallback when diagram-design is unavailable: Mermaid rendered to PNG via
`mmdc` (mermaid-cli) or a headless browser, or Graphviz `dot -Tpng`.

Export every diagram to 1920x1080 PNG into `diagrams/`. See
[references/diagrams.md](references/diagrams.md) for type selection and export
commands.

## Phase 5 - Script and manifest

Write a 1-3 minute narration in the user's requested language (default:
English). Read [references/script-writing.md](references/script-writing.md)
before writing; it contains the narration structure, pacing rules, and the full
manifest schema.

Hard constraints:

- Total duration 60-180 seconds (validate with
  `python <skill>/scripts/estimate_duration.py --manifest manifest.json`).
- ~150-160 words per minute of narration (English), ~2.5-3.5 characters per
  second (Japanese/Chinese).
- Scene types: `title` -> `hook` -> `architecture`/`datamodel`/`flow` ->
  `demo` (screenshots) -> `insight` -> `outro`.
- Every scene references visuals that exist on disk (screenshot or diagram PNG).
- No claim in the narration that is not supported by the analysis; include real
  numbers (stars, LOC, modules, commits, benchmarks) from analysis/report.json.

Output both `script.md` (readable script with scene headings) and
`manifest.json` (machine-readable, used by TTS + rendering).

## Phase 6 - Voiceover (TTS)

Generate the narration audio with:

```bash
python <skill>/scripts/tts.py --manifest manifest.json --engine qwen3   # best quality, needs GPU
python <skill>/scripts/tts.py --manifest manifest.json --engine edge    # fast fallback, CPU-only
```

Output: `audio/scene-<NN>.mp3` (one per scene) and `audio/voiceover.mp3`
(concatenated). The script also reports per-scene durations so scene timing can
be adjusted if narration overruns the planned duration.

Engine details, speakers, language support, and local Qwen3-TTS setup: see
[references/tts.md](references/tts.md).

## Phase 7 - Render

Choose the render engine:

- **Remotion (default)** - self-contained, deterministic, works anywhere
  Node.js runs. Copy the bundled template, install deps, drop in the manifest
  and media, render.
- **HyperFrames** - use when the environment already has the hyperframes skills
  or the user prefers it; build the HTML composition from the manifest and
  render with the HyperFrames CLI.

### Remotion

```bash
cp -r <skill>/assets/remotion-template video
cd video
npm install
cp ../manifest.json public/manifest.json
cp -r ../audio public/audio
cp ../captures public/captures
cp ../diagrams public/diagrams
npx remotion render src/index.ts Explainer out.mp4
```

### HyperFrames

Follow [references/rendering.md](references/rendering.md#hyperframes): init the
project, translate each manifest scene into a timed clip, run
`npx hyperframes check`, then `npx hyperframes render --quality high --output out.mp4`.

## Quality gates (all must pass before delivery)

1. `manifest.json` total duration is 60-180 s and matches the rendered video.
2. `audio/voiceover.mp3` exists and is non-empty.
3. At least one screenshot and one diagram are used in the video.
4. Every visual referenced by a scene exists on disk.
5. The final MP4 exists, is non-empty, and `ffprobe` reports 60-180 s duration.

If a gate fails, fix the underlying issue and re-render; do not deliver.

## References (read when needed)

- [references/analysis.md](references/analysis.md) - deep codebase analysis
  playbook (codebase-memory-mcp + fallbacks).
- [references/screenshots.md](references/screenshots.md) - capture playbook per
  project type + Playwright helper usage.
- [references/diagrams.md](references/diagrams.md) - diagram type selection,
  diagram-design usage, and PNG export.
- [references/script-writing.md](references/script-writing.md) - narration
  structure, pacing rules, manifest schema.
- [references/tts.md](references/tts.md) - TTS engine setup (Qwen3-TTS,
  edge-tts) and speaker guidance.
- [references/rendering.md](references/rendering.md) - Remotion template and
  HyperFrames rendering details.
