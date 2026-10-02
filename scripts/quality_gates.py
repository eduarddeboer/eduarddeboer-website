#!/usr/bin/env python3
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

MAX_HTML_BYTES = 180_000
MAX_CSS_BYTES = 220_000
MAX_JS_BYTES = 120_000
MAX_IMAGE_BYTES = 250_000
MAX_TOTAL_JS_BYTES = 180_000

THIRD_PARTY_SCRIPT = re.compile(r'https?://(?!eduarddeboer\.com)', re.I)
EXTERNAL_FONT = re.compile(r'(fonts\.googleapis\.com|fonts\.gstatic\.com|use\.typekit\.net)', re.I)


class AccessibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.h1_count = 0
        self.problems: list[str] = []
        self._link_stack: list[dict[str, object]] = []
        self._button_stack: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs_list)
        if tag == "html":
            self.lang = (attrs.get("lang") or "").strip()
        if tag == "h1":
            self.h1_count += 1

        tabindex = attrs.get("tabindex")
        if tabindex and tabindex.lstrip("+").isdigit() and int(tabindex) > 0:
            self.problems.append("positive tabindex")

        if tag == "img":
            if "alt" not in attrs:
                self.problems.append("image without alt")
            if not attrs.get("width") or not attrs.get("height"):
                self.problems.append("image without intrinsic width/height")

        if tag == "svg" and attrs.get("aria-hidden") != "true":
            if attrs.get("role") == "img" and not (attrs.get("aria-label") or attrs.get("aria-labelledby")):
                self.problems.append("informative SVG without accessible name")

        if tag == "a":
            self._link_stack.append({
                "named": bool((attrs.get("aria-label") or attrs.get("title") or "").strip()),
                "depth": 1,
            })
        elif self._link_stack:
            self._link_stack[-1]["depth"] = int(self._link_stack[-1]["depth"]) + 1

        if tag == "button":
            self._button_stack.append({
                "named": bool((attrs.get("aria-label") or attrs.get("title") or "").strip()),
                "depth": 1,
            })
        elif self._button_stack:
            self._button_stack[-1]["depth"] = int(self._button_stack[-1]["depth"]) + 1

    def handle_data(self, data: str) -> None:
        if data.strip():
            if self._link_stack:
                self._link_stack[-1]["named"] = True
            if self._button_stack:
                self._button_stack[-1]["named"] = True

    def handle_endtag(self, tag: str) -> None:
        if self._link_stack:
            if tag == "a" and int(self._link_stack[-1]["depth"]) == 1:
                item = self._link_stack.pop()
                if not item["named"]:
                    self.problems.append("link without accessible name")
            else:
                self._link_stack[-1]["depth"] = max(1, int(self._link_stack[-1]["depth"]) - 1)

        if self._button_stack:
            if tag == "button" and int(self._button_stack[-1]["depth"]) == 1:
                item = self._button_stack.pop()
                if not item["named"]:
                    self.problems.append("button without accessible name")
            else:
                self._button_stack[-1]["depth"] = max(1, int(self._button_stack[-1]["depth"]) - 1)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> None:
    problems: list[str] = []
    html_files = sorted(DIST.rglob("*.html"))

    for path in html_files:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if len(raw) > MAX_HTML_BYTES:
            problems.append(f"{rel(path)}: HTML exceeds {MAX_HTML_BYTES} bytes")

        parser = AccessibilityParser()
        parser.feed(text)

        if not parser.lang:
            problems.append(f"{rel(path)}: missing html lang")

        # Hugo emits dist/index.html as the multilingual root entry point.
        # The actual localized content documents are /en/ and /nl/.
        is_multilingual_root = path == DIST / "index.html"
        if not is_multilingual_root and parser.h1_count != 1:
            problems.append(f"{rel(path)}: expected exactly one h1, found {parser.h1_count}")
        for issue in parser.problems:
            problems.append(f"{rel(path)}: {issue}")

        if EXTERNAL_FONT.search(text):
            problems.append(f"{rel(path)}: external font dependency")
        for match in re.finditer(r"<script\b[^>]*\bsrc=[\"']([^\"']+)", text, re.I):
            src = match.group(1)
            if src.startswith(("http://", "https://")) and THIRD_PARTY_SCRIPT.search(src):
                problems.append(f"{rel(path)}: third-party script {src}")

    css_files = sorted(DIST.rglob("*.css"))
    for path in css_files:
        if path.stat().st_size > MAX_CSS_BYTES:
            problems.append(f"{rel(path)}: CSS exceeds {MAX_CSS_BYTES} bytes")

    js_files = sorted(DIST.rglob("*.js"))
    total_js = sum(path.stat().st_size for path in js_files)
    if total_js > MAX_TOTAL_JS_BYTES:
        problems.append(f"total JavaScript exceeds {MAX_TOTAL_JS_BYTES} bytes")
    for path in js_files:
        if path.stat().st_size > MAX_JS_BYTES:
            problems.append(f"{rel(path)}: JavaScript exceeds {MAX_JS_BYTES} bytes")

    for suffix in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.avif"):
        for path in DIST.rglob(suffix):
            if path.stat().st_size > MAX_IMAGE_BYTES:
                problems.append(f"{rel(path)}: image exceeds {MAX_IMAGE_BYTES} bytes")

    if problems:
        raise SystemExit("\n".join(problems))

    print(
        f"Quality gates passed: {len(html_files)} HTML, {len(css_files)} CSS, "
        f"{len(js_files)} JS files; total JS={total_js} bytes"
    )


if __name__ == "__main__":
    main()
