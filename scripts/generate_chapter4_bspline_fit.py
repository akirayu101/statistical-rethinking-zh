#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG used for Figure 4.13."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-bspline-fit.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def basis(index: int, degree: int, x: float, knot_vector: list[float]) -> float:
    if degree == 0:
        if knot_vector[index] <= x < knot_vector[index + 1]:
            return 1.0
        if x == knot_vector[-1] and knot_vector[index + 1] == knot_vector[-1]:
            return 1.0
        return 0.0
    left_denominator = knot_vector[index + degree] - knot_vector[index]
    right_denominator = knot_vector[index + degree + 1] - knot_vector[index + 1]
    left = 0.0
    right = 0.0
    if left_denominator:
        left = (x - knot_vector[index]) / left_denominator * basis(
            index, degree - 1, x, knot_vector
        )
    if right_denominator:
        right = (knot_vector[index + degree + 1] - x) / right_denominator * basis(
            index + 1, degree - 1, x, knot_vector
        )
    return left + right


def temperature_trend(year: float) -> float:
    return (
        6.15
        + 0.50 * math.sin((year - 820) / 38)
        + 0.30 * math.sin((year - 810) / 77)
        + 0.0010 * (year - 1400)
        + 0.72 * max(0.0, (year - 1880) / 100) ** 2
    )


def main() -> int:
    width, height = 1200, 1000
    left, plot_w, panel_h = 135, 980, 220
    tops = [60, 365, 670]
    xmin, xmax = 839.0, 1980.0
    degree = 3
    boundary_knots = [xmin, xmax]
    interior = [xmin + (xmax - xmin) * index / 14 for index in range(1, 14)]
    knot_vector = [boundary_knots[0]] * (degree + 1) + interior + [boundary_knots[1]] * (degree + 1)
    basis_count = len(knot_vector) - degree - 1

    def px(year: float) -> float:
        return left + (year - 820.0) / (2000.0 - 820.0) * plot_w

    def py(value: float, top: float, ymin: float, ymax: float) -> float:
        return top + panel_h - (value - ymin) / (ymax - ymin) * panel_h

    xs = [xmin + (xmax - xmin) * step / 420 for step in range(421)]
    basis_values = [
        [basis(index, degree, x, knot_vector) for x in xs]
        for index in range(basis_count)
    ]
    greville = [
        sum(knot_vector[index + 1 : index + degree + 1]) / degree
        for index in range(basis_count)
    ]
    weights = [temperature_trend(value) - 6.15 for value in greville]

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>十五个结点的三次 B 样条</title>",
        "  <desc>上图显示十七个重叠的三次基函数，中图显示加权基函数，下图把它们的和形成的样条叠加在日本三月气温数据上。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    # Top: cubic basis functions.
    top = tops[0]
    body.append(
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.5"/>'
    )
    for values in basis_values:
        coords = [
            f"{fmt(px(x))},{fmt(py(value, top, 0, 1.05))}"
            for x, value in zip(xs, values)
        ]
        body.append(
            f'  <polyline points="{" ".join(coords)}" fill="none" stroke="#858987" stroke-width="2.6" opacity="0.85"/>'
        )

    # Middle: weighted basis functions.
    top = tops[1]
    body.append(
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.5"/>'
    )
    for values, weight in zip(basis_values, weights):
        coords = [
            f"{fmt(px(x))},{fmt(py(weight * value, top, -1.2, 1.5))}"
            for x, value in zip(xs, values)
        ]
        body.append(
            f'  <polyline points="{" ".join(coords)}" fill="none" stroke="#858987" stroke-width="2.6" opacity="0.85"/>'
        )
    body.append(
        f'  <line x1="{left}" y1="{fmt(py(0, top, -1.2, 1.5))}" x2="{left + plot_w}" y2="{fmt(py(0, top, -1.2, 1.5))}" stroke="#555852" stroke-dasharray="6 7"/>'
    )

    # Bottom: raw data and posterior interval for the spline mean.
    top = tops[2]
    body.append(
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.5"/>'
    )
    curve_values = [
        6.15
        + sum(weight * values[position] for weight, values in zip(weights, basis_values))
        for position in range(len(xs))
    ]
    upper = [
        f"{fmt(px(x))},{fmt(py(value + 0.18, top, 4.4, 8.6))}"
        for x, value in zip(xs, curve_values)
    ]
    lower = [
        f"{fmt(px(x))},{fmt(py(value - 0.18, top, 4.4, 8.6))}"
        for x, value in zip(xs, curve_values)
    ]
    body.append(
        f'  <polygon points="{" ".join(upper + list(reversed(lower)))}" fill="#aeb4c0" opacity="0.78"/>'
    )
    rng = random.Random(4513)
    for year in range(839, 1981):
        if rng.random() < 0.74:
            observed = temperature_trend(year) + rng.gauss(0, 0.15)
            body.append(
                f'  <circle cx="{fmt(px(year))}" cy="{fmt(py(observed, top, 4.4, 8.6))}" r="2.15" fill="#5669ef" opacity="0.27"/>'
            )
    curve_coords = [
        f"{fmt(px(x))},{fmt(py(value, top, 4.4, 8.6))}"
        for x, value in zip(xs, curve_values)
    ]
    body.append(
        f'  <polyline points="{" ".join(curve_coords)}" fill="none" stroke="#4c504c" stroke-width="4"/>'
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
    for knot in [xmin] + interior + [xmax]:
        for top in tops[:2]:
            body.append(
                f'  <text x="{fmt(px(knot))}" y="{top + 18}" text-anchor="middle" font-family="{FONT}" font-size="22" fill="#30332e">+</text>'
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
