#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG for Chapter 7 Figure 7.5."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-07-information-divergence.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def divergence(q1: float) -> float:
    return 0.3 * math.log(0.3 / q1) + 0.7 * math.log(0.7 / (1 - q1))


def main() -> int:
    width, height = 900, 620
    left, top, plot_width, plot_height = 120, 70, 690, 430
    xmin, xmax, ymin, ymax = 0.0, 1.0, 0.0, 2.65

    def px(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_width

    def py(value: float) -> float:
        return top + plot_height - (value - ymin) / (ymax - ymin) * plot_height

    sequence = [0.01 + 0.98 * step / 240 for step in range(241)]
    points = " ".join(f"{fmt(px(value))},{fmt(py(divergence(value)))}" for value in sequence)
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>近似分布 q 相对于真实分布 p 的信息散度</title>",
        "<desc>当 q 的第一个概率等于 p 的 0.3 时散度为零；向两侧偏离时散度均增大。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
        f'<polyline points="{points}" fill="none" stroke="#6670ee" stroke-width="4"/>',
        f'<line x1="{fmt(px(0.3))}" y1="{top}" x2="{fmt(px(0.3))}" y2="{top + plot_height}" stroke="#454842" stroke-width="1.7" stroke-dasharray="7 6"/>',
        f'<text x="{fmt(px(0.3) + 13)}" y="180" font-family="{FONT}" font-size="20" fill="#30332e">q = p</text>',
    ]
    for tick in [0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        x = px(tick)
        body.extend([
            f'<line x1="{fmt(x)}" y1="{top + plot_height}" x2="{fmt(x)}" y2="{top + plot_height + 7}" stroke="#343732"/>',
            f'<text x="{fmt(x)}" y="{top + plot_height + 31}" text-anchor="middle" font-family="{FONT}" font-size="17">{tick:.1f}</text>',
        ])
    for tick in [0, 0.5, 1.0, 1.5, 2.0, 2.5]:
        y = py(tick)
        body.extend([
            f'<line x1="{left - 7}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#343732"/>',
            f'<text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="17">{tick:.1f}</text>',
        ])
    body.extend([
        f'<text x="{left + plot_width / 2}" y="570" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">q[1]</text>',
        f'<text x="38" y="{top + plot_height / 2}" transform="rotate(-90 38 {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">q 相对于 p 的散度</text>',
        "</svg>",
        "",
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
