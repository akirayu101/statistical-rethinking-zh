#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG for Chapter 7 Figure 7.2."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-07-hominin-brains.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def main() -> int:
    species = [
        ("afarensis", 37.0, 438, 14, 34),
        ("africanus", 35.5, 452, -110, 13),
        ("habilis", 34.5, 612, -72, -18),
        ("boisei", 41.5, 521, 14, 24),
        ("rudolfensis", 55.5, 752, -118, 28),
        ("ergaster", 61.0, 871, 14, -16),
        ("sapiens", 53.5, 1350, 14, -17),
    ]
    width, height = 900, 650
    left, top, plot_width, plot_height = 112, 62, 720, 500
    xmin, xmax, ymin, ymax = 30.0, 70.0, 400.0, 1400.0

    def px(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_width

    def py(value: float) -> float:
        return top + plot_height - (value - ymin) / (ymax - ymin) * plot_height

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>七种人族的脑容量与体重</title>",
        "<desc>横轴是体重千克，纵轴是脑容量立方厘米；七个散点分别标注物种名。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
    ]
    for tick in [30, 40, 50, 60, 70]:
        x = px(tick)
        body.extend([
            f'<line x1="{x:.1f}" y1="{top + plot_height}" x2="{x:.1f}" y2="{top + plot_height + 7}" stroke="#343732"/>',
            f'<text x="{x:.1f}" y="{top + plot_height + 30}" text-anchor="middle" font-family="{FONT}" font-size="17">{tick}</text>',
        ])
    for tick in [400, 600, 800, 1000, 1200, 1400]:
        y = py(tick)
        body.extend([
            f'<line x1="{left - 7}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="#343732"/>',
            f'<text x="{left - 16}" y="{y + 6:.1f}" text-anchor="end" font-family="{FONT}" font-size="17">{tick}</text>',
        ])
    for name, mass, brain, dx, dy in species:
        x, y = px(mass), py(brain)
        anchor = "end" if dx < 0 else "start"
        body.extend([
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="#30332e"/>',
            f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" font-family="Georgia, Times New Roman, serif" font-size="19" font-style="italic" fill="#263f86">{name}</text>',
        ])
    body.extend([
        f'<text x="{left + plot_width / 2}" y="625" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">体重（千克）</text>',
        f'<text x="36" y="{top + plot_height / 2}" transform="rotate(-90 36 {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">脑容量（立方厘米）</text>',
        "</svg>",
        "",
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
