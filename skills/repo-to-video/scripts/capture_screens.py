#!/usr/bin/env python3
"""Capture 1920x1080 screenshots of web routes or local HTML files with Playwright.

Usage:
    python capture_screens.py --config captures.json [--base-url http://localhost:3000]

Config shape:
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

`path` may be a full URL or file:// path, in which case base_url is ignored.
Requires: python -m pip install playwright && playwright install chromium
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def slugify(name: str) -> str:
    """Turn an arbitrary route name into a safe, readable filename stem."""
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", name or "")
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    return stem or "shot"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--base-url", default=None, help="Override base URL")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"[ERROR] config not found: {args.config}", file=sys.stderr)
        return 1

    try:
        cfg = json.loads(args.config.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        print(f"[ERROR] invalid config JSON: {exc}", file=sys.stderr)
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "[ERROR] playwright not installed. Run: python -m pip install playwright && "
            "playwright install chromium",
            file=sys.stderr,
        )
        return 1

    base_url = (args.base_url or cfg.get("base_url", "")).rstrip("/")
    viewport = cfg.get("viewport", {"width": 1920, "height": 1080})
    wait_ms = int(cfg.get("wait_ms", 1500))
    output_dir = Path(cfg.get("output_dir", "../captures"))
    output_dir.mkdir(parents=True, exist_ok=True)
    routes = cfg.get("routes", [])
    if not routes:
        print("[ERROR] config has no routes", file=sys.stderr)
        return 1

    saved = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=viewport, device_scale_factor=1.0, ignore_https_errors=True
        )
        page = context.new_page()
        for route in routes:
            name = route.get("name", "shot")
            path = route.get("path", "/")
            if path.startswith(("http://", "https://", "file://")):
                url = path
            elif not path:
                url = base_url
            elif path.startswith("/"):
                url = f"{base_url}{path}"
            else:
                url = f"{base_url}/{path}"
            out = output_dir / f"capture-{slugify(name)}.png"
            print(f"[capture] {name}: {url}")
            try:
                page.goto(url, wait_until="load", timeout=30000)
                selector = route.get("wait_selector")
                if selector:
                    page.wait_for_selector(selector, timeout=15000)
                else:
                    page.wait_for_timeout(int(route.get("wait_ms", wait_ms)))
                page.screenshot(
                    path=str(out),
                    full_page=bool(route.get("full_page", False)),
                )
                saved.append(out)
                print(f"        saved {out}")
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"[WARN] failed to capture {name}: {exc}", file=sys.stderr)
        browser.close()

    print(f"[OK] captured {len(saved)}/{len(routes)} screenshots into {output_dir}")
    return 0 if saved else 2


if __name__ == "__main__":
    sys.exit(main())
