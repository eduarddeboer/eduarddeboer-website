#!/usr/bin/env python3
"""Submit Article entity URLs from the website KG snapshot to the Wayback Machine.

The script is intentionally non-destructive and idempotent by default:
- Article entities without a valid HTTP(S) URL are reported.
- URLs that already have an available Wayback capture are skipped.
- Missing URLs are submitted to Save Page Now.
- Per-URL failures are recorded in a JSON report but do not make the run fail.

Use --force to request a fresh capture even when an older snapshot exists.
Use --list-only to validate/extract the URL inventory without network access.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen


DEFAULT_SNAPSHOT = Path("data/kg/snapshot.json")
DEFAULT_REPORT = Path("wayback-report.json")
USER_AGENT = "eduarddeboer.com-wayback/1.0 (+https://eduarddeboer.com/)"


def canonical_http_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None
    # Fragments are browser-local and should not create duplicate archive targets.
    return parts._replace(fragment="").geturl()


def load_inventory(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entities = payload.get("entities")
    if not isinstance(entities, dict):
        raise SystemExit(f"{path}: expected an object at key 'entities'")

    by_url: dict[str, dict[str, Any]] = {}
    missing: list[dict[str, Any]] = []

    for entity_id, entity in sorted(entities.items()):
        if not isinstance(entity, dict) or entity.get("type") != "Article":
            continue

        url = canonical_http_url(entity.get("url"))
        name = entity.get("name")
        if not url:
            missing.append({"entity_id": entity_id, "name": name, "url": entity.get("url")})
            continue

        item = by_url.setdefault(
            url,
            {
                "url": url,
                "entity_ids": [],
                "names": [],
            },
        )
        item["entity_ids"].append(entity_id)
        if name is not None:
            item["names"].append(name)

    return list(by_url.values()), missing


def fetch_json(url: str, timeout: float, attempts: int = 2) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                url,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            )
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(float(attempt))
    assert last_error is not None
    raise last_error


def existing_capture(target_url: str, timeout: float) -> dict[str, Any] | None:
    endpoint = "https://archive.org/wayback/available?" + urlencode({"url": target_url})
    payload = fetch_json(endpoint, timeout=timeout)
    closest = (payload.get("archived_snapshots") or {}).get("closest")
    if not isinstance(closest, dict) or not closest.get("available"):
        return None
    return {
        "url": closest.get("url"),
        "timestamp": closest.get("timestamp"),
        "status": closest.get("status"),
    }


def submit_capture(target_url: str, timeout: float, attempts: int = 2) -> dict[str, Any]:
    encoded = quote(target_url, safe=":/?&=%;,+@!$'()*[]~")
    endpoint = f"https://web.archive.org/save/{encoded}"
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                endpoint,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                },
            )
            with urlopen(request, timeout=timeout) as response:
                location = (
                    response.headers.get("Content-Location")
                    or response.headers.get("Location")
                    or response.geturl()
                )
                if isinstance(location, str) and location.startswith("/"):
                    location = "https://web.archive.org" + location
                return {
                    "http_status": getattr(response, "status", None),
                    "capture_url": location,
                }
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            retryable = not isinstance(exc, HTTPError) or exc.code in {408, 425, 429, 500, 502, 503, 504}
            if attempt < attempts and retryable:
                time.sleep(float(attempt) * 2.0)
                continue
            break

    assert last_error is not None
    raise last_error


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--sleep", type=float, default=1.5)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="0 means all URLs")
    args = parser.parse_args()

    inventory, missing = load_inventory(args.snapshot)
    if args.limit > 0:
        inventory = inventory[: args.limit]

    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot": str(args.snapshot),
        "mode": "list-only" if args.list_only else ("force" if args.force else "missing-only"),
        "article_url_count": len(inventory),
        "missing_url_count": len(missing),
        "missing_urls": missing,
        "entries": [],
        "summary": {
            "already_archived": 0,
            "submitted": 0,
            "failed": 0,
        },
    }

    if args.list_only:
        for item in inventory:
            report["entries"].append({**item, "result": "listed"})
        write_report(args.output, report)
        print(
            f"Article URL inventory: {len(inventory)} unique URL(s); "
            f"{len(missing)} Article entity/entities without a valid URL."
        )
        return 0

    for index, item in enumerate(inventory, start=1):
        target_url = item["url"]
        entry = {**item}
        availability_error: str | None = None

        if not args.force:
            try:
                capture = existing_capture(target_url, timeout=args.timeout)
            except Exception as exc:  # continue with a save attempt if lookup fails
                capture = None
                availability_error = f"{type(exc).__name__}: {exc}"

            if capture:
                entry.update({"result": "already_archived", "capture": capture})
                report["summary"]["already_archived"] += 1
                report["entries"].append(entry)
                print(f"[{index}/{len(inventory)}] already archived: {target_url}")
                continue

        try:
            capture = submit_capture(target_url, timeout=args.timeout)
            entry.update({"result": "submitted", "capture": capture})
            if availability_error:
                entry["availability_error"] = availability_error
            report["summary"]["submitted"] += 1
            print(f"[{index}/{len(inventory)}] submitted: {target_url}")
        except Exception as exc:
            entry.update(
                {
                    "result": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            if availability_error:
                entry["availability_error"] = availability_error
            report["summary"]["failed"] += 1
            print(f"[{index}/{len(inventory)}] FAILED: {target_url}: {exc}")

        report["entries"].append(entry)
        if index < len(inventory) and args.sleep > 0:
            time.sleep(args.sleep)

    write_report(args.output, report)
    summary = report["summary"]
    print(
        "Wayback summary: "
        f"{summary['already_archived']} already archived, "
        f"{summary['submitted']} submitted, "
        f"{summary['failed']} failed; "
        f"{len(missing)} Article entity/entities without a valid URL."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
