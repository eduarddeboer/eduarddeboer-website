#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def require(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"Required build output missing: {path.relative_to(ROOT)}")


def jsonld_nodes(html: str) -> list[dict]:
    blocks = re.findall(
        r'<script[^>]+type=(?:"application/ld\+json"|\'application/ld\+json\'|application/ld\+json)[^>]*>(.*?)</script>',
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


def require_unified_structured_data(path: Path, lang: str) -> None:
    html = path.read_text(encoding="utf-8")
    nodes = jsonld_nodes(html)

    websites = [node for node in nodes if node.get("@type") == "WebSite"]
    if len(websites) != 1:
        raise SystemExit(
            f"{path.relative_to(DIST)}: expected exactly one WebSite node, found {len(websites)}"
        )
    website = websites[0]
    if website.get("@id") != "https://eduarddeboer.com/#website":
        raise SystemExit(
            f"{path.relative_to(DIST)}: unexpected WebSite @id {website.get('@id')!r}"
        )
    if website.get("url") != "https://eduarddeboer.com/":
        raise SystemExit(f"{path.relative_to(DIST)}: WebSite URL must be site root")

    persons = [
        node
        for node in nodes
        if node.get("@type") == "Person"
        and node.get("@id") == "https://eduarddeboer.com/#person"
    ]
    if len(persons) != 1:
        raise SystemExit(
            f"{path.relative_to(DIST)}: expected one canonical Person node, found {len(persons)}"
        )

    profile_pages = [node for node in nodes if node.get("@type") == "ProfilePage"]
    if len(profile_pages) != 1:
        raise SystemExit(
            f"{path.relative_to(DIST)}: expected one ProfilePage, found {len(profile_pages)}"
        )
    page = profile_pages[0]
    expected_url = f"https://eduarddeboer.com/{lang}/"
    if page.get("url") != expected_url:
        raise SystemExit(
            f"{path.relative_to(DIST)}: ProfilePage URL {page.get('url')!r} != {expected_url!r}"
        )
    if page.get("inLanguage") != lang:
        raise SystemExit(
            f"{path.relative_to(DIST)}: ProfilePage language must be {lang!r}"
        )
    if (page.get("isPartOf") or {}).get("@id") != "https://eduarddeboer.com/#website":
        raise SystemExit(
            f"{path.relative_to(DIST)}: ProfilePage must be part of canonical WebSite"
        )
    if (page.get("mainEntity") or {}).get("@id") != "https://eduarddeboer.com/#person":
        raise SystemExit(
            f"{path.relative_to(DIST)}: ProfilePage mainEntity must be canonical Person"
        )

    language_site_ids = {
        f"https://eduarddeboer.com/{lang}/",
        f"https://eduarddeboer.com/{lang}/#website",
    }
    if any(
        node.get("@type") == "WebSite" and node.get("@id") in language_site_ids
        for node in nodes
    ):
        raise SystemExit(
            f"{path.relative_to(DIST)}: language homepage must not define a separate WebSite"
        )



def require_reputatiecoaching_archive_links() -> None:
    index = DIST / "nl/archief/reputatiecoaching/index.html"
    episode = DIST / "nl/archief/reputatiecoaching/167/index.html"
    require(index)
    require(episode)

    index_html = index.read_text(encoding="utf-8")
    relative_episode = re.compile(
        r"""href=(?:["']?)/nl/archief/reputatiecoaching/167/(?:["']?)""",
        re.I,
    )
    if not relative_episode.search(index_html):
        raise SystemExit(
            "nl/archief/reputatiecoaching/index.html: podcast episode links must "
            "be host-independent relative URLs"
        )
    if "https://eduarddeboer.com/nl/archief/reputatiecoaching/167/" in index_html:
        raise SystemExit(
            "nl/archief/reputatiecoaching/index.html: production-absolute episode "
            "link would break staging navigation"
        )

    episode_html = episode.read_text(encoding="utf-8")
    if "/nl/archive/reputatiecoaching/podcasts/" in episode_html:
        raise SystemExit(
            "nl/archief/reputatiecoaching/167/index.html: legacy podcast archive "
            "back-link returned"
        )
    if not re.search(
        r"""href=(?:["']?)/nl/archief/reputatiecoaching/(?:["']?)""",
        episode_html,
        re.I,
    ):
        raise SystemExit(
            "nl/archief/reputatiecoaching/167/index.html: current archive back-link missing"
        )


def main() -> None:
    for path in (
        DIST / "_worker.js",
        DIST / "release-manifest.json",
        DIST / "en/index.html",
        DIST / "nl/index.html",
    ):
        require(path)

    manifest = json.loads((DIST / "release-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("artifact_contract") != 1:
        raise SystemExit("Unexpected release artifact contract")
    if manifest.get("production_host") != "eduarddeboer.com":
        raise SystemExit("Release artifact has an unexpected production host")

    require_unified_structured_data(DIST / "en/index.html", "en")
    require_unified_structured_data(DIST / "nl/index.html", "nl")
    require_reputatiecoaching_archive_links()

    for lang in ("en", "nl"):
        home = (DIST / lang / "index.html").read_text(encoding="utf-8")
        for forbidden_home_block in ("edb-summary", "edb-proof"):
            if forbidden_home_block in home:
                raise SystemExit(
                    f"{lang}/index.html: obsolete homepage block {forbidden_home_block!r} returned"
                )

    llms = list(DIST.rglob("llms.txt"))
    if not llms:
        raise SystemExit("No llms.txt output was generated")

    html_files = list(DIST.rglob("*.html"))
    if not html_files:
        raise SystemExit("No HTML files were generated")

    asset_refs: set[str] = set()
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        if "<iframe" in lowered:
            raise SystemExit(f"Privacy regression: eager iframe in {path.relative_to(DIST)}")
        if "staging.eduarddeboer" in lowered:
            raise SystemExit(f"Staging hostname leaked into {path.relative_to(DIST)}")
        if "https://eduarddeboer.com/css/" in lowered or "https://eduarddeboer.com/js/" in lowered:
            raise SystemExit(
                f"Host-coupled asset URL in {path.relative_to(DIST)}; "
                "CSS/JS must use host-independent relative URLs"
            )

        for match in re.finditer(r"""(?:href|src)=(?:["']?)(/(?:css|js)/[^"' >]+)""", text, re.I):
            asset_refs.add(match.group(1))

    if not asset_refs:
        raise SystemExit("No host-independent CSS/JS asset references found in generated HTML")

    for ref in sorted(asset_refs):
        asset = DIST / ref.lstrip("/")
        if not asset.is_file():
            raise SystemExit(f"Generated HTML references missing asset: {ref}")

    print(
        f"Verified dist: {len(html_files)} HTML files, {len(llms)} llms.txt output(s), "
        f"{len(asset_refs)} host-independent CSS/JS assets"
    )


if __name__ == "__main__":
    main()
