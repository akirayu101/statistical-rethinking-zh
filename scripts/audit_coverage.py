#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "book.json").read_text(encoding="utf-8"))
PROGRESS = json.loads((ROOT / "translations" / "zh" / "progress.json").read_text(encoding="utf-8"))
CONTRACTS = json.loads((ROOT / "config" / "chapter-contracts.json").read_text(encoding="utf-8"))
SITE = ROOT / "site"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    chapters = CONFIG["chapters"]
    slugs = [chapter["slug"] for chapter in chapters]
    if set(slugs) != set(PROGRESS) or set(slugs) != set(CONTRACTS):
        fail("book config, progress ledger, and contracts do not contain the same slugs")

    configured_pages: list[int] = []
    for chapter in chapters:
        configured_pages.extend(range(chapter["start"], chapter["end"] + 1))
    expected_book = list(range(1, int(CONFIG["pdf_pages"]) + 1))
    if configured_pages != expected_book:
        fail("configured chapter ranges do not cover PDF pages 1..pdf_pages exactly once")

    for field in ("translated_pages", "reviewed_pages", "verified_pages"):
        ledger_pages: list[int] = []
        for chapter in chapters:
            slug = chapter["slug"]
            expected = list(range(chapter["start"], chapter["end"] + 1))
            if PROGRESS[slug].get("status") != "verified":
                fail(f"{slug}: status is not verified")
            if CONTRACTS[slug].get("required_status") != "verified":
                fail(f"{slug}: contract status is not verified")
            if PROGRESS[slug].get(field) != expected:
                fail(f"{slug}: {field} does not match its configured page range")
            ledger_pages.extend(PROGRESS[slug][field])
        duplicates = [page for page, count in Counter(ledger_pages).items() if count != 1]
        if ledger_pages != expected_book or duplicates:
            fail(f"{field} does not cover every PDF page exactly once")

    expected_files = {f"{slug}.html" for slug in slugs}
    actual_files = {path.name for path in (SITE / "chapters").glob("*.html")}
    if actual_files != expected_files:
        fail("built chapter pages do not match configured slugs")

    page_paths = [SITE / "index.html", *(SITE / "chapters").glob("*.html")]
    page_ids: dict[str, set[str]] = {}
    for path in page_paths:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        ids = [node["id"] for node in soup.select("[id]")]
        if len(ids) != len(set(ids)):
            fail(f"{path.name}: duplicate HTML id")
        page_ids[path.name] = set(ids)

    for path in page_paths:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for anchor in soup.select("a[href]"):
            href = anchor["href"]
            if href.startswith("#"):
                if href[1:] not in page_ids[path.name]:
                    fail(f"{path.name}: missing local target {href}")
            elif href.startswith("/chapters/"):
                target_path, _, fragment = href.partition("#")
                target_name = Path(target_path).name
                if target_name not in actual_files:
                    fail(f"{path.name}: missing chapter target {href}")
                if fragment and fragment not in page_ids[target_name]:
                    fail(f"{path.name}: missing chapter fragment {href}")
            elif href == "/" and not (SITE / "index.html").exists():
                fail(f"{path.name}: missing site index")

    index = BeautifulSoup((SITE / "index.html").read_text(encoding="utf-8"), "html.parser")
    progress_values = [int(node.get_text(strip=True)) for node in index.select(".progress-grid strong")]
    expected_count = int(CONFIG["pdf_pages"])
    if progress_values != [expected_count] * 4:
        fail(f"index progress is {progress_values}, expected four {expected_count} values")
    if index.select(".status:not(.status-verified)"):
        fail("index contains a non-verified status")

    print(
        f"PASS: {expected_count} PDF pages covered exactly once; "
        f"{len(actual_files)} pages and all internal links verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
