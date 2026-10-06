#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "data" / "archive" / "link-repair"
PODCAST_ROOT = ROOT / "content" / "nl" / "archief" / "reputatiecoaching"

def target_episode(url: str) -> int | None:
    patterns = [
        r"reputatiecoaching\.nl/(\d{1,3})/?$",
        r"reputatiecoaching\.nl/podcast-(\d{1,3})/?$",
        r"reputatiecoaching\.nl(\d{1,3})/?$",
    ]
    for pattern in patterns:
        m = re.search(pattern, url, re.I)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 167:
                return n
    return None

def replace_once(text: str, old: str, new: str, context: str) -> tuple[str, bool]:
    if new in text:
        return text, False
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{context}: expected exactly one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1), True

def replace_all(text: str, old: str, new: str, context: str) -> tuple[str, int]:
    count = text.count(old)
    if count == 0:
        if new in text:
            return text, 0
        raise RuntimeError(f"{context}: could not find {old!r}")
    return text.replace(old, new), count

PRETTY_TARGETS = {
    "backwpup": "https://nl.wordpress.org/plugins/backwpup/",
    "dropbox": "https://www.dropbox.com/",
    "facebook": "https://www.facebook.com/reputatiecoaching/",
    "gplus": "https://www.google.com/maps?cid=4978892197645719955",
    "keepass": "https://keepass.info/",
    "lastpass": "https://www.lastpass.com/nl",
    "linkedin": "https://www.linkedin.com/in/eduarddeboer/nl",
    "mijndomein": "https://www.mijndomein.nl/",
    "pinterest": "https://nl.pinterest.com/reputatiecoach/",
    "powerpress": "https://nl.wordpress.org/plugins/powerpress/",
    "simplybook": "https://simplybook.me/nl/",
    "webinarignition": "https://webinarignition.com/",
    "yubikey": "https://www.yubico.com/",
}

def restore_aliases() -> list[str]:
    changed = []
    by_episode: dict[int, list[tuple[str,int]]] = {}
    for report in sorted(REPORT_ROOT.glob("batch-???-???.json")):
        data = json.loads(report.read_text(encoding="utf-8"))
        for ep in data.get("episodes", []):
            number = int(ep["episode"])
            for link in ep.get("links", []):
                if link.get("action") != "unlinked":
                    continue
                target = target_episode(link.get("original_url") or "")
                if target is None:
                    continue
                label = link.get("label") or ""
                if not label:
                    continue
                by_episode.setdefault(number, []).append((label, target))

    for number, links in sorted(by_episode.items()):
        path = PODCAST_ROOT / f"{number:03d}" / "index.md"
        text = path.read_text(encoding="utf-8")
        original = text
        for label, target in links:
            if number == 66 and target == 65:
                continue
            destination = f"/nl/archief/reputatiecoaching/{target:03d}/"
            replacement = f"[{label}]({destination})"
            text, _ = replace_all(text, label, replacement, f"episode {number:03d} alias")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    # Restore additional labels that shared the same original alias URL but
    # were omitted from the one-decision-per-URL audit report.
    extras = {
        7: [("www.reputatiecoaching.nl/podcast-7", 7)],
        55: [("ReputatieCoaching Podcast aflevering 55", 55)],
        62: [("ReputatieCoaching Podcast aflevering 62", 62)],
        63: [("ReputatieCoaching Podcast nummer 62", 62)],
        65: [("ReputatieCoaching Podcast aflevering 65", 65)],
        79: [("ReputatieCoaching Podcast aflevering 79", 79)],
    }
    for number, items in extras.items():
        path = PODCAST_ROOT / f"{number:03d}" / "index.md"
        text = path.read_text(encoding="utf-8")
        original = text
        for label, target in items:
            destination = f"/nl/archief/reputatiecoaching/{target:03d}/"
            if f"[{label}]({destination})" in text:
                continue
            if label in text:
                text = text.replace(label, f"[{label}]({destination})")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

    # Episode 066 had a reference-style link in the original source. Its
    # imported audit label accidentally swallowed the preceding image marker.
    path = PODCAST_ROOT / "066" / "index.md"
    text = path.read_text(encoding="utf-8")
    old = "Vorige week vertelde ik dat de nieuwe Google Maps nu officieel live is"
    new = "[Vorige week](/nl/archief/reputatiecoaching/065/) vertelde ik dat de nieuwe Google Maps nu officieel live is"
    if old in text:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

    return changed

def restore_pretty_links() -> list[str]:
    changed = []
    by_episode: dict[int, list[tuple[str, str, str]]] = {}
    for report in sorted(REPORT_ROOT.glob("batch-???-???.json")):
        data = json.loads(report.read_text(encoding="utf-8"))
        for ep in data.get("episodes", []):
            number = int(ep["episode"])
            for link in ep.get("links", []):
                if link.get("action") != "unlinked":
                    continue
                url = link.get("original_url") or ""
                m = re.search(r"reputatiecoaching\.nl/([^/?#]+)/?$", url, re.I)
                if not m:
                    continue
                slug = m.group(1).lower()
                if slug in {"itunes", "stitcher"}:
                    continue
                destination = PRETTY_TARGETS.get(slug)
                label = link.get("label") or ""
                if destination and label:
                    by_episode.setdefault(number, []).append((label, slug, destination))

    for number, links in sorted(by_episode.items()):
        path = PODCAST_ROOT / f"{number:03d}" / "index.md"
        text = path.read_text(encoding="utf-8")
        original = text
        for label, slug, destination in links:
            replacement = f"[{label}]({destination})"
            if replacement in text:
                continue
            count = text.count(label)
            if count == 0:
                continue
            # URL-shaped labels can safely be restored everywhere. For generic
            # names restore the first historical occurrence only; the report
            # records the first occurrence of each unique shortlink URL.
            if "reputatiecoaching.nl/" in label:
                text = text.replace(label, replacement)
            else:
                text = text.replace(label, replacement, 1)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return changed

def restore_slideshare() -> list[str]:
    changes = []

    profile = "https://web.archive.org/web/20160322214551/http://www.slideshare.net:80/ReputatieCoaching/"
    tandarts = "https://web.archive.org/web/20230126131639/https://www.slideshare.net/ReputatieCoaching/hoe-werf-je-als-tandarts-nieuwe-patienten-online"
    restaurants = "https://web.archive.org/web/20160314212738/http://www.slideshare.net/ReputatieCoaching/vragen-over-lokale-restaurants-in-google-maps-op-ios"

    replacements = {
        120: (
            r"\*\* Hoe werf je als tandarts nieuwe patiënten online? \*\* from **Eduard de Boer**",
            rf"\*\* [Hoe werf je als tandarts nieuwe patiënten online?]({tandarts}) \*\* from **[Eduard de Boer]({profile})**",
        ),
        153: (
            r"\*\* Vragen over lokale restaurants in Google Maps op iOS \*\* from **Eduard de Boer**",
            rf"\*\* [Vragen over lokale restaurants in Google Maps op iOS]({restaurants}) \*\* from **[Eduard de Boer]({profile})**",
        ),
    }

    for number, (old, new) in replacements.items():
        path = PODCAST_ROOT / f"{number:03d}" / "index.md"
        text = path.read_text(encoding="utf-8")
        text2, changed = replace_once(text, old, new, f"episode {number:03d} SlideShare")
        if changed:
            path.write_text(text2, encoding="utf-8")
            changes.append(str(path.relative_to(ROOT)))
    return changes

def restore_image_markup() -> list[str]:
    changed = []

    cases = {
        35: [(
            "*Historische afbeelding niet beschikbaar: 10-SEO-Copywriting-Tips-For-Writing-Content-That-Ranks-In-2013-Infographic*",
            "![10 SEO Copywriting Tips For Writing Content That Ranks In 2013](10-SEO-Copywriting-Tips-For-Writing-Content-That-Ranks-In-2013-Infographic.png)",
        )],
        48: [(
            "*Historische afbeelding niet beschikbaar: 20131028-AppleMaps-info*\u00a0 *Historische afbeelding niet beschikbaar: 20131028-AppleMaps-reviews**Historische afbeelding niet beschikbaar: 20131028-AppleMaps-fotos*",
            "![Apple Maps bedrijfsinformatie](20131028-AppleMaps-info.png)\n\n![Apple Maps reviews](20131028-AppleMaps-reviews.png)\n\n![Apple Maps foto's](20131028-AppleMaps-fotos.png)",
        )],
        154: [(
            "*Historische afbeelding niet beschikbaar: 20151112-Lokale-Gidsen-punten*Hotels en restaurants in het buitenland kunnen nog wel wat aan hun exposure doen.",
            "![Google Lokale Gidsen punten](20151112-Lokale-Gidsen-punten.png)\n\nHotels en restaurants in het buitenland kunnen nog wel wat aan hun exposure doen.",
        )],
        155: [(
            "## 20151119-google-lokale-gidsen-punten\n\nStatus Google Lokale Gidsen",
            "## 20151119-google-lokale-gidsen-punten\n\n![Google Lokale Gidsen punten](20151119-google-lokale-gidsen-punten.jpg)\n\nStatus Google Lokale Gidsen",
        )],
    }

    for number, reps in cases.items():
        path = PODCAST_ROOT / f"{number:03d}" / "index.md"
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in reps:
            text, _ = replace_once(text, old, new, f"episode {number:03d} image")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return changed

def main():
    changed = []
    changed += restore_aliases()
    changed += restore_pretty_links()
    changed += restore_slideshare()
    changed += restore_image_markup()
    print(json.dumps({"changed_files": sorted(set(changed)), "count": len(set(changed))}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

# Trigger restoration workflow after workflow registration.
