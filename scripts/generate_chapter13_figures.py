#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 13."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-13-tank-shrinkage.svg"
OUT2 = ROOT / "translations" / "zh" / "media" / "chapter-13-tank-population.svg"
OUT3 = ROOT / "translations" / "zh" / "media" / "chapter-13-pond-errors.svg"
OUT4 = ROOT / "translations" / "zh" / "media" / "chapter-13-cluster-variation.svg"
OUT5 = ROOT / "translations" / "zh" / "media" / "chapter-13-devils-funnel.svg"
OUT6 = ROOT / "translations" / "zh" / "media" / "chapter-13-neff-comparison.svg"
OUT7 = ROOT / "translations" / "zh" / "media" / "chapter-13-chimp-predictions.svg"
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


def figure_13_3() -> None:
    """Rebuild the no-pooling versus partial-pooling simulation."""
    pond_sizes = [5] * 15 + [10] * 15 + [25] * 15 + [35] * 15
    # Exact R draws produced by set.seed(5005), a_bar=1.5, and sigma=1.5.
    true_intercepts = [
        0.56673123, 1.99002317, -0.13775688, 1.85676651, 3.91208800, 1.95414869,
        1.48963805, 2.52407196, 2.17828010, 2.04776578, 2.74564559, -0.63722320,
        3.03948315, 1.90733694, 3.54119394, 0.65165674, -1.16943954, 0.59568973,
        0.38530177, 1.02961242, 0.07034006, 1.34936971, 2.45730258, -0.05251326,
        2.20677386, 1.82918746, 1.33997120, 1.57233138, 1.25467353, 0.82663309,
        2.65834264, 2.08241191, 1.50758907, 0.86265946, 0.22721714, 4.61568929,
        -1.75144380, -1.03306026, 0.23817747, 5.35841158, 3.84572461, 1.81628755,
        -0.34267584, 0.76111582, -1.55979666, -0.08456073, 4.37882074, 2.32597649,
        1.78144089, 1.86990933, 1.58196519, 0.15560642, 1.50345864, 4.49654575,
        0.56518221, 2.55806132, 0.56742678, 2.74606408, 1.50422253, 2.49737954,
    ]
    survivor_counts = [
        4, 5, 1, 5, 5, 5, 2, 5, 4, 4, 5, 2, 5, 5, 5,
        8, 1, 7, 2, 8, 4, 9, 10, 6, 10, 9, 7, 9, 8, 7,
        23, 22, 21, 19, 16, 25, 6, 5, 16, 25, 25, 23, 11, 16, 5,
        17, 35, 31, 30, 33, 32, 20, 31, 35, 26, 33, 23, 35, 29, 32,
    ]
    true_probabilities = [logistic(value) for value in true_intercepts]
    no_pooling = [count / size for count, size in zip(survivor_counts, pond_sizes)]

    rng = random.Random(1313)
    intercepts = [
        math.log(((count + 0.5) / (size + 1.0)) / (1.0 - (count + 0.5) / (size + 1.0)))
        for count, size in zip(survivor_counts, pond_sizes)
    ]
    alpha_bar = sum(intercepts) / len(intercepts)
    sigma = 1.5
    probability_sums = [0.0] * len(intercepts)
    saved = 0

    def tank_log_density(value: float, count: int, size: int) -> float:
        return count * value - size * log1pexp(value) - (value - alpha_bar) ** 2 / (2.0 * sigma**2)

    for iteration in range(70_000):
        for index, (count, size) in enumerate(zip(survivor_counts, pond_sizes)):
            old = intercepts[index]
            proposal = old + rng.gauss(0.0, 0.32)
            if math.log(rng.random()) < tank_log_density(proposal, count, size) - tank_log_density(old, count, size):
                intercepts[index] = proposal
        variance = 1.0 / (len(intercepts) / sigma**2 + 1.0 / 1.5**2)
        alpha_bar = rng.gauss(variance * sum(intercepts) / sigma**2, math.sqrt(variance))
        old_log_sigma = math.log(sigma)
        proposal_log_sigma = old_log_sigma + rng.gauss(0.0, 0.07)

        def sigma_log_density(log_sigma: float) -> float:
            candidate = math.exp(log_sigma)
            sum_squares = sum((value - alpha_bar) ** 2 for value in intercepts)
            return -(len(intercepts) - 1) * math.log(candidate) - sum_squares / (2.0 * candidate**2) - candidate

        if math.log(rng.random()) < sigma_log_density(proposal_log_sigma) - sigma_log_density(old_log_sigma):
            sigma = math.exp(proposal_log_sigma)
        if iteration >= 20_000 and iteration % 10 == 0:
            saved += 1
            for index, value in enumerate(intercepts):
                probability_sums[index] += logistic(value)

    partial_pooling = [value / saved for value in probability_sums]
    no_pooling_error = [abs(estimate - truth) for estimate, truth in zip(no_pooling, true_probabilities)]
    partial_pooling_error = [abs(estimate - truth) for estimate, truth in zip(partial_pooling, true_probabilities)]
    no_pooling_average = [sum(no_pooling_error[start:start + 15]) / 15 for start in range(0, 60, 15)]
    partial_pooling_average = [sum(partial_pooling_error[start:start + 15]) / 15 for start in range(0, 60, 15)]

    width, height = 1200, 720
    x0, y0, x1, y1 = 105.0, 85.0, 1120.0, 590.0

    def xy(pond: float, error: float) -> tuple[float, float]:
        return x0 + (pond - 1.0) / 59.0 * (x1 - x0), y1 - error / 0.45 * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 13.3：无汇聚与部分汇聚估计的绝对误差</title>',
        '<desc>六十个模拟池塘按初始蝌蚪数量分为四组。蓝色实心点是无汇聚估计的绝对误差，黑色空心点是部分汇聚估计的误差；小池塘误差更大，部分汇聚平均改善最明显。</desc>',
        '<rect width="1200" height="720" fill="#fff"/>',
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
    ]
    for value in [0.0, 0.1, 0.2, 0.3, 0.4]:
        _, y = xy(1, value)
        svg.extend([
            f'<line x1="{x0 - 7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
            text_el(x0 - 15, y + 6, f"{value:.1f}", size=17, anchor="end"),
        ])
    for pond in [1, 10, 20, 30, 40, 50, 60]:
        x, _ = xy(pond, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1 + 7}" stroke="{INK}"/>',
            text_el(x, y1 + 29, pond, size=17, anchor="middle"),
        ])
    for divider in [15.5, 30.5, 45.5]:
        x, _ = xy(divider, 0)
        svg.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" stroke="#777" stroke-width="1.4"/>')
    labels = ["极小池塘（5）", "小池塘（10）", "中池塘（25）", "大池塘（35）"]
    for group, label in enumerate(labels):
        center, _ = xy(group * 15 + 8, 0.43)
        svg.append(text_el(center, y0 + 5, label, size=18, anchor="middle"))
        start_x, _ = xy(group * 15 + 1, 0)
        end_x, _ = xy(group * 15 + 15, 0)
        _, blue_y = xy(1, no_pooling_average[group])
        _, black_y = xy(1, partial_pooling_average[group])
        svg.extend([
            f'<line x1="{start_x:.1f}" y1="{blue_y:.1f}" x2="{end_x:.1f}" y2="{blue_y:.1f}" stroke="{BLUE}" stroke-width="3"/>',
            f'<line x1="{start_x:.1f}" y1="{black_y:.1f}" x2="{end_x:.1f}" y2="{black_y:.1f}" stroke="{INK}" stroke-width="3" stroke-dasharray="9 7"/>',
        ])
    for pond, (no_error, partial_error) in enumerate(zip(no_pooling_error, partial_pooling_error), start=1):
        x, blue_y = xy(pond, no_error)
        _, black_y = xy(pond, partial_error)
        svg.extend([
            f'<circle cx="{x:.1f}" cy="{blue_y:.1f}" r="6.5" fill="{BLUE}"/>',
            f'<circle cx="{x:.1f}" cy="{black_y:.1f}" r="6.5" fill="#fff" stroke="{INK}" stroke-width="2"/>',
        ])
    svg.extend([
        text_el((x0 + x1) / 2, 670, "池塘编号", size=22, anchor="middle"),
        text_el(30, (y0 + y1) / 2, "绝对误差", size=22, anchor="middle", rotate=-90),
        '<circle cx="800" cy="690" r="6.5" fill="#6670ee"/>',
        text_el(818, 696, "无汇聚", size=17),
        '<circle cx="930" cy="690" r="6.5" fill="#fff" stroke="#30332e" stroke-width="2"/>',
        text_el(948, 696, "部分汇聚", size=17),
        '</svg>',
    ])
    OUT3.write_text("\n".join(svg), encoding="utf-8")


def figure_13_4() -> None:
    """Rebuild the published coefficient summary and cluster-scale densities."""
    estimates = [
        ("b[1]", -0.12, -0.59, 0.39),
        ("b[2]", 0.40, -0.07, 0.88),
        ("b[3]", -0.48, -0.96, 0.00),
        ("b[4]", 0.30, -0.17, 0.80),
        ("a[1]", -0.37, -0.94, 0.24),
        ("a[2]", 4.61, 2.98, 6.83),
        ("a[3]", -0.67, -1.24, -0.08),
        ("a[4]", -0.68, -1.26, -0.09),
        ("a[5]", -0.37, -0.93, 0.19),
        ("a[6]", 0.57, 0.01, 1.12),
        ("a[7]", 2.09, 1.41, 2.82),
        ("g[1]", -0.17, -0.57, 0.07),
        ("g[2]", 0.05, -0.19, 0.36),
        ("g[3]", 0.05, -0.22, 0.39),
        ("g[4]", 0.02, -0.25, 0.31),
        ("g[5]", -0.02, -0.31, 0.24),
        ("g[6]", 0.12, -0.11, 0.49),
        ("a_bar", 0.58, -0.58, 1.79),
        ("sigma_a", 2.00, 1.17, 3.16),
        ("sigma_g", 0.21, 0.03, 0.52),
    ]
    width, height = 1200, 760
    left = (120.0, 58.0, 590.0, 620.0)
    right = (710.0, 100.0, 1145.0, 620.0)
    lx0, ly0, lx1, ly1 = left
    rx0, ry0, rx1, ry1 = right

    def left_x(value: float) -> float:
        return lx0 + (value + 2.0) / 9.2 * (lx1 - lx0)

    def right_xy(value: float, density: float) -> tuple[float, float]:
        return rx0 + value / 4.2 * (rx1 - rx0), ry1 - density / 3.7 * (ry1 - ry0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 13.4：行动者与区组变化截距的后验比较</title>',
        '<desc>左图显示模型 m13.4 各参数的后验均值与百分之八十九相容区间；行动者截距比区组截距分散得多。右图显示行动者和区组变化截距标准差的边际后验密度。</desc>',
        '<rect width="1200" height="760" fill="#fff"/>',
        f'<line x1="{lx0}" y1="{ly1}" x2="{lx1}" y2="{ly1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{lx0}" y1="{ly0}" x2="{lx0}" y2="{ly1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{rx0}" y1="{ry1}" x2="{rx1}" y2="{ry1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{rx0}" y1="{ry0}" x2="{rx0}" y2="{ry1}" stroke="{INK}" stroke-width="2"/>',
    ]

    row_step = (ly1 - ly0) / len(estimates)
    for index, (label, mean, low, high) in enumerate(estimates):
        y = ly0 + (index + 0.5) * row_step
        svg.extend([
            f'<line x1="{lx0}" y1="{y:.1f}" x2="{lx1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1" stroke-dasharray="4 5"/>',
            text_el(lx0 - 14, y + 6, label, size=17, anchor="end"),
            f'<line x1="{left_x(low):.1f}" y1="{y:.1f}" x2="{left_x(high):.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="3"/>',
            f'<circle cx="{left_x(mean):.1f}" cy="{y:.1f}" r="6.5" fill="#fff" stroke="{INK}" stroke-width="2"/>',
        ])
    for value in [0, 2, 4, 6]:
        x = left_x(value)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{ly1}" x2="{x:.1f}" y2="{ly1 + 7}" stroke="{INK}"/>',
            text_el(x, ly1 + 30, value, size=17, anchor="middle"),
        ])

    xs = [index * 4.2 / 210 for index in range(211)]
    actor_density = [gaussian_density(value, 1.85, 0.62) for value in xs]
    block_density = [value / 0.11**2 * math.exp(-value / 0.11) for value in xs]
    svg.extend([
        polyline([right_xy(x, y) for x, y in zip(xs, block_density)], fill="none", stroke=BLUE, stroke_width="4"),
        polyline([right_xy(x, y) for x, y in zip(xs, actor_density)], fill="none", stroke=INK, stroke_width="4"),
    ])
    for value in [0, 1, 2, 3, 4]:
        x, _ = right_xy(value, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{ry1}" x2="{x:.1f}" y2="{ry1 + 7}" stroke="{INK}"/>',
            text_el(x, ry1 + 30, value, size=17, anchor="middle"),
        ])
    for value in [0, 1, 2, 3]:
        _, y = right_xy(0, value)
        svg.extend([
            f'<line x1="{rx0 - 7}" y1="{y:.1f}" x2="{rx0}" y2="{y:.1f}" stroke="{INK}"/>',
            text_el(rx0 - 15, y + 6, f"{value:.1f}", size=17, anchor="end"),
        ])
    svg.extend([
        text_el((lx0 + lx1) / 2, 700, "参数值", size=22, anchor="middle"),
        text_el((rx0 + rx1) / 2, 700, "标准差", size=22, anchor="middle"),
        text_el(655, (ry0 + ry1) / 2, "密度", size=22, anchor="middle", rotate=-90),
        text_el(right_xy(0.42, 2.55)[0], right_xy(0.42, 2.55)[1], "区组", size=20, fill=BLUE),
        text_el(right_xy(2.65, 0.46)[0], right_xy(2.65, 0.46)[1], "行动者", size=20),
        '</svg>',
    ])
    OUT4.write_text("\n".join(svg), encoding="utf-8")


def figure_13_5() -> None:
    """Draw the centered funnel and its non-centered Gaussian form."""
    width, height = 1200, 690
    left = (90.0, 95.0, 555.0, 560.0)
    right = (665.0, 95.0, 1130.0, 560.0)
    lx0, ly0, lx1, ly1 = left
    rx0, ry0, rx1, ry1 = right

    def left_xy(x: float, v: float) -> tuple[float, float]:
        return lx0 + (x + 5.0) / 10.0 * (lx1 - lx0), ly1 - (v + 4.5) / 9.0 * (ly1 - ly0)

    def right_xy(z: float, v: float) -> tuple[float, float]:
        return rx0 + (z + 2.3) / 4.6 * (rx1 - rx0), ry1 - (v + 4.5) / 9.0 * (ry1 - ry0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 13.5：魔鬼漏斗的中心化与非中心化参数化</title>',
        '<desc>左图是中心化参数化的漏斗形联合密度等高线，灰色 HMC 轨迹越过陡峭谷壁形成发散转移；右图是同一模型的非中心化参数化，联合密度变为平缓的二维高斯。</desc>',
        '<rect width="1200" height="690" fill="#fff"/>',
        text_el((lx0 + lx1) / 2, 48, "中心化参数化", size=23, anchor="middle", weight=600),
        text_el((rx0 + rx1) / 2, 48, "非中心化参数化", size=23, anchor="middle", weight=600),
    ]

    for x0, y0, x1, y1 in [left, right]:
        svg.extend([
            f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
            f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
        ])

    # Exact contour branches of log p(v, x), apart from an additive constant.
    for level in [-4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0]:
        positive: list[tuple[float, float]] = []
        negative: list[tuple[float, float]] = []
        branches: list[tuple[list[tuple[float, float]], list[tuple[float, float]]]] = []
        for index in range(361):
            v = -4.45 + index * 8.9 / 360
            radicand = 2.0 * math.exp(2.0 * v) * (-v * v / 18.0 - v - level)
            x = math.sqrt(radicand) if radicand > 0 else 99.0
            if x <= 5.05:
                positive.append(left_xy(x, v))
                negative.append(left_xy(-x, v))
            elif len(positive) > 1:
                branches.append((positive, negative))
                positive, negative = [], []
        if len(positive) > 1:
            branches.append((positive, negative))
        for positive_branch, negative_branch in branches:
            svg.extend([
                polyline(positive_branch, fill="none", stroke="#777a74", stroke_width="1.2"),
                polyline(negative_branch, fill="none", stroke="#777a74", stroke_width="1.2"),
            ])

    # The non-centered joint density is Gaussian in v and z.
    for radius in [0.30, 0.48, 0.66, 0.84, 1.02, 1.20, 1.38, 1.46]:
        points = [
            right_xy(radius * math.cos(angle), 3.0 * radius * math.sin(angle))
            for angle in [index * 2.0 * math.pi / 240 for index in range(241)]
        ]
        svg.append(polyline(points, fill="none", stroke="#777a74", stroke_width="1.2"))

    left_trajectory = [(-0.20, -0.55), (0.72, 0.18), (0.02, -2.25), (1.06, 0.38), (-1.85, 3.05)]
    right_trajectory = [(0.02, -0.20), (-1.55, 1.05), (-0.20, 1.78), (0.38, -0.28), (-1.48, -1.05), (-0.30, -4.05)]
    svg.extend([
        polyline([left_xy(x, v) for x, v in left_trajectory], fill="none", stroke="#a8aaa5", stroke_width="4"),
        polyline([right_xy(z, v) for z, v in right_trajectory], fill="none", stroke="#a8aaa5", stroke_width="4"),
    ])
    for x, v in left_trajectory[:-1]:
        px, py = left_xy(x, v)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{INK}"/>')
    open_x, open_y = left_xy(*left_trajectory[-1])
    svg.append(f'<circle cx="{open_x:.1f}" cy="{open_y:.1f}" r="7" fill="#fff" stroke="{INK}" stroke-width="2.3"/>')
    for z, v in right_trajectory:
        px, py = right_xy(z, v)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{INK}"/>')
    for mapper in [left_xy, right_xy]:
        px, py = mapper(0, 0)
        svg.extend([
            f'<line x1="{px - 8:.1f}" y1="{py - 8:.1f}" x2="{px + 8:.1f}" y2="{py + 8:.1f}" stroke="{INK}" stroke-width="2.2"/>',
            f'<line x1="{px - 8:.1f}" y1="{py + 8:.1f}" x2="{px + 8:.1f}" y2="{py - 8:.1f}" stroke="{INK}" stroke-width="2.2"/>',
        ])

    for value in [-4, -2, 0, 2, 4]:
        x, _ = left_xy(value, -4.5)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{ly1}" x2="{x:.1f}" y2="{ly1 + 7}" stroke="{INK}"/>',
            text_el(x, ly1 + 30, value, size=17, anchor="middle"),
        ])
    for value in [-2, -1, 0, 1, 2]:
        x, _ = right_xy(value, -4.5)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{ry1}" x2="{x:.1f}" y2="{ry1 + 7}" stroke="{INK}"/>',
            text_el(x, ry1 + 30, value, size=17, anchor="middle"),
        ])
    for value in [-4, -2, 0, 2, 4]:
        for x0, mapper in [(lx0, left_xy), (rx0, right_xy)]:
            _, y = mapper(0, value)
            svg.extend([
                f'<line x1="{x0 - 7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
                text_el(x0 - 15, y + 6, value, size=17, anchor="end"),
            ])
    svg.extend([
        text_el((lx0 + lx1) / 2, 635, "x", size=22, anchor="middle"),
        text_el((rx0 + rx1) / 2, 635, "z", size=22, anchor="middle"),
        text_el(30, (ly0 + ly1) / 2, "v", size=22, anchor="middle", rotate=-90),
        text_el(605, (ry0 + ry1) / 2, "v", size=22, anchor="middle", rotate=-90),
        '</svg>',
    ])
    OUT5.write_text("\n".join(svg), encoding="utf-8")


def figure_13_6() -> None:
    """Compare effective sample sizes under centered and non-centered forms."""
    centered = [158, 310, 515, 186, 446, 915, 709, 235, 338, 560, 721, 426, 921, 1062, 939, 873, 533, 800, 1106, 229]
    non_centered = [1330, 1310, 1450, 1240, 1390, 2110, 1370, 750, 1350, 1500, 1840, 1300, 2020, 1660, 1710, 1810, 1440, 1900, 790, 1360]
    width, height = 920, 760
    x0, y0, x1, y1 = 115.0, 75.0, 850.0, 640.0

    def xy(x: float, y: float) -> tuple[float, float]:
        return x0 + x / 2200.0 * (x1 - x0), y1 - y / 2200.0 * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 13.6：中心化与非中心化参数化的有效样本量</title>',
        '<desc>横轴是中心化黑猩猩模型的有效样本量，纵轴是非中心化模型的有效样本量。二十个参数中除两个外都位于对角线之上，表明非中心化参数化的抽样效率更高。</desc>',
        '<rect width="920" height="760" fill="#fff"/>',
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{xy(0, 0)[0]:.1f}" y1="{xy(0, 0)[1]:.1f}" x2="{xy(2200, 2200)[0]:.1f}" y2="{xy(2200, 2200)[1]:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="10 8"/>',
    ]
    for value in [500, 1000, 1500, 2000]:
        x, _ = xy(value, 0)
        _, y = xy(0, value)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1 + 7}" stroke="{INK}"/>',
            text_el(x, y1 + 30, value, size=17, anchor="middle"),
            f'<line x1="{x0 - 7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
            text_el(x0 - 15, y + 6, value, size=17, anchor="end"),
        ])
    for x_value, y_value in zip(centered, non_centered):
        x, y = xy(x_value, y_value)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    svg.extend([
        text_el((x0 + x1) / 2, 715, "n_eff（中心化）", size=22, anchor="middle"),
        text_el(35, (y0 + y1) / 2, "n_eff（非中心化）", size=22, anchor="middle", rotate=-90),
        '</svg>',
    ])
    OUT6.write_text("\n".join(svg), encoding="utf-8")


def figure_13_7() -> None:
    """Compare average, marginal, and simulated-actor predictions."""
    width, height = 1200, 600
    panels = [(70.0, 90.0, 350.0, 485.0), (460.0, 90.0, 740.0, 485.0), (850.0, 90.0, 1130.0, 485.0)]
    labels = ["R/N", "L/N", "R/P", "L/P"]

    def mapper(panel: tuple[float, float, float, float]):
        x0, y0, x1, y1 = panel

        def xy(treatment: float, probability: float) -> tuple[float, float]:
            return x0 + (treatment - 1.0) / 3.0 * (x1 - x0), y1 - probability * (y1 - y0)

        return xy

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 13.7：黑猩猩多层模型的三种后验预测</title>',
        '<desc>左图把行动者截距固定在总体均值，显示平均行动者预测；中图对行动者间变异取平均；右图显示一百个从后验总体模拟的新行动者，既呈现处理的锯齿影响，也呈现个体差异。</desc>',
        '<rect width="1200" height="600" fill="#fff"/>',
    ]
    for panel, title in zip(panels, ["平均行动者", "对行动者取边际", "模拟行动者"]):
        x0, y0, x1, y1 = panel
        xy = mapper(panel)
        svg.extend([
            text_el((x0 + x1) / 2, 45, title, size=22, anchor="middle", weight=600),
            f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
            f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="2"/>',
        ])
        for value in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            _, y = xy(1, value)
            svg.extend([
                f'<line x1="{x0 - 6}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
                text_el(x0 - 12, y + 6, f"{value:.1f}", size=15, anchor="end"),
            ])
        for treatment, label in enumerate(labels, start=1):
            x, _ = xy(treatment, 0)
            svg.extend([
                f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1 + 6}" stroke="{INK}"/>',
                text_el(x, y1 + 28, label, size=16, anchor="middle"),
            ])
        svg.extend([
            text_el((x0 + x1) / 2, 555, "处理", size=20, anchor="middle"),
            text_el(x0 - 52, (y0 + y1) / 2, "拉左侧杠杆的比例", size=18, anchor="middle", rotate=-90),
        ])

    left_xy = mapper(panels[0])
    left_mean = [0.59, 0.70, 0.52, 0.68]
    left_low = [0.33, 0.44, 0.27, 0.42]
    left_high = [0.84, 0.90, 0.76, 0.87]
    upper = [left_xy(i, value) for i, value in enumerate(left_high, start=1)]
    lower = [left_xy(i, value) for i, value in reversed(list(enumerate(left_low, start=1)))]
    area = " ".join(f"{x:.1f},{y:.1f}" for x, y in upper + lower)
    svg.extend([
        f'<polygon points="{area}" fill="#cfd1ce" opacity="0.85"/>',
        polyline([left_xy(i, value) for i, value in enumerate(left_mean, start=1)], fill="none", stroke=INK, stroke_width="3"),
    ])

    middle_xy = mapper(panels[1])
    middle_mean = [0.56, 0.63, 0.51, 0.63]
    middle_low = [0.05, 0.04, 0.02, 0.06]
    middle_high = [0.96, 0.97, 0.95, 0.98]
    upper = [middle_xy(i, value) for i, value in enumerate(middle_high, start=1)]
    lower = [middle_xy(i, value) for i, value in reversed(list(enumerate(middle_low, start=1)))]
    area = " ".join(f"{x:.1f},{y:.1f}" for x, y in upper + lower)
    svg.extend([
        f'<polygon points="{area}" fill="#cfd1ce" opacity="0.85"/>',
        polyline([middle_xy(i, value) for i, value in enumerate(middle_mean, start=1)], fill="none", stroke=INK, stroke_width="3"),
    ])

    rng = random.Random(1370)
    right_xy = mapper(panels[2])
    treatment_effects = [-0.12, 0.40, -0.48, 0.30]
    for _ in range(100):
        intercept = rng.gauss(0.58, 2.0)
        probabilities = [logistic(intercept + effect) for effect in treatment_effects]
        svg.append(polyline([right_xy(i, value) for i, value in enumerate(probabilities, start=1)], fill="none", stroke=INK, stroke_width="2", opacity="0.23"))
    svg.append('</svg>')
    OUT7.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    posterior_means, hyperparameters = sample_posterior()
    figure_13_1(posterior_means, hyperparameters)
    figure_13_2(hyperparameters)
    figure_13_3()
    figure_13_4()
    figure_13_5()
    figure_13_6()
    figure_13_7()
    print(OUT1)
    print(OUT2)
    print(OUT3)
    print(OUT4)
    print(OUT5)
    print(OUT6)
    print(OUT7)


if __name__ == "__main__":
    main()
