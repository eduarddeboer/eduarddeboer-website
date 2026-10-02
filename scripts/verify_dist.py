#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def require(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"Required build output missing: {path.relative_to(ROOT)}")


def main() -> None:
    for path in (
        DIST / "_worker.js",
        DIST / "release-manifest.json",
        DIST / "en/index.html",
        DIST / "nl/index.html",
    ):
        require(path)

    manifest = json.loads((DIST / "release-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("artifact_contract") != 1:
        raise SystemExit("Unexpected release artifact contract")
    if manifest.get("production_host") != "eduarddeboer.com":
        raise SystemExit("Release artifact has an unexpected production host")

    llms = list(DIST.rglob("llms.txt"))
    if not llms:
        raise SystemExit("No llms.txt output was generated")

    html_files = list(DIST.rglob("*.html"))
    if not html_files:
        raise SystemExit("No HTML files were generated")

    for path in html_files:
        text = path.read_text(encoding="utf-8").lower()
        if "<iframe" in text:
            raise SystemExit(f"Privacy regression: eager iframe in {path.relative_to(DIST)}")
        if "staging.eduarddeboer" in text:
            raise SystemExit(f"Staging hostname leaked into {path.relative_to(DIST)}")

    print(f"Verified dist: {len(html_files)} HTML files, {len(llms)} llms.txt output(s)")


if __name__ == "__main__":
    main()
