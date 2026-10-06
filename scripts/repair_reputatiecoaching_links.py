#!/usr/bin/env python3
"""Repair historical ReputatieCoaching podcast links in small reviewed batches.

Rules:
- Ensure every processed episode has the canonical KG `kgRef`.
- Historical reputatiecoaching.nl HTTP(S) links always resolve through Wayback.
- External HTTP(S) links are left alone when clearly live.
- Clearly dead external links are replaced by a Wayback capture when available.
- If a clearly dead link has no Wayback capture, remove the link but retain its label.
- Ambiguous/transient external failures are retained and reported for review.

The report is deterministic apart from network observations and records every decision.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import socket
import ssl
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PODCAST_ROOT = ROOT / "content" / "nl" / "archief" / "reputatiecoaching"
REPORT_ROOT = ROOT / "data" / "archive" / "link-repair"
USER_AGENT = "eduarddeboer.com-historical-link-repair/1.0 (+https://eduarddeboer.com/)"

# Markdown links only. Images are intentionally excluded: image localization is a
# separate archive concern and should not be silently converted to hyperlinks.
MD_LINK = re.compile(
    r"(?<!!)\[([^\]]+)\]\((https?://[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\)",
    re.IGNORECASE,
)

RC_HOSTS = {"reputatiecoaching.nl", "www.reputatiecoaching.nl", "dev.reputatiecoaching.nl"}
ARCHIVE_HOSTS = {"web.archive.org", "archive.org", "www.archive.org"}

CLEARLY_ALIVE = set(range(200, 400)) | {401, 403, 405, 406, 407, 409, 423, 426, 429}
CLEARLY_DEAD = {404, 410, 451}


@dataclass
class LinkDecision:
    label: str
    original_url: str
    kind: str
    live_status: str | None = None
    live_http_status: int | None = None
    action: str = "kept"
    replacement_url: str | None = None
    wayback_timestamp: str | None = None
    note: str | None = None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=int, required=True)
    p.add_argument("--end", type=int, required=True)
    p.add_argument("--timeout", type=float, default=12.0)
    p.add_argument("--sleep", type=float, default=0.35)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def episode_path(number: int) -> Path:
    return PODCAST_ROOT / f"{number:03d}" / "index.md"


def normalize_url(value: str) -> str:
    value = html.unescape(value.strip())
    parts = urlsplit(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def is_internal_rc(url: str) -> bool:
    return host_of(url) in RC_HOSTS


def is_archive(url: str) -> bool:
    return host_of(url) in ARCHIVE_HOSTS


def kg_ref(number: int) -> str:
    return f"podcast_episode/reputatiecoaching_{number:03d}"


def ensure_kg_ref(text: str, number: int) -> tuple[str, bool]:
    wanted = kg_ref(number)
    m = re.match(r"^---\n([\s\S]*?)\n---\n", text)
    if not m:
        raise SystemExit(f"{episode_path(number)}: no YAML front matter")
    front = m.group(1)
    current = re.search(r"(?m)^kgRef:\s*(.+?)\s*$", front)
    if current:
        if current.group(1).strip().strip("'\"") != wanted:
            raise SystemExit(
                f"{episode_path(number)}: unexpected kgRef {current.group(1)!r}, expected {wanted!r}"
            )
        return text, False

    episode_line = re.search(r"(?m)^episode:\s*\d+\s*$", front)
    if not episode_line:
        raise SystemExit(f"{episode_path(number)}: no episode field in front matter")
    insert_at = m.start(1) + episode_line.end()
    updated = text[:insert_at] + f"\nkgRef: {wanted}" + text[insert_at:]
    return updated, True


def request_status(url: str, timeout: float) -> tuple[str, int | None, str | None]:
    """Return (live|dead|uncertain, status, note)."""
    last_note: str | None = None
    for method in ("HEAD", "GET"):
        try:
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.5",
            }
            if method == "GET":
                headers["Range"] = "bytes=0-1023"
            req = Request(url, headers=headers, method=method)
            with urlopen(req, timeout=timeout) as response:
                status = int(getattr(response, "status", 200) or 200)
                if status in CLEARLY_ALIVE:
                    return "live", status, None
                if status in CLEARLY_DEAD:
                    return "dead", status, None
                return "uncertain", status, f"HTTP {status}"
        except HTTPError as exc:
            status = int(exc.code)
            if status in CLEARLY_ALIVE:
                return "live", status, f"HTTP {status} but resource is reachable"
            if status in CLEARLY_DEAD:
                return "dead", status, None
            last_note = f"HTTP {status}"
            if method == "HEAD" and status in {400, 500, 501, 503}:
                continue
            return "uncertain", status, last_note
        except URLError as exc:
            reason = exc.reason
            note = f"{type(reason).__name__}: {reason}"
            last_note = note
            if isinstance(reason, socket.gaierror):
                return "dead", None, note
            if isinstance(reason, ConnectionRefusedError):
                return "dead", None, note
            if isinstance(reason, ssl.SSLCertVerificationError):
                return "uncertain", None, note
            if isinstance(reason, (TimeoutError, socket.timeout)):
                return "uncertain", None, note
        except (TimeoutError, socket.timeout) as exc:
            return "uncertain", None, f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            last_note = f"{type(exc).__name__}: {exc}"

    return "uncertain", None, last_note or "request failed"


def wayback_variants(url: str) -> list[str]:
    url = normalize_url(url)
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    variants: list[str] = []

    def add(candidate: str) -> None:
        if candidate not in variants:
            variants.append(candidate)

    add(url)
    alt_scheme = "http" if parts.scheme == "https" else "https"
    add(urlunsplit((alt_scheme, parts.netloc, parts.path, parts.query, "")))

    if host in RC_HOSTS:
        bare = "reputatiecoaching.nl"
        for scheme in ("http", "https"):
            for h in (bare, "www." + bare):
                path = parts.path or "/"
                add(urlunsplit((scheme, h, path, parts.query, "")))
                if path != "/":
                    if path.endswith("/"):
                        add(urlunsplit((scheme, h, path.rstrip("/"), parts.query, "")))
                    else:
                        add(urlunsplit((scheme, h, path + "/", parts.query, "")))
    return variants


def fetch_json(url: str, timeout: float) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def wayback_lookup(url: str, episode_date: str, timeout: float) -> dict[str, str] | None:
    target_stamp = re.sub(r"[^0-9]", "", episode_date)[:8] or None
    variants = wayback_variants(url)

    def capture_for(candidate: str, use_target: bool) -> dict[str, str] | None:
        params = {"url": candidate}
        if use_target and target_stamp:
            params["timestamp"] = target_stamp
        endpoint = "https://archive.org/wayback/available?" + urlencode(params)
        try:
            payload = fetch_json(endpoint, timeout)
        except Exception:
            return None
        closest = (payload.get("archived_snapshots") or {}).get("closest")
        if not isinstance(closest, dict) or not closest.get("available"):
            return None
        capture_url = str(closest.get("url") or "")
        stamp = str(closest.get("timestamp") or "")
        status = str(closest.get("status") or "")
        if not capture_url or status not in {"", "200"}:
            return None
        if capture_url.startswith("http://web.archive.org/"):
            capture_url = "https://" + capture_url[len("http://") :]
        return {"url": capture_url, "timestamp": stamp, "original": candidate}

    def score(capture: dict[str, str]) -> tuple[int, int, str]:
        stamp = re.sub(r"[^0-9]", "", capture.get("timestamp", ""))
        if not target_stamp or len(stamp) < 8:
            return (10**12, 1, stamp)
        try:
            target = datetime.strptime(target_stamp, "%Y%m%d")
            captured = datetime.strptime(stamp[:8], "%Y%m%d")
            distance = abs((captured - target).days)
            # With equal distance prefer a capture at/before the episode date.
            after_penalty = 1 if captured > target else 0
            return (distance, after_penalty, stamp)
        except ValueError:
            return (10**12, 1, stamp)

    # Query every URL variant with the episode date. A historical http:// capture
    # can be years closer than the first https:// capture, so never accept the
    # first result blindly.
    captures = [
        capture
        for candidate in variants
        if (capture := capture_for(candidate, use_target=True)) is not None
    ]
    if captures:
        return min(captures, key=score)

    # Only when the timestamp-aware lookup finds nothing, try the generic
    # availability lookup across all variants.
    captures = [
        capture
        for candidate in variants
        if (capture := capture_for(candidate, use_target=False)) is not None
    ]
    if captures:
        return min(captures, key=score)
    return None


def front_date(text: str) -> str:
    m = re.search(r"(?m)^date:\s*['\"]?([^'\"\n]+)", text)
    return m.group(1).strip() if m else ""


def repair_episode(number: int, timeout: float, sleep: float) -> tuple[str, dict[str, Any]]:
    path = episode_path(number)
    original = path.read_text(encoding="utf-8")
    text, kg_added = ensure_kg_ref(original, number)
    date_value = front_date(text)
    decisions: list[LinkDecision] = []
    replacements: dict[str, str | None] = {}

    for match in MD_LINK.finditer(text):
        label, raw_url = match.group(1), match.group(2)
        url = normalize_url(raw_url)
        if url in replacements or is_archive(url):
            continue

        if is_internal_rc(url):
            decision = LinkDecision(label=label, original_url=url, kind="internal_reputatiecoaching")
            capture = wayback_lookup(url, date_value, timeout)
            if capture:
                replacements[url] = capture["url"]
                decision.action = "wayback"
                decision.replacement_url = capture["url"]
                decision.wayback_timestamp = capture["timestamp"]
            else:
                replacements[url] = None
                decision.action = "unlinked"
                decision.note = "No usable Wayback capture found"
            decisions.append(decision)
        else:
            live, status, note = request_status(url, timeout)
            decision = LinkDecision(
                label=label,
                original_url=url,
                kind="external",
                live_status=live,
                live_http_status=status,
                note=note,
            )
            if live == "live":
                replacements[url] = url
                decision.action = "kept_live"
            elif live == "dead":
                capture = wayback_lookup(url, date_value, timeout)
                if capture:
                    replacements[url] = capture["url"]
                    decision.action = "wayback"
                    decision.replacement_url = capture["url"]
                    decision.wayback_timestamp = capture["timestamp"]
                else:
                    replacements[url] = None
                    decision.action = "unlinked"
                    decision.note = (decision.note + "; " if decision.note else "") + "No usable Wayback capture found"
            else:
                replacements[url] = url
                decision.action = "kept_uncertain"
            decisions.append(decision)

        if sleep > 0:
            time.sleep(sleep)

    def replace_match(match: re.Match[str]) -> str:
        label, raw_url = match.group(1), match.group(2)
        url = normalize_url(raw_url)
        if url not in replacements:
            return match.group(0)
        replacement = replacements[url]
        if replacement is None:
            return label
        if replacement == url:
            return match.group(0)
        return f"[{label}]({replacement})"

    text = MD_LINK.sub(replace_match, text)
    changed = text != original
    path.write_text(text, encoding="utf-8")

    report = {
        "episode": number,
        "path": str(path.relative_to(ROOT)),
        "kg_ref": kg_ref(number),
        "kg_ref_added": kg_added,
        "changed": changed,
        "links": [asdict(d) for d in decisions],
        "summary": {
            "links_examined": len(decisions),
            "wayback": sum(d.action == "wayback" for d in decisions),
            "unlinked": sum(d.action == "unlinked" for d in decisions),
            "kept_live": sum(d.action == "kept_live" for d in decisions),
            "kept_uncertain": sum(d.action == "kept_uncertain" for d in decisions),
        },
    }
    return text, report


def main() -> int:
    args = parse_args()
    if not (1 <= args.start <= args.end <= 167):
        raise SystemExit("Require 1 <= start <= end <= 167")
    if args.end - args.start + 1 > 5:
        raise SystemExit("A repair batch may contain at most 5 podcast episodes")

    reports: list[dict[str, Any]] = []
    for number in range(args.start, args.end + 1):
        print(f"START podcast {number:03d}", flush=True)
        _, report = repair_episode(number, args.timeout, args.sleep)
        reports.append(report)
        print(
            f"DONE podcast {number:03d}: "
            f"{report['summary']['wayback']} Wayback, "
            f"{report['summary']['unlinked']} unlinked, "
            f"{report['summary']['kept_live']} live retained, "
            f"{report['summary']['kept_uncertain']} uncertain retained",
            flush=True,
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch": {"start": args.start, "end": args.end},
        "policy": {
            "max_batch_size": 5,
            "internal_reputatiecoaching": "Wayback if available; otherwise unlink",
            "external_live": "retain",
            "external_clearly_dead": "Wayback if available; otherwise unlink",
            "external_uncertain": "retain for review",
        },
        "episodes": reports,
        "summary": {
            "episodes": len(reports),
            "changed_episodes": sum(r["changed"] for r in reports),
            "wayback": sum(r["summary"]["wayback"] for r in reports),
            "unlinked": sum(r["summary"]["unlinked"] for r in reports),
            "kept_live": sum(r["summary"]["kept_live"] for r in reports),
            "kept_uncertain": sum(r["summary"]["kept_uncertain"] for r in reports),
        },
    }

    report_path = REPORT_ROOT / f"batch-{args.start:03d}-{args.end:03d}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.dry_run:
        print(json.dumps(payload["summary"], ensure_ascii=False))
        return 0

    print(f"Report: {report_path.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
