#!/usr/bin/env python3
"""Generate deterministic Chinese SVG figures for Chapter 11."""
from pathlib import Path
import math
import random


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations/zh/media/chapter-11-logistic-priors.svg"
OUT2 = ROOT / "translations/zh/media/chapter-11-actor-probabilities.svg"
OUT3 = ROOT / "translations/zh/media/chapter-11-treatment-effects.svg"
OUT4 = ROOT / "translations/zh/media/chapter-11-treatment-contrasts.svg"
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


def interval_plot(path: Path, *, title_value: str, description: str,
                  labels: list[str], estimates: list[float], lower: list[float], upper: list[float],
                  xmin: float, xmax: float, ticks: list[float], xlabel: str) -> None:
    width = 900
    height = 150 + len(labels) * 55
    left, right, top, bottom = 145, 850, 35, height - 90
    sx = lambda value: left + (value - xmin) / (xmax - xmin) * (right - left)
    row_step = (bottom - top) / max(1, len(labels) - 1)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f'<title>{esc(title_value)}</title>',
        f'<desc>{esc(description)}</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        f'<rect x="{left}" y="{top - 24}" width="{right - left}" height="{bottom - top + 48}" fill="#fff" stroke="{GRID}"/>',
    ]
    if xmin < 0 < xmax:
        parts.append(f'<line x1="{sx(0):.1f}" y1="{top - 24}" x2="{sx(0):.1f}" y2="{bottom + 24}" stroke="{GRID}" stroke-width="2"/>')
    for index, (label, estimate, low, high) in enumerate(zip(labels, estimates, lower, upper)):
        yy = top + index * row_step
        parts.extend([
            f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="4 5"/>',
            text(left - 18, yy + 6, label, size=19, anchor="end"),
            f'<line x1="{sx(low):.1f}" y1="{yy:.1f}" x2="{sx(high):.1f}" y2="{yy:.1f}" stroke="{INK}" stroke-width="4"/>',
            f'<circle cx="{sx(estimate):.1f}" cy="{yy:.1f}" r="7" fill="#fff" stroke="{INK}" stroke-width="3"/>',
        ])
    for tick in ticks:
        xx = sx(tick)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom + 24}" x2="{xx:.1f}" y2="{bottom + 32}" stroke="{INK}"/>',
            text(xx, bottom + 48, f"{tick:g}", size=17, anchor="middle"),
        ])
    parts.extend([
        text((left + right) / 2, height - 12, xlabel, size=19, anchor="middle"),
        '</svg>',
    ])
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def parameter_plots() -> None:
    actor_means = [-0.45, 3.86, -0.75, -0.74, -0.44, 0.48, 1.95]
    actor_lower = [-0.95, 2.78, -1.28, -1.26, -0.94, -0.02, 1.32]
    actor_upper = [0.04, 5.09, -0.23, -0.21, 0.10, 1.00, 2.63]
    interval_plot(
        OUT2,
        title_value="七只黑猩猩拉左侧杠杆的后验概率",
        description="每行给出一只黑猩猩拉左侧杠杆概率的后验均值与百分之八十九相容区间。",
        labels=[f"个体 {index}" for index in range(1, 8)],
        estimates=[inv_logit(value) for value in actor_means],
        lower=[inv_logit(value) for value in actor_lower],
        upper=[inv_logit(value) for value in actor_upper],
        xmin=0,
        xmax=1,
        ticks=[0, .2, .4, .6, .8, 1],
        xlabel="拉左侧杠杆的概率",
    )
    interval_plot(
        OUT3,
        title_value="四种处理效应的后验分布",
        description="四行分别给出亲社会选项位于右侧或左侧以及伙伴缺席或在场时的 logit 尺度处理效应。",
        labels=["R/N", "L/N", "R/P", "L/P"],
        estimates=[-0.04, 0.48, -0.38, 0.37],
        lower=[-0.51, 0.04, -0.83, -0.07],
        upper=[0.40, 0.92, 0.06, 0.79],
        xmin=-.9,
        xmax=1,
        ticks=[-.5, 0, .5, 1],
        xlabel="logit 尺度上的处理效应",
    )
    interval_plot(
        OUT4,
        title_value="无伙伴与有伙伴处理之间的后验对比",
        description="db13 与 db24 分别比较亲社会选项在右侧与左侧时，无伙伴处理减去有伙伴处理的后验差异。",
        labels=["db13", "db24"],
        estimates=[.34, .12],
        lower=[-.11, -.31],
        upper=[.78, .54],
        xmin=-.35,
        xmax=.82,
        ticks=[-.2, 0, .2, .4, .6, .8],
        xlabel="log-odds 差异",
    )


if __name__ == "__main__":
    figure_11_3()
    parameter_plots()
    for path in (OUT1, OUT2, OUT3, OUT4):
        print(path)
