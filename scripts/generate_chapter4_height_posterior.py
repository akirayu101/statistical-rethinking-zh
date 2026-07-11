#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG used for Figure 4.4."""

from __future__ import annotations

import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-height-posterior.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def main() -> int:
    rng = random.Random(4404)
    count = 10_000

    width, height = 900, 650
    left, top = 135, 65
    plot_width, plot_height = 650, 465
    xmin, xmax = 152.8, 156.4
    ymin, ymax = 6.7, 9.0

    def px(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_width

    def py(value: float) -> float:
        return top + plot_height - (value - ymin) / (ymax - ymin) * plot_height

    marks: list[str] = []
    for _ in range(count):
        mu = rng.gauss(154.6, 0.42)
        sigma = rng.gauss(7.75, 0.32)
        if xmin <= mu <= xmax and ymin <= sigma <= ymax:
            marks.append(f"M{fmt(px(mu))} {fmt(py(sigma))}h.01")

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>身高数据的联合后验样本</title>",
        "  <desc>一万个均值与标准差组合的后验样本。中心点最密集，表示这些参数组合在模型条件下最能产生观测数据。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fbfbfe" stroke="#333630" stroke-width="2"/>',
        f'  <path d="{" ".join(marks)}" fill="none" stroke="#5b63ed" stroke-width="3.2" stroke-linecap="round" opacity="0.11"/>',
    ]

    for tick in [153, 154, 155, 156]:
        x = px(tick)
        body.extend(
            [
                f'  <line x1="{fmt(x)}" y1="{top + plot_height}" x2="{fmt(x)}" y2="{top + plot_height + 8}" stroke="#333630" stroke-width="2"/>',
                f'  <text x="{fmt(x)}" y="{top + plot_height + 32}" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">{tick:.1f}</text>',
            ]
        )

    for tick in [7.0, 7.5, 8.0, 8.5, 9.0]:
        y = py(tick)
        body.extend(
            [
                f'  <line x1="{left - 8}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#333630" stroke-width="2"/>',
                f'  <text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="18" fill="#30332e">{tick:.1f}</text>',
            ]
        )

    body.extend(
        [
            f'  <text x="{left + plot_width / 2}" y="{top + plot_height + 78}" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">均值 μ（厘米）</text>',
            f'  <text x="38" y="{top + plot_height / 2}" transform="rotate(-90 38 {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">标准差 σ（厘米）</text>',
            f'  <text x="{width / 2}" y="625" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">点的密度表示参数组合的相对后验可信程度</text>',
            "</svg>",
            "",
        ]
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
