#!/usr/bin/env python3
from __future__ import annotations

import json
import re
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

    asset_refs: set[str] = set()
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        if "<iframe" in lowered:
            raise SystemExit(f"Privacy regression: eager iframe in {path.relative_to(DIST)}")
        if "staging.eduarddeboer" in lowered:
            raise SystemExit(f"Staging hostname leaked into {path.relative_to(DIST)}")
        if "https://eduarddeboer.com/css/" in lowered or "https://eduarddeboer.com/js/" in lowered:
            raise SystemExit(
                f"Host-coupled asset URL in {path.relative_to(DIST)}; "
                "CSS/JS must use host-independent relative URLs"
            )

        for match in re.finditer(r"""(?:href|src)=(?:["']?)(/(?:css|js)/[^"' >]+)""", text, re.I):
            asset_refs.add(match.group(1))

    if not asset_refs:
        raise SystemExit("No host-independent CSS/JS asset references found in generated HTML")

    for ref in sorted(asset_refs):
        asset = DIST / ref.lstrip("/")
        if not asset.is_file():
            raise SystemExit(f"Generated HTML references missing asset: {ref}")

    print(
        f"Verified dist: {len(html_files)} HTML files, {len(llms)} llms.txt output(s), "
        f"{len(asset_refs)} host-independent CSS/JS assets"
    )


if __name__ == "__main__":
    main()
