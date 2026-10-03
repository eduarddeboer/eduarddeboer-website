#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
GRAPH_BASE = "https://data.eduarddeboer.com/entity/"
PERSON_ID = "https://eduarddeboer.com/#person"


def jsonld_nodes(html: str) -> list[dict]:
    blocks = re.findall(
        r'<script[^>]+type=(?:"application/ld\\+json"|\'application/ld\\+json\'|application/ld\\+json)[^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    )
    nodes: list[dict] = []
    for block in blocks:
        data = json.loads(block.strip())
        if isinstance(data, dict) and isinstance(data.get("@graph"), list):
            nodes.extend(item for item in data["@graph"] if isinstance(item, dict))
        elif isinstance(data, dict):
            nodes.append(data)
    return nodes


def relation_ids(node: dict, predicate: str) -> set[str]:
    value = node.get(predicate)
    if value is None:
        return set()
    values = value if isinstance(value, list) else [value]
    result: set[str] = set()
    for item in values:
        if isinstance(item, dict) and isinstance(item.get("@id"), str):
            result.add(item["@id"])
        elif isinstance(item, str):
            result.add(item)
    return result


def node_with_id(nodes: list[dict], node_id: str) -> dict:
    matches = [node for node in nodes if node.get("@id") == node_id]
    if len(matches) != 1:
        raise SystemExit(f"Expected one JSON-LD node {node_id!r}, found {len(matches)}")
    return matches[0]


def require_relation(node: dict, predicate: str, target: str) -> None:
    if target not in relation_ids(node, predicate):
        raise SystemExit(f"{node.get('@id')}: missing {predicate} -> {target}")


def page_url(path: Path) -> str:
    rel = path.relative_to(DIST).as_posix()
    if not rel.endswith("index.html"):
        raise SystemExit(f"Unexpected page path: {rel}")
    return "https://eduarddeboer.com/" + rel.removesuffix("index.html")


def require_page(
    path: Path,
    page_type: str,
    *,
    main_entity: str | None = None,
    expected_entities: set[str] | None = None,
) -> tuple[list[dict], dict]:
    if not path.is_file():
        raise SystemExit(f"Required page missing: {path.relative_to(DIST)}")
    nodes = jsonld_nodes(path.read_text(encoding="utf-8"))
    url = page_url(path)
    page = node_with_id(nodes, f"{url}#webpage")
    if page.get("@type") != page_type:
        raise SystemExit(
            f"{path.relative_to(DIST)}: {page.get('@type')!r} != expected {page_type!r}"
        )
    if main_entity and (page.get("mainEntity") or {}).get("@id") != main_entity:
        raise SystemExit(
            f"{path.relative_to(DIST)}: wrong mainEntity "
            f"{(page.get('mainEntity') or {}).get('@id')!r}"
        )

    ids = {node.get("@id") for node in nodes}
    for entity_id in expected_entities or set():
        expected = PERSON_ID if entity_id == "person/eduard_de_boer" else GRAPH_BASE + entity_id
        if expected not in ids:
            raise SystemExit(
                f"{path.relative_to(DIST)}: contextual entity node missing {expected}"
            )
    return nodes, page


def require_item_list(nodes: list[dict], node_id: str, expected_count: int) -> None:
    node = node_with_id(nodes, node_id)
    if node.get("@type") != "ItemList":
        raise SystemExit(f"{node_id}: expected ItemList")
    if node.get("numberOfItems") != expected_count:
        raise SystemExit(
            f"{node_id}: numberOfItems {node.get('numberOfItems')!r} != {expected_count}"
        )
    elements = node.get("itemListElement") or []
    if len(elements) != expected_count:
        raise SystemExit(
            f"{node_id}: expected {expected_count} ListItems, found {len(elements)}"
        )
    positions = [item.get("position") for item in elements]
    if positions != list(range(1, expected_count + 1)):
        raise SystemExit(f"{node_id}: ListItem positions are not contiguous")


def main() -> None:
    focus = {
        "organization/ingenieursbureau_evan_buytendijk",
        "legislation/eudr_2023_1115",
        "legislation/eutr_995_2010",
        "organization/fsc",
        "organization/pefc",
        "defined_term/due_diligence_eudr",
        "defined_term/supply_chain_traceability",
    }
    countries = {
        "country/congo_brazzaville",
        "country/gabon",
        "country/ivoorkust",
        "country/india",
        "country/libanon",
        "country/noord_macedonie",
    }

    for lang in ("nl", "en"):
        home_nodes, home_page = require_page(
            DIST / lang / "index.html",
            "ProfilePage",
            main_entity=PERSON_ID,
            expected_entities=focus | countries | {"person/eduard_de_boer"},
        )
        expected_mentions = {GRAPH_BASE + entity_id for entity_id in focus | countries}
        if not expected_mentions <= relation_ids(home_page, "mentions"):
            raise SystemExit(f"{lang}/: homepage is missing visible entity mentions")

        person = node_with_id(home_nodes, PERSON_ID)
        require_relation(
            person,
            "worksFor",
            GRAPH_BASE + "organization/ingenieursbureau_evan_buytendijk",
        )
        for entity_id in focus - {"organization/ingenieursbureau_evan_buytendijk"}:
            if entity_id in {
                "legislation/eudr_2023_1115",
                "legislation/eutr_995_2010",
                "organization/fsc",
                "organization/pefc",
                "defined_term/due_diligence_eudr",
                "defined_term/supply_chain_traceability",
            }:
                require_relation(person, "knowsAbout", GRAPH_BASE + entity_id)

        parts = relation_ids(home_page, "hasPart")
        home_articles = [
            node
            for node in home_nodes
            if node.get("@type") == "Article" and node.get("@id") in parts
        ]
        if len(home_articles) != 3:
            raise SystemExit(f"{lang}/: expected three latest Article hasPart nodes")
        for article in home_articles:
            require_relation(article, "author", PERSON_ID)

        eudr = node_with_id(home_nodes, GRAPH_BASE + "legislation/eudr_2023_1115")
        if not any(
            isinstance(item, dict)
            and item.get("propertyID") == "CELEX"
            and item.get("value") == "32023R1115"
            for item in (eudr.get("identifier") or [])
        ):
            raise SystemExit(f"{lang}/: EUDR node lacks CELEX entity identifier")

        about_nodes, about_page = require_page(
            DIST / lang / "about" / "index.html",
            "AboutPage",
            main_entity=PERSON_ID,
            expected_entities={
                "person/eduard_de_boer",
                "organization/ingenieursbureau_evan_buytendijk",
                "certification/iso_19011_internal_auditor",
                "legislation/eudr_2023_1115",
                "legislation/eutr_995_2010",
                "organization/fsc",
                "organization/pefc",
            },
        )
        if len(relation_ids(about_page, "mentions")) < 6:
            raise SystemExit(f"{lang}/about/: expected professional-context mentions")
        certification = node_with_id(
            about_nodes, GRAPH_BASE + "certification/iso_19011_internal_auditor"
        )
        require_relation(certification, "about", PERSON_ID)

        expertise_nodes, expertise_page = require_page(
            DIST / lang / "expertise" / "index.html",
            "WebPage",
            expected_entities={
                "legislation/eudr_2023_1115",
                "legislation/eutr_995_2010",
                "defined_term/due_diligence_eudr",
                "defined_term/due_diligence_eutr",
                "defined_term/geolocation_eudr",
                "defined_term/supply_chain_traceability",
                "defined_term/risk_assessment",
                "defined_term/auditing",
                "organization/fsc",
                "organization/pefc",
            },
        )
        if len(relation_ids(expertise_page, "about")) < 8:
            raise SystemExit(f"{lang}/expertise/: expected rich about-relations")
        if len(relation_ids(expertise_page, "mentions")) < 4:
            raise SystemExit(f"{lang}/expertise/: expected guidance/certification mentions")

        experience_nodes, _ = require_page(
            DIST / lang / "experience" / "index.html",
            "WebPage",
            main_entity=PERSON_ID,
            expected_entities=countries
            | {
                "person/eduard_de_boer",
                "article/ieb_eutr_supplier_audit_congo_2022",
                "article/ieb_eutr_supplier_audit_india_2023",
                "article/ieb_eutr_audit_lebanon_2023",
            },
        )
        india_article = node_with_id(
            experience_nodes, GRAPH_BASE + "article/ieb_eutr_supplier_audit_india_2023"
        )
        require_relation(india_article, "author", PERSON_ID)
        require_relation(
            india_article, "about", GRAPH_BASE + "legislation/eutr_995_2010"
        )

        speaking_nodes, speaking_page = require_page(
            DIST / lang / "speaking" / "index.html",
            "CollectionPage",
            expected_entities={
                "event/houtwereld_praktijkdag_2026",
                "event/interu_eudr_risk_assessment_webinar",
                "creative_work/houtwereld_speaker_profile_eduard_de_boer_2026",
                "tv_series/de_rijdende_rechter",
                "tv_episode/gevloerd_rijdende_rechter",
                "tv_episode/t_heen_en_weer_krijgen_rijdende_rechter",
                "tv_episode/door_het_stof_rijdende_rechter",
                "tv_episode/schutting_van_de_rekening_rijdende_rechter",
                "tv_episode/laat_je_niet_kisten_rijdende_rechter",
            },
        )
        speaking_base = f"https://eduarddeboer.com/{lang}/speaking/"
        professional_list = speaking_base + "#professional-speaking"
        historical_list = speaking_base + "#historical-media"
        require_item_list(speaking_nodes, professional_list, 3)
        require_item_list(speaking_nodes, historical_list, 6)
        if {professional_list, historical_list} - relation_ids(speaking_page, "hasPart"):
            raise SystemExit(f"{lang}/speaking/: CollectionPage must link both ItemLists")
        episode = node_with_id(
            speaking_nodes, GRAPH_BASE + "tv_episode/gevloerd_rijdende_rechter"
        )
        require_relation(episode, "contributor", PERSON_ID)
        require_relation(
            episode, "isPartOf", GRAPH_BASE + "tv_series/de_rijdende_rechter"
        )

        insights_nodes, insights_page = require_page(
            DIST / lang / "insights" / "index.html",
            "CollectionPage",
            expected_entities={
                "article/linkedin_eudr_taric_codes_2026",
                "article/houtwereld_waarom_zoveel_lods_nvwa_2026",
                "legislation/eudr_2023_1115",
                "legislation/eutr_995_2010",
            },
        )
        insights_base = f"https://eduarddeboer.com/{lang}/insights/"
        authored_list = insights_base + "#authored-publications"
        media_list = insights_base + "#interviews-and-media"
        require_item_list(insights_nodes, authored_list, 34)
        require_item_list(insights_nodes, media_list, 5)
        if {authored_list, media_list} - relation_ids(insights_page, "hasPart"):
            raise SystemExit(f"{lang}/insights/: CollectionPage must link both ItemLists")

        articles = [node for node in insights_nodes if node.get("@type") == "Article"]
        if len(articles) != 39:
            raise SystemExit(
                f"{lang}/insights/: expected 39 Article nodes, found {len(articles)}"
            )
        authored = node_with_id(
            insights_nodes, GRAPH_BASE + "article/linkedin_eudr_taric_codes_2026"
        )
        require_relation(authored, "author", PERSON_ID)
        media = node_with_id(
            insights_nodes, GRAPH_BASE + "article/houtwereld_waarom_zoveel_lods_nvwa_2026"
        )
        require_relation(media, "contributor", PERSON_ID)

    print("Verified contextual JSON-LD entity graphs for NL and EN core pages")


if __name__ == "__main__":
    main()
