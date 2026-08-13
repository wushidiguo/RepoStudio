# Contributing to RepoStudio

Thanks for helping improve RepoStudio! This project is a
[Codex](https://openai.com/codex/) skill plus a small set of Python/TypeScript
tools. Contributions are welcome in the form of bug reports, documentation
fixes, new scene layouts, better analysis heuristics, and — especially —
"friction reports" from generating an explainer video for a repo you know well.

## Getting started

You need:

- **Python** — use [uv](https://docs.astral.sh/uv/) (recommended) or any Python
  `>=3.9`. `uv` reads `.python-version` and `pyproject.toml` automatically.
- **Node.js `>=18`** — only required to build/render the bundled Remotion
  template.

### Python tooling

```bash
uv sync --extra dev   # creates .venv with edge-tts, playwright, pytest, ruff
uv run pytest         # run the test suite
uv run ruff check .   # lint
uv run ruff format .  # format
```

If you don't use uv, install the same deps with
`pip install -r requirements.txt -r requirements-dev.txt`.

### Remotion template

```bash
cd skills/repo-to-video/assets/remotion-template
npm install
npm run build   # tsc --noEmit typecheck
npm run dev     # remotion studio
```

## Making a change

1. Fork the repo and create a branch.
2. Make your change. Keep each pull request focused on one thing.
3. Add or update tests in `tests/` when you touch `scripts/` behavior.
4. Run `uv run pytest`, `uv run ruff check .`, and
   `uv run ruff format --check .`; run `npm run build` in the template if you
   touch `assets/remotion-template`.
5. Update `CHANGELOG.md` and docs (`README.md`, `SKILL.md`, `references/`) if
   the change affects usage.
6. Open a pull request. CI runs the same checks automatically.

## What makes a great contribution

- **Fixes grounded in code.** The skill's whole point is "analysis, not just the
  README". Improvements that make the analysis, screenshots, diagrams, script,
  TTS, or render steps more robust and verifiable are the most valuable.
- **Evidence-based narration.** Script changes should keep the rule that every
  claim traces back to `analysis/report.json` or an on-disk visual.
- **Determinism.** The pipeline advertises deterministic rendering — avoid
  adding steps that depend on machine-local fonts, un-pinned tool versions, or
  the network at render time.

## Testing the skill end-to-end

The most useful manual test is to run the whole pipeline against a small repo:

```text
Use $repo-to-video to turn https://github.com/owner/repo into a 2-minute explainer video.
```

Report where it broke or felt awkward — that is a first-class contribution.
