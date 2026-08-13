# Capturing Key Screens

Capture 3-8 visuals that show the repository in action. All captures must be
1920x1080 and stored in `captures/` with stable slug names
(`capture-<slug>.png`).

## Web app

1. Install deps and start the dev server
   (`npm install && npm run dev`, `uvicorn app.main:app`, etc.). Note the base
   URL.
2. Write a capture config:

```json
{
  "base_url": "http://localhost:3000",
  "viewport": {"width": 1920, "height": 1080},
  "output_dir": "../captures",
  "wait_ms": 1500,
  "routes": [
    {"name": "home", "path": "/"},
    {"name": "dashboard", "path": "/dashboard", "wait_selector": ".main"}
  ]
}
```

3. Run: `python <skill>/scripts/capture_screens.py --config captures.json`.
4. If the app needs login, seed a demo account or use a Playwright persistent
   context; otherwise capture what is reachable without auth and note it.

If the app cannot run (missing services, heavy build), fall back to:

- Screenshot the rendered README/docs from the GitHub page or docs site.
- Capture code cards (see below) instead of live screenshots.

## CLI tool

- Run `repo/<bin> --help` and one realistic example.
- Render the session as a styled terminal card: create a small HTML page with a
  dark terminal frame, monospace text, colored prompt, then screenshot it with
  the capture helper (`"base_url": "file:///abs/path/captures/terminal.html"`).

## Library / SDK

- Write a small example program using the library, run it, and capture the
  output. Pair the output card with a code snippet card showing the minimal
  usage (`visual.kind = "code"` in the manifest).

## Static / infra / non-runnable

- Create code cards: an HTML page with syntax-highlighted source (key config,
  entry point, core algorithm) on a dark background, then screenshot it. Keep
  each card to 8-20 lines so it reads at 1080p.

## Helper notes

- `capture_screens.py` uses Playwright:
  `python -m pip install playwright && playwright install chromium`.
- Route names become file names: `{"name": "home"}` ->
  `captures/capture-home.png`.
- If `wait_selector` is set, the helper waits for it instead of a fixed wait.
