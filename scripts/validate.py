#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/kg/snapshot.json"
CONTENT = ROOT / "content"

WIKILINK = re.compile(r"\[\[[^\]\n]+\]\]")
KG_REF = re.compile(r"^kgRef:\s*[\"']?([^\"'\s#]+)", re.MULTILINE)
FORBIDDEN = ("<iframe", "youtube.com/embed", "youtube-nocookie.com/embed", "<script")


def load_snapshot() -> dict:
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    required = {"schema_version", "source", "entities", "relations", "media"}
    if set(data) != required:
        raise SystemExit(f"KG snapshot keys must be exactly {sorted(required)}")
    if data["schema_version"] != 1:
        raise SystemExit("Unsupported KG snapshot schema_version")
    if data["source"].get("repository") != "eduarddeboer/eduarddeboer-kg":
        raise SystemExit("Unexpected KG source repository")
    if data["source"].get("production_base") != "https://data.eduarddeboer.com/":
        raise SystemExit("Unexpected KG production base")
    if not isinstance(data["entities"], dict):
        raise SystemExit("KG entities must be an object")
    if not isinstance(data["relations"], list):
        raise SystemExit("KG relations must be an array")
    if not isinstance(data["media"], dict):
        raise SystemExit("KG media must be an object")
    return data


def main() -> None:
    snapshot = load_snapshot()
    entities = snapshot["entities"]
    problems: list[str] = []

    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        if WIKILINK.search(text):
            problems.append(f"{rel}: Obsidian wikilink found; use portable Markdown links")
        lowered = text.lower()
        for token in FORBIDDEN:
            if token in lowered:
                problems.append(f"{rel}: forbidden raw embed/script token: {token}")
        match = KG_REF.search(text)
        if match:
            entity_id = match.group(1).strip()
            if entity_id and entity_id not in entities:
                problems.append(f"{rel}: kgRef {entity_id!r} is absent from data/kg/snapshot.json")

    if problems:
        raise SystemExit("\n".join(problems))

    print(
        f"Validated content and KG snapshot: "
        f"{len(list(CONTENT.rglob('*.md')))} Markdown files, "
        f"{len(entities)} projected entities"
    )


if __name__ == "__main__":
    main()
