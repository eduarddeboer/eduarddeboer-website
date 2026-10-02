#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data/kg/snapshot.json"


def validate(data: dict) -> None:
    required = {"schema_version", "source", "entities", "relations", "media"}
    if set(data) != required:
        raise SystemExit(f"Snapshot keys must be exactly {sorted(required)}")
    if data["schema_version"] != 1:
        raise SystemExit("Unsupported snapshot schema_version")
    source = data["source"]
    if source.get("repository") != "eduarddeboer/eduarddeboer-kg":
        raise SystemExit("Snapshot came from an unexpected repository")
    if source.get("production_base") != "https://data.eduarddeboer.com/":
        raise SystemExit("Snapshot has an unexpected production_base")
    if not isinstance(data["entities"], dict):
        raise SystemExit("entities must be an object")
    if not isinstance(data["relations"], list):
        raise SystemExit("relations must be an array")
    if not isinstance(data["media"], dict):
        raise SystemExit("media must be an object")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a validated website projection from the knowledge graph.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    validate(data)
    encoded = (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    tmp = TARGET.with_suffix(".json.tmp")
    tmp.write_bytes(encoded)
    tmp.replace(TARGET)

    print("Imported", TARGET.relative_to(ROOT))
    print("SHA256", hashlib.sha256(encoded).hexdigest())
    print("KG commit", data["source"].get("commit"))


if __name__ == "__main__":
    main()
