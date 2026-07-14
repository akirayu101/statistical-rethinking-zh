#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 15."""

from __future__ import annotations

import math
from pathlib import Path

from generate_chapter5_waffle_divorce import rows


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-15-measurement-error.svg"
OUT2 = ROOT / "translations" / "zh" / "media" / "chapter-15-divorce-shrinkage.svg"
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


def main() -> None:
    figure_15_1()
    figure_15_2()
    print(OUT1)
    print(OUT2)


if __name__ == "__main__":
    main()
