#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG used for Figure 4.12."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-bspline-intro.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def basis_value(year: float, index: int, knots: list[float]) -> float:
    if index == 0:
        if year <= knots[0]:
            return 1.0
        if year >= knots[1]:
            return 0.0
        return (knots[1] - year) / (knots[1] - knots[0])
    if index == len(knots) - 1:
        if year <= knots[-2]:
            return 0.0
        if year >= knots[-1]:
            return 1.0
        return (year - knots[-2]) / (knots[-1] - knots[-2])
    if year <= knots[index - 1] or year >= knots[index + 1]:
        return 0.0
    if year <= knots[index]:
        return (year - knots[index - 1]) / (knots[index] - knots[index - 1])
    return (knots[index + 1] - year) / (knots[index + 1] - knots[index])


def main() -> int:
    width, height = 1200, 1000
    left, plot_w, panel_h = 135, 980, 220
    tops = [60, 365, 670]
    xmin, xmax = 820.0, 2000.0
    knots = [840.0, 1130.0, 1410.0, 1700.0, 1980.0]
    weights = [0.68, -0.55, 0.18, -0.72, 0.82]
    highlight = 1306.0

    def px(year: float) -> float:
        return left + (year - xmin) / (xmax - xmin) * plot_w

    def py(value: float, top: float, ymin: float, ymax: float) -> float:
        return top + panel_h - (value - ymin) / (ymax - ymin) * panel_h

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>B 样条的局部线性近似</title>",
        "  <desc>上图显示五个基函数，中图显示基函数乘以权重，下图把所得样条叠加在日本三月气温原始数据上。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    # Top: five local basis functions.
    top = tops[0]
    body.append(
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.5"/>'
    )
    for index in range(5):
        coords = []
        for step in range(241):
            year = xmin + (xmax - xmin) * step / 240
            coords.append(f"{fmt(px(year))},{fmt(py(basis_value(year, index, knots), top, 0, 1.05))}")
        body.append(
            f'  <polyline points="{" ".join(coords)}" fill="none" stroke="#878b88" stroke-width="3"/>'
        )
        body.append(
            f'  <text x="{fmt(px(knots[index]))}" y="{fmt(py(0.84, top, 0, 1.05))}" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">{index + 1}</text>'
        )
        body.append(
            f'  <text x="{fmt(px(knots[index]))}" y="{fmt(py(1.02, top, 0, 1.05))}" text-anchor="middle" font-family="{FONT}" font-size="24" fill="#30332e">+</text>'
        )
    hx = px(highlight)
    body.extend(
        [
            f'  <line x1="{fmt(hx)}" y1="{top}" x2="{fmt(hx)}" y2="{top + panel_h}" stroke="#5669ef" stroke-width="2.4" stroke-dasharray="7 8"/>',
            f'  <text x="{fmt(hx)}" y="{top + 24}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#5669ef">1306</text>',
        ]
    )

    # Middle: weighted basis functions and their sum.
    top = tops[1]
    body.append(
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.5"/>'
    )
    total_coords = []
    for index, weight in enumerate(weights):
        coords = []
        for step in range(241):
            year = xmin + (xmax - xmin) * step / 240
            value = weight * basis_value(year, index, knots)
            coords.append(f"{fmt(px(year))},{fmt(py(value, top, -0.85, 0.95))}")
        body.append(
            f'  <polyline points="{" ".join(coords)}" fill="none" stroke="#878b88" stroke-width="3"/>'
        )
        label_y = weight * 0.82
        body.append(
            f'  <text x="{fmt(px(knots[index]))}" y="{fmt(py(label_y, top, -0.85, 0.95))}" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">{index + 1}</text>'
        )
    for step in range(241):
        year = xmin + (xmax - xmin) * step / 240
        total = sum(weight * basis_value(year, index, knots) for index, weight in enumerate(weights))
        total_coords.append(f"{fmt(px(year))},{fmt(py(total, top, -0.85, 0.95))}")
    body.extend(
        [
            f'  <line x1="{left}" y1="{fmt(py(0, top, -0.85, 0.95))}" x2="{left + plot_w}" y2="{fmt(py(0, top, -0.85, 0.95))}" stroke="#555852" stroke-dasharray="6 7"/>',
            f'  <polyline points="{" ".join(total_coords)}" fill="none" stroke="#1f211d" stroke-width="3.2"/>',
            f'  <line x1="{fmt(hx)}" y1="{top}" x2="{fmt(hx)}" y2="{top + panel_h}" stroke="#5669ef" stroke-width="2.4" stroke-dasharray="7 8"/>',
        ]
    )

    # Bottom: reconstructed temperature record with the coarse spline and interval.
    top = tops[2]
    body.append(
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.5"/>'
    )
    spline_upper: list[str] = []
    spline_lower: list[str] = []
    spline_curve: list[str] = []
    for step in range(241):
        year = xmin + (xmax - xmin) * step / 240
        spline = 6.25 + sum(weight * basis_value(year, index, knots) for index, weight in enumerate(weights))
        spline_curve.append(f"{fmt(px(year))},{fmt(py(spline, top, 4.4, 8.5))}")
        spline_upper.append(f"{fmt(px(year))},{fmt(py(spline + 0.22, top, 4.4, 8.5))}")
        spline_lower.append(f"{fmt(px(year))},{fmt(py(spline - 0.22, top, 4.4, 8.5))}")
    body.append(
        f'  <polygon points="{" ".join(spline_upper + list(reversed(spline_lower)))}" fill="#b9bdc6" opacity="0.75"/>'
    )
    rng = random.Random(4512)
    for year in range(839, 1981):
        if rng.random() < 0.74:
            observed = 6.25 + 0.52 * math.sin((year - 820) / 38) + 0.34 * math.sin((year - 820) / 15) + 0.0011 * (year - 1400) + rng.gauss(0, 0.16)
            body.append(
                f'  <circle cx="{fmt(px(year))}" cy="{fmt(py(observed, top, 4.4, 8.5))}" r="2.25" fill="#5669ef" opacity="0.28"/>'
            )
    body.append(
        f'  <polyline points="{" ".join(spline_curve)}" fill="none" stroke="#555852" stroke-width="4"/>'
    )
    body.append(
        f'  <line x1="{fmt(hx)}" y1="{top}" x2="{fmt(hx)}" y2="{top + panel_h}" stroke="#5669ef" stroke-width="2.4" stroke-dasharray="7 8"/>'
    )

    for top in tops:
        for year in [800, 1000, 1200, 1400, 1600, 1800, 2000]:
            x = px(year)
            body.extend(
                [
                    f'  <line x1="{fmt(x)}" y1="{top + panel_h}" x2="{fmt(x)}" y2="{top + panel_h + 7}" stroke="#333630"/>',
                    f'  <text x="{fmt(x)}" y="{top + panel_h + 28}" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">{year}</text>',
                ]
            )
        body.append(
            f'  <text x="{left + plot_w / 2}" y="{top + panel_h + 56}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">年份</text>'
        )
    body.extend(
        [
            f'  <text x="42" y="{tops[0] + panel_h / 2}" transform="rotate(-90 42 {tops[0] + panel_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">基函数值</text>',
            f'  <text x="42" y="{tops[1] + panel_h / 2}" transform="rotate(-90 42 {tops[1] + panel_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">基函数 × 权重</text>',
            f'  <text x="42" y="{tops[2] + panel_h / 2}" transform="rotate(-90 42 {tops[2] + panel_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">三月气温</text>',
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
