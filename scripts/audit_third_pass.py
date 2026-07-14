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
LEDGER_PATH = ROOT / "translations" / "zh" / "third-pass.json"
CHAPTERS = ROOT / "translations" / "zh" / "chapters"
MEDIA = ROOT / "translations" / "zh" / "media"
GLOSSARY_PATH = ROOT / "translations" / "zh" / "glossary.json"
TRACKS = ("semantic_accuracy", "natural_chinese", "contextual_terminology")
VISIBLE_ENGLISH = re.compile(r"\b(?:Bayes|Bayesian|Gaussian|likelihood|Likelihood)\b")
TERM_SPACING = re.compile(r"[\u4e00-\u9fff] (?:贝叶斯|高斯|似然)|(?:贝叶斯|高斯|似然) [\u4e00-\u9fff]")
VISIBLE_ATTRIBUTES = ("alt", "title", "aria-label")
EXCLUDED_TAGS = {"code", "pre", "script", "style", "cite"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit third-pass semantic, natural-Chinese, and terminology review")
    parser.add_argument("--require-complete", action="store_true", help="fail unless all tracks cover every PDF page")
    return parser.parse_args()


def excluded(tag) -> bool:
    if tag is None:
        return False
    if tag.name in EXCLUDED_TAGS or tag.find_parent(EXCLUDED_TAGS):
        return True
    return tag.get("lang") == "en" or tag.find_parent(attrs={"lang": "en"}) is not None


def allowed_english(path: Path, value: str) -> bool:
    if path.name == "chapter-09.html" and "BUGS（Bayesian inference Using Gibbs Sampling）" in value:
        return True
    if path.name == "chapter-15.html" and "likelihood（似然）" in value and "significant（显著）" in value:
        return True
    return False


def expand_range(value: object, slug: str, track: str, failures: list[str]) -> set[int]:
    if not isinstance(value, list) or len(value) != 2 or not all(isinstance(item, int) for item in value):
        failures.append(f"{slug}: {track}_reviewed_range must be [start, end]")
        return set()
    start, end = value
    if start > end:
        failures.append(f"{slug}: {track}_reviewed_range starts after it ends")
        return set()
    return set(range(start, end + 1))


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    if not LEDGER_PATH.exists():
        print(f"missing {LEDGER_PATH}", file=sys.stderr)
        return 1
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    if tuple(ledger.get("tracks", [])) != TRACKS:
        failures.append(f"third-pass tracks must be {list(TRACKS)!r}")
    records = ledger.get("chapters", {})
    configured_slugs = {chapter["slug"] for chapter in CONFIG["chapters"]}
    for slug in records:
        if slug not in configured_slugs:
            failures.append(f"unknown chapter in third-pass ledger: {slug}")

    totals = {track: 0 for track in TRACKS}
    print("chapter\tsemantic\tnatural\tterminology\ttotal")
    for chapter in CONFIG["chapters"]:
        slug = chapter["slug"]
        allowed = set(range(int(chapter["start"]), int(chapter["end"]) + 1))
        record = records.get(slug, {})
        counts: dict[str, int] = {}
        for track in TRACKS:
            reviewed = expand_range(record.get(f"{track}_reviewed_range"), slug, track, failures)
            if not reviewed <= allowed:
                failures.append(f"{slug}: {track} contains a page outside {min(allowed)}-{max(allowed)}")
            if args.require_complete and reviewed != allowed:
                failures.append(f"{slug}: {track} does not cover the complete source range")
            counts[track] = len(reviewed)
            totals[track] += len(reviewed)
        print(
            f"{slug}\t{counts['semantic_accuracy']}\t{counts['natural_chinese']}\t"
            f"{counts['contextual_terminology']}\t{len(allowed)}"
        )

    for path in sorted(CHAPTERS.glob("*.html")):
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for tag in soup.find_all(True):
            if excluded(tag):
                continue
            for attribute in VISIBLE_ATTRIBUTES:
                value = tag.get(attribute)
                if value and VISIBLE_ENGLISH.search(value) and not allowed_english(path, value):
                    failures.append(f"{path.name}: untranslated visible term in {attribute}: {value[:100]}")
                if value and TERM_SPACING.search(value):
                    failures.append(f"{path.name}: inconsistent Chinese term spacing in {attribute}: {value[:100]}")
        for node in soup.find_all(string=True):
            if excluded(node.parent):
                continue
            value = " ".join(str(node).split())
            if VISIBLE_ENGLISH.search(value) and not allowed_english(path, value):
                failures.append(f"{path.name}: untranslated visible term: {value[:100]}")
            if TERM_SPACING.search(value):
                failures.append(f"{path.name}: inconsistent Chinese term spacing: {value[:100]}")

    for path in sorted(MEDIA.glob("*.svg")):
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "xml")
        for node in soup.find_all("text"):
            label = " ".join(node.get_text(" ", strip=True).split())
            if label in {"密度", "负对数密度"}:
                failures.append(f"{path.name}: standalone figure label must say 概率密度: {label}")

    glossary = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    terms = glossary.get("terms", glossary)
    required_terms = {
        "density": "概率密度",
        "probability density": "概率密度",
        "Gaussian process": "高斯过程",
        "Bayesian imputation": "贝叶斯插补",
        "log-pointwise predictive density": "对数逐点预测密度",
        "lppd": "对数逐点预测密度",
    }
    for source, expected in required_terms.items():
        if terms.get(source) != expected:
            failures.append(f"glossary: {source!r} must map to {expected!r}")

    figure = (MEDIA / "chapter-10-gaussian-maxent.svg").read_text(encoding="utf-8")
    for required in ("概率密度", "高斯分布（β = 2）", "最大值（β = 2）"):
        if required not in figure:
            failures.append(f"chapter-10-gaussian-maxent.svg: missing reader-facing label {required!r}")

    total_pages = int(CONFIG["pdf_pages"])
    print(
        "TOTAL\t"
        f"{totals['semantic_accuracy']}/{total_pages}\t"
        f"{totals['natural_chinese']}/{total_pages}\t"
        f"{totals['contextual_terminology']}/{total_pages}\t{total_pages}"
    )
    if failures:
        print("\nFailures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
