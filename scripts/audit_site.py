#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "book.json").read_text(encoding="utf-8"))
PROGRESS = json.loads((ROOT / "translations" / "zh" / "progress.json").read_text(encoding="utf-8"))
SITE = ROOT / "site"
CHINESE = re.compile(r"[\u4e00-\u9fff]")
PLACEHOLDER = re.compile(r"__(?:KEEP|PROTECT|PLACEHOLDER)_?\d*__", re.I)


def chinese_ratio(text: str) -> float:
    letters = [ch for ch in text if ch.isalpha()]
    return sum(bool(CHINESE.match(ch)) for ch in letters) / len(letters) if letters else 1.0


def parse_page_ranges(value: str) -> set[int]:
    pages: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = (int(item) for item in part.split("-", 1))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return pages


def main() -> int:
    failures: list[str] = []
    index = SITE / "index.html"
    if not index.exists():
        failures.append("site/index.html missing; run scripts/build_site.py")
    else:
        soup = BeautifulSoup(index.read_text(encoding="utf-8"), "html.parser")
        if soup.html is None or soup.html.get("lang") != "zh-CN":
            failures.append("index.html lang must be zh-CN")
        if len(soup.select(".toc-list > li")) != len(CONFIG["chapters"]):
            failures.append("index chapter count differs from config")

    configured_slugs = {chapter["slug"] for chapter in CONFIG["chapters"]}
    for slug, item in PROGRESS.items():
        if slug not in configured_slugs:
            failures.append(f"progress contains unknown slug: {slug}")
            continue
        translated = set(item.get("translated_pages", []))
        reviewed = set(item.get("reviewed_pages", []))
        verified = set(item.get("verified_pages", []))
        chapter = next(ch for ch in CONFIG["chapters"] if ch["slug"] == slug)
        allowed = set(range(int(chapter["start"]), int(chapter["end"]) + 1))
        if not translated <= allowed:
            failures.append(f"{slug}: translated_pages outside configured range")
        if not verified <= reviewed <= translated:
            failures.append(f"{slug}: expected verified ⊆ reviewed ⊆ translated")

    print("page\tzh_ratio\tsections\tsource_pages")
    for path in sorted((SITE / "chapters").glob("*.html")):
        html = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        article = soup.select_one("article.book-article")
        if article is None:
            failures.append(f"{path.name}: article.book-article missing")
            continue
        if PLACEHOLDER.search(html):
            failures.append(f"{path.name}: translation placeholder leaked")
        if soup.select("script[src], iframe, object, embed"):
            failures.append(f"{path.name}: unexpected active/external content")
        ids = [tag.get("id") for tag in soup.select("[id]")]
        if len(ids) != len(set(ids)):
            failures.append(f"{path.name}: duplicate HTML id")
        text = article.get_text(" ", strip=True)
        ratio = chinese_ratio(text)
        if ratio < 0.58:
            failures.append(f"{path.name}: Chinese ratio too low ({ratio:.3f})")
        source_pages = article.get("data-source-pages", "")
        if not source_pages:
            failures.append(f"{path.name}: data-source-pages missing")
        else:
            try:
                declared_pages = parse_page_ranges(source_pages)
            except ValueError:
                failures.append(f"{path.name}: invalid data-source-pages value {source_pages!r}")
                declared_pages = set()
            progress_pages = set(PROGRESS.get(path.stem, {}).get("translated_pages", []))
            if declared_pages != progress_pages:
                failures.append(f"{path.name}: data-source-pages differs from translated_pages")
        for link in article.select('a[href^="#"]'):
            target = link.get("href", "")[1:]
            if target and soup.find(id=target) is None:
                failures.append(f"{path.name}: broken internal link #{target}")
        for figure in article.select("figure"):
            if figure.select_one("figcaption") is None:
                failures.append(f"{path.name}: figure without figcaption")
            for svg in figure.select("svg[role='img']"):
                if svg.select_one("title") is None or svg.select_one("desc") is None:
                    failures.append(f"{path.name}: accessible SVG requires title and desc")
            for image in figure.select("img[src]"):
                src = image.get("src", "")
                if not image.get("alt", "").strip():
                    failures.append(f"{path.name}: figure image requires non-empty alt text")
                if src.startswith("/"):
                    asset = SITE / src.lstrip("/")
                    if not asset.is_file():
                        failures.append(f"{path.name}: missing image asset {src}")
                    else:
                        try:
                            with Image.open(asset) as decoded:
                                width, height = decoded.size
                                decoded.verify()
                            if width < 80 or height < 80:
                                failures.append(f"{path.name}: image asset too small {src} ({width}x{height})")
                        except Exception as error:
                            failures.append(f"{path.name}: unreadable image asset {src}: {error}")
        print(f"{path.name}\t{ratio:.3f}\t{len(article.select('section'))}\t{source_pages}")

    if failures:
        print("\nFailures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
