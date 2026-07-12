#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Chapter 7 Figures 7.3 and 7.4."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "translations" / "zh" / "media"
POLY_OUT = MEDIA / "chapter-07-polynomial-overfit.svg"
LOO_OUT = MEDIA / "chapter-07-loo-sensitivity.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"

MASSES = [37.0, 35.5, 34.5, 41.5, 55.5, 61.0, 53.5]
BRAINS = [438.0, 452.0, 612.0, 521.0, 752.0, 871.0, 1350.0]
MASS_MEAN = sum(MASSES) / len(MASSES)
MASS_SD = math.sqrt(sum((value - MASS_MEAN) ** 2 for value in MASSES) / (len(MASSES) - 1))


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def solve(matrix: list[list[float]], values: list[float]) -> list[float]:
    size = len(values)
    augmented = [row[:] + [values[index]] for index, row in enumerate(matrix)]
    for pivot in range(size):
        best = max(range(pivot, size), key=lambda row: abs(augmented[row][pivot]))
        augmented[pivot], augmented[best] = augmented[best], augmented[pivot]
        scale = augmented[pivot][pivot]
        if abs(scale) < 1e-12:
            raise ValueError("singular polynomial design")
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


def standardized(mass: float) -> float:
    return (mass - MASS_MEAN) / MASS_SD


def design_row(mass: float, degree: int) -> list[float]:
    value = standardized(mass)
    return [value**power for power in range(degree + 1)]


def fit_polynomial(
    masses: list[float], brains: list[float], degree: int
) -> tuple[list[float], list[list[float]], float]:
    rows = [design_row(mass, degree) for mass in masses]
    size = degree + 1
    cross = [
        [sum(row[i] * row[j] for row in rows) for j in range(size)]
        for i in range(size)
    ]
    target = [sum(row[i] * brain for row, brain in zip(rows, brains)) for i in range(size)]
    coefficients = solve(cross, target)
    inverse = [solve(cross, [1.0 if row == column else 0.0 for row in range(size)]) for column in range(size)]
    inverse = [list(column) for column in zip(*inverse)]
    residuals = [
        brain - sum(coefficient * value for coefficient, value in zip(coefficients, row))
        for row, brain in zip(rows, brains)
    ]
    degrees_of_freedom = len(masses) - size
    sigma = (
        math.sqrt(sum(residual * residual for residual in residuals) / degrees_of_freedom)
        if degrees_of_freedom > 0
        else 1.35
    )
    return coefficients, inverse, sigma


def predict(coefficients: list[float], mass: float) -> float:
    return sum(
        coefficient * standardized(mass) ** power
        for power, coefficient in enumerate(coefficients)
    )


def mean_sd(inverse: list[list[float]], sigma: float, mass: float) -> float:
    row = design_row(mass, len(inverse) - 1)
    leverage = sum(row[i] * inverse[i][j] * row[j] for i in range(len(row)) for j in range(len(row)))
    return sigma * math.sqrt(max(0.0, leverage))


def generate_polynomial_figure() -> None:
    width, height = 1200, 1240
    panel_width, panel_height = 420, 270
    lefts, tops = [125, 665], [70, 445, 820]
    xmin, xmax = 32.0, 64.0
    labels = ["0.51", "0.54", "0.69", "0.82", "0.99", "1"]
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>次数递增的人族脑容量多项式模型</title>",
        "<desc>六个面板依次展示一次到六次多项式；次数越高，样本内拟合越好，但曲线在观测间隙内越来越荒谬。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        "<defs>",
    ]
    for index in range(6):
        left, top = lefts[index % 2], tops[index // 2]
        body.append(f'<clipPath id="poly7-{index}"><rect x="{left}" y="{top}" width="{panel_width}" height="{panel_height}"/></clipPath>')
    body.append("</defs>")
    for index, degree in enumerate(range(1, 7)):
        left, top = lefts[index % 2], tops[index // 2]
        ymin, ymax = ((-650.0, 1600.0) if degree == 6 else (250.0, 1450.0))

        def px(value: float) -> float:
            return left + (value - xmin) / (xmax - xmin) * panel_width

        def py(value: float) -> float:
            return top + panel_height - (value - ymin) / (ymax - ymin) * panel_height

        coefficients, inverse, sigma = fit_polynomial(MASSES, BRAINS, degree)
        sequence = [xmin + (xmax - xmin) * step / 180 for step in range(181)]
        curve = [(px(mass), py(predict(coefficients, mass))) for mass in sequence]
        body.extend([
            f'<text x="{left}" y="{top - 22}" font-family="{FONT}" font-size="20" font-weight="700" fill="#30332e">m7.{degree}：R² = {labels[index]}</text>',
            f'<rect x="{left}" y="{top}" width="{panel_width}" height="{panel_height}" fill="#fff" stroke="#343732" stroke-width="1.4"/>',
        ])
        if degree < 6:
            upper, lower = [], []
            for mass in sequence:
                mean = predict(coefficients, mass)
                interval = 1.6 * mean_sd(inverse, sigma, mass)
                upper.append((px(mass), py(mean + interval)))
                lower.append((px(mass), py(mean - interval)))
            points = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in upper + list(reversed(lower)))
            body.append(f'<polygon points="{points}" fill="#d8d9dc" clip-path="url(#poly7-{index})"/>')
        if degree == 6:
            zero = py(0)
            body.append(f'<line x1="{left}" y1="{fmt(zero)}" x2="{left + panel_width}" y2="{fmt(zero)}" stroke="#666" stroke-width="1.4" stroke-dasharray="7 6"/>')
        body.append(f'<polyline points="{" ".join(f"{fmt(x)},{fmt(y)}" for x, y in curve)}" fill="none" stroke="#171915" stroke-width="3" clip-path="url(#poly7-{index})"/>')
        for mass, brain in zip(MASSES, BRAINS):
            body.append(f'<circle cx="{fmt(px(mass))}" cy="{fmt(py(brain))}" r="5.3" fill="#6670ee" stroke="#fff" stroke-width="1.3"/>')
        for tick in [35, 47, 60]:
            x = px(tick)
            body.extend([
                f'<line x1="{fmt(x)}" y1="{top + panel_height}" x2="{fmt(x)}" y2="{top + panel_height + 6}" stroke="#343732"/>',
                f'<text x="{fmt(x)}" y="{top + panel_height + 25}" text-anchor="middle" font-family="{FONT}" font-size="15">{tick}</text>',
            ])
        yticks = [0, 450, 1300] if degree == 6 else [450, 900, 1300]
        for tick in yticks:
            y = py(tick)
            body.extend([
                f'<line x1="{left - 6}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#343732"/>',
                f'<text x="{left - 13}" y="{fmt(y + 5)}" text-anchor="end" font-family="{FONT}" font-size="15">{tick}</text>',
            ])
        body.extend([
            f'<text x="{left + panel_width / 2}" y="{top + panel_height + 51}" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="#263f86">体重（千克）</text>',
            f'<text x="{left - 69}" y="{top + panel_height / 2}" transform="rotate(-90 {left - 69} {top + panel_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="#263f86">脑容量（立方厘米）</text>',
        ])
    body.extend([
        f'<text x="{width / 2}" y="1210" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#656963">黑线为后验均值；灰色区域为均值的 89% 区间</text>',
        "</svg>",
        "",
    ])
    POLY_OUT.write_text("\n".join(body), encoding="utf-8")


def generate_loo_figure() -> None:
    width, height = 1100, 580
    panel_width, panel_height = 410, 350
    lefts, top = [120, 650], 70
    xmin, xmax = 32.0, 64.0
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>欠拟合与过拟合对样本构成的敏感性</title>",
        "<desc>左图七条一次回归线变化很小；右图七条四次多项式曲线在每次删除一个观测后剧烈变化。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<defs><clipPath id="loo-left"><rect x="120" y="70" width="410" height="350"/></clipPath><clipPath id="loo-right"><rect x="650" y="70" width="410" height="350"/></clipPath></defs>',
    ]
    for panel, degree in enumerate([1, 4]):
        left = lefts[panel]
        ymin, ymax = ((350.0, 1400.0) if degree == 1 else (-100.0, 2100.0))

        def px(value: float) -> float:
            return left + (value - xmin) / (xmax - xmin) * panel_width

        def py(value: float) -> float:
            return top + panel_height - (value - ymin) / (ymax - ymin) * panel_height

        body.extend([
            f'<text x="{left}" y="{top - 24}" font-family="{FONT}" font-size="22" font-weight="700" fill="#30332e">m7.{degree}</text>',
            f'<rect x="{left}" y="{top}" width="{panel_width}" height="{panel_height}" fill="#fff" stroke="#343732" stroke-width="1.4"/>',
        ])
        clip = "loo-left" if panel == 0 else "loo-right"
        sequence = [xmin + (xmax - xmin) * step / 150 for step in range(151)]
        for dropped in range(len(MASSES)):
            masses = [value for index, value in enumerate(MASSES) if index != dropped]
            brains = [value for index, value in enumerate(BRAINS) if index != dropped]
            coefficients, _, _ = fit_polynomial(masses, brains, degree)
            points = " ".join(f"{fmt(px(mass))},{fmt(py(predict(coefficients, mass)))}" for mass in sequence)
            body.append(f'<polyline points="{points}" fill="none" stroke="#9b9d9a" stroke-width="2.6" opacity="0.76" clip-path="url(#{clip})"/>')
        for mass, brain in zip(MASSES, BRAINS):
            body.append(f'<circle cx="{fmt(px(mass))}" cy="{fmt(py(brain))}" r="5.4" fill="#6670ee" stroke="#fff" stroke-width="1.2"/>')
        for tick in [35, 47, 60]:
            x = px(tick)
            body.extend([
                f'<line x1="{fmt(x)}" y1="{top + panel_height}" x2="{fmt(x)}" y2="{top + panel_height + 6}" stroke="#343732"/>',
                f'<text x="{fmt(x)}" y="{top + panel_height + 26}" text-anchor="middle" font-family="{FONT}" font-size="16">{tick}</text>',
            ])
        yticks = [450, 900, 1300] if degree == 1 else [0, 900, 2000]
        for tick in yticks:
            y = py(tick)
            body.extend([
                f'<line x1="{left - 6}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#343732"/>',
                f'<text x="{left - 13}" y="{fmt(y + 5)}" text-anchor="end" font-family="{FONT}" font-size="16">{tick}</text>',
            ])
        body.extend([
            f'<text x="{left + panel_width / 2}" y="{top + panel_height + 58}" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="#263f86">体重（千克）</text>',
            f'<text x="{left - 72}" y="{top + panel_height / 2}" transform="rotate(-90 {left - 72} {top + panel_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="#263f86">脑容量（立方厘米）</text>',
        ])
    body.extend([
        f'<text x="{width / 2}" y="555" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#656963">每条灰线代表删除一个物种后重新拟合的模型</text>',
        "</svg>",
        "",
    ])
    LOO_OUT.write_text("\n".join(body), encoding="utf-8")


def main() -> int:
    MEDIA.mkdir(parents=True, exist_ok=True)
    generate_polynomial_figure()
    generate_loo_figure()
    print(f"generated {POLY_OUT}")
    print(f"generated {LOO_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
