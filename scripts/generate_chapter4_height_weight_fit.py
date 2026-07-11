#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG used for Figure 4.6."""

from __future__ import annotations

import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-height-weight-fit.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def main() -> int:
    rng = random.Random(4606)
    points: list[tuple[float, float]] = []
    while len(points) < 352:
        weight = rng.gauss(45, 8)
        if 31 <= weight <= 63:
            height = 154.6 + 0.90 * (weight - 45) + rng.gauss(0, 5.07)
            if 135 <= height <= 181:
                points.append((weight, height))

    width, height = 900, 650
    left, top = 125, 55
    plot_width, plot_height = 660, 465
    xmin, xmax, ymin, ymax = 30.0, 63.0, 134.0, 181.0

    def px(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_width

    def py(value: float) -> float:
        return top + plot_height - (value - ymin) / (ymax - ymin) * plot_height

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>身高、体重与后验均值回归线</title>",
        "  <desc>成人身高对体重的散点图，以及由后验均值斜率和截距定义的黑色直线。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#ffffff" stroke="#333630" stroke-width="2"/>',
    ]
    for weight, stature in points:
        body.append(
            f'  <circle cx="{fmt(px(weight))}" cy="{fmt(py(stature))}" r="3.4" fill="#ffffff" stroke="#5669ef" stroke-width="1.35" opacity="0.82"/>'
        )

    y1 = 154.6 + 0.90 * (xmin - 45)
    y2 = 154.6 + 0.90 * (xmax - 45)
    body.append(
        f'  <line x1="{fmt(px(xmin))}" y1="{fmt(py(y1))}" x2="{fmt(px(xmax))}" y2="{fmt(py(y2))}" stroke="#1f211d" stroke-width="3"/>'
    )
    for tick in [30, 35, 40, 45, 50, 55, 60]:
        x = px(tick)
        body.extend(
            [
                f'  <line x1="{fmt(x)}" y1="{top + plot_height}" x2="{fmt(x)}" y2="{top + plot_height + 8}" stroke="#333630"/>',
                f'  <text x="{fmt(x)}" y="{top + plot_height + 31}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
            ]
        )
    for tick in [140, 150, 160, 170, 180]:
        y = py(tick)
        body.extend(
            [
                f'  <line x1="{left - 8}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#333630"/>',
                f'  <text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{left + plot_width / 2}" y="{top + plot_height + 76}" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">体重（千克）</text>',
            f'  <text x="38" y="{top + plot_height / 2}" transform="rotate(-90 38 {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">身高（厘米）</text>',
            f'  <text x="{width / 2}" y="632" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">蓝色圆点为个体；黑线由后验均值 α = 154.6、β = 0.90 定义</text>',
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
