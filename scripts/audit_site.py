#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "book.json").read_text(encoding="utf-8"))
CONTRACTS_PATH = ROOT / "config" / "chapter-contracts.json"
CONTRACTS = json.loads(CONTRACTS_PATH.read_text(encoding="utf-8")) if CONTRACTS_PATH.exists() else {}
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
        scripts = soup.select("script[src]")
        if any(not script.get("src", "").startswith("/assets/book.js?v=") for script in scripts):
            failures.append(f"{path.name}: unexpected script source")
        if len(scripts) != 1 or soup.select("iframe, object, embed"):
            failures.append(f"{path.name}: unexpected active/external content")
        audio_players = article.select(".audio-reader")
        expected_audio = path.stem in {"chapter-01", "chapter-02", "chapter-03"}
        if expected_audio and len(audio_players) != 1:
            failures.append(f"{path.name}: expected one chapter audio player")
        if not expected_audio and audio_players:
            failures.append(f"{path.name}: unexpected chapter audio player")
        for audio in article.select(".audio-reader audio[src]"):
            src = audio.get("src", "")
            asset = SITE / src.lstrip("/")
            if not asset.is_file():
                failures.append(f"{path.name}: missing audio asset {src}")
            if audio.get("preload") != "metadata":
                failures.append(f"{path.name}: chapter audio must use metadata preload")
        ids = [tag.get("id") for tag in soup.select("[id]")]
        if len(ids) != len(set(ids)):
            failures.append(f"{path.name}: duplicate HTML id")
        contract = CONTRACTS.get(path.stem)
        text = article.get_text(" ", strip=True)
        ratio = chinese_ratio(text)
        minimum_ratio = float(contract.get("minimum_chinese_ratio", 0.58)) if contract else 0.58
        if ratio < minimum_ratio:
            failures.append(
                f"{path.name}: Chinese ratio too low ({ratio:.3f}; minimum {minimum_ratio:.3f})"
            )
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
            for image in figure.select("img[src]"):
                src = image.get("src", "")
                if not image.get("alt", "").strip():
                    failures.append(f"{path.name}: figure image requires non-empty alt text")
                if src.startswith("/"):
                    asset = SITE / src.lstrip("/")
                    if not asset.is_file():
                        failures.append(f"{path.name}: missing image asset {src}")
                    elif asset.suffix.lower() == ".svg":
                        try:
                            svg_root = ET.parse(asset).getroot()
                            if not svg_root.tag.endswith("svg") or not svg_root.get("viewBox"):
                                failures.append(f"{path.name}: invalid SVG image asset {src}")
                            if not svg_root.get("width") or not svg_root.get("height"):
                                failures.append(f"{path.name}: SVG image asset lacks explicit dimensions {src}")
                            if svg_root.find("{http://www.w3.org/2000/svg}title") is None:
                                failures.append(f"{path.name}: SVG image asset lacks title {src}")
                            if svg_root.find("{http://www.w3.org/2000/svg}desc") is None:
                                failures.append(f"{path.name}: SVG image asset lacks desc {src}")
                        except Exception as error:
                            failures.append(f"{path.name}: unreadable SVG image asset {src}: {error}")
                    else:
                        try:
                            with Image.open(asset) as decoded:
                                width, height = decoded.size
                                decoded.verify()
                            if width < 80 or height < 80:
                                failures.append(f"{path.name}: image asset too small {src} ({width}x{height})")
                        except Exception as error:
                            failures.append(f"{path.name}: unreadable image asset {src}: {error}")
        for listing in article.select("figure.code-listing"):
            direct_captions = listing.find_all("figcaption", recursive=False)
            if len(direct_captions) != 1:
                failures.append(f"{path.name}: code listing requires one direct figcaption")
            direct_pres = listing.find_all("pre", recursive=False)
            if not direct_pres:
                failures.append(f"{path.name}: code listing requires a direct pre block")
            for pre in direct_pres:
                children = [child for child in pre.children if getattr(child, "name", None)]
                if len(children) != 1 or children[0].name != "code":
                    failures.append(f"{path.name}: code pre must contain exactly one code element")
        for pre in article.select("pre"):
            if pre.find_parent("figure", class_="code-listing") is None:
                failures.append(f"{path.name}: pre outside figure.code-listing")
        for equation in article.select(".equation-block"):
            if not equation.get("id"):
                failures.append(f"{path.name}: display equation requires stable id")
        for svg in article.select("svg[role='img']"):
            if svg.select_one("title") is None or svg.select_one("desc") is None:
                failures.append(f"{path.name}: accessible SVG requires title and desc")
        if contract:
            required_status = contract.get("required_status")
            actual_status = PROGRESS.get(path.stem, {}).get("status")
            if required_status and actual_status != required_status:
                failures.append(
                    f"{path.name}: chapter contract requires status {required_status!r}, found {actual_status!r}"
                )
            expected_start, expected_end = contract.get("source_pages", [0, -1])
            if declared_pages != set(range(int(expected_start), int(expected_end) + 1)):
                failures.append(f"{path.name}: source pages do not satisfy chapter contract")
            present_ids = {tag.get("id") for tag in article.select("[id]")}
            for required_id in contract.get("required_ids", []):
                if required_id not in present_ids:
                    failures.append(f"{path.name}: chapter contract missing id #{required_id}")
            headings = {heading.get_text(" ", strip=True) for heading in article.select("h1,h2,h3,h4")}
            for required_heading in contract.get("required_headings", []):
                if required_heading not in headings:
                    failures.append(f"{path.name}: chapter contract missing heading {required_heading!r}")
            for selector, expected_count in contract.get("counts", {}).items():
                actual_count = len(article.select(selector))
                if actual_count != int(expected_count):
                    failures.append(
                        f"{path.name}: chapter contract expected {expected_count} for {selector!r}, found {actual_count}"
                    )
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
