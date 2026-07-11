#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "book.json").read_text(encoding="utf-8"))
SOURCE = ROOT / "source"


def resolve_pdf(value: str | None) -> Path:
    raw = value or CONFIG["default_pdf"]
    path = Path(raw).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"Source PDF not found: {path}")
    return path


def chapter_by_slug(slug: str) -> dict[str, object]:
    for chapter in CONFIG["chapters"]:
        if chapter["slug"] == slug:
            return chapter
    choices = ", ".join(chapter["slug"] for chapter in CONFIG["chapters"])
    raise SystemExit(f"Unknown chapter {slug!r}. Choose one of: {choices}")


def node_text(node: ET.Element) -> str:
    return html.unescape("".join(node.itertext())).replace("\u00a0", " ").strip()


def extract_chapter(pdf: Path, chapter: dict[str, object]) -> None:
    slug = str(chapter["slug"])
    out_dir = SOURCE / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    xml_path = out_dir / f"{slug}.xml"
    command = [
        "pdftohtml", "-xml", "-hidden", "-i",
        "-f", str(chapter["start"]), "-l", str(chapter["end"]),
        str(pdf), str(xml_path),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    root = ET.parse(xml_path).getroot()
    pages: list[dict[str, object]] = []
    text_parts: list[str] = []
    for page in root.findall("page"):
        number = int(page.attrib["number"])
        spans: list[dict[str, object]] = []
        for node in page.findall("text"):
            text = node_text(node)
            if not text:
                continue
            spans.append({
                "top": int(node.attrib.get("top", "0")),
                "left": int(node.attrib.get("left", "0")),
                "width": int(node.attrib.get("width", "0")),
                "height": int(node.attrib.get("height", "0")),
                "font": int(node.attrib.get("font", "-1")),
                "bold": node.find("b") is not None,
                "italic": node.find("i") is not None,
                "text": text,
            })
        spans.sort(key=lambda item: (int(item["top"]), int(item["left"])))
        pages.append({"page": number, "width": int(page.attrib["width"]), "height": int(page.attrib["height"]), "spans": spans})
        text_parts.append(f"\n===== PDF PAGE {number} =====\n")
        current_top = None
        current: list[str] = []
        for span in spans:
            top = int(span["top"])
            if current_top is None or abs(top - current_top) <= 2:
                current.append(str(span["text"]))
                current_top = top if current_top is None else current_top
            else:
                text_parts.append(" ".join(current) + "\n")
                current = [str(span["text"])]
                current_top = top
        if current:
            text_parts.append(" ".join(current) + "\n")

    (out_dir / "pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "layout.txt").write_text("".join(text_parts).lstrip(), encoding="utf-8")
    manifest = {
        "slug": slug,
        "pdf": str(pdf),
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "start": chapter["start"],
        "end": chapter["end"],
        "pages_extracted": len(pages),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"extracted {slug}: PDF pages {chapter['start']}-{chapter['end']} -> {out_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract page-positioned local review material from the source PDF.")
    parser.add_argument("--pdf", help="Override source PDF path.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chapter", help="Chapter slug, for example chapter-01.")
    group.add_argument("--all", action="store_true", help="Extract all configured page ranges.")
    args = parser.parse_args()
    pdf = resolve_pdf(args.pdf)
    chapters = CONFIG["chapters"] if args.all else [chapter_by_slug(args.chapter)]
    for chapter in chapters:
        extract_chapter(pdf, chapter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
