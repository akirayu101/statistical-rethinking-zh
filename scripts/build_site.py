#!/usr/bin/env python3
from __future__ import annotations

import html
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "book.json").read_text(encoding="utf-8"))
PROGRESS = json.loads((ROOT / "translations" / "zh" / "progress.json").read_text(encoding="utf-8"))
CHAPTERS = ROOT / "translations" / "zh" / "chapters"
MEDIA = ROOT / "translations" / "zh" / "media"
SITE = ROOT / "site"
CSS_VERSION = hashlib.sha256((ROOT / "assets" / "book.css").read_bytes()).hexdigest()[:12]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def status_label(status: str) -> str:
    return {"in_progress": "翻译中", "draft": "翻译中", "reviewed": "已审校", "verified": "已验收"}.get(status, "待翻译")


def shell(title: str, body: str, *, page_class: str = "") -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | {esc(CONFIG['title_zh'])}</title>
  <meta name="color-scheme" content="light">
  <link rel="stylesheet" href="/assets/book.css?v={CSS_VERSION}">
</head>
<body class="{esc(page_class)}">
  <nav class="topbar"><a href="/">目录</a><span>{esc(CONFIG['title_zh'])}</span></nav>
  <main>{body}</main>
</body>
</html>
"""


def build_index() -> str:
    rows: list[str] = []
    verified = 0
    reviewed = 0
    translated = 0
    total = int(CONFIG["pdf_pages"])
    for chapter in CONFIG["chapters"]:
        slug = chapter["slug"]
        item = PROGRESS.get(slug, {})
        translated += len(item.get("translated_pages", []))
        reviewed += len(item.get("reviewed_pages", []))
        verified += len(item.get("verified_pages", []))
        status = item.get("status", "pending")
        prefix = f"第 {chapter['number']} 章" if chapter["number"] else ("书前" if slug == "front-matter" else "书后")
        title = chapter["title_zh"]
        fragment = CHAPTERS / f"{slug}.html"
        title_html = f'<a href="/chapters/{esc(slug)}.html">{esc(title)}</a>' if fragment.exists() else esc(title)
        rows.append(
            f'<li><span class="toc-number">{esc(prefix)}</span><span class="toc-title">{title_html}'
            f'<small>{esc(chapter["title_en"])}</small></span>'
            f'<span class="status status-{esc(status)}">{esc(status_label(status))}</span></li>'
        )
    body = f"""
<section class="landing">
  <p class="eyebrow">第二版 · 中文化项目</p>
  <h1>{esc(CONFIG['title_zh'])}</h1>
  <p class="subtitle">{esc(CONFIG['author'])}</p>
  <div class="progress-grid">
    <div><strong>{translated}</strong><span>已译 PDF 页</span></div>
    <div><strong>{reviewed}</strong><span>已审校 PDF 页</span></div>
    <div><strong>{verified}</strong><span>已验收 PDF 页</span></div>
    <div><strong>{total}</strong><span>全书 PDF 页</span></div>
  </div>
  <p class="scope-note">当前为本地工作稿。目录只链接已有中文稿的章节；“待翻译”页面不会生成占位正文。</p>
</section>
<section class="toc-panel">
  <h2>目录与进度</h2>
  <ol class="toc-list">{''.join(rows)}</ol>
</section>
"""
    return shell("目录", body, page_class="contents-page")


def main() -> int:
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True)
    (SITE / "chapters").mkdir(parents=True)
    shutil.copy2(ROOT / "assets" / "book.css", SITE / "assets" / "book.css")
    if MEDIA.exists():
        shutil.copytree(MEDIA, SITE / "media")
    (SITE / "index.html").write_text(build_index(), encoding="utf-8")
    for fragment in sorted(CHAPTERS.glob("*.html")):
        chapter = next((item for item in CONFIG["chapters"] if item["slug"] == fragment.stem), None)
        if chapter is None:
            raise SystemExit(f"Translation fragment has no config entry: {fragment.name}")
        body = fragment.read_text(encoding="utf-8")
        output = shell(str(chapter["title_zh"]), body, page_class="chapter-page")
        (SITE / "chapters" / fragment.name).write_text(output, encoding="utf-8")
    print(f"built {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
