#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Figures 5.1 and 5.2."""

from __future__ import annotations

import csv
import io
import math
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


def main() -> int:
    data = rows()
    MEDIA.mkdir(parents=True, exist_ok=True)
    outputs = {
        MEDIA / "chapter-05-waffle-divorce.svg": waffle_figure(data),
        MEDIA / "chapter-05-divorce-predictors.svg": predictors_figure(data),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
        print(f"generated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
