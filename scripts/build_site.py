#!/usr/bin/env python3
from __future__ import annotations

import html
import hashlib
import json
import os
import re
import shutil
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "book.json").read_text(encoding="utf-8"))
PROGRESS = json.loads((ROOT / "translations" / "zh" / "progress.json").read_text(encoding="utf-8"))
CHAPTERS = ROOT / "translations" / "zh" / "chapters"
MEDIA = ROOT / "translations" / "zh" / "media"
AUDIO = ROOT / "translations" / "zh" / "audio"
SITE = ROOT / "site"
SITE_BASE_PATH = os.environ.get("SITE_BASE_PATH", "").strip()
if SITE_BASE_PATH:
    SITE_BASE_PATH = f"/{SITE_BASE_PATH.strip('/')}"
CSS_VERSION = hashlib.sha256((ROOT / "assets" / "book.css").read_bytes()).hexdigest()[:12]
JS_VERSION = hashlib.sha256((ROOT / "assets" / "book.js").read_bytes()).hexdigest()[:12]
NUMBERED_CODE_CAPTION = re.compile(r"^(R(?:/Stan)?|Stan)\s+代码\s+(\d+(?:\.\d+)?)(（续）)?$")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def site_url(path: str) -> str:
    """Return a root-relative URL that also works on project GitHub Pages."""
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{SITE_BASE_PATH}{path}"


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
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="{site_url('/assets/book.css')}?v={CSS_VERSION}">
  <script src="{site_url('/assets/book.js')}?v={JS_VERSION}" defer></script>
</head>
<body class="{esc(page_class)}">
  <nav class="topbar"><a href="{site_url('/')}">目录</a><span>{esc(CONFIG['title_zh'])}</span></nav>
  <main>{body}</main>
</body>
</html>
"""


def prepare_chapter_body(body: str, chapter: dict[str, object]) -> str:
    """Normalize code-listing chrome without changing executable source text."""
    soup = BeautifulSoup(body, "html.parser")
    for listing in soup.select("figure.code-listing"):
        caption = listing.find("figcaption", recursive=False)
        if caption is None:
            continue

        raw_caption = caption.get_text(" ", strip=True)
        language = ""
        title = raw_caption
        numbered = NUMBERED_CODE_CAPTION.fullmatch(raw_caption)
        if numbered:
            language, number, continuation = numbered.groups()
            title = f"代码清单 {number}{continuation or ''}"
        elif raw_caption.startswith("Stan 警告"):
            language = "Stan"
            title = raw_caption.replace("Stan 警告", "诊断信息", 1)
            listing["class"] = [*listing.get("class", []), "code-diagnostic"]
        elif raw_caption.startswith("Stan："):
            language = "Stan"
            title = raw_caption.removeprefix("Stan：")
        elif raw_caption.startswith("R/Stan："):
            language = "R / Stan"
            title = raw_caption.removeprefix("R/Stan：")
        elif raw_caption.startswith("R："):
            language = "R"
            title = raw_caption.removeprefix("R：")
        elif raw_caption.startswith("Stan "):
            language = "Stan"
            title = raw_caption.removeprefix("Stan ")
        elif "Stan" in raw_caption:
            language = "R / Stan"
        elif raw_caption.startswith("习题代码"):
            language = "R"

        direct_pres = listing.find_all("pre", recursive=False)
        source_pres = [pre for pre in direct_pres if "code-output" not in pre.get("class", [])]
        if not source_pres:
            listing["class"] = [*listing.get("class", []), "code-diagnostic"]

        caption.clear()
        caption["class"] = [*caption.get("class", []), "code-caption"]
        title_node = soup.new_tag("span")
        title_node["class"] = "code-caption-title"
        title_node.string = title
        caption.append(title_node)
        controls = soup.new_tag("span")
        controls["class"] = "code-caption-controls"
        if language:
            badge = soup.new_tag("span")
            badge["class"] = "code-language"
            badge.string = language.replace("/", " / ")
            controls.append(badge)
        if source_pres:
            button = soup.new_tag("button", type="button")
            button["class"] = "copy-code"
            button["aria-label"] = f"复制{title}"
            button.string = "复制"
            controls.append(button)
        caption.append(controls)

    audio_file = AUDIO / f"{chapter['slug']}.m4a"
    if audio_file.is_file():
        header = soup.select_one("article.book-article > header.chapter-header")
        if header is None:
            raise SystemExit(f"Chapter with audio has no chapter header: {chapter['slug']}")
        header["class"] = [*header.get("class", []), "has-audio"]
        chapter_label = f"第 {chapter['number']} 章"
        player_html = f"""
<div class="audio-reader" data-audio-id="{esc(chapter['slug'])}" role="region" aria-label="{esc(chapter_label)}音频播放器">
  <div class="audio-reader-heading">
    <div>
      <p class="audio-reader-kicker">本章音频 · AAC 24 kbps</p>
      <p class="audio-reader-title">聆听{esc(chapter_label)}</p>
    </div>
    <p class="audio-reader-memory">播放进度仅保存在当前设备</p>
  </div>
  <audio class="audio-reader-native" controls preload="metadata" src="/audio/{esc(chapter['slug'])}.m4a"></audio>
  <div class="audio-reader-controls">
    <button class="audio-reader-toggle" type="button" data-audio-toggle aria-pressed="false">播放</button>
    <div class="audio-reader-timeline">
      <input type="range" min="0" max="1000" step="1" value="0" data-audio-seek aria-label="播放进度">
      <span class="audio-reader-time"><span data-audio-current>0:00</span><span aria-hidden="true"> / </span><span data-audio-duration>--:--</span></span>
    </div>
    <div class="audio-reader-actions">
      <button type="button" data-audio-skip="-15" aria-label="后退十五秒">后退 15 秒</button>
      <button type="button" data-audio-skip="15" aria-label="前进十五秒">前进 15 秒</button>
      <label>速度
        <select data-audio-rate aria-label="播放速度">
          <option value="0.75">0.75×</option>
          <option value="1" selected>1×</option>
          <option value="1.25">1.25×</option>
          <option value="1.5">1.5×</option>
          <option value="2">2×</option>
        </select>
      </label>
      <button type="button" data-audio-reset>清除进度</button>
    </div>
    <p class="audio-reader-status" data-audio-status aria-live="polite">可边读边听，播放进度会自动保存。</p>
  </div>
</div>
"""
        player = BeautifulSoup(player_html, "html.parser").select_one(".audio-reader")
        if player is None:
            raise SystemExit(f"Failed to build audio player: {chapter['slug']}")
        header.insert_after(player)

    if SITE_BASE_PATH:
        for attribute in ("href", "src"):
            for node in soup.find_all(attrs={attribute: True}):
                value = node.get(attribute)
                if isinstance(value, str) and value.startswith("/") and not value.startswith("//"):
                    node[attribute] = site_url(value)
    return str(soup)


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
        chapter_url = esc(site_url(f"/chapters/{slug}.html"))
        title_html = f'<a href="{chapter_url}">{esc(title)}</a>' if fragment.exists() else esc(title)
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
  <p class="scope-note">当前为完整中文工作稿。全书正文、公式、代码与书后材料均已完成第二次精译和验收。</p>
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
    shutil.copy2(ROOT / "assets" / "book.js", SITE / "assets" / "book.js")
    if MEDIA.exists():
        shutil.copytree(MEDIA, SITE / "media")
    if AUDIO.exists():
        shutil.copytree(AUDIO, SITE / "audio")
    (SITE / "index.html").write_text(build_index(), encoding="utf-8")
    for fragment in sorted(CHAPTERS.glob("*.html")):
        chapter = next((item for item in CONFIG["chapters"] if item["slug"] == fragment.stem), None)
        if chapter is None:
            raise SystemExit(f"Translation fragment has no config entry: {fragment.name}")
        body = prepare_chapter_body(fragment.read_text(encoding="utf-8"), chapter)
        output = shell(str(chapter["title_zh"]), body, page_class="chapter-page")
        (SITE / "chapters" / fragment.name).write_text(output, encoding="utf-8")
    print(f"built {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
