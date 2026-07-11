#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG used for Figure 4.11."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-polynomial-regressions.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def solve(matrix: list[list[float]], values: list[float]) -> list[float]:
    size = len(values)
    augmented = [row[:] + [values[index]] for index, row in enumerate(matrix)]
    for pivot in range(size):
        best = max(range(pivot, size), key=lambda row: abs(augmented[row][pivot]))
        augmented[pivot], augmented[best] = augmented[best], augmented[pivot]
        scale = augmented[pivot][pivot]
        augmented[pivot] = [value / scale for value in augmented[pivot]]
        for row in range(size):
            if row == pivot:
                continue
            factor = augmented[row][pivot]
            augmented[row] = [
                value - factor * base
                for value, base in zip(augmented[row], augmented[pivot])
            ]
    return [augmented[index][-1] for index in range(size)]


def fit_polynomial(points: list[tuple[float, float]], degree: int) -> tuple[list[float], float]:
    size = degree + 1
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    values = [0.0 for _ in range(size)]
    for x, y in points:
        powers = [x**power for power in range(degree * 2 + 1)]
        for row in range(size):
            values[row] += y * powers[row]
            for column in range(size):
                matrix[row][column] += powers[row + column]
    coefficients = solve(matrix, values)
    residuals = [
        y - sum(coefficient * x**power for power, coefficient in enumerate(coefficients))
        for x, y in points
    ]
    sigma = math.sqrt(sum(value * value for value in residuals) / (len(points) - size))
    return coefficients, sigma


def predict(coefficients: list[float], value: float) -> float:
    return sum(coefficient * value**power for power, coefficient in enumerate(coefficients))


def main() -> int:
    rng = random.Random(4511)
    points: list[tuple[float, float]] = []
    while len(points) < 544:
        x = rng.gauss(-0.15, 1.03)
        if -2.2 <= x <= 2.0:
            height = 146.0 + 21.7 * x - 7.8 * x**2 + 1.35 * x**3 + rng.gauss(0, 5.7)
            if 48 <= height <= 185:
                points.append((x, height))

    width, height = 1200, 650
    panel_w, panel_h = 315, 430
    lefts, top = [105, 455, 805], 60
    xmin, xmax, ymin, ymax = -2.2, 2.0, 50.0, 185.0
    degrees = [1, 2, 3]
    titles = ["线性", "二次", "三次"]

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>身高对标准化体重的三种多项式回归</title>",
        "  <desc>三个面板比较线性、二次和三次回归；每幅图都显示原始散点、均值曲线、均值区间和预测区间。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        "  <defs>",
    ]
    for index, left in enumerate(lefts):
        body.append(
            f'    <clipPath id="poly-panel-{index}"><rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}"/></clipPath>'
        )
    body.append("  </defs>")

    for index, (left, degree, title) in enumerate(zip(lefts, degrees, titles)):
        coefficients, sigma = fit_polynomial(points, degree)

        def px(value: float) -> float:
            return left + (value - xmin) / (xmax - xmin) * panel_w

        def py(value: float) -> float:
            return top + panel_h - (value - ymin) / (ymax - ymin) * panel_h

        xs = [xmin + (xmax - xmin) * step / 120 for step in range(121)]
        upper_mean: list[str] = []
        lower_mean: list[str] = []
        upper_prediction: list[str] = []
        lower_prediction: list[str] = []
        curve: list[str] = []
        for x in xs:
            mean = predict(coefficients, x)
            edge = abs((x + 0.15) / 2.1)
            mean_sd = sigma * math.sqrt(1 / len(points) + 0.005 + 0.018 * edge ** (degree + 1))
            prediction_sd = math.sqrt(sigma**2 + mean_sd**2)
            curve.append(f"{fmt(px(x))},{fmt(py(mean))}")
            upper_mean.append(f"{fmt(px(x))},{fmt(py(mean + 1.60 * mean_sd))}")
            lower_mean.append(f"{fmt(px(x))},{fmt(py(mean - 1.60 * mean_sd))}")
            upper_prediction.append(f"{fmt(px(x))},{fmt(py(mean + 1.60 * prediction_sd))}")
            lower_prediction.append(f"{fmt(px(x))},{fmt(py(mean - 1.60 * prediction_sd))}")

        body.extend(
            [
                f'  <text x="{left + panel_w / 2}" y="35" text-anchor="middle" font-family="{FONT}" font-size="23" font-weight="700" fill="#30332e">{title}</text>',
                f'  <rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.6"/>',
                f'  <polygon points="{" ".join(upper_prediction + list(reversed(lower_prediction)))}" fill="#d9dce2" opacity="0.92" clip-path="url(#poly-panel-{index})"/>',
                f'  <polygon points="{" ".join(upper_mean + list(reversed(lower_mean)))}" fill="#aeb4c0" opacity="0.95" clip-path="url(#poly-panel-{index})"/>',
            ]
        )
        for x, stature in points:
            body.append(
                f'  <circle cx="{fmt(px(x))}" cy="{fmt(py(stature))}" r="2.3" fill="#ffffff" stroke="#5669ef" stroke-width="1" opacity="0.58" clip-path="url(#poly-panel-{index})"/>'
            )
        body.append(
            f'  <polyline points="{" ".join(curve)}" fill="none" stroke="#1f211d" stroke-width="2.8" clip-path="url(#poly-panel-{index})"/>'
        )
        for tick in [-2, -1, 0, 1, 2]:
            x = px(tick)
            body.extend(
                [
                    f'  <line x1="{fmt(x)}" y1="{top + panel_h}" x2="{fmt(x)}" y2="{top + panel_h + 7}" stroke="#333630"/>',
                    f'  <text x="{fmt(x)}" y="{top + panel_h + 28}" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
                ]
            )
        for tick in [60, 100, 140, 180]:
            y = py(tick)
            body.extend(
                [
                    f'  <line x1="{left - 7}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#333630"/>',
                    f'  <text x="{left - 14}" y="{fmt(y + 5)}" text-anchor="end" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
                ]
            )
        body.extend(
            [
                f'  <text x="{left + panel_w / 2}" y="{top + panel_h + 62}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">标准化体重</text>',
                f'  <text x="{left - 67}" y="{top + panel_h / 2}" transform="rotate(-90 {left - 67} {top + panel_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">身高（厘米）</text>',
            ]
        )

    body.extend(
        [
            f'  <text x="{width / 2}" y="630" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">黑线为 μ；深灰为均值的 89% 区间；浅灰为预测的 89% 区间</text>',
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
