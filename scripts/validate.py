#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/kg/snapshot.json"
SECTIONS = ROOT / "data/kg/sections.json"
CONTENT = ROOT / "content"
AUTHORING_TEMPLATE_DIR = CONTENT / "_templates"

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

    entities = data["entities"]
    if entities:
        commit = data["source"].get("commit")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise SystemExit("Non-empty KG snapshot must pin a 40-character source commit")

    for entity_id, entity in entities.items():
        if not isinstance(entity, dict):
            raise SystemExit(f"KG entity {entity_id!r} must be an object")
        if entity.get("id") != entity_id:
            raise SystemExit(f"KG entity key/id mismatch for {entity_id!r}")

    for relation in data["relations"]:
        if not isinstance(relation, dict):
            raise SystemExit("KG relations must contain objects")
        subject = relation.get("subject")
        target = relation.get("target")
        predicate = relation.get("predicate")
        if subject not in entities:
            raise SystemExit(f"KG relation has missing subject {subject!r}")
        if target not in entities:
            raise SystemExit(f"KG relation {subject!r} -> {target!r} has missing target")
        if not predicate:
            raise SystemExit(f"KG relation for {subject!r} lacks a predicate")

    authored_articles = []
    for entity in entities.values():
        if entity.get("type") != "Article":
            continue
        relations = entity.get("relations") or []
        if any(
            relation.get("predicate") == "author"
            and relation.get("target") == "person/eduard_de_boer"
            for relation in relations
        ):
            for required_field in ("name", "description", "url", "date_published"):
                if not entity.get(required_field):
                    raise SystemExit(
                        f"Authored article {entity.get('id')!r} lacks {required_field}"
                    )
            authored_articles.append(entity)

    if entities and len(authored_articles) < 3:
        raise SystemExit("KG website projection must contain at least three authored articles")

    return data


def validate_section_projections(snapshot: dict) -> dict:
    data = json.loads(SECTIONS.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise SystemExit("Unsupported KG section projection schema_version")

    source_commit = data.get("source_commit")
    if source_commit != snapshot["source"].get("commit"):
        raise SystemExit(
            "KG section projection source_commit must match the pinned snapshot commit"
        )

    sections = data.get("sections")
    if not isinstance(sections, dict) or not sections:
        raise SystemExit("KG section projections must contain a non-empty sections object")

    entities = snapshot["entities"]
    seen_ids: set[str] = set()

    for section_key, section in sections.items():
        if not isinstance(section, dict):
            raise SystemExit(f"KG section {section_key!r} must be an object")
        groups = section.get("groups")
        if not isinstance(groups, list) or not groups:
            raise SystemExit(f"KG section {section_key!r} must contain groups")

        schema_config = section.get("schema") or {}
        if not isinstance(schema_config, dict):
            raise SystemExit(f"KG section {section_key!r} schema config must be an object")
        page_type = schema_config.get("page_type")
        if page_type not in {"ProfilePage", "AboutPage", "WebPage", "CollectionPage"}:
            raise SystemExit(
                f"KG section {section_key!r} must define a supported schema page_type"
            )
        main_entity = schema_config.get("main_entity")
        if main_entity and main_entity not in entities:
            raise SystemExit(
                f"KG section {section_key!r} main_entity {main_entity!r} is absent from the snapshot"
            )

        seen_in_section: set[str] = set()

        for group in groups:
            selection_basis = group.get("selection_basis")
            if selection_basis not in {"visible_claim", "primary_context", "visible_collection"}:
                raise SystemExit(
                    f"KG section {section_key!r} group lacks a supported selection_basis"
                )
            selection_note = group.get("selection_note")
            if not isinstance(selection_note, dict) or not selection_note.get("nl") or not selection_note.get("en"):
                raise SystemExit(
                    f"KG section {section_key!r} group must explain selection in nl and en"
                )

            schema_relation = group.get("schema_relation", "mentions")
            if schema_relation not in {"about", "mentions", "hasPart"}:
                raise SystemExit(
                    f"KG section {section_key!r} has unsupported schema_relation "
                    f"{schema_relation!r}"
                )
            if group.get("item_list") and not group.get("schema_id"):
                raise SystemExit(
                    f"KG section {section_key!r} item-list group must define schema_id"
                )
            ids = group.get("entities")
            if not isinstance(ids, list) or not ids:
                raise SystemExit(
                    f"KG section {section_key!r} contains an empty entity group"
                )
            for entity_id in ids:
                if entity_id not in entities:
                    raise SystemExit(
                        f"KG section {section_key!r} references missing entity {entity_id!r}"
                    )
                if entity_id in seen_in_section:
                    raise SystemExit(
                        f"KG section {section_key!r} selects entity {entity_id!r} more than once"
                    )
                seen_in_section.add(entity_id)

                entity = entities[entity_id]
                if not entity.get("type") or not entity.get("name"):
                    raise SystemExit(
                        f"Projected entity {entity_id!r} lacks type or name"
                    )
                seen_ids.add(entity_id)

    # Publication archive semantics: keep authorship separate from interviews/media.
    insights = sections.get("insights") or {}
    insight_groups = insights.get("groups") or []
    if len(insight_groups) < 2:
        raise SystemExit("Insights projection must separate authored publications and media")

    authored_ids = insight_groups[0].get("entities") or []
    media_ids = insight_groups[1].get("entities") or []

    for entity_id in authored_ids:
        relations = entities[entity_id].get("relations") or []
        if not any(
            relation.get("predicate") == "author"
            and relation.get("target") == "person/eduard_de_boer"
            for relation in relations
        ):
            raise SystemExit(
                f"Authored publications group contains non-authored entity {entity_id!r}"
            )

    for entity_id in media_ids:
        relations = entities[entity_id].get("relations") or []
        if any(
            relation.get("predicate") == "author"
            and relation.get("target") == "person/eduard_de_boer"
            for relation in relations
        ):
            raise SystemExit(
                f"Media group must not contain an Eduard-authored article {entity_id!r}"
            )
        if not any(
            relation.get("target") == "person/eduard_de_boer"
            and relation.get("predicate") in {"contributor", "mentions"}
            for relation in relations
        ):
            raise SystemExit(
                f"Media group lacks contributor/mentions relation for {entity_id!r}"
            )

    if len(authored_ids) < 30:
        raise SystemExit("Current professional publication archive unexpectedly lost authored items")
    if len(media_ids) < 4:
        raise SystemExit("Current professional media archive unexpectedly lost contributed items")

    # The core public sections must all be mapped.
    required_sections = {"home", "about", "expertise", "experience", "speaking", "insights"}
    missing = required_sections - set(sections)
    if missing:
        raise SystemExit(
            f"KG section projection lacks required sections: {sorted(missing)}"
        )

    home = sections["home"]
    home_ids = {
        entity_id
        for group in home["groups"]
        for entity_id in group.get("entities", [])
    }
    required_home_entities = {
        "organization/ingenieursbureau_evan_buytendijk",
        "legislation/eudr_2023_1115",
        "legislation/eutr_995_2010",
        "organization/fsc",
        "organization/pefc",
        "defined_term/due_diligence_eudr",
        "defined_term/supply_chain_traceability",
        "country/congo_brazzaville",
        "country/gabon",
        "country/ivoorkust",
        "country/india",
        "country/libanon",
        "country/noord_macedonie",
    }
    missing_home_entities = required_home_entities - home_ids
    if missing_home_entities:
        raise SystemExit(
            "Homepage schema projection lost visible entities: "
            f"{sorted(missing_home_entities)}"
        )

    required_by_section = {
        "about": {
            "organization/ingenieursbureau_evan_buytendijk",
            "certification/iso_19011_internal_auditor",
            "legislation/eudr_2023_1115",
            "legislation/eutr_995_2010",
            "organization/fsc",
            "organization/pefc",
            "defined_term/due_diligence_eudr",
            "defined_term/due_diligence_eutr",
            "defined_term/supply_chain_traceability",
            "defined_term/auditing",
        },
        "expertise": {
            "legislation/eudr_2023_1115",
            "legislation/eutr_995_2010",
            "defined_term/due_diligence_eudr",
            "defined_term/due_diligence_eutr",
            "defined_term/supply_chain_traceability",
            "defined_term/risk_assessment",
            "defined_term/auditing",
            "certification/iso_19011_internal_auditor",
            "organization/fsc",
            "organization/pefc",
        },
        "experience": {
            "organization/ingenieursbureau_evan_buytendijk",
            "certification/iso_19011_internal_auditor",
            "legislation/eudr_2023_1115",
            "legislation/eutr_995_2010",
            "defined_term/due_diligence_eudr",
            "defined_term/due_diligence_eutr",
            "defined_term/supply_chain_traceability",
            "defined_term/auditing",
            "country/congo_brazzaville",
            "country/gabon",
            "country/ivoorkust",
            "country/india",
            "country/libanon",
            "country/noord_macedonie",
            "article/ieb_eutr_supplier_audit_congo_2022",
            "article/ieb_eutr_supplier_audit_india_2023",
            "article/ieb_eutr_audit_lebanon_2023",
        },
    }
    for section_key, required_ids in required_by_section.items():
        selected = {
            entity_id
            for group in sections[section_key]["groups"]
            for entity_id in group.get("entities", [])
        }
        missing = required_ids - selected
        if missing:
            raise SystemExit(
                f"KG section {section_key!r} lost required page-specific entities: {sorted(missing)}"
            )

    person_relations = entities["person/eduard_de_boer"].get("relations") or []
    person_relation_pairs = {
        (relation.get("predicate"), relation.get("target"))
        for relation in person_relations
    }
    for target in {
        "organization/ingenieursbureau_evan_buytendijk",
        "legislation/eudr_2023_1115",
        "legislation/eutr_995_2010",
        "organization/fsc",
        "organization/pefc",
        "defined_term/due_diligence_eudr",
        "defined_term/supply_chain_traceability",
    }:
        predicate = "worksFor" if target == "organization/ingenieursbureau_evan_buytendijk" else "knowsAbout"
        if (predicate, target) not in person_relation_pairs:
            raise SystemExit(
                f"Canonical Person projection lacks {predicate} -> {target}"
            )

    return data


def is_authoring_template(path: Path) -> bool:
    try:
        path.relative_to(AUTHORING_TEMPLATE_DIR)
        return True
    except ValueError:
        return False


def content_markdown_files() -> list[Path]:
    return sorted(
        path
        for path in CONTENT.rglob("*.md")
        if not is_authoring_template(path)
    )


def public_text_files() -> list[Path]:
    files: set[Path] = set()
    for root in PUBLIC_TEXT_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in PUBLIC_TEXT_SUFFIXES
                and not is_authoring_template(path)
            ):
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
    section_data = validate_section_projections(snapshot)
    entities = snapshot["entities"]
    problems: list[str] = []

    content_files = content_markdown_files()
    for path in content_files:
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

        frontmatter_section = re.search(
            r'^kg_section:\s*["\']?([^"\'\s#]+)', text, re.MULTILINE
        )
        if frontmatter_section:
            section_key = frontmatter_section.group(1).strip()
            if section_key not in section_data["sections"]:
                problems.append(
                    f"{rel}: kg_section {section_key!r} is absent from data/kg/sections.json"
                )

    validate_public_claims(problems)

    if problems:
        raise SystemExit("\n".join(problems))

    print(
        f"Validated content and KG snapshot: "
        f"{len(content_files)} published-content Markdown files, "
        f"{len(entities)} projected entities across "
        f"{len(section_data['sections'])} website sections; "
        f"claim and FSC® guardrails passed"
    )


if __name__ == "__main__":
    main()
