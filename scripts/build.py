#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SNAPSHOT = ROOT / "data/kg/snapshot.json"
EDGE_WORKER = ROOT / "edge/_worker.js"


def git_sha() -> str:
    value = os.environ.get("GITHUB_SHA")
    if value:
        return value
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)

    subprocess.run(
        ["hugo", "--environment", "production", "--destination", str(DIST), "--minify", "--gc"],
        cwd=ROOT,
        check=True,
    )

    shutil.copy2(EDGE_WORKER, DIST / "_worker.js")

    snapshot_bytes = SNAPSHOT.read_bytes()
    snapshot = json.loads(snapshot_bytes)
    manifest = {
        "artifact_contract": 1,
        "website_commit": git_sha(),
        "kg_source_commit": snapshot["source"].get("commit"),
        "kg_snapshot_sha256": hashlib.sha256(snapshot_bytes).hexdigest(),
        "production_host": "eduarddeboer.com",
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
    }
    (DIST / "release-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
