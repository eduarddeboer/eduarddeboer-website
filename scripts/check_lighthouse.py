#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

THRESHOLDS = {
    "performance": 0.95,
    "accessibility": 1.00,
    "best-practices": 0.95,
    "seo": 0.95,
}

problems = []
for raw in sys.argv[1:]:
    path = Path(raw)
    report = json.loads(path.read_text(encoding="utf-8"))
    categories = report.get("categories", {})
    for key, minimum in THRESHOLDS.items():
        score = categories.get(key, {}).get("score")
        if score is None:
            problems.append(f"{path}: missing Lighthouse category {key}")
            continue
        print(f"{path.name}: {key}={score:.2f} (minimum {minimum:.2f})")
        if score < minimum:
            problems.append(f"{path}: {key} score {score:.2f} < {minimum:.2f}")

if problems:
    raise SystemExit("\n".join(problems))
