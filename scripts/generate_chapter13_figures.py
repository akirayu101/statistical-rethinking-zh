#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 13."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-13-tank-shrinkage.svg"
OUT2 = ROOT / "translations" / "zh" / "media" / "chapter-13-tank-population.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
BLUE = "#6670ee"
GRID = "#d9d5c8"

# McElreath's reedfrogs data, in the published row order.
DENSITY = [10] * 16 + [25] * 16 + [35] * 16
SURVIVED = [
    9, 10, 7, 10, 9, 9, 10, 9, 4, 9, 7, 6, 7, 5, 9, 9,
    24, 23, 22, 25, 23, 23, 23, 21, 6, 13, 4, 9, 13, 20, 8, 10,
    34, 33, 33, 31, 31, 35, 33, 32, 4, 12, 13, 14, 22, 12, 31, 17,
]


def logistic(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def log1pexp(value: float) -> float:
    if value > 0:
        return value + math.log1p(math.exp(-value))
    return math.log1p(math.exp(value))


def escape(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_el(
    x: float,
    y: float,
    value: object,
    *,
    size: int = 18,
    anchor: str = "start",
    weight: int = 400,
    fill: str = INK,
    rotate: int | None = None,
) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}"{transform}>'
        f"{escape(value)}</text>"
    )


def polyline(points: list[tuple[float, float]], **attrs: object) -> str:
    attributes = " ".join(f'{key.replace("_", "-")}="{value}"' for key, value in attrs.items())
    coordinates = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{coordinates}" {attributes}/>'


def sample_posterior() -> tuple[list[float], list[tuple[float, float]]]:
    """Sample the two-level tank model with deterministic Gibbs/Metropolis updates."""
    rng = random.Random(1302)
    tank_intercepts = [
        math.log(((survived + 0.5) / (density + 1.0)) / (1.0 - (survived + 0.5) / (density + 1.0)))
        for survived, density in zip(SURVIVED, DENSITY)
    ]
    alpha_bar = sum(tank_intercepts) / len(tank_intercepts)
    sigma = 1.6
    saved_hyperparameters: list[tuple[float, float]] = []
    intercept_sums = [0.0] * len(tank_intercepts)

    def tank_log_density(value: float, survived: int, density: int, center: float, scale: float) -> float:
        return (
            survived * value
            - density * log1pexp(value)
            - (value - center) ** 2 / (2.0 * scale * scale)
        )

    for iteration in range(90_000):
        for index, (survived, density) in enumerate(zip(SURVIVED, DENSITY)):
            old = tank_intercepts[index]
            proposal = old + rng.gauss(0.0, 0.32)
            log_ratio = tank_log_density(proposal, survived, density, alpha_bar, sigma)
            log_ratio -= tank_log_density(old, survived, density, alpha_bar, sigma)
            if math.log(rng.random()) < log_ratio:
                tank_intercepts[index] = proposal

        conditional_variance = 1.0 / (len(tank_intercepts) / sigma**2 + 1.0 / 1.5**2)
        conditional_mean = conditional_variance * sum(tank_intercepts) / sigma**2
        alpha_bar = rng.gauss(conditional_mean, math.sqrt(conditional_variance))

        old_log_sigma = math.log(sigma)
        proposed_log_sigma = old_log_sigma + rng.gauss(0.0, 0.08)

        def sigma_log_density(log_sigma: float) -> float:
            candidate = math.exp(log_sigma)
            sum_squares = sum((value - alpha_bar) ** 2 for value in tank_intercepts)
            # Includes the Jacobian for the log(sigma) proposal scale.
            return -(len(tank_intercepts) - 1) * math.log(candidate) - sum_squares / (2 * candidate**2) - candidate

        if math.log(rng.random()) < sigma_log_density(proposed_log_sigma) - sigma_log_density(old_log_sigma):
            sigma = math.exp(proposed_log_sigma)

        if iteration >= 20_000 and iteration % 10 == 0:
            saved_hyperparameters.append((alpha_bar, sigma))
            for index, value in enumerate(tank_intercepts):
                intercept_sums[index] += value

    count = len(saved_hyperparameters)
    posterior_means = [value / count for value in intercept_sums]
    return posterior_means, saved_hyperparameters


def figure_13_1(posterior_means: list[float], hyperparameters: list[tuple[float, float]]) -> None:
    width, height = 1200, 720
    x0, y0, x1, y1 = 115.0, 70.0, 1110.0, 565.0

    def xy(tank: float, probability: float) -> tuple[float, float]:
        x = x0 + (tank - 1.0) / 47.0 * (x1 - x0)
        y = y1 - probability * (y1 - y0)
        return x, y

    raw_proportions = [survived / density for survived, density in zip(SURVIVED, DENSITY)]
    estimated_proportions = [logistic(value) for value in posterior_means]
    average_survival = sum(logistic(alpha_bar) for alpha_bar, _ in hyperparameters) / len(hyperparameters)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 13.1：水槽存活率的部分汇聚</title>',
        '<desc>蓝色实心点是四十八个水槽的经验存活比例，黑色空心点是多层模型的后验均值；多层估计均向总体平均存活率收缩，小水槽的收缩更明显。</desc>',
        '<rect width="1200" height="720" fill="#fff"/>',
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
    ]

    for value in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        _, y = xy(1, value)
        svg.extend([
            f'<line x1="{x0 - 7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
            text_el(x0 - 15, y + 6, f"{value:.1f}", size=17, anchor="end"),
        ])
    for tank in [1, 16, 32, 48]:
        x, _ = xy(tank, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1 + 7}" stroke="{INK}"/>',
            text_el(x, y1 + 29, tank, size=17, anchor="middle"),
        ])
    for divider in [16.5, 32.5]:
        x, _ = xy(divider, 0)
        svg.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" stroke="#777" stroke-width="1.5"/>')

    _, average_y = xy(1, average_survival)
    svg.append(f'<line x1="{x0}" y1="{average_y:.1f}" x2="{x1}" y2="{average_y:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="10 8"/>')

    for tank, (raw, estimated) in enumerate(zip(raw_proportions, estimated_proportions), start=1):
        x, raw_y = xy(tank, raw)
        _, estimated_y = xy(tank, estimated)
        svg.extend([
            f'<circle cx="{x:.1f}" cy="{raw_y:.1f}" r="7" fill="{BLUE}"/>',
            f'<circle cx="{x:.1f}" cy="{estimated_y:.1f}" r="7" fill="#fff" stroke="{INK}" stroke-width="2.2"/>',
        ])

    svg.extend([
        text_el((x0 + x1) / 2, 650, "水槽编号", size=22, anchor="middle"),
        text_el(35, (y0 + y1) / 2, "存活比例", size=22, anchor="middle", rotate=-90),
        text_el((xy(1, 0)[0] + xy(16, 0)[0]) / 2, y1 - 15, "小水槽", size=20, anchor="middle"),
        text_el((xy(17, 0)[0] + xy(32, 0)[0]) / 2, y1 - 15, "中水槽", size=20, anchor="middle"),
        text_el((xy(33, 0)[0] + xy(48, 0)[0]) / 2, y1 - 15, "大水槽", size=20, anchor="middle"),
        '<circle cx="785" cy="680" r="7" fill="#6670ee"/>',
        text_el(803, 686, "经验存活比例", size=17),
        '<circle cx="955" cy="680" r="7" fill="#fff" stroke="#30332e" stroke-width="2.2"/>',
        text_el(973, 686, "多层模型后验均值", size=17),
        '</svg>',
    ])
    OUT1.parent.mkdir(parents=True, exist_ok=True)
    OUT1.write_text("\n".join(svg), encoding="utf-8")


def gaussian_density(value: float, mean: float, sigma: float) -> float:
    return math.exp(-0.5 * ((value - mean) / sigma) ** 2) / (sigma * math.sqrt(2.0 * math.pi))


def figure_13_2(hyperparameters: list[tuple[float, float]]) -> None:
    width, height = 1200, 670
    left = (90.0, 75.0, 555.0, 535.0)
    right = (690.0, 75.0, 1155.0, 535.0)
    lx0, ly0, lx1, ly1 = left
    rx0, ry0, rx1, ry1 = right

    def left_xy(value: float, density: float) -> tuple[float, float]:
        return lx0 + (value + 3.0) / 7.0 * (lx1 - lx0), ly1 - density / 0.35 * (ly1 - ly0)

    def right_xy(probability: float, density: float) -> tuple[float, float]:
        return rx0 + probability * (rx1 - rx0), ry1 - density / 3.5 * (ry1 - ry0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 13.2：水槽总体存活率的后验分布</title>',
        '<desc>左图是从总体位置和尺度后验中取得的一百条存活对数赔率高斯分布；右图是八千个新水槽的存活概率密度，传播了位置和尺度的不确定性。</desc>',
        '<rect width="1200" height="670" fill="#fff"/>',
        f'<line x1="{lx0}" y1="{ly1}" x2="{lx1}" y2="{ly1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{lx0}" y1="{ly0}" x2="{lx0}" y2="{ly1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{rx0}" y1="{ry1}" x2="{rx1}" y2="{ry1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{rx0}" y1="{ry0}" x2="{rx0}" y2="{ry1}" stroke="{INK}" stroke-width="2"/>',
    ]

    left_xs = [-3.0 + index * 7.0 / 140 for index in range(141)]
    step = max(1, len(hyperparameters) // 100)
    selected = hyperparameters[::step][:100]
    for alpha_bar, sigma in selected:
        points = [left_xy(value, gaussian_density(value, alpha_bar, sigma)) for value in left_xs]
        svg.append(polyline(points, fill="none", stroke="#50534e", stroke_width="1.4", opacity="0.20"))

    rng = random.Random(1306)
    simulated_probabilities = []
    for index in range(8_000):
        alpha_bar, sigma = hyperparameters[index % len(hyperparameters)]
        simulated_probabilities.append(logistic(rng.gauss(alpha_bar, sigma)))
    bandwidth = 0.018
    probability_xs = [index / 200 for index in range(201)]
    normalization = len(simulated_probabilities) * bandwidth * math.sqrt(2.0 * math.pi)
    probability_density = [
        sum(math.exp(-0.5 * ((value - sample) / bandwidth) ** 2) for sample in simulated_probabilities) / normalization
        for value in probability_xs
    ]
    max_density = max(probability_density)
    if max_density > 3.45:
        probability_density = [value * 3.45 / max_density for value in probability_density]
    probability_density[-1] = 0.0
    svg.append(polyline([right_xy(x, y) for x, y in zip(probability_xs, probability_density)], fill="none", stroke=INK, stroke_width="4"))

    for value in range(-3, 5):
        x, _ = left_xy(value, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{ly1}" x2="{x:.1f}" y2="{ly1 + 7}" stroke="{INK}"/>',
            text_el(x, ly1 + 29, value, size=17, anchor="middle"),
        ])
    for value in [0.0, 0.1, 0.2, 0.3]:
        _, y = left_xy(-3, value)
        svg.extend([
            f'<line x1="{lx0 - 7}" y1="{y:.1f}" x2="{lx0}" y2="{y:.1f}" stroke="{INK}"/>',
            text_el(lx0 - 15, y + 6, f"{value:.2f}", size=17, anchor="end"),
        ])
    for value in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        x, _ = right_xy(value, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{ry1}" x2="{x:.1f}" y2="{ry1 + 7}" stroke="{INK}"/>',
            text_el(x, ry1 + 29, f"{value:.1f}", size=17, anchor="middle"),
        ])
    for value in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
        _, y = right_xy(0, value)
        svg.extend([
            f'<line x1="{rx0 - 7}" y1="{y:.1f}" x2="{rx0}" y2="{y:.1f}" stroke="{INK}"/>',
            text_el(rx0 - 15, y + 6, f"{value:.1f}", size=17, anchor="end"),
        ])
    svg.extend([
        text_el((lx0 + lx1) / 2, 620, "存活对数赔率", size=22, anchor="middle"),
        text_el(28, (ly0 + ly1) / 2, "密度", size=22, anchor="middle", rotate=-90),
        text_el((rx0 + rx1) / 2, 620, "存活概率", size=22, anchor="middle"),
        text_el(625, (ry0 + ry1) / 2, "密度", size=22, anchor="middle", rotate=-90),
        '</svg>',
    ])
    OUT2.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    posterior_means, hyperparameters = sample_posterior()
    figure_13_1(posterior_means, hyperparameters)
    figure_13_2(hyperparameters)
    print(OUT1)
    print(OUT2)


if __name__ == "__main__":
    main()
