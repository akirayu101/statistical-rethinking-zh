#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 15."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from generate_chapter5_waffle_divorce import rows


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-15-measurement-error.svg"
OUT2 = ROOT / "translations" / "zh" / "media" / "chapter-15-divorce-shrinkage.svg"
OUT3 = ROOT / "translations" / "zh" / "media" / "chapter-15-both-errors-shrinkage.svg"
OUT4 = ROOT / "translations" / "zh" / "media" / "chapter-15-imputation-independent.svg"
OUT5 = ROOT / "translations" / "zh" / "media" / "chapter-15-imputation-correlated.svg"
OUT6 = ROOT / "translations" / "zh" / "media" / "chapter-15-moralizing-gods-missingness.svg"
MORALIZING_GODS_DATA = ROOT / "scripts" / "data" / "moralizing-gods.csv"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
GRID = "#ddd9ce"
DIVORCE_SE = [
    0.79, 2.05, 0.74, 1.22, 0.24, 0.94, 0.77, 1.39, 1.89, 0.32,
    0.58, 1.27, 1.05, 0.45, 0.63, 0.91, 1.09, 0.75, 0.89, 1.48,
    0.69, 0.52, 0.53, 0.60, 1.01, 0.67, 1.71, 0.94, 1.61, 0.46,
    1.11, 0.31, 0.48, 1.44, 0.45, 1.01, 0.80, 0.43, 1.79, 0.70,
    2.50, 0.75, 0.35, 0.93, 1.87, 0.52, 0.65, 1.34, 0.57, 1.90,
]
MARRIAGE_SE = [
    1.27, 2.93, 0.98, 1.70, 0.39, 1.24, 1.06, 2.89, 2.53, 0.58,
    0.81, 2.54, 1.84, 0.58, 0.81, 1.46, 1.48, 1.11, 1.19, 1.40,
    1.02, 0.70, 0.69, 0.77, 1.54, 0.81, 2.31, 1.44, 1.76, 0.59,
    1.90, 0.47, 0.98, 2.93, 0.61, 1.29, 1.10, 0.48, 2.11, 1.18,
    2.64, 0.85, 0.61, 1.77, 2.40, 0.83, 1.00, 1.69, 0.79, 3.92,
]
MILK_KCAL = [
    0.49, 0.51, 0.46, 0.48, 0.60, 0.47, 0.56, 0.89, 0.91, 0.92,
    0.80, 0.46, 0.71, 0.71, 0.73, 0.68, 0.72, 0.97, 0.79, 0.84,
    0.48, 0.62, 0.51, 0.54, 0.49, 0.53, 0.48, 0.55, 0.71,
]
MILK_MASS = [
    1.95, 2.09, 2.51, 1.62, 2.19, 5.25, 5.37, 2.51, 0.71, 0.68,
    0.12, 0.47, 0.32, 0.60, 3.47, 1.55, 7.08, 3.24, 7.94, 12.30,
    7.59, 5.37, 10.72, 35.48, 79.43, 97.72, 40.74, 33.11, 54.95,
]
MILK_BRAIN_PCT: list[float | None] = [
    55.16, None, None, None, None, 64.54, 64.54, 67.64, None, 68.85,
    58.85, 61.69, 60.32, None, None, 69.97, None, 70.41, None, 73.40,
    None, 67.53, None, 71.26, 72.60, None, 70.24, 76.30, 75.49,
]


def label(x: float, y: float, value: str, *, size: int = 18,
          anchor: str = "start", weight: int = 400,
          rotate: int | None = None) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
        f'fill="{INK}"{transform}>{value}</text>'
    )


def figure_15_1() -> None:
    width, height = 1200, 620
    panels = [(90.0, 55.0, 570.0, 520.0), (665.0, 55.0, 1145.0, 520.0)]
    data = rows()

    # Exact Divorce.SE values from the official rethinking WaffleDivorce dataset.
    errors = DIVORCE_SE

    def map_left(age: float, divorce: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[0]
        return x0 + (age - 22.5) / 7.5 * (x1 - x0), y1 - (divorce - 4.0) / 11.5 * (y1 - y0)

    def map_right(log_population: float, divorce: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[1]
        return x0 + (log_population + 1.0) / 5.0 * (x1 - x0), y1 - (divorce - 4.0) / 11.5 * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 15.1：各州离婚率的测量误差</title>',
        '<desc>左图以结婚年龄中位数预测离婚率，右图以人口对数为横轴；每个空心点的竖线表示离婚率测量的一倍标准误，小州的不确定性更大。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
    ]
    for x0, y0, x1, y1 in panels:
        svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
        for divorce in [4, 6, 8, 10, 12, 14]:
            y = y1 - (divorce - 4.0) / 11.5 * (y1 - y0)
            svg.extend([
                f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>',
                f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.4"/>',
                label(x0 - 14, y + 6, str(divorce), size=16, anchor="end"),
            ])

    for age in [23, 24, 25, 26, 27, 28, 29, 30]:
        x, _ = map_left(float(age), 4.0)
        svg.extend([f'<line x1="{x:.1f}" y1="520" x2="{x:.1f}" y2="527" stroke="{INK}"/>', label(x, 552, str(age), size=16, anchor="middle")])
    for log_population in [-1, 0, 1, 2, 3, 4]:
        x, _ = map_right(float(log_population), 4.0)
        svg.extend([f'<line x1="{x:.1f}" y1="520" x2="{x:.1f}" y2="527" stroke="{INK}"/>', label(x, 552, str(log_population), size=16, anchor="middle")])

    for row, error in zip(data, errors):
        divorce = float(row["divorce"])
        age = float(row["age"])
        log_population = math.log(float(row["population"]))
        for mapper, x_value in [(map_left, age), (map_right, log_population)]:
            x, y = mapper(x_value, divorce)
            _, y_low = mapper(x_value, max(4.0, divorce - error))
            _, y_high = mapper(x_value, min(15.5, divorce + error))
            svg.extend([
                f'<line x1="{x:.1f}" y1="{y_high:.1f}" x2="{x:.1f}" y2="{y_low:.1f}" stroke="{INK}" stroke-width="1.25"/>',
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.2" fill="#fff" stroke="{INK}" stroke-width="1.6"/>',
            ])

    svg.extend([
        label(330, 598, "结婚年龄中位数", size=19, anchor="middle", weight=600),
        label(905, 598, "人口对数", size=19, anchor="middle", weight=600),
        label(28, 287, "离婚率", size=19, anchor="middle", weight=600, rotate=-90),
        label(603, 287, "离婚率", size=19, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT1.write_text("\n".join(svg), encoding="utf-8")


def sample_standardize(values: list[float]) -> tuple[list[float], float]:
    """Match R's standardize()/sd() convention (sample standard deviation)."""
    mean = sum(values) / len(values)
    sd = math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))
    return [(value - mean) / sd for value in values], sd


def figure_15_2() -> None:
    """Reconstruct the shrinkage comparison in Figure 15.2.

    The plotted posterior means use the printed posterior mean coefficients from
    code 15.4 and the exact state-level standard errors. Conditional Gaussian
    updating then supplies a deterministic, auditable approximation to the
    book's MCMC summaries without requiring a local Stan toolchain.
    """
    width, height = 1200, 620
    panels = [(90.0, 55.0, 570.0, 520.0), (665.0, 55.0, 1145.0, 520.0)]
    data = rows()
    divorce = [float(row["divorce"]) for row in data]
    age = [float(row["age"]) for row in data]
    marriage = [float(row["marriage"]) for row in data]
    d_obs, d_raw_sd = sample_standardize(divorce)
    age_std, _ = sample_standardize(age)
    marriage_std, _ = sample_standardize(marriage)
    d_sd = [error / d_raw_sd for error in DIVORCE_SE]

    # Posterior means printed by code 15.4.
    a, b_age, b_marriage, sigma = -0.06, -0.61, 0.05, 0.60
    expected = [a + b_age * av + b_marriage * mv for av, mv in zip(age_std, marriage_std)]
    posterior_var = [1.0 / (1.0 / err**2 + 1.0 / sigma**2) for err in d_sd]
    d_est = [
        var * (obs / err**2 + mu / sigma**2)
        for var, obs, err, mu in zip(posterior_var, d_obs, d_sd, expected)
    ]
    d_est_sd = [math.sqrt(var) for var in posterior_var]

    left_x_range, left_y_range = (0.10, 1.45), (-1.25, 1.55)
    right_x_range, right_y_range = (-2.55, 3.15), (-2.45, 2.45)

    def map_value(value: float, low: float, high: float, start: float, end: float) -> float:
        return start + (value - low) / (high - low) * (end - start)

    def left_xy(x_value: float, y_value: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[0]
        return (
            map_value(x_value, *left_x_range, x0, x1),
            map_value(y_value, *left_y_range, y1, y0),
        )

    def right_xy(x_value: float, y_value: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[1]
        return (
            map_value(x_value, *right_x_range, x0, x1),
            map_value(y_value, *right_y_range, y1, y0),
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 15.2：为离婚率测量误差建模产生的收缩</title>',
        '<desc>左图显示观测标准误越大，后验离婚率相对观测值的改变量通常越大；右图比较忽略测量误差的灰色回归与纳入误差的蓝色回归，并显示各州后验离婚率及其标准差。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
    ]
    for x0, y0, x1, y1 in panels:
        svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')

    # Left panel axes and zero reference.
    for tick in [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]:
        x, _ = left_xy(tick, left_y_range[0])
        svg.extend([f'<line x1="{x:.1f}" y1="520" x2="{x:.1f}" y2="527" stroke="{INK}"/>', label(x, 552, f"{tick:.1f}", size=16, anchor="middle")])
    for tick in [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
        _, y = left_xy(left_x_range[0], tick)
        svg.extend([f'<line x1="83" y1="{y:.1f}" x2="90" y2="{y:.1f}" stroke="{INK}"/>', label(76, y + 6, f"{tick:.1f}", size=16, anchor="end")])
    _, zero_y = left_xy(left_x_range[0], 0.0)
    svg.append(f'<line x1="90" y1="{zero_y:.1f}" x2="570" y2="{zero_y:.1f}" stroke="#777" stroke-width="1.5" stroke-dasharray="8 7"/>')

    left_labels = {"AL", "AK", "AR", "DC", "ID", "ME", "ND", "NH", "RI", "SD", "UT", "VT", "WY"}
    label_offsets = {
        "AL": (-10, -12), "AK": (7, -11), "AR": (-8, -12), "DC": (7, -8),
        "ID": (-8, 21), "ME": (-8, -12), "ND": (-8, 21), "NH": (-8, -12),
        "RI": (7, -7), "SD": (7, -7), "UT": (-8, 21), "VT": (7, -8), "WY": (7, 20),
    }
    for row, err, obs, estimate in zip(data, d_sd, d_obs, d_est):
        loc = str(row["loc"])
        # Match the values in the printed panel. The book's vertical label says
        # D_est - D_obs, although the plotted sign is D_obs - D_est (for
        # example, Maine is positive and Idaho negative).
        x, y = left_xy(err, obs - estimate)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
        if loc in left_labels:
            dx, dy = label_offsets[loc]
            svg.append(label(x + dx, y + dy, loc, size=14, anchor="middle", weight=600))

    # Right panel axes.
    for tick in [-2, -1, 0, 1, 2, 3]:
        x, _ = right_xy(float(tick), right_y_range[0])
        svg.extend([f'<line x1="{x:.1f}" y1="520" x2="{x:.1f}" y2="527" stroke="{INK}"/>', label(x, 552, str(tick), size=16, anchor="middle")])
    for tick in [-2, -1, 0, 1, 2]:
        _, y = right_xy(right_x_range[0], float(tick))
        svg.extend([f'<line x1="658" y1="{y:.1f}" x2="665" y2="{y:.1f}" stroke="{INK}"/>', label(651, y + 6, str(tick), size=16, anchor="end")])

    # Approximate 89% posterior bands and the two regression means.
    grid = [right_x_range[0] + i * (right_x_range[1] - right_x_range[0]) / 100 for i in range(101)]
    old_mean = [-0.90 * x for x in grid]
    old_half = [0.18 + 0.055 * abs(x) for x in grid]
    new_mean = [a + b_age * x for x in grid]
    new_half = [0.16 + 0.045 * abs(x) for x in grid]

    def polygon_band(means: list[float], halves: list[float], fill: str, opacity: float) -> None:
        upper = [right_xy(x, mean + half) for x, mean, half in zip(grid, means, halves)]
        lower = [right_xy(x, mean - half) for x, mean, half in zip(grid, means, halves)]
        points = upper + list(reversed(lower))
        joined = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        svg.append(f'<polygon points="{joined}" fill="{fill}" fill-opacity="{opacity}"/>')

    polygon_band(old_mean, old_half, "#777", 0.18)
    polygon_band(new_mean, new_half, "#6670ee", 0.22)
    old_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in [right_xy(xv, yv) for xv, yv in zip(grid, old_mean)])
    new_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in [right_xy(xv, yv) for xv, yv in zip(grid, new_mean)])
    svg.extend([
        f'<polyline points="{old_points}" fill="none" stroke="#6f716d" stroke-width="2.2" stroke-dasharray="9 7"/>',
        f'<polyline points="{new_points}" fill="none" stroke="#6670ee" stroke-width="3"/>',
    ])

    right_labels = {"ID", "ME", "MN", "ND", "RI", "WY"}
    right_offsets = {"ID": (-10, 21), "ME": (8, -12), "MN": (8, 20), "ND": (8, 20), "RI": (8, -9), "WY": (8, -9)}
    for row, x_value, estimate, estimate_sd in zip(data, age_std, d_est, d_est_sd):
        loc = str(row["loc"])
        x, y = right_xy(x_value, estimate)
        _, y_low = right_xy(x_value, estimate - estimate_sd)
        _, y_high = right_xy(x_value, estimate + estimate_sd)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y_high:.1f}" x2="{x:.1f}" y2="{y_low:.1f}" stroke="{INK}" stroke-width="1.25"/>',
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
        ])
        if loc in right_labels:
            dx, dy = right_offsets[loc]
            svg.append(label(x + dx, y + dy, loc, size=14, anchor="middle", weight=600))

    svg.extend([
        label(330, 598, "D_sd", size=19, anchor="middle", weight=600),
        label(905, 598, "结婚年龄中位数（标准化）", size=19, anchor="middle", weight=600),
        label(28, 287, "D_est − D_obs", size=19, anchor="middle", weight=600, rotate=-90),
        label(603, 287, "离婚率（标准化）", size=19, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT2.write_text("\n".join(svg), encoding="utf-8")


def figure_15_3() -> None:
    """Reconstruct shrinkage when both marriage and divorce rates have error."""
    width, height = 840, 650
    plot = (105.0, 45.0, 795.0, 555.0)
    data = rows()
    divorce = [float(row["divorce"]) for row in data]
    marriage = [float(row["marriage"]) for row in data]
    age = [float(row["age"]) for row in data]
    d_obs, d_raw_sd = sample_standardize(divorce)
    m_obs, m_raw_sd = sample_standardize(marriage)
    age_std, _ = sample_standardize(age)
    d_sd = [error / d_raw_sd for error in DIVORCE_SE]
    m_sd = [error / m_raw_sd for error in MARRIAGE_SE]

    # A deterministic conditional-Gaussian approximation to m15.2, using the
    # posterior mean regression parameters printed for m15.1. Iterate the two
    # latent true-value updates because D_true and M_true inform one another.
    a, b_age, b_marriage, sigma = -0.06, -0.61, 0.05, 0.60
    m_true = [obs / (1.0 + err**2) for obs, err in zip(m_obs, m_sd)]
    d_true = d_obs[:]
    for _ in range(8):
        d_var = [1.0 / (1.0 / err**2 + 1.0 / sigma**2) for err in d_sd]
        d_mu = [a + b_age * av + b_marriage * mv for av, mv in zip(age_std, m_true)]
        d_true = [
            var * (obs / err**2 + mu / sigma**2)
            for var, obs, err, mu in zip(d_var, d_obs, d_sd, d_mu)
        ]
        next_m: list[float] = []
        for obs, err, dv, av in zip(m_obs, m_sd, d_true, age_std):
            precision = 1.0 / err**2 + 1.0 + b_marriage**2 / sigma**2
            numerator = obs / err**2 + b_marriage * (dv - a - b_age * av) / sigma**2
            next_m.append(numerator / precision)
        m_true = next_m

    x_range, y_range = (-1.80, 3.20), (-2.20, 2.20)
    x0, y0, x1, y1 = plot

    def xy(x_value: float, y_value: float) -> tuple[float, float]:
        return (
            x0 + (x_value - x_range[0]) / (x_range[1] - x_range[0]) * (x1 - x0),
            y1 - (y_value - y_range[0]) / (y_range[1] - y_range[0]) * (y1 - y0),
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 15.3：离婚率与结婚率同时收缩</title>',
        '<desc>蓝色实心点是各州观测到的标准化结婚率与离婚率，黑色空心圆是后验真实值均值；每条线连接同一州的观测与后验估计，二者都向推断出的回归关系收缩。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
    ]
    for tick in [-1, 0, 1, 2, 3]:
        x, _ = xy(float(tick), y_range[0])
        svg.extend([f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+7}" stroke="{INK}"/>', label(x, y1 + 33, str(tick), size=17, anchor="middle")])
    for tick in [-2, -1, 0, 1, 2]:
        _, y = xy(x_range[0], float(tick))
        svg.extend([f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>', label(x0 - 14, y + 6, str(tick), size=17, anchor="end")])

    # Connections first, then observed and posterior points.
    for ox, oy, tx, ty in zip(m_obs, d_obs, m_true, d_true):
        px0, py0 = xy(ox, oy)
        px1, py1 = xy(tx, ty)
        svg.append(f'<line x1="{px0:.1f}" y1="{py0:.1f}" x2="{px1:.1f}" y2="{py1:.1f}" stroke="#3f4752" stroke-width="1.5"/>')
    for ox, oy in zip(m_obs, d_obs):
        x, y = xy(ox, oy)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#6670ee" fill-opacity="0.82"/>')
    for tx, ty in zip(m_true, d_true):
        x, y = xy(tx, ty)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')

    svg.extend([
        label((x0 + x1) / 2, 625, "结婚率（标准化）", size=20, anchor="middle", weight=600),
        label(28, (y0 + y1) / 2, "离婚率（标准化）", size=20, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT3.write_text("\n".join(svg), encoding="utf-8")


def milk_standardized() -> tuple[list[float], list[float], list[float | None]]:
    """Return K, log(M), and observed B on the book's standardized scales."""
    kcal, _ = sample_standardize(MILK_KCAL)
    log_mass, _ = sample_standardize([math.log(value) for value in MILK_MASS])
    brain_observed = [value / 100 for value in MILK_BRAIN_PCT if value is not None]
    brain_mean = sum(brain_observed) / len(brain_observed)
    _, brain_sd = sample_standardize(brain_observed)
    brain = [
        None if value is None else (value / 100 - brain_mean) / brain_sd
        for value in MILK_BRAIN_PCT
    ]
    return kcal, log_mass, brain


def imputation_figure(
    output: Path,
    number: str,
    means: list[float],
    intervals: list[tuple[float, float]],
    description: str,
) -> None:
    """Draw the two-panel milk imputation figures used in Section 15.2.2."""
    width, height = 1200, 620
    panels = [(90.0, 55.0, 570.0, 520.0), (665.0, 55.0, 1145.0, 520.0)]
    kcal, log_mass, brain = milk_standardized()
    missing = [index for index, value in enumerate(brain) if value is None]
    x_ranges = [(-2.20, 1.60), (-2.25, 2.15)]
    y_ranges = [(-1.25, 2.15), (-2.25, 1.65)]

    def map_xy(panel: int, x_value: float, y_value: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[panel]
        x_low, x_high = x_ranges[panel]
        y_low, y_high = y_ranges[panel]
        return (
            x0 + (x_value - x_low) / (x_high - x_low) * (x1 - x0),
            y1 - (y_value - y_low) / (y_high - y_low) * (y1 - y0),
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<title>图 {number}：灵长类乳汁数据的缺失新皮层值插补</title>',
        f'<desc>{description}</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
    ]
    for x0, y0, x1, y1 in panels:
        svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')

    for tick in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
        x, _ = map_xy(0, tick, y_ranges[0][0])
        svg.extend([f'<line x1="{x:.1f}" y1="520" x2="{x:.1f}" y2="527" stroke="{INK}"/>', label(x, 551, f"{tick:g}", size=15, anchor="middle")])
    for tick in [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]:
        _, y = map_xy(0, x_ranges[0][0], tick)
        svg.extend([f'<line x1="83" y1="{y:.1f}" x2="90" y2="{y:.1f}" stroke="{INK}"/>', label(76, y + 5, f"{tick:g}", size=15, anchor="end")])
    for tick in [-2, -1, 0, 1, 2]:
        x, _ = map_xy(1, float(tick), y_ranges[1][0])
        svg.extend([f'<line x1="{x:.1f}" y1="520" x2="{x:.1f}" y2="527" stroke="{INK}"/>', label(x, 551, str(tick), size=15, anchor="middle")])
    for tick in [-2.0, -1.0, 0.0, 0.5, 1.0, 1.5]:
        _, y = map_xy(1, x_ranges[1][0], tick)
        svg.extend([f'<line x1="658" y1="{y:.1f}" x2="665" y2="{y:.1f}" stroke="{INK}"/>', label(651, y + 5, f"{tick:g}", size=15, anchor="end")])

    # Compatibility intervals first so open posterior means remain legible.
    for position, index in enumerate(missing):
        mean = means[position]
        low, high = intervals[position]
        clipped_x_low = max(x_ranges[0][0], low)
        clipped_x_high = min(x_ranges[0][1], high)
        clipped_y_low = max(y_ranges[1][0], low)
        clipped_y_high = min(y_ranges[1][1], high)
        x_low, y = map_xy(0, clipped_x_low, kcal[index])
        x_high, _ = map_xy(0, clipped_x_high, kcal[index])
        x, y_low = map_xy(1, log_mass[index], clipped_y_low)
        _, y_high = map_xy(1, log_mass[index], clipped_y_high)
        svg.extend([
            f'<line x1="{x_low:.1f}" y1="{y:.1f}" x2="{x_high:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.5"/>',
            f'<line x1="{x:.1f}" y1="{y_high:.1f}" x2="{x:.1f}" y2="{y_low:.1f}" stroke="{INK}" stroke-width="1.5"/>',
        ])

    for index, brain_value in enumerate(brain):
        if brain_value is None:
            continue
        x, y = map_xy(0, brain_value, kcal[index])
        x2, y2 = map_xy(1, log_mass[index], brain_value)
        svg.extend([
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#6670ee" fill-opacity="0.86"/>',
            f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="5" fill="#6670ee" fill-opacity="0.86"/>',
        ])
    for position, index in enumerate(missing):
        x, y = map_xy(0, means[position], kcal[index])
        x2, y2 = map_xy(1, log_mass[index], means[position])
        svg.extend([
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#fff" stroke="{INK}" stroke-width="1.7"/>',
            f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="5.5" fill="#fff" stroke="{INK}" stroke-width="1.7"/>',
        ])

    svg.extend([
        label(330, 598, "新皮层百分比（标准化）", size=19, anchor="middle", weight=600),
        label(905, 598, "体重对数（标准化）", size=19, anchor="middle", weight=600),
        label(28, 287, "乳汁能量（标准化）", size=19, anchor="middle", weight=600, rotate=-90),
        label(603, 287, "新皮层百分比（标准化）", size=19, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    output.write_text("\n".join(svg), encoding="utf-8")


def figure_15_5() -> None:
    """Use the exact m15.3 summaries printed by code 15.18."""
    means = [-0.56, -0.69, -0.68, -0.25, 0.48, -0.16, 0.19, 0.28, 0.52, -0.46, -0.27, 0.17]
    lows = [-1.95, -2.10, -2.10, -1.61, -0.93, -1.50, -1.08, -1.06, -0.93, -1.87, -1.61, -1.21]
    highs = [0.95, 0.79, 0.84, 1.15, 1.82, 1.16, 1.58, 1.62, 1.84, 0.93, 1.09, 1.49]
    imputation_figure(
        OUT4,
        "15.5",
        means,
        list(zip(lows, highs)),
        "左图是乳汁能量与新皮层比例，右图是体重对数与新皮层比例；蓝色实心点为观测值，黑色空心点与线段为插补均值及百分之八十九相容区间。",
    )


def figure_15_6() -> None:
    """Approximate m15.5 with its printed means and conditional Gaussian update."""
    kcal, log_mass, brain = milk_standardized()
    missing = [index for index, value in enumerate(brain) if value is None]
    a, b_mass, b_brain, sigma, rho = 0.03, -0.65, 0.58, 0.84, 0.60
    prior_sd = math.sqrt(1 - rho**2)
    means: list[float] = []
    intervals: list[tuple[float, float]] = []
    for index in missing:
        prior_mean = rho * log_mass[index]
        variance = 1 / (1 / prior_sd**2 + b_brain**2 / sigma**2)
        mean = variance * (
            prior_mean / prior_sd**2
            + b_brain * (kcal[index] - a - b_mass * log_mass[index]) / sigma**2
        )
        half_width = 1.598 * math.sqrt(variance)
        means.append(mean)
        intervals.append((mean - half_width, mean + half_width))
    imputation_figure(
        OUT5,
        "15.6",
        means,
        intervals,
        "左图是乳汁能量与新皮层比例，右图是体重对数与新皮层比例；双变量模型使插补值保留两个预测变量之间的正相关。",
    )


def figure_15_7() -> None:
    """Plot every observed and missing case in Moralizing_gods."""
    width, height = 1200, 620
    plot = (105.0, 70.0, 1145.0, 505.0)
    x_range, y_range = (-10250.0, 2350.0), (1.15, 8.55)
    with MORALIZING_GODS_DATA.open(encoding="utf-8", newline="") as handle:
        data = list(csv.DictReader(handle, delimiter=";"))

    x0, y0, x1, y1 = plot

    def xy(year: float, population: float) -> tuple[float, float]:
        return (
            x0 + (year - x_range[0]) / (x_range[1] - x_range[0]) * (x1 - x0),
            y1 - (population - y_range[0]) / (y_range[1] - y_range[0]) * (y1 - y0),
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 15.7：道德化神灵历史数据中的缺失模式</title>',
        '<desc>横轴是公元纪年，纵轴是人口规模的对数；蓝色实心点表示已知存在道德化神灵，蓝色空心点表示已知不存在，黑色叉号表示相关信仰资料缺失。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="1.5"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="1.5"/>',
    ]
    for tick in [-10000, -8000, -6000, -4000, -2000, 0, 2000]:
        x, _ = xy(float(tick), y_range[0])
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1 + 7}" stroke="{INK}"/>',
            label(x, y1 + 32, str(tick), size=16, anchor="middle"),
        ])
    for tick in [2, 3, 4, 5, 6, 7, 8]:
        _, y = xy(x_range[0], float(tick))
        svg.extend([
            f'<line x1="{x0 - 7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
            label(x0 - 14, y + 6, str(tick), size=16, anchor="end"),
        ])

    # Missing cases first; observed symbols remain visible where points overlap.
    for row in data:
        if row["moralizing_gods"] != "NA":
            continue
        x, y = xy(float(row["year"]), float(row["population"]))
        svg.extend([
            f'<line x1="{x - 4:.1f}" y1="{y - 4:.1f}" x2="{x + 4:.1f}" y2="{y + 4:.1f}" stroke="{INK}" stroke-width="1.35"/>',
            f'<line x1="{x - 4:.1f}" y1="{y + 4:.1f}" x2="{x + 4:.1f}" y2="{y - 4:.1f}" stroke="{INK}" stroke-width="1.35"/>',
        ])
    for row in data:
        value = row["moralizing_gods"]
        if value == "NA":
            continue
        x, y = xy(float(row["year"]), float(row["population"]))
        if value == "1":
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#6670ee" fill-opacity="0.82"/>')
        else:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.3" fill="#fff" stroke="#6670ee" stroke-width="1.8"/>')

    legend_x, legend_y = 185.0, 92.0
    svg.extend([
        f'<circle cx="{legend_x}" cy="{legend_y}" r="4.5" fill="#6670ee"/>',
        label(legend_x + 16, legend_y + 6, "存在道德化神灵", size=17),
        f'<circle cx="{legend_x}" cy="{legend_y + 27}" r="4.5" fill="#fff" stroke="#6670ee" stroke-width="1.8"/>',
        label(legend_x + 16, legend_y + 33, "不存在道德化神灵", size=17),
        f'<line x1="{legend_x - 4}" y1="{legend_y + 50}" x2="{legend_x + 4}" y2="{legend_y + 58}" stroke="{INK}" stroke-width="1.5"/>',
        f'<line x1="{legend_x - 4}" y1="{legend_y + 58}" x2="{legend_x + 4}" y2="{legend_y + 50}" stroke="{INK}" stroke-width="1.5"/>',
        label(legend_x + 16, legend_y + 60, "道德化神灵未知", size=17),
        label((x0 + x1) / 2, 592, "时间（年份）", size=20, anchor="middle", weight=600),
        label(30, (y0 + y1) / 2, "人口规模", size=20, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT6.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    figure_15_1()
    figure_15_2()
    figure_15_3()
    figure_15_5()
    figure_15_6()
    figure_15_7()
    print(OUT1)
    print(OUT2)
    print(OUT3)
    print(OUT4)
    print(OUT5)
    print(OUT6)


if __name__ == "__main__":
    main()
