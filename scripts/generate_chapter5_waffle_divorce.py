#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Figures 5.1 and 5.2."""

from __future__ import annotations

import csv
import io
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "translations" / "zh" / "media"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"
DATA = """Loc,Population,MedianAgeMarriage,Marriage,Divorce,WaffleHouses,South
AL,4.78,25.3,20.2,12.7,128,1
AK,0.71,25.2,26.0,12.5,0,0
AZ,6.33,25.8,20.3,10.8,18,0
AR,2.92,24.3,26.4,13.5,41,1
CA,37.25,26.8,19.1,8.0,0,0
CO,5.03,25.7,23.5,11.6,11,0
CT,3.57,27.6,17.1,6.7,0,0
DE,0.90,26.6,23.1,8.9,3,0
DC,0.60,29.7,17.7,6.3,0,0
FL,18.80,26.4,17.0,8.5,133,1
GA,9.69,25.9,22.1,11.5,381,1
HI,1.36,26.9,24.9,8.3,0,0
ID,1.57,23.2,25.8,7.7,0,0
IL,12.83,27.0,17.9,8.0,2,0
IN,6.48,25.7,19.8,11.0,17,0
IA,3.05,25.4,21.5,10.2,0,0
KS,2.85,25.0,22.1,10.6,6,0
KY,4.34,24.8,22.2,12.6,64,1
LA,4.53,25.9,20.6,11.0,66,1
ME,1.33,26.4,13.5,13.0,0,0
MD,5.77,27.3,18.3,8.8,11,0
MA,6.55,28.5,15.8,7.8,0,0
MI,9.88,26.4,16.5,9.2,0,0
MN,5.30,26.3,15.3,7.4,0,0
MS,2.97,25.8,19.3,11.1,72,1
MO,5.99,25.6,18.6,9.5,39,1
MT,0.99,25.7,18.5,9.1,0,0
NE,1.83,25.4,19.6,8.8,0,0
NH,1.32,26.8,16.7,10.1,0,0
NJ,8.79,27.7,14.8,6.1,0,0
NM,2.06,25.8,20.4,10.2,2,0
NY,19.38,28.4,16.8,6.6,0,0
NC,9.54,25.7,20.4,9.9,142,1
ND,0.67,25.3,26.7,8.0,0,0
OH,11.54,26.3,16.9,9.5,64,0
OK,3.75,24.4,23.8,12.8,16,0
OR,3.83,26.0,18.9,10.4,0,0
PA,12.70,27.1,15.5,7.7,11,0
RI,1.05,28.2,15.0,9.4,0,0
SC,4.63,26.4,18.1,8.1,144,1
SD,0.81,25.6,20.1,10.9,0,0
TN,6.35,25.2,19.4,11.4,103,1
TX,25.15,25.2,21.5,10.0,99,1
UT,2.76,23.3,29.6,10.2,0,0
VT,0.63,26.9,16.4,9.6,0,0
VA,8.00,26.4,20.5,8.9,40,1
WA,6.72,25.9,21.4,10.0,0,0
WV,1.85,25.0,22.2,10.9,4,1
WI,5.69,26.3,17.2,8.3,0,0
WY,0.56,24.2,30.7,10.3,0,0
"""


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def rows() -> list[dict[str, float | str]]:
    result: list[dict[str, float | str]] = []
    for row in csv.DictReader(io.StringIO(DATA)):
        result.append(
            {
                "loc": row["Loc"],
                "population": float(row["Population"]),
                "age": float(row["MedianAgeMarriage"]),
                "marriage": float(row["Marriage"]),
                "divorce": float(row["Divorce"]),
                "waffles": float(row["WaffleHouses"]),
                "south": float(row["South"]),
            }
        )
    return result


def fit_line(xs: list[float], ys: list[float]) -> tuple[float, float, float, float, float]:
    count = len(xs)
    x_mean = sum(xs) / count
    y_mean = sum(ys) / count
    sxx = sum((x - x_mean) ** 2 for x in xs)
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / sxx
    intercept = y_mean - slope * x_mean
    residual_sd = math.sqrt(
        sum((y - intercept - slope * x) ** 2 for x, y in zip(xs, ys)) / (count - 2)
    )
    return intercept, slope, residual_sd, x_mean, sxx


def regression_band(
    xs: list[float], ys: list[float], grid: list[float]
) -> tuple[list[float], list[float], list[float]]:
    intercept, slope, residual_sd, x_mean, sxx = fit_line(xs, ys)
    critical = 1.62  # close to the two-sided 89% t interval for 48 degrees of freedom
    means = [intercept + slope * x for x in grid]
    half = [
        critical * residual_sd * math.sqrt(1 / len(xs) + (x - x_mean) ** 2 / sxx)
        for x in grid
    ]
    return means, [m - h for m, h in zip(means, half)], [m + h for m, h in zip(means, half)]


def point_string(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def plot_panel(
    data: list[dict[str, float | str]],
    *,
    x_key: str,
    x_range: tuple[float, float],
    x_ticks: list[float],
    x_label: str,
    x: float,
    y: float,
    width: float,
    height: float,
    color_south: bool = False,
    labels: set[str] | None = None,
) -> list[str]:
    labels = labels or set()
    y_min, y_max = 5.5, 14.5

    def px(value: float) -> float:
        return x + (value - x_range[0]) / (x_range[1] - x_range[0]) * width

    def py(value: float) -> float:
        return y + height - (value - y_min) / (y_max - y_min) * height

    xs = [float(row[x_key]) for row in data]
    ys = [float(row["divorce"]) for row in data]
    grid = [x_range[0] + (x_range[1] - x_range[0]) * index / 160 for index in range(161)]
    means, lower, upper = regression_band(xs, ys, grid)
    upper_points = [(px(value), py(bound)) for value, bound in zip(grid, upper)]
    lower_points = [(px(value), py(bound)) for value, bound in zip(grid, lower)]
    body = [
        f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
        f'  <polygon points="{point_string(upper_points + list(reversed(lower_points)))}" fill="#cfd2d5" opacity="0.8"/>',
        f'  <polyline points="{point_string([(px(value), py(mean)) for value, mean in zip(grid, means)])}" fill="none" stroke="#242724" stroke-width="3"/>',
    ]
    for row in data:
        loc = str(row["loc"])
        color = "#6670ee" if color_south and row["south"] else "#ffffff"
        stroke = "#6670ee" if color_south and row["south"] else "#343732"
        body.append(
            f'  <circle cx="{fmt(px(float(row[x_key])))}" cy="{fmt(py(float(row["divorce"])))}" r="5.2" fill="{color}" stroke="{stroke}" stroke-width="2"/>'
        )
        if loc in labels:
            dx = -9 if loc == "SC" else 9
            anchor = "end" if dx < 0 else "start"
            body.append(
                f'  <text x="{fmt(px(float(row[x_key])) + dx)}" y="{fmt(py(float(row["divorce"])) - 8)}" text-anchor="{anchor}" font-family="{FONT}" font-size="17" font-weight="700" fill="#30332e">{loc}</text>'
            )
    for tick in x_ticks:
        tx = px(tick)
        body.extend(
            [
                f'  <line x1="{fmt(tx)}" y1="{y + height}" x2="{fmt(tx)}" y2="{y + height + 8}" stroke="#343732"/>',
                f'  <text x="{fmt(tx)}" y="{y + height + 31}" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">{fmt(tick)}</text>',
            ]
        )
    for tick in [6, 8, 10, 12, 14]:
        ty = py(tick)
        body.extend(
            [
                f'  <line x1="{x - 8}" y1="{fmt(ty)}" x2="{x}" y2="{fmt(ty)}" stroke="#343732"/>',
                f'  <text x="{x - 14}" y="{fmt(ty + 6)}" text-anchor="end" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{fmt(x + width / 2)}" y="{y + height + 67}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">{x_label}</text>',
            f'  <text x="{x - 67}" y="{fmt(y + height / 2)}" transform="rotate(-90 {x - 67} {fmt(y + height / 2)})" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">离婚率</text>',
        ]
    )
    return body


def waffle_figure(data: list[dict[str, float | str]]) -> str:
    enriched = [dict(row, waffle_density=float(row["waffles"]) / float(row["population"])) for row in data]
    width, height = 900, 650
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>华夫饼屋密度与离婚率</title>",
        "  <desc>美国五十州散点图。每百万人华夫饼屋数量越多的州往往离婚率越高；南方州以蓝色表示。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
    ]
    body.extend(
        plot_panel(
            enriched,
            x_key="waffle_density",
            x_range=(-2, 52),
            x_ticks=[0, 10, 20, 30, 40, 50],
            x_label="每百万人拥有的华夫饼屋数量",
            x=125,
            y=55,
            width=690,
            height=470,
            color_south=True,
            labels={"ME", "AR", "OK", "AL", "GA", "SC", "NJ"},
        )
    )
    body.extend(
        [
            f'  <circle cx="265" cy="620" r="5" fill="#6670ee" stroke="#6670ee"/><text x="279" y="626" font-family="{FONT}" font-size="16" fill="#30332e">南方州</text>',
            f'  <circle cx="390" cy="620" r="5" fill="#fff" stroke="#343732" stroke-width="2"/><text x="404" y="626" font-family="{FONT}" font-size="16" fill="#30332e">其他州</text>',
            f'  <rect x="515" y="614" width="34" height="12" fill="#cfd2d5"/><text x="559" y="626" font-family="{FONT}" font-size="16" fill="#30332e">均值的 89% 区间</text>',
            "</svg>",
            "",
        ]
    )
    return "\n".join(body)


def predictors_figure(data: list[dict[str, float | str]]) -> str:
    width, height = 1200, 620
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>离婚率与结婚率及结婚年龄</title>",
        "  <desc>左图显示结婚率越高离婚率往往越高，右图显示结婚年龄中位数越高离婚率往往越低。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
    ]
    body.extend(
        plot_panel(
            data,
            x_key="marriage",
            x_range=(13, 31),
            x_ticks=[13, 20, 30],
            x_label="结婚率",
            x=100,
            y=65,
            width=440,
            height=430,
        )
    )
    body.extend(
        plot_panel(
            data,
            x_key="age",
            x_range=(23, 30),
            x_ticks=[23, 26, 29],
            x_label="结婚年龄中位数",
            x=700,
            y=65,
            width=440,
            height=430,
        )
    )
    body.extend(["</svg>", ""])
    return "\n".join(body)


def prior_lines_figure() -> str:
    width, height = 900, 600
    left, top, plot_width, plot_height = 125, 55, 690, 430

    def px(value: float) -> float:
        return left + (value + 2) / 4 * plot_width

    def py(value: float) -> float:
        return top + plot_height - (value + 2) / 4 * plot_height

    rng = random.Random(10)
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>m5.1 先验隐含的可信回归线</title>",
        "  <desc>五十条从截距和斜率先验模拟出的标准化结婚年龄与标准化离婚率回归线。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
        f'  <rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
        f'  <line x1="{fmt(px(0))}" y1="{top}" x2="{fmt(px(0))}" y2="{top + plot_height}" stroke="#b9bcb8" stroke-width="1"/>',
        f'  <line x1="{left}" y1="{fmt(py(0))}" x2="{left + plot_width}" y2="{fmt(py(0))}" stroke="#b9bcb8" stroke-width="1"/>',
    ]
    for _ in range(50):
        intercept = rng.gauss(0, 0.2)
        slope = rng.gauss(0, 0.5)
        body.append(
            f'  <line x1="{fmt(px(-2))}" y1="{fmt(py(intercept - 2 * slope))}" x2="{fmt(px(2))}" y2="{fmt(py(intercept + 2 * slope))}" stroke="#313431" stroke-width="2" opacity="0.38" clip-path="url(#clip)"/>'
        )
    body.insert(
        6,
        f'  <defs><clipPath id="clip"><rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}"/></clipPath></defs>',
    )
    for tick in [-2, -1, 0, 1, 2]:
        tx, ty = px(tick), py(tick)
        body.extend(
            [
                f'  <line x1="{fmt(tx)}" y1="{top + plot_height}" x2="{fmt(tx)}" y2="{top + plot_height + 8}" stroke="#343732"/>',
                f'  <text x="{fmt(tx)}" y="{top + plot_height + 32}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
                f'  <line x1="{left - 8}" y1="{fmt(ty)}" x2="{left}" y2="{fmt(ty)}" stroke="#343732"/>',
                f'  <text x="{left - 15}" y="{fmt(ty + 6)}" text-anchor="end" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{fmt(left + plot_width / 2)}" y="{top + plot_height + 72}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">结婚年龄中位数（标准化）</text>',
            f'  <text x="45" y="{fmt(top + plot_height / 2)}" transform="rotate(-90 45 {fmt(top + plot_height / 2)})" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">离婚率（标准化）</text>',
            "</svg>",
            "",
        ]
    )
    return "\n".join(body)


def residual_diagnostics_figure(data: list[dict[str, float | str]]) -> str:
    def standardize(values: list[float]) -> list[float]:
        mean = sum(values) / len(values)
        sd = math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))
        return [(value - mean) / sd for value in values]

    ages = standardize([float(row["age"]) for row in data])
    marriages = standardize([float(row["marriage"]) for row in data])
    divorces = standardize([float(row["divorce"]) for row in data])
    a_m_intercept, a_m_slope, *_ = fit_line(ages, marriages)
    m_a_intercept, m_a_slope, *_ = fit_line(marriages, ages)
    marriage_residuals = [m - (a_m_intercept + a_m_slope * a) for a, m in zip(ages, marriages)]
    age_residuals = [a - (m_a_intercept + m_a_slope * m) for a, m in zip(ages, marriages)]

    width, height = 1200, 1000
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>通过残差理解多元回归</title>",
        "  <desc>上排让两个预测变量互相回归并显示残差，下排用两组残差分别预测离婚率。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
    ]

    def add_panel(
        xs: list[float],
        ys: list[float],
        *,
        x: float,
        y: float,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        x_label: str,
        y_label: str,
        residual_segments: bool = False,
        vertical_zero: bool = False,
        labels: set[str] | None = None,
    ) -> None:
        labels = labels or set()
        panel_w, panel_h = 430, 335

        def px(value: float) -> float:
            return x + (value - x_range[0]) / (x_range[1] - x_range[0]) * panel_w

        def py(value: float) -> float:
            return y + panel_h - (value - y_range[0]) / (y_range[1] - y_range[0]) * panel_h

        intercept, slope, *_ = fit_line(xs, ys)
        if residual_segments:
            for xv, yv in zip(xs, ys):
                expected = intercept + slope * xv
                body.append(f'  <line x1="{fmt(px(xv))}" y1="{fmt(py(expected))}" x2="{fmt(px(xv))}" y2="{fmt(py(yv))}" stroke="#9b9e9a" stroke-width="2"/>')
        if vertical_zero:
            body.append(f'  <line x1="{fmt(px(0))}" y1="{y}" x2="{fmt(px(0))}" y2="{y + panel_h}" stroke="#777b76" stroke-width="2" stroke-dasharray="7 7"/>')
        x1, x2 = x_range
        body.extend(
            [
                f'  <rect x="{x}" y="{y}" width="{panel_w}" height="{panel_h}" fill="none" stroke="#343732" stroke-width="1.5"/>',
                f'  <line x1="{fmt(px(x1))}" y1="{fmt(py(intercept + slope * x1))}" x2="{fmt(px(x2))}" y2="{fmt(py(intercept + slope * x2))}" stroke="#242724" stroke-width="3"/>',
            ]
        )
        for row, xv, yv in zip(data, xs, ys):
            body.append(f'  <circle cx="{fmt(px(xv))}" cy="{fmt(py(yv))}" r="4.8" fill="#fff" stroke="#6670ee" stroke-width="2"/>')
            loc = str(row["loc"])
            if loc in labels:
                dx = -8 if loc in {"ME", "ID"} else 8
                anchor = "end" if dx < 0 else "start"
                body.append(f'  <text x="{fmt(px(xv) + dx)}" y="{fmt(py(yv) - 8)}" text-anchor="{anchor}" font-family="{FONT}" font-size="16" font-weight="700" fill="#30332e">{loc}</text>')
        for tick in [-2, -1, 0, 1, 2, 3]:
            if x_range[0] <= tick <= x_range[1]:
                body.append(f'  <text x="{fmt(px(tick))}" y="{y + panel_h + 27}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="#30332e">{tick}</text>')
            if y_range[0] <= tick <= y_range[1]:
                body.append(f'  <text x="{x - 13}" y="{fmt(py(tick) + 5)}" text-anchor="end" font-family="{FONT}" font-size="14" fill="#30332e">{tick}</text>')
        body.extend(
            [
                f'  <text x="{x + panel_w / 2}" y="{y + panel_h + 58}" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="#263f86">{x_label}</text>',
                f'  <text x="{x - 58}" y="{y + panel_h / 2}" transform="rotate(-90 {x - 58} {y + panel_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="#263f86">{y_label}</text>',
            ]
        )

    add_panel(ages, marriages, x=105, y=60, x_range=(-2.2, 3.2), y_range=(-2, 3.1), x_label="结婚年龄（标准化）", y_label="结婚率（标准化）", residual_segments=True, labels={"WY", "ND", "HI", "ME", "DC"})
    add_panel(marriages, ages, x=690, y=60, x_range=(-2, 3.1), y_range=(-2.2, 3.2), x_label="结婚率（标准化）", y_label="结婚年龄（标准化）", residual_segments=True, labels={"DC", "HI", "ID"})
    add_panel(marriage_residuals, divorces, x=105, y=555, x_range=(-1.8, 1.8), y_range=(-2.2, 2.2), x_label="结婚率残差", y_label="离婚率（标准化）", vertical_zero=True, labels={"ME", "WY", "HI", "ND", "DC"})
    add_panel(age_residuals, divorces, x=690, y=555, x_range=(-1.5, 2.2), y_range=(-2.2, 2.2), x_label="结婚年龄残差", y_label="离婚率（标准化）", vertical_zero=True, labels={"DC", "HI", "ID"})
    body.extend(["</svg>", ""])
    return "\n".join(body)


def posterior_predictive_figure(data: list[dict[str, float | str]]) -> str:
    def standardize(values: list[float]) -> list[float]:
        mean = sum(values) / len(values)
        sd = math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))
        return [(value - mean) / sd for value in values]

    ages = standardize([float(row["age"]) for row in data])
    marriages = standardize([float(row["marriage"]) for row in data])
    observed = standardize([float(row["divorce"]) for row in data])
    predicted = [-0.07 * marriage - 0.61 * age for age, marriage in zip(ages, marriages)]
    half_widths = [0.20 + 0.055 * (abs(age) + abs(marriage)) for age, marriage in zip(ages, marriages)]
    width, height = 900, 650
    left, top, plot_w, plot_h = 125, 55, 690, 475
    low, high = -2.5, 2.5

    def px(value: float) -> float:
        return left + (value - low) / (high - low) * plot_w

    def py(value: float) -> float:
        return top + plot_h - (value - low) / (high - low) * plot_h

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>多变量离婚模型的后验预测图</title>",
        "  <desc>横轴是各州观测离婚率，纵轴是后验预测离婚率；蓝色线段表示均值的百分之八十九区间。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
        f'  <line x1="{fmt(px(low))}" y1="{fmt(py(low))}" x2="{fmt(px(high))}" y2="{fmt(py(high))}" stroke="#555852" stroke-width="2.5" stroke-dasharray="8 7"/>',
    ]
    for row, x_value, y_value, half in zip(data, observed, predicted, half_widths):
        body.append(f'  <line x1="{fmt(px(x_value))}" y1="{fmt(py(y_value - half))}" x2="{fmt(px(x_value))}" y2="{fmt(py(y_value + half))}" stroke="#6670ee" stroke-width="2.5" opacity="0.75"/>')
        body.append(f'  <circle cx="{fmt(px(x_value))}" cy="{fmt(py(y_value))}" r="5.2" fill="#6670ee" stroke="#263f86" stroke-width="1.5"/>')
        loc = str(row["loc"])
        if loc in {"ID", "UT", "RI", "ME"}:
            dx = -9 if loc in {"ID", "RI"} else 9
            anchor = "end" if dx < 0 else "start"
            body.append(f'  <text x="{fmt(px(x_value) + dx)}" y="{fmt(py(y_value) - 10)}" text-anchor="{anchor}" font-family="{FONT}" font-size="18" font-weight="700" fill="#30332e">{loc}</text>')
    for tick in [-2, -1, 0, 1, 2]:
        body.extend(
            [
                f'  <text x="{fmt(px(tick))}" y="{top + plot_h + 31}" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
                f'  <text x="{left - 15}" y="{fmt(py(tick) + 6)}" text-anchor="end" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{left + plot_w / 2}" y="{top + plot_h + 72}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">观测离婚率</text>',
            f'  <text x="45" y="{top + plot_h / 2}" transform="rotate(-90 45 {top + plot_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">预测离婚率</text>',
            "</svg>",
            "",
        ]
    )
    return "\n".join(body)


def counterfactual_figures(data: list[dict[str, float | str]]) -> dict[str, str]:
    def standardize(values: list[float]) -> list[float]:
        mean = sum(values) / len(values)
        sd = math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))
        return [(value - mean) / sd for value in values]

    ages = standardize([float(row["age"]) for row in data])
    marriages = standardize([float(row["marriage"]) for row in data])
    _, b_am, *_ = fit_line(ages, marriages)
    b_a, b_m = -0.61, -0.07
    total_a = b_a + b_m * b_am

    def panel(
        *, x: float, y: float, plot_w: float, plot_h: float, slope: float,
        title: str, x_label: str, y_label: str, interval: float,
    ) -> list[str]:
        def px(value: float) -> float:
            return x + (value + 2) / 4 * plot_w

        def py(value: float) -> float:
            return y + plot_h - (value + 2) / 4 * plot_h

        grid = [-2 + 4 * index / 120 for index in range(121)]
        upper = [(px(value), py(slope * value + interval)) for value in grid]
        lower = [(px(value), py(slope * value - interval)) for value in grid]
        body = [
            f'  <text x="{x + plot_w / 2}" y="{y - 22}" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">{title}</text>',
            f'  <rect x="{x}" y="{y}" width="{plot_w}" height="{plot_h}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
            f'  <polygon points="{point_string(upper + list(reversed(lower)))}" fill="#cfd2d5" opacity="0.82"/>',
            f'  <line x1="{fmt(px(-2))}" y1="{fmt(py(-2 * slope))}" x2="{fmt(px(2))}" y2="{fmt(py(2 * slope))}" stroke="#242724" stroke-width="3"/>',
        ]
        for tick in [-2, -1, 0, 1, 2]:
            body.extend([
                f'  <text x="{fmt(px(tick))}" y="{y + plot_h + 29}" text-anchor="middle" font-family="{FONT}" font-size="15" fill="#30332e">{tick}</text>',
                f'  <text x="{x - 13}" y="{fmt(py(tick) + 5)}" text-anchor="end" font-family="{FONT}" font-size="15" fill="#30332e">{tick}</text>',
            ])
        body.extend([
            f'  <text x="{x + plot_w / 2}" y="{y + plot_h + 65}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">{x_label}</text>',
            f'  <text x="{x - 58}" y="{y + plot_h / 2}" transform="rotate(-90 {x - 58} {y + plot_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">{y_label}</text>',
        ])
        return body

    body56 = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650" role="img">',
        "  <title>结婚年龄干预的反事实效应</title>",
        "  <desc>左图显示操纵结婚年龄对离婚率的总因果效应，右图显示操纵结婚年龄对结婚率的效应。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
    ]
    body56.extend(panel(x=105, y=90, plot_w=430, plot_h=420, slope=total_a, title="A 对 D 的总反事实效应", x_label="操纵后的 A", y_label="反事实 D", interval=0.22))
    body56.extend(panel(x=690, y=90, plot_w=430, plot_h=420, slope=b_am, title="反事实效应 A → M", x_label="操纵后的 A", y_label="反事实 M", interval=0.20))
    body56.extend(["</svg>", ""])

    body57 = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650" viewBox="0 0 900 650" role="img">',
        "  <title>结婚率干预对离婚率的反事实效应</title>",
        "  <desc>操纵结婚率对离婚率几乎没有趋势。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
    ]
    body57.extend(panel(x=155, y=90, plot_w=600, plot_h=420, slope=b_m, title="M 对 D 的总反事实效应", x_label="操纵后的 M", y_label="反事实 D", interval=0.24))
    body57.extend(["</svg>", ""])
    return {
        "chapter-05-counterfactual-age.svg": "\n".join(body56),
        "chapter-05-counterfactual-marriage.svg": "\n".join(body57),
    }


def main() -> int:
    data = rows()
    MEDIA.mkdir(parents=True, exist_ok=True)
    outputs = {
        MEDIA / "chapter-05-waffle-divorce.svg": waffle_figure(data),
        MEDIA / "chapter-05-divorce-predictors.svg": predictors_figure(data),
        MEDIA / "chapter-05-prior-regression-lines.svg": prior_lines_figure(),
        MEDIA / "chapter-05-residual-diagnostics.svg": residual_diagnostics_figure(data),
        MEDIA / "chapter-05-posterior-predictive.svg": posterior_predictive_figure(data),
    }
    outputs.update({MEDIA / name: content for name, content in counterfactual_figures(data).items()})
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
        print(f"generated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
