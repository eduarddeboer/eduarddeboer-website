#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

EXCLUDED_PARTS = {".obsidian", "_templates"}


def git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def changed_markdown_files(website_root: Path, base_sha: str, head_sha: str) -> list[Path]:
    output = git(
        "diff",
        "--name-only",
        "--diff-filter=ACMR",
        f"{base_sha}...{head_sha}",
        "--",
        "content",
        cwd=website_root,
    )
    paths: list[Path] = []
    for raw in output.splitlines():
        rel = Path(raw.strip())
        if not raw.strip() or rel.suffix.lower() != ".md":
            continue
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        path = website_root / rel
        if path.is_file():
            paths.append(path)
    return sorted(set(paths))


def all_markdown_files(website_root: Path) -> list[Path]:
    content_root = website_root / "content"
    return sorted(
        path
        for path in content_root.rglob("*.md")
        if path.is_file()
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(content_root).parts)
    )


def sanitize_document(result: dict) -> dict:
    """Return a public-safe review record.

    Canonical KG ids for resolver matches are deliberately omitted. The public
    report only repeats aliases/candidates already present in website content.
    Explicit front-matter ids are safe to show because the website source itself
    already contains them.
    """
    known = result.get("known_mentions") or []
    unlinked = result.get("unlinked_known_mentions") or []
    return {
        "source_id": result.get("source_id"),
        "known_mentions": len(known),
        "already_linked_known_mentions": sum(
            bool(item.get("already_linked")) for item in known
        ),
        "unlinked_known_mentions": [
            {
                "aliases": list(item.get("aliases") or []),
                "occurrences": int(item.get("occurrences") or 0),
                "suggested_predicate": item.get("suggested_predicate") or "mentions",
            }
            for item in unlinked
        ],
        "unknown_candidates": list(result.get("unknown_candidates") or []),
        "declared_entity_links": list(result.get("declared_entity_links") or []),
        "unknown_declared_entity_links": list(
            result.get("unknown_declared_entity_links") or []
        ),
    }


def build_public_payload(documents: list[dict], *, website_commit: str, kg_commit: str) -> dict:
    return {
        "schema_version": 1,
        "source": {
            "website_commit": website_commit,
            "kg_commit": kg_commit,
            "kg_repository": "eduarddeboer/eduarddeboer-kg",
        },
        "summary": {
            "documents": len(documents),
            "known_mentions": sum(item["known_mentions"] for item in documents),
            "already_linked_known_mentions": sum(
                item["already_linked_known_mentions"] for item in documents
            ),
            "unlinked_known_mentions": sum(
                len(item["unlinked_known_mentions"]) for item in documents
            ),
            "unknown_candidates": sum(
                len(item["unknown_candidates"]) for item in documents
            ),
            "unknown_declared_entity_links": sum(
                len(item["unknown_declared_entity_links"]) for item in documents
            ),
        },
        "documents": documents,
    }


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "## Entity review",
        "",
        f"- Website commit: `{payload['source']['website_commit'][:12]}`",
        f"- KG commit: `{payload['source']['kg_commit'][:12]}`",
        f"- Gewijzigde Markdown-documenten: **{summary['documents']}**",
        f"- Bekende KG-vermeldingen: **{summary['known_mentions']}**",
        f"- Bekende vermeldingen al gelinkt: **{summary['already_linked_known_mentions']}**",
        f"- Bekende vermeldingen zonder expliciete relatie: **{summary['unlinked_known_mentions']}**",
        f"- Nieuwe/onzekere kandidaten: **{summary['unknown_candidates']}**",
        f"- Frontmatter-links naar onbekende KG-id's: **{summary['unknown_declared_entity_links']}**",
        "",
    ]

    actionable = [
        item
        for item in payload["documents"]
        if item["unlinked_known_mentions"]
        or item["unknown_candidates"]
        or item["unknown_declared_entity_links"]
    ]

    if not actionable:
        lines.append("Geen aanvullende entity-reviewpunten voor de gewijzigde content.")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "### Reviewpunten",
            "",
            "De termen hieronder komen uit de websitecopy zelf. De private KG-records "
            "en resolver-id's worden niet naar de publieke website-CI gelekt.",
            "",
        ]
    )

    for item in actionable[:30]:
        lines.append(f"#### `{item['source_id']}`")
        for match in item["unlinked_known_mentions"][:20]:
            aliases = ", ".join(f"`{alias}`" for alias in match["aliases"])
            lines.append(
                f"- Bekende KG-match zonder frontmatter-relatie: {aliases} "
                f"({match['occurrences']}×; voorstel: `{match['suggested_predicate']}`)."
            )
        if item["unknown_candidates"]:
            values = ", ".join(f"`{value}`" for value in item["unknown_candidates"][:20])
            lines.append(f"- Nieuwe/onzekere kandidaten: {values}.")
        if item["unknown_declared_entity_links"]:
            values = ", ".join(
                f"`{value}`" for value in item["unknown_declared_entity_links"][:20]
            )
            lines.append(f"- Onbekende expliciete KG-id's: {values}.")
        lines.append("")

    if len(actionable) > 30:
        lines.append(
            f"_Nog {len(actionable) - 30} documenten met reviewpunten; "
            "zie het geschoonde JSON-artifact._"
        )
        lines.append("")

    return "\n".join(lines)


def run_review(
    website_root: Path,
    kg_root: Path,
    files: list[Path],
    *,
    website_commit: str,
) -> dict:
    sys.path.insert(0, str(kg_root))
    from kg.entity_discovery import build_alias_index, build_matchers, load_entities
    from kg.website_content_scan import scan_markdown

    entities = load_entities(kg_root)
    alias_index = build_alias_index(entities)
    matchers = build_matchers(entities)

    documents: list[dict] = []
    for path in files:
        rel = path.relative_to(website_root).as_posix()
        raw = scan_markdown(
            path.read_text(encoding="utf-8"),
            entities,
            source_id=f"website/{rel}",
            matchers=matchers,
            alias_index=alias_index,
        )
        documents.append(sanitize_document(raw))

    return build_public_payload(
        documents,
        website_commit=website_commit,
        kg_commit=git("rev-parse", "HEAD", cwd=kg_root),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review changed website Markdown against the private curated KG."
    )
    parser.add_argument("--website-root", type=Path, default=Path("."))
    parser.add_argument("--kg-root", type=Path, required=True)
    parser.add_argument("--base-sha")
    parser.add_argument("--head-sha")
    parser.add_argument("--all", action="store_true", dest="scan_all")
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()

    website_root = args.website_root.resolve()
    kg_root = args.kg_root.resolve()

    if args.scan_all:
        files = all_markdown_files(website_root)
        website_commit = git("rev-parse", "HEAD", cwd=website_root)
    else:
        if not args.base_sha or not args.head_sha:
            parser.error("--base-sha and --head-sha are required unless --all is used")
        files = changed_markdown_files(website_root, args.base_sha, args.head_sha)
        website_commit = args.head_sha

    payload = run_review(
        website_root,
        kg_root,
        files,
        website_commit=website_commit,
    )

    args.json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")

    print(json.dumps(payload["summary"], ensure_ascii=False, sort_keys=True))

    # A front-matter id that does not exist in the full curated KG is a
    # deterministic authoring error. Missing relations and unknown proper nouns
    # remain review signals at this stage of the bridge.
    return 3 if payload["summary"]["unknown_declared_entity_links"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
