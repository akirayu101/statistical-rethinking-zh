#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG for Chapter 6 Figure 6.1."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-06-selection-distortion.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def main() -> int:
    rng = random.Random(1234)
    count = 200
    news = [rng.gauss(0, 1) for _ in range(count)]
    trust = [rng.gauss(0, 1) for _ in range(count)]
    selected = set(sorted(range(count), key=lambda i: news[i] + trust[i])[-20:])
    sx = [news[i] for i in selected]
    sy = [trust[i] for i in selected]
    xbar, ybar = sum(sx) / len(sx), sum(sy) / len(sy)
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(sx, sy)) / sum((x - xbar) ** 2 for x in sx)
    intercept = ybar - slope * xbar
    corr = sum((x - xbar) * (y - ybar) for x, y in zip(sx, sy)) / math.sqrt(
        sum((x - xbar) ** 2 for x in sx) * sum((y - ybar) ** 2 for y in sy)
    )
    width, height = 900, 650
    left, top, pw, ph = 125, 55, 690, 475
    low, high = -3.2, 3.2

    def px(value: float) -> float:
        return left + (value - low) / (high - low) * pw

    def py(value: float) -> float:
        return top + ph - (value - low) / (high - low) * ph

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>科研资助筛选造成的选择扭曲</title>",
        f"  <desc>两百份提案在筛选前可信度与新闻价值不相关；获选的百分之十内部出现约 {corr:.2f} 的负相关。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
        f'  <rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
    ]
    for i, (x, y) in enumerate(zip(news, trust)):
        chosen = i in selected
        body.append(
            f'  <circle cx="{px(x):.2f}" cy="{py(y):.2f}" r="{5 if chosen else 3.5}" fill="{"#6670ee" if chosen else "#a9aca8"}" opacity="{0.9 if chosen else 0.55}"/>'
        )
    x1, x2 = min(sx), max(sx)
    body.append(f'  <line x1="{px(x1):.2f}" y1="{py(intercept+slope*x1):.2f}" x2="{px(x2):.2f}" y2="{py(intercept+slope*x2):.2f}" stroke="#263f86" stroke-width="3"/>')
    for tick in range(-3, 4):
        body.extend([
            f'  <text x="{px(tick):.2f}" y="560" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
            f'  <text x="105" y="{py(tick)+5:.2f}" text-anchor="end" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
        ])
    body.extend([
        f'  <text x="470" y="606" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">新闻价值</text>',
        f'  <text x="48" y="292" transform="rotate(-90 48 292)" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">可信度</text>',
        f'  <circle cx="640" cy="620" r="5" fill="#6670ee"/><text x="654" y="626" font-family="{FONT}" font-size="16" fill="#30332e">获选</text>',
        f'  <circle cx="720" cy="620" r="4" fill="#a9aca8"/><text x="734" y="626" font-family="{FONT}" font-size="16" fill="#30332e">落选</text>',
        "</svg>", "",
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
