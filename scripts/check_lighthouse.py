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
    audits = report.get("audits", {})

    for key, minimum in THRESHOLDS.items():
        category = categories.get(key, {})
        score = category.get("score")
        if score is None:
            problems.append(f"{path}: missing Lighthouse category {key}")
            continue
        print(f"{path.name}: {key}={score:.2f} (minimum {minimum:.2f})")

        if score < 1:
            failed = []
            for ref in category.get("auditRefs", []):
                audit = audits.get(ref.get("id"), {})
                audit_score = audit.get("score")
                if audit_score is not None and audit_score < 1:
                    failed.append(
                        f"{ref.get('id')}: {audit.get('title')} "
                        f"(score={audit_score}, display={audit.get('displayValue', '')})"
                    )
            if failed:
                print(f"{path.name}: non-perfect {key} audits:")
                for item in failed:
                    print(f"  - {item}")

        if score < minimum:
            problems.append(f"{path}: {key} score {score:.2f} < {minimum:.2f}")

if problems:
    raise SystemExit("\n".join(problems))
