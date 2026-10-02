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

PUBLIC_TEXT_ROOTS = (
    CONTENT,
    ROOT / "config",
    ROOT / "layouts",
    ROOT / "static",
)
PUBLIC_TEXT_SUFFIXES = {".md", ".html", ".toml", ".json", ".xml", ".txt"}
UNMARKED_FSC = re.compile(r"(?<![\w®])FSC(?!®|\w)")
VAGUE_MARKETING_CLAIMS = (
    re.compile(r"\bduurzame\s+toekomst\b", re.IGNORECASE),
    re.compile(r"\bduurzame\s+impact\b", re.IGNORECASE),
    re.compile(r"\bduurzame\s+kansen\b", re.IGNORECASE),
    re.compile(r"\bgroene\s+keuzes?\b", re.IGNORECASE),
    re.compile(r"\bgoed\s+voor\s+de\s+planeet\b", re.IGNORECASE),
    re.compile(r"\bmilieuvriendelijk(?:e|er|ste)?\b", re.IGNORECASE),
    re.compile(r"\beco[- ]vriendelijk(?:e|er|ste)?\b", re.IGNORECASE),
    re.compile(r"\bsustainable\s+future\b", re.IGNORECASE),
    re.compile(r"\bsustainable\s+impact\b", re.IGNORECASE),
    re.compile(r"\bsustainable\s+opportunit(?:y|ies)\b", re.IGNORECASE),
    re.compile(r"\bgreen\s+choices?\b", re.IGNORECASE),
    re.compile(r"\bgood\s+for\s+the\s+planet\b", re.IGNORECASE),
    re.compile(r"\benvironmentally\s+friendly\b", re.IGNORECASE),
    re.compile(r"\beco[- ]friendly\b", re.IGNORECASE),
)


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


def public_text_files() -> list[Path]:
    files: set[Path] = set()
    for root in PUBLIC_TEXT_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in PUBLIC_TEXT_SUFFIXES:
                files.add(path)
    return sorted(files)


def validate_public_claims(problems: list[str]) -> None:
    for path in public_text_files():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)

        match = UNMARKED_FSC.search(text)
        if match:
            problems.append(
                f"{rel}: public-facing 'FSC' must be written as 'FSC®'"
            )

        for pattern in VAGUE_MARKETING_CLAIMS:
            match = pattern.search(text)
            if match:
                problems.append(
                    f"{rel}: vague environmental/sustainability marketing claim "
                    f"{match.group(0)!r}; use specific, verifiable wording"
                )


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

    validate_public_claims(problems)

    if problems:
        raise SystemExit("\n".join(problems))

    print(
        f"Validated content and KG snapshot: "
        f"{len(list(CONTENT.rglob('*.md')))} Markdown files, "
        f"{len(entities)} projected entities; "
        f"claim and FSC® guardrails passed"
    )


if __name__ == "__main__":
    main()
