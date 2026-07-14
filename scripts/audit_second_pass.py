#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "book.json").read_text(encoding="utf-8"))
LEDGER_PATH = ROOT / "translations" / "zh" / "second-pass.json"
CHAPTERS = ROOT / "translations" / "zh" / "chapters"
TRACKS = ("translation", "formula", "code")
CHINESE = re.compile(r"[\u4e00-\u9fff]")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit second-pass translation, formula, and code review progress")
    parser.add_argument("--require-complete", action="store_true", help="fail unless all three tracks cover all PDF pages")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures: list[str] = []
    warnings: list[str] = []

    if not LEDGER_PATH.exists():
        print(f"missing {LEDGER_PATH}", file=sys.stderr)
        return 1
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    if tuple(ledger.get("tracks", [])) != TRACKS:
        failures.append(f"second-pass tracks must be {list(TRACKS)!r}")
    records = ledger.get("chapters", {})
    configured_slugs = {chapter["slug"] for chapter in CONFIG["chapters"]}
    for slug in records:
        if slug not in configured_slugs:
            failures.append(f"unknown chapter in second-pass ledger: {slug}")

    totals = {track: 0 for track in TRACKS}
    print("chapter\ttranslation\tformula\tcode\ttotal")
    for chapter in CONFIG["chapters"]:
        slug = chapter["slug"]
        allowed = set(range(int(chapter["start"]), int(chapter["end"]) + 1))
        record = records.get(slug, {})
        counts: dict[str, int] = {}
        for track in TRACKS:
            key = f"{track}_reviewed_pages"
            pages = record.get(key, [])
            if len(pages) != len(set(pages)):
                failures.append(f"{slug}: duplicate page in {key}")
            reviewed = set(pages)
            if not reviewed <= allowed:
                failures.append(f"{slug}: {key} contains a page outside {min(allowed)}-{max(allowed)}")
            if args.require_complete and reviewed != allowed:
                missing = sorted(allowed - reviewed)
                failures.append(f"{slug}: {track} track missing {len(missing)} page(s)")
            counts[track] = len(reviewed)
            totals[track] += len(reviewed)
        print(f"{slug}\t{counts['translation']}\t{counts['formula']}\t{counts['code']}\t{len(allowed)}")

    for path in sorted(CHAPTERS.glob("*.html")):
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        article = soup.select_one("article.book-article")
        if article is None:
            failures.append(f"{path.name}: article.book-article missing")
            continue
        for equation in article.select(".equation-block"):
            if not equation.get("id"):
                failures.append(f"{path.name}: display equation requires a stable id")
        for pre in article.select("pre"):
            listing = pre.find_parent("figure", class_="code-listing")
            if listing is None:
                failures.append(f"{path.name}: pre outside figure.code-listing")
                continue
            children = [child for child in pre.children if getattr(child, "name", None)]
            if len(children) != 1 or children[0].name != "code":
                failures.append(f"{path.name}: pre must contain exactly one code element")
            if "code-output" in pre.get("class", []):
                continue
            for line_number, line in enumerate(pre.get_text("", strip=False).splitlines(), 1):
                comment = re.match(r"^\s*(?:#|//)\s*(.+)$", line)
                if not comment:
                    continue
                value = comment.group(1)
                if LATIN_WORD.search(value) and not CHINESE.search(value):
                    listing_id = listing.get("id", "unidentified-listing")
                    warnings.append(f"{path.name}#{listing_id}:{line_number}: English-only narrative comment")

    total_pages = int(CONFIG["pdf_pages"])
    print(
        "TOTAL\t"
        f"{totals['translation']}/{total_pages}\t"
        f"{totals['formula']}/{total_pages}\t"
        f"{totals['code']}/{total_pages}\t{total_pages}"
    )
    print(f"COMMENT WARNINGS\t{len(warnings)}")
    for warning in warnings[:20]:
        print(f"- {warning}")
    if len(warnings) > 20:
        print(f"- … {len(warnings) - 20} more")

    if failures:
        print("\nFailures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
