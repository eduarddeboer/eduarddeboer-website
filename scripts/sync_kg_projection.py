#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_SNAPSHOT = ROOT / "data/kg/snapshot.json"
SECTIONS = ROOT / "data/kg/sections.json"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class SnapshotSyncError(ValueError):
    pass


def validate_snapshot(data: dict) -> None:
    required = {"schema_version", "source", "entities", "relations", "media"}
    if set(data) != required:
        raise SnapshotSyncError(f"Snapshot keys must be exactly {sorted(required)}")
    if data["schema_version"] != 1:
        raise SnapshotSyncError("Unsupported snapshot schema_version")
    source = data["source"]
    if source.get("repository") != "eduarddeboer/eduarddeboer-kg":
        raise SnapshotSyncError("Snapshot came from an unexpected repository")
    if source.get("production_base") != "https://data.eduarddeboer.com/":
        raise SnapshotSyncError("Snapshot has an unexpected production_base")
    commit = source.get("commit")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise SnapshotSyncError("Snapshot must pin an exact 40-character KG commit")
    if not isinstance(data["entities"], dict):
        raise SnapshotSyncError("entities must be an object")
    if not isinstance(data["relations"], list):
        raise SnapshotSyncError("relations must be an array")
    if not isinstance(data["media"], dict):
        raise SnapshotSyncError("media must be an object")

    entities = data["entities"]
    for entity_id, entity in entities.items():
        if not isinstance(entity, dict) or entity.get("id") != entity_id:
            raise SnapshotSyncError(f"Invalid projected entity record: {entity_id!r}")

    for relation in data["relations"]:
        if not isinstance(relation, dict):
            raise SnapshotSyncError("relations must contain objects")
        subject = relation.get("subject")
        target = relation.get("target")
        predicate = relation.get("predicate")
        if subject not in entities or target not in entities or not predicate:
            raise SnapshotSyncError(
                f"Projection contains a non-closed relation: {relation!r}"
            )


def semantic_view(data: dict) -> dict:
    validate_snapshot(data)
    return {
        "schema_version": data["schema_version"],
        "source": {
            "repository": data["source"]["repository"],
            "production_base": data["source"]["production_base"],
        },
        "entities": data["entities"],
        "relations": data["relations"],
        "media": data["media"],
    }


def semantic_digest(data: dict) -> str:
    encoded = json.dumps(
        semantic_view(data),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_release_manifest(manifest: dict, snapshot: dict) -> None:
    commit = manifest.get("commit_sha")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise SnapshotSyncError("Production release manifest lacks a valid commit_sha")
    if snapshot["source"]["commit"] != commit:
        raise SnapshotSyncError(
            "Production site-snapshot.json and release-manifest.json do not pin the same KG commit"
        )
    if manifest.get("production_host") != "data.eduarddeboer.com":
        raise SnapshotSyncError("Production release manifest has an unexpected host")


def validate_sections_compatible(sections: dict, snapshot: dict) -> None:
    if sections.get("schema_version") != 1:
        raise SnapshotSyncError("Unsupported section projection schema_version")
    projected = set(snapshot["entities"])
    missing: set[str] = set()
    for section in (sections.get("sections") or {}).values():
        schema = section.get("schema") or {}
        if schema.get("main_entity") and schema["main_entity"] not in projected:
            missing.add(schema["main_entity"])
        for group in section.get("groups") or []:
            for entity_id in group.get("entities") or []:
                if entity_id not in projected:
                    missing.add(entity_id)
    if missing:
        raise SnapshotSyncError(
            "New KG projection would break section references: "
            + ", ".join(sorted(missing))
        )


def canonical_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sync_projection(
    *,
    candidate: dict,
    release_manifest: dict,
    current: dict,
    sections: dict,
    apply: bool,
    snapshot_path: Path = CURRENT_SNAPSHOT,
    sections_path: Path = SECTIONS,
) -> dict:
    validate_snapshot(candidate)
    validate_snapshot(current)
    validate_release_manifest(release_manifest, candidate)

    current_digest = semantic_digest(current)
    candidate_digest = semantic_digest(candidate)
    changed = current_digest != candidate_digest

    result = {
        "changed": changed,
        "current_commit": current["source"]["commit"],
        "candidate_commit": candidate["source"]["commit"],
        "current_semantic_sha256": current_digest,
        "candidate_semantic_sha256": candidate_digest,
    }

    if not changed:
        return result

    validate_sections_compatible(sections, candidate)

    if apply:
        snapshot_path.write_text(canonical_json(candidate), encoding="utf-8")
        updated_sections = dict(sections)
        updated_sections["source_commit"] = candidate["source"]["commit"]
        sections_path.write_text(canonical_json(updated_sections), encoding="utf-8")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare/apply the validated production KG website projection."
    )
    parser.add_argument("candidate", type=Path)
    parser.add_argument("release_manifest", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--status-json", type=Path)
    args = parser.parse_args()

    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    manifest = json.loads(args.release_manifest.read_text(encoding="utf-8"))
    current = json.loads(CURRENT_SNAPSHOT.read_text(encoding="utf-8"))
    sections = json.loads(SECTIONS.read_text(encoding="utf-8"))

    result = sync_projection(
        candidate=candidate,
        release_manifest=manifest,
        current=current,
        sections=sections,
        apply=args.apply,
    )
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True)
    print(encoded)
    if args.status_json:
        args.status_json.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
