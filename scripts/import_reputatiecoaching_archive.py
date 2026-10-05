#!/usr/bin/env python3
"""Import ReputatieCoaching as an explicitly historical, KG-backed website archive."""

from __future__ import annotations

import argparse
import csv
import difflib
import email.utils
import hashlib
import html
import json
import re
import shutil
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import yaml
from PIL import Image

try:
    from bs4 import BeautifulSoup
    from markdownify import markdownify as html_to_markdown
except ImportError:
    BeautifulSoup = None
    html_to_markdown = None

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "content" / "nl" / "archief" / "reputatiecoaching"
FEED = ROOT / "static" / "podcast" / "reputatiecoaching.xml"
MEDIA_ROOT = ROOT / "static" / "media" / "archive" / "reputatiecoaching"
SOURCE_CSV = ROOT / "source_data" / "archive" / "reputatiecoaching-source.csv"
MANIFEST = ROOT / "data" / "archive" / "reputatiecoaching-import.json"
KG_SNAPSHOT = ROOT / "data" / "kg" / "snapshot.json"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
VIDEO_SHORTCODE = re.compile(
    r"\{\{[<%]\s*(youtube|vimeo)\s+([^\s>%}]+).*?[>%]\}\}", re.IGNORECASE
)
GENERIC_SHORTCODE = re.compile(r"\{\{[<%]\s*([^>%}]+).*?[>%]\}\}", re.DOTALL)
MD_IMAGE = re.compile(
    r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\)"
)
MD_DESTINATION = re.compile(r"\]\(([^)\s]+)\)")
HTML_IMG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
HTML_IFRAME = re.compile(r"<iframe\b[\s\S]*?</iframe>", re.IGNORECASE)
HTML_AUDIO = re.compile(r"<audio\b[\s\S]*?</audio>", re.IGNORECASE)
SCRIPT_STYLE = re.compile(r"<(script|style)\b[\s\S]*?</\1>", re.IGNORECASE)
WP_SIZE = re.compile(r"-\d{2,5}x\d{2,5}(?=\.[^.]+$)", re.IGNORECASE)


def git_commit(path: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def parse_csv() -> dict[int, dict[str, str]]:
    raw = SOURCE_CSV.read_text(encoding="utf-8-sig")
    # Historical export anomaly: rows 164 and 165 were concatenated.
    raw = re.sub(
        r"\s+(?=165,https://www\.reputatiecoaching\.nl/)",
        "\n",
        raw,
        count=1,
    )
    rows: dict[int, dict[str, str]] = {}
    for fields in csv.reader(raw.splitlines()):
        if not fields or not fields[0].strip().isdigit():
            continue
        if len(fields) < 7:
            raise SystemExit(f"Malformed podcast metadata row: {fields[:3]!r}")
        episode = int(fields[0].strip())
        rows[episode] = {
            "old_url": fields[1].strip(),
            "audio": fields[2].strip(),
            "date": fields[3].strip(),
            "title": fields[4].strip(),
            "type": fields[5].strip(),
            "tags": fields[6].strip(),
        }
    missing = sorted(set(range(1, 168)) - set(rows))
    if missing:
        raise SystemExit(f"Podcast metadata is missing episodes: {missing}")
    return rows


def load_kg_podcasts() -> tuple[dict[int, dict], str | None]:
    payload = json.loads(KG_SNAPSHOT.read_text(encoding="utf-8"))
    entities = payload.get("entities")
    if not isinstance(entities, dict):
        raise SystemExit("KG snapshot has no entities object")

    episodes: dict[int, dict] = {}
    for episode in range(1, 168):
        entity_id = f"podcast_episode/reputatiecoaching_{episode:03d}"
        entity = entities.get(entity_id)
        if not isinstance(entity, dict):
            raise SystemExit(
                f"KG snapshot is missing required podcast entity {entity_id}; "
                "sync the website projection from the KG before importing the archive"
            )
        audio = str(entity.get("audio_url") or "").strip()
        if not audio.startswith("https://archive.org/"):
            raise SystemExit(f"{entity_id} has no valid Archive.org audio_url in the KG")
        size = entity.get("audio_size_bytes")
        if not isinstance(size, int) or size <= 0:
            raise SystemExit(f"{entity_id} has no positive audio_size_bytes in the KG")
        episodes[episode] = entity

    return episodes, (payload.get("source") or {}).get("commit")


def parse_date(value: object, fallback: str | None = None) -> datetime:
    if isinstance(value, datetime):
        dt = value
    elif value:
        text = str(value).strip()
        dt = None
        for candidate in (text, text.replace("Z", "+00:00")):
            try:
                dt = datetime.fromisoformat(candidate)
                break
            except ValueError:
                pass
        if dt is None:
            for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M"):
                try:
                    dt = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    pass
        if dt is None:
            try:
                dt = email.utils.parsedate_to_datetime(text)
            except Exception:
                dt = None
        if dt is None:
            raise ValueError(f"Unsupported date: {value!r}")
    elif fallback:
        return parse_date(fallback)
    else:
        raise ValueError("No date available")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def yaml_front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$", text)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    return data if isinstance(data, dict) else {}, match.group(2)


def normalize_stem(path_or_name: str) -> str:
    name = Path(urllib.parse.unquote(path_or_name)).name
    stem = WP_SIZE.sub("", name)
    stem = Path(stem).stem.lower()
    stem = re.sub(r"\bpodcast[-_ ]?0*(\d+)\b", r"podcast\1", stem)
    return re.sub(r"[^a-z0-9]+", "", stem)


def image_quality(path: Path) -> tuple[int, int, int, int]:
    try:
        with Image.open(path) as im:
            width, height = im.size
    except Exception:
        width = height = 0
    ext_rank = {".png": 4, ".webp": 3, ".jpg": 2, ".jpeg": 2, ".gif": 1}.get(
        path.suffix.lower(), 0
    )
    return width * height, min(width, height), ext_rank, path.stat().st_size


def choose_best_image(
    requested: str, source_root: Path, source_page: Path | None, episode: int
) -> Path | None:
    parsed = urllib.parse.urlsplit(html.unescape(requested))
    ref = urllib.parse.unquote(parsed.path)
    candidates: list[Path] = []

    def add(path: Path) -> None:
        try:
            if path.is_file() and path.suffix.lower() in IMAGE_EXTS and path not in candidates:
                candidates.append(path)
            unsized = Path(WP_SIZE.sub("", str(path)))
            if unsized != path and unsized.is_file() and unsized not in candidates:
                candidates.append(unsized)
        except OSError:
            # Historical content contains a few remote image URLs whose path
            # component exceeds local filesystem name limits. Those are not
            # local archive paths and should simply fall through.
            return

    rc_hosts = {
        "",
        "reputatiecoaching.nl",
        "www.reputatiecoaching.nl",
        "dev.reputatiecoaching.nl",
    }
    host = parsed.netloc.lower().split("@")[-1].split(":")[0]
    localizable_host = host in rc_hosts

    if localizable_host:
        if ref.startswith("/wp-content/"):
            add(source_root / "static" / ref.lstrip("/"))
            add(source_root / ref.lstrip("/"))
        elif ref.startswith("/"):
            add(source_root / "static" / ref.lstrip("/"))
            add(source_root / ref.lstrip("/"))
        elif source_page is not None:
            add(source_page.parent / ref)

    original_dir = source_root / "000-origineel" / "podcasts" / f"{episode:03d}"
    requested_stem = normalize_stem(ref)
    if original_dir.is_dir():
        for p in original_dir.iterdir():
            if not p.is_file() or p.suffix.lower() not in IMAGE_EXTS:
                continue
            similarity = difflib.SequenceMatcher(
                None, requested_stem, normalize_stem(p.name)
            ).ratio()
            if normalize_stem(p.name) == requested_stem or similarity >= 0.84:
                add(p)

    if not candidates:
        return None
    return max(candidates, key=image_quality)


def safe_asset_name(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", path.stem).strip("-._") or "image"
    return stem + path.suffix.lower()


def copy_asset(source: Path, destination_dir: Path, used_names: dict[str, Path]) -> str:
    name = safe_asset_name(source)
    if name in used_names and used_names[name] != source:
        digest = hashlib.sha1(str(source).encode()).hexdigest()[:8]
        name = f"{Path(name).stem}-{digest}{Path(name).suffix}"
    used_names[name] = source
    destination = destination_dir / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return name


def replace_html_images(body: str) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        src_match = re.search(r"\bsrc\s*=\s*([\"']?)([^\"'\s>]+)\1", tag, re.I)
        alt_match = re.search(r"\balt\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S)
        if not src_match:
            return ""
        src = src_match.group(2)
        alt = html.unescape(alt_match.group(2)) if alt_match else ""
        return f"![{alt}]({src})"

    return HTML_IMG.sub(repl, body)


def sanitize_historical_body(body: str, unsupported: set[str]) -> str:
    body = SCRIPT_STYLE.sub("", body)
    body = HTML_AUDIO.sub("", body)

    def iframe_repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        src = re.search(r"\bsrc\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S)
        return f"\n[Historische ingesloten media]({src.group(2)})\n" if src else ""

    body = HTML_IFRAME.sub(iframe_repl, body)
    body = replace_html_images(body)

    def video_repl(match: re.Match[str]) -> str:
        provider = match.group(1).lower()
        ident = match.group(2).strip("\"'")
        if provider == "youtube":
            return f"[Historische video op YouTube](https://www.youtube.com/watch?v={ident})"
        return f"[Historische video op Vimeo](https://vimeo.com/{ident})"

    body = VIDEO_SHORTCODE.sub(video_repl, body)

    def generic_repl(match: re.Match[str]) -> str:
        value = " ".join(match.group(1).split())
        unsupported.add(value[:120])
        return f"*Historische ingesloten media niet rechtstreeks overgenomen ({value}).*"

    body = GENERIC_SHORTCODE.sub(generic_repl, body)
    body = body.replace("https://dev.reputatiecoaching.nl", "https://www.reputatiecoaching.nl")
    return body.strip()


def localize_images(
    body: str,
    source_root: Path,
    source_page: Path | None,
    episode: int,
    destination: Path,
    missing: list[dict],
    copied: list[dict],
) -> str:
    used_names: dict[str, Path] = {}

    def repl(match: re.Match[str]) -> str:
        alt, requested = match.group(1), match.group(2)
        if requested.startswith(("data:", "#")):
            return match.group(0)
        source = choose_best_image(requested, source_root, source_page, episode)
        if source is None:
            if requested.startswith(("http://", "https://")):
                missing.append(
                    {"episode": episode, "requested": requested, "reason": "external-only"}
                )
                return f"[Historische afbeelding: {alt or 'bekijk bron'}]({requested})"
            missing.append(
                {"episode": episode, "requested": requested, "reason": "not-found"}
            )
            return f"*Historische afbeelding niet beschikbaar: {alt or Path(requested).name}*"
        name = copy_asset(source, destination, used_names)
        area, short_side, _, size = image_quality(source)
        copied.append(
            {
                "episode": episode,
                "requested": requested,
                "source": str(source.relative_to(source_root)),
                "destination": name,
                "pixels": area,
                "short_side": short_side,
                "bytes": size,
            }
        )
        return f"![{alt}]({name})"

    return MD_IMAGE.sub(repl, body)


def _is_reputatiecoaching_host(host: str) -> bool:
    host = host.lower().split("@")[-1].split(":")[0]
    return host == "reputatiecoaching.nl" or host.endswith(".reputatiecoaching.nl")


def _legacy_path(value: str) -> str | None:
    parsed = urllib.parse.urlsplit(html.unescape(value))
    if parsed.netloc and not _is_reputatiecoaching_host(parsed.netloc):
        return None
    path = parsed.path or "/"
    if not path.startswith("/"):
        return None
    return re.sub(r"/+$", "", path) or "/"


def rewrite_historical_links(
    body: str,
    metadata: dict[int, dict[str, str]],
) -> str:
    episode_paths = {
        _legacy_path(row["old_url"]): episode
        for episode, row in metadata.items()
        if _legacy_path(row["old_url"])
    }

    def rewrite_destination(destination: str) -> str:
        destination = html.unescape(destination)
        if destination.startswith(("#", "mailto:", "tel:", "data:")):
            return destination

        parsed = urllib.parse.urlsplit(destination)
        is_rc = destination.startswith("/") or _is_reputatiecoaching_host(parsed.netloc)
        if not is_rc:
            return destination

        if destination.startswith("/"):
            original = urllib.parse.urljoin("https://www.reputatiecoaching.nl", destination)
        else:
            original = parsed._replace(
                scheme="https",
                netloc="www.reputatiecoaching.nl",
            ).geturl()

        path = _legacy_path(original)
        episode = episode_paths.get(path)
        if episode is not None:
            target = f"/nl/archief/reputatiecoaching/{episode:03d}/"
            if parsed.fragment:
                target += f"#{parsed.fragment}"
            return target

        return "https://web.archive.org/web/*/" + urllib.parse.quote(
            original,
            safe=":/?&=%;,+@!~",
        )

    return MD_DESTINATION.sub(
        lambda match: "](" + rewrite_destination(match.group(1)) + ")",
        body,
    )


def strip_duplicate_title(body: str, title: str) -> str:
    lines = body.lstrip().splitlines()
    if lines and lines[0].startswith("# "):
        lhs = re.sub(r"\W+", "", lines[0][2:].lower())
        rhs = re.sub(r"\W+", "", title.lower())
        if lhs and (lhs == rhs or lhs in rhs or rhs in lhs):
            body = "\n".join(lines[1:]).lstrip()

    # The page template supplies the document H1. Historical body-level H1s
    # become H2s so every rendered episode keeps one unambiguous page heading.
    return re.sub(r"(?m)^# (.+)$", r"## \1", body)


def historical_wrapper(episode: int, dt: datetime, full: bool) -> str:
    status = (
        "Volledige transcriptie uit het oorspronkelijke archief."
        if full
        else "Oorspronkelijke shownotes. Vanaf aflevering 153 werd de podcast niet meer volledig uitgeschreven."
    )
    date_label = dt.strftime("%d-%m-%Y").lstrip("0")
    return (
        f"> **Historisch archief.** Deze aflevering verscheen op {date_label} als onderdeel "
        "van ReputatieCoaching (2012–2016). De oorspronkelijke tekst is hieronder "
        "historisch bewaard. Diensten, contactgegevens, links, tools en adviezen kunnen "
        "inmiddels verouderd zijn.\n\n"
        f"**Transcriptiestatus:** {status}\n\n"
    )


def write_episode(
    episode: int,
    title: str,
    description: str,
    dt: datetime,
    body: str,
    source_root: Path,
    source_page: Path | None,
    manifest: dict,
) -> None:
    destination = TARGET / f"{episode:03d}"
    destination.mkdir(parents=True, exist_ok=True)
    body = sanitize_historical_body(body, manifest["unsupported_shortcodes"])
    body = localize_images(
        body,
        source_root,
        source_page,
        episode,
        destination,
        manifest["missing_images"],
        manifest["images"],
    )
    body = rewrite_historical_links(body, manifest["legacy_metadata"])
    body = strip_duplicate_title(body, title)
    full = episode <= 152
    front = {
        "title": title,
        "date": dt.isoformat(),
        "description": description.strip(),
        "episode": episode,
        "kgRef": f"podcast_episode/reputatiecoaching_{episode:03d}",
        "source_url": manifest["legacy_metadata"][episode]["old_url"],
        "historical": True,
        "archivePeriod": "2012–2016",
        "transcriptStatus": "full" if full else "shownotes",
        # Historical transcript assets named *feature*/*cover* are inline source
        # material, not article hero images. Disable Congo's filename auto-match.
        "feature": "__archive_feature_disabled__",
        "cover": "__archive_cover_disabled__",
        "thumbnail": "__archive_thumbnail_disabled__",
        "showAuthor": False,
        "showReadingTime": False,
        "showTableOfContents": True,
        "showTaxonomies": False,
    }
    yaml_text = yaml.safe_dump(front, allow_unicode=True, sort_keys=False, width=1000).strip()
    output = (
        "---\n" + yaml_text + "\n---\n\n"
        + historical_wrapper(episode, dt, full)
        + body.strip() + "\n"
    )
    (destination / "index.md").write_text(output, encoding="utf-8")


def private_episodes(
    source_root: Path,
    metadata: dict[int, dict[str, str]],
    kg_episodes: dict[int, dict],
) -> list[dict]:
    pages = sorted(source_root.glob("content/podcast/*/*/index.md"))
    if len(pages) != 167:
        raise SystemExit(f"Private source must contain exactly 167 podcast pages, found {len(pages)}")
    result: list[dict] = []
    for page in pages:
        fm, body = yaml_front_matter(page)
        episode = int(fm.get("episode") or page.parent.name)
        auxiliary = source_root / "data" / "podcasts" / f"episode-{episode:03d}.yml"
        extra = yaml.safe_load(auxiliary.read_text(encoding="utf-8")) or {} if auxiliary.exists() else {}
        row = metadata[episode]
        title = str(fm.get("title") or extra.get("title") or row["title"]).strip()
        description = str(fm.get("description") or fm.get("intro") or extra.get("description") or "").strip()
        if not description:
            description = re.sub(r"\s+", " ", re.sub(r"[#*_>\[\]()]", " ", body))[:500].strip()
        audio = str(kg_episodes[episode]["audio_url"]).strip()
        dt = parse_date(fm.get("date") or extra.get("date"), row["date"])
        result.append(
            {
                "episode": episode,
                "title": title,
                "description": description,
                "audio": audio,
                "audio_size_bytes": int(kg_episodes[episode]["audio_size_bytes"]),
                "date": dt,
                "body": body,
                "source_page": page,
            }
        )
    return sorted(result, key=lambda item: item["episode"])


def public_episodes(
    source_root: Path,
    metadata: dict[int, dict[str, str]],
    kg_episodes: dict[int, dict],
) -> list[dict]:
    if BeautifulSoup is None or html_to_markdown is None:
        raise SystemExit("BeautifulSoup and markdownify are required for public mirror fallback")
    feed = source_root / "podcast" / "index.xml"
    items = ET.parse(feed).findall("./channel/item")
    if len(items) != 167:
        raise SystemExit(f"Public mirror feed must contain exactly 167 items, found {len(items)}")
    result: list[dict] = []
    for index, item in enumerate(items):
        episode = 167 - index
        title = (item.findtext("title") or metadata[episode]["title"]).strip()
        link = (item.findtext("link") or "").strip()
        page = source_root / urllib.parse.urlsplit(link).path.strip("/") / "index.html"
        if not page.exists():
            raise SystemExit(f"Public mirror page missing for episode {episode}: {page}")
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        content = soup.select_one(".content")
        if content is None:
            raise SystemExit(f"No .content element for episode {episode}")
        body = html_to_markdown(str(content), heading_style="ATX", bullets="-").strip()
        description = (item.findtext("description") or "").strip()
        description = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(description)))
        dt = parse_date(item.findtext("pubDate"), metadata[episode]["date"])
        result.append(
            {
                "episode": episode,
                "title": html.unescape(title),
                "description": description,
                "audio": str(kg_episodes[episode]["audio_url"]).strip(),
                "audio_size_bytes": int(kg_episodes[episode]["audio_size_bytes"]),
                "date": dt,
                "body": body,
                "source_page": page,
            }
        )
    return sorted(result, key=lambda item: item["episode"])


def prepare_feed_art(source_root: Path, manifest: dict) -> str:
    candidates = [
        source_root / "static" / "images" / "logos" / "reputatie-coaching-podcast-logo-groot.jpg",
        source_root / "static" / "wp-content" / "uploads" / "2016" / "02" / "Reputatie-Coaching-Podcast-logo-groot-1024x1024.jpg",
    ]
    candidates = [p for p in candidates if p.exists()]
    if not candidates:
        candidates = sorted(source_root.glob("000-origineel/podcasts/*/ReputatieCoaching-Podcast-*.png"))
    if not candidates:
        candidates = [source_root / "images" / "rc-header.png"]
        candidates = [p for p in candidates if p.exists()]
    if not candidates:
        raise SystemExit("No historical ReputatieCoaching artwork found")

    source = max(candidates, key=image_quality)
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    original = MEDIA_ROOT / ("podcast-artwork-original" + source.suffix.lower())
    shutil.copy2(source, original)

    with Image.open(source) as im:
        im = im.convert("RGB")
        width, height = im.size
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        im = im.crop((left, top, left + side, top + side))
        target_side = max(1400, min(3000, side))
        if im.size != (target_side, target_side):
            im = im.resize((target_side, target_side), Image.Resampling.LANCZOS)
        art = MEDIA_ROOT / "reputatiecoaching-podcast.jpg"
        im.save(art, format="JPEG", quality=95, optimize=True, progressive=True)

    manifest["feed_artwork"] = {
        "source": str(source.relative_to(source_root)),
        "original_copy": str(original.relative_to(ROOT)),
        "aggregator_copy": str(art.relative_to(ROOT)),
        "source_quality": image_quality(source),
    }
    return "https://eduarddeboer.com/media/archive/reputatiecoaching/reputatiecoaching-podcast.jpg"


def add_text(parent: ET.Element, name: str, value: object, **attrs: str) -> ET.Element:
    node = ET.SubElement(parent, name, attrs)
    node.text = str(value)
    return node


def write_feed(episodes: list[dict], art_url: str, manifest: dict) -> None:
    atom = "http://www.w3.org/2005/Atom"
    itunes = "http://www.itunes.com/dtds/podcast-1.0.dtd"
    content_ns = "http://purl.org/rss/1.0/modules/content/"
    ET.register_namespace("atom", atom)
    ET.register_namespace("itunes", itunes)
    ET.register_namespace("content", content_ns)

    lengths = {
        item["episode"]: int(item["audio_size_bytes"])
        for item in episodes
    }

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    add_text(channel, "title", "ReputatieCoaching Podcast — historisch archief")
    add_text(channel, "link", "https://eduarddeboer.com/nl/archief/reputatiecoaching/")
    add_text(channel, "description", "Historisch archief van de 167 ReputatieCoaching Podcast-afleveringen van Eduard de Boer, gepubliceerd van 2012 tot en met 2016.")
    add_text(channel, "language", "nl-NL")
    add_text(channel, "copyright", "© Eduard de Boer")
    add_text(channel, f"{{{itunes}}}author", "Eduard de Boer")
    add_text(channel, f"{{{itunes}}}summary", "Historische podcastserie over online reputatie, lokale vindbaarheid en online marketing, oorspronkelijk gepubliceerd tussen 2012 en 2016.")
    add_text(channel, f"{{{itunes}}}explicit", "false")
    add_text(channel, f"{{{itunes}}}type", "episodic")
    add_text(channel, f"{{{itunes}}}complete", "Yes")
    ET.SubElement(channel, f"{{{itunes}}}image", {"href": art_url})
    category = ET.SubElement(channel, f"{{{itunes}}}category", {"text": "Business"})
    ET.SubElement(category, f"{{{itunes}}}category", {"text": "Marketing"})
    owner = ET.SubElement(channel, f"{{{itunes}}}owner")
    add_text(owner, f"{{{itunes}}}name", "Eduard de Boer")
    add_text(owner, f"{{{itunes}}}email", "info@reputatiecoaching.nl")
    image = ET.SubElement(channel, "image")
    add_text(image, "url", art_url)
    add_text(image, "title", "ReputatieCoaching Podcast — historisch archief")
    add_text(image, "link", "https://eduarddeboer.com/nl/archief/reputatiecoaching/")
    ET.SubElement(channel, f"{{{atom}}}link", {"href": "https://eduarddeboer.com/podcast/reputatiecoaching.xml", "rel": "self", "type": "application/rss+xml"})
    latest = max(item["date"] for item in episodes)
    add_text(channel, "lastBuildDate", email.utils.format_datetime(latest.astimezone(timezone.utc)))

    for item_data in sorted(episodes, key=lambda item: item["episode"], reverse=True):
        episode = item_data["episode"]
        item = ET.SubElement(channel, "item")
        add_text(item, "title", item_data["title"])
        link = f"https://eduarddeboer.com/nl/archief/reputatiecoaching/{episode:03d}/"
        add_text(item, "link", link)
        add_text(item, "guid", f"reputatiecoaching-podcast-{episode:03d}", isPermaLink="false")
        add_text(item, "pubDate", email.utils.format_datetime(item_data["date"].astimezone(timezone.utc)))
        description = item_data["description"]
        if episode >= 153:
            description = (description + " Historisch archief: voor deze aflevering zijn de oorspronkelijke shownotes beschikbaar; de podcast werd vanaf aflevering 153 niet meer volledig uitgeschreven.").strip()
        add_text(item, "description", description)
        ET.SubElement(item, "enclosure", {"url": item_data["audio"], "length": str(lengths.get(episode, 0)), "type": "audio/mpeg"})
        add_text(item, f"{{{itunes}}}author", "Eduard de Boer")
        add_text(item, f"{{{itunes}}}episode", episode)
        add_text(item, f"{{{itunes}}}episodeType", "full")
        add_text(item, f"{{{itunes}}}explicit", "false")
        add_text(item, f"{{{itunes}}}summary", description)
        ET.SubElement(item, f"{{{itunes}}}image", {"href": art_url})

    FEED.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    tree.write(FEED, encoding="utf-8", xml_declaration=True)

    manifest["feed"] = {
        "path": str(FEED.relative_to(ROOT)),
        "items": len(episodes),
        "enclosure_lengths_resolved": sum(1 for value in lengths.values() if value > 0),
        "enclosure_lengths_unresolved": sorted(episode for episode, value in lengths.items() if value <= 0),
    }


def write_section() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    text = """---
title: "ReputatieCoaching Podcast — historisch archief"
description: "De 167 afleveringen van de ReputatieCoaching Podcast (2012–2016), met oorspronkelijke transcripties of shownotes en historisch beeldmateriaal waar beschikbaar."
showDate: false
showAuthor: false
showReadingTime: false
groupByYear: true
type: "reputatiecoaching-podcast"
cascade:
  type: "reputatiecoaching-podcast"
---

Van december 2012 tot en met mei 2016 maakte ik **167 afleveringen van de ReputatieCoaching Podcast**. Dit is het historische archief van die serie.

De afleveringen staan hier bewust als **historisch materiaal**. Ze laten zien waar ik mij in die jaren mee bezighield — online reputatie, lokale vindbaarheid, reviews, sociale media, WordPress en online marketing — maar ze zijn geen weergave van mijn huidige werk of van actuele adviezen. Diensten, contactgegevens, platforms, functies, links en aanbevelingen uit de oorspronkelijke teksten kunnen inmiddels zijn veranderd of verdwenen.

Bij **aflevering 1 tot en met 152** is de oorspronkelijke volledige uitgeschreven tekst opgenomen waar die in het archief aanwezig is. Vanaf **aflevering 153** veranderde het format en werd de podcast niet meer volledig uitgeschreven; daar publiceer ik de oorspronkelijke shownotes.

De audio wordt niet opnieuw gehost: de oorspronkelijke MP3-bestanden blijven via Internet Archive beschikbaar. Afbeeldingen zijn waar mogelijk vanuit het oorspronkelijke ReputatieCoaching-archief overgenomen, waarbij de grootste beschikbare bronvariant als uitgangspunt is gekozen.

[RSS-feed voor podcastapps](/podcast/reputatiecoaching.xml)
"""
    (TARGET / "_index.md").write_text(text, encoding="utf-8")


def validate_output(episodes: list[dict], manifest: dict) -> None:
    pages = sorted(TARGET.glob("[0-9][0-9][0-9]/index.md"))
    if len(pages) != 167:
        raise SystemExit(f"Expected 167 imported episode pages, found {len(pages)}")
    items = ET.parse(FEED).findall("./channel/item")
    if len(items) != 167:
        raise SystemExit(f"Expected 167 RSS items, found {len(items)}")
    for item in items:
        enclosure = item.find("enclosure")
        if enclosure is None or not enclosure.attrib.get("url", "").startswith("https://archive.org/"):
            raise SystemExit("Every RSS item must have an Archive.org audio enclosure")
    manifest["validation"] = {
        "episode_pages": len(pages),
        "rss_items": len(items),
        "full_transcript_episodes": 152,
        "shownotes_episodes": 15,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Checked-out ReputatieCoaching source")
    args = parser.parse_args()
    source_root = args.source.resolve()
    metadata = parse_csv()
    kg_episodes, kg_commit = load_kg_podcasts()

    private = (source_root / "content" / "podcast").is_dir()
    if private:
        episodes = private_episodes(source_root, metadata, kg_episodes)
        source_kind = "private-normalized-source"
    else:
        episodes = public_episodes(source_root, metadata, kg_episodes)
        source_kind = "public-static-mirror"

    if [item["episode"] for item in episodes] != list(range(1, 168)):
        raise SystemExit("Episodes are not a complete 1..167 sequence")

    if TARGET.exists():
        shutil.rmtree(TARGET)
    if MEDIA_ROOT.exists():
        shutil.rmtree(MEDIA_ROOT)

    manifest: dict = {
        "schema_version": 1,
        "source_kind": source_kind,
        "source_commit": git_commit(source_root),
        "source_repository": "eduarddeboer/reputatiecoaching.nl" if private else "reputatiecoaching/reputatiecoaching.github.io",
        "historical_period": "2012–2016",
        "episodes": 167,
        "kg_source_commit": kg_commit,
        "audio_source": "data/kg/snapshot.json",
        "legacy_metadata": metadata,
        "images": [],
        "missing_images": [],
        "unsupported_shortcodes": set(),
    }

    write_section()
    for item in episodes:
        write_episode(
            episode=item["episode"],
            title=item["title"],
            description=item["description"],
            dt=item["date"],
            body=item["body"],
            source_root=source_root,
            source_page=item["source_page"],
            manifest=manifest,
        )

    art_url = prepare_feed_art(source_root, manifest)
    write_feed(episodes, art_url, manifest)
    validate_output(episodes, manifest)

    manifest.pop("legacy_metadata", None)
    manifest["unsupported_shortcodes"] = sorted(manifest["unsupported_shortcodes"])
    manifest["image_count"] = len(manifest["images"])
    manifest["missing_image_count"] = len(manifest["missing_images"])
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_kind": source_kind,
        "episodes": 167,
        "images": manifest["image_count"],
        "missing_images": manifest["missing_image_count"],
        "unsupported_shortcodes": len(manifest["unsupported_shortcodes"]),
        "feed_lengths_resolved": manifest["feed"]["enclosure_lengths_resolved"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
