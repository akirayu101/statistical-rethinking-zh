#!/usr/bin/env python3
"""Generate deterministic Chinese SVG figures for Chapter 11."""
from pathlib import Path
import math
import random


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations/zh/media/chapter-11-logistic-priors.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
BLUE = "#6670ee"
GRID = "#d9d5c8"


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: float, y: float, value: object, *, size: int = 18, anchor: str = "start",
         weight: int = 400, fill: str = INK, rotate: int | None = None) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}"{transform}>'
        f'{esc(value)}</text>'
    )


def inv_logit(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def transformed_normal_density(probability: float, sigma: float) -> float:
    logit = math.log(probability / (1 - probability))
    normal = math.exp(-0.5 * (logit / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))
    return normal / (probability * (1 - probability))


def difference_density(sigma: float, *, seed: int) -> list[float]:
    """Simulate and smooth the prior density of absolute treatment differences."""
    rng = random.Random(seed)
    bins = 180
    counts = [0.0] * bins
    samples = 160_000
    for _ in range(samples):
        intercept = rng.gauss(0, 1.5)
        p1 = inv_logit(intercept + rng.gauss(0, sigma))
        p2 = inv_logit(intercept + rng.gauss(0, sigma))
        difference = abs(p1 - p2)
        index = min(bins - 1, int(difference * bins))
        counts[index] += 1
    kernel = [1, 2, 3, 4, 3, 2, 1]
    smoothed = []
    for index in range(bins):
        weighted = 0.0
        total_weight = 0.0
        for offset, weight in zip(range(-3, 4), kernel):
            neighbor = index + offset
            if 0 <= neighbor < bins:
                weighted += counts[neighbor] * weight
                total_weight += weight
        smoothed.append(weighted / total_weight * bins / samples)
    return smoothed


def axes(parts: list[str], *, x: float, y: float, width: float, height: float,
         ymax: float, xlabel: str) -> tuple[callable, callable]:
    left, right, top, bottom = x + 68, x + width - 22, y + 25, y + height - 68
    sx = lambda value: left + value * (right - left)
    sy = lambda value: bottom - value / ymax * (bottom - top)
    parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="#fff" stroke="{GRID}"/>')
    for tick in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        xx = sx(tick)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + 7}" stroke="{INK}"/>',
            text(xx, bottom + 29, f"{tick:.1f}", size=15, anchor="middle"),
        ])
    for fraction in (0, .25, .5, .75, 1):
        value = fraction * ymax
        yy = sy(value)
        parts.extend([
            f'<line x1="{left - 7}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
            text(left - 12, yy + 5, f"{value:g}", size=15, anchor="end"),
        ])
    parts.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.5"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}" stroke-width="1.5"/>',
        text((left + right) / 2, y + height - 16, xlabel, size=18, anchor="middle"),
        text(x + 20, (top + bottom) / 2, "密度", size=18, anchor="middle", rotate=-90),
    ])
    return sx, sy


def polyline(parts: list[str], points: list[tuple[float, float]], sx, sy, *, color: str, width: float) -> None:
    coords = " ".join(f"{sx(px):.1f},{sy(py):.1f}" for px, py in points)
    parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')


def figure_11_3() -> None:
    width, height = 1200, 620
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>基础逻辑斯蒂回归的先验预测模拟</title>',
        '<desc>左图比较截距标准差为十与一点五时拉左侧杠杆概率的先验；右图比较处理效应标准差为十与零点五时处理间绝对差异的先验。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]

    sx1, sy1 = axes(parts, x=30, y=35, width=555, height=530, ymax=18, xlabel="拉左侧杠杆的先验概率")
    left_points_10 = []
    left_points_15 = []
    for index in range(1, 800):
        probability = index / 800
        left_points_10.append((probability, min(18, transformed_normal_density(probability, 10))))
        left_points_15.append((probability, min(18, transformed_normal_density(probability, 1.5))))
    polyline(parts, left_points_10, sx1, sy1, color="#111", width=3)
    polyline(parts, left_points_15, sx1, sy1, color=BLUE, width=4)
    parts.extend([
        text(sx1(.16), sy1(6.6), "α ∼ Normal(0, 10)", size=18, fill="#111"),
        text(sx1(.37), sy1(2.1), "α ∼ Normal(0, 1.5)", size=18, fill=BLUE),
    ])

    sx2, sy2 = axes(parts, x=615, y=35, width=555, height=530, ymax=14, xlabel="处理之间的先验绝对差异")
    density_10 = difference_density(10, seed=1110)
    density_05 = difference_density(.5, seed=1105)
    right_points_10 = [((index + .5) / len(density_10), min(14, value)) for index, value in enumerate(density_10)]
    right_points_05 = [((index + .5) / len(density_05), min(14, value)) for index, value in enumerate(density_05)]
    polyline(parts, right_points_10, sx2, sy2, color="#111", width=3)
    polyline(parts, right_points_05, sx2, sy2, color=BLUE, width=4)
    parts.extend([
        text(sx2(.43), sy2(9.3), "β ∼ Normal(0, 10)", size=18, fill="#111"),
        text(sx2(.17), sy2(5.8), "β ∼ Normal(0, 0.5)", size=18, fill=BLUE),
        '</svg>',
    ])
    OUT1.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    figure_11_3()
    print(OUT1)
