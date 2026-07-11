#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Figures 4.7 through 4.10."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "translations" / "zh" / "media"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def height_weight_data() -> list[tuple[float, float]]:
    rng = random.Random(4606)
    points: list[tuple[float, float]] = []
    while len(points) < 352:
        weight = rng.gauss(45, 8)
        if 31 <= weight <= 63:
            height = 154.6 + 0.90 * (weight - 45) + rng.gauss(0, 5.07)
            if 135 <= height <= 181:
                points.append((weight, height))
    return points


def regression_samples(
    points: list[tuple[float, float]], rng: random.Random
) -> tuple[float, list[tuple[float, float]]]:
    xbar = sum(x for x, _ in points) / len(points)
    ybar = sum(y for _, y in points) / len(points)
    sxx = sum((x - xbar) ** 2 for x, _ in points)
    slope = sum((x - xbar) * (y - ybar) for x, y in points) / sxx
    residuals = [y - (ybar + slope * (x - xbar)) for x, y in points]
    sigma = math.sqrt(sum(value * value for value in residuals) / (len(points) - 2))
    sd_a = sigma / math.sqrt(len(points))
    sd_b = sigma / math.sqrt(sxx)
    samples = [
        (rng.gauss(ybar, sd_a), rng.gauss(slope, sd_b)) for _ in range(20)
    ]
    return xbar, samples


def generate_figure_47(points: list[tuple[float, float]]) -> None:
    width, height = 1200, 1030
    panel_w, panel_h = 470, 350
    lefts, tops = [125, 665], [75, 535]
    xmin, xmax, ymin, ymax = 30.0, 63.0, 134.0, 181.0
    counts = [10, 50, 150, 352]
    rng = random.Random(4707)

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>随样本量增加而收紧的回归线后验</title>",
        "  <desc>四个面板分别使用十、五十、一百五十和三百五十二个个体；每个面板显示二十条后验回归线。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        "  <defs>",
    ]
    for index in range(4):
        left = lefts[index % 2]
        top = tops[index // 2]
        body.append(
            f'    <clipPath id="panel-clip-{index}"><rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}"/></clipPath>'
        )
    body.append("  </defs>")

    for index, count in enumerate(counts):
        left = lefts[index % 2]
        top = tops[index // 2]

        def px(value: float) -> float:
            return left + (value - xmin) / (xmax - xmin) * panel_w

        def py(value: float) -> float:
            return top + panel_h - (value - ymin) / (ymax - ymin) * panel_h

        subset = points[:count]
        xbar, lines = regression_samples(subset, rng)
        body.extend(
            [
                f'  <text x="{left + panel_w / 2}" y="{top - 25}" text-anchor="middle" font-family="{FONT}" font-size="24" font-weight="700" fill="#30332e">N = {count}</text>',
                f'  <rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.6"/>',
            ]
        )
        for intercept, slope in lines:
            y1 = intercept + slope * (xmin - xbar)
            y2 = intercept + slope * (xmax - xbar)
            body.append(
                f'  <line x1="{fmt(px(xmin))}" y1="{fmt(py(y1))}" x2="{fmt(px(xmax))}" y2="{fmt(py(y2))}" stroke="#1f211d" stroke-width="1.6" opacity="0.35" clip-path="url(#panel-clip-{index})"/>'
            )
        for weight, stature in subset:
            body.append(
                f'  <circle cx="{fmt(px(weight))}" cy="{fmt(py(stature))}" r="3.6" fill="#ffffff" stroke="#5669ef" stroke-width="1.25" opacity="0.88" clip-path="url(#panel-clip-{index})"/>'
            )
        for tick in [30, 40, 50, 60]:
            x = px(tick)
            body.extend(
                [
                    f'  <line x1="{fmt(x)}" y1="{top + panel_h}" x2="{fmt(x)}" y2="{top + panel_h + 7}" stroke="#333630"/>',
                    f'  <text x="{fmt(x)}" y="{top + panel_h + 27}" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
                ]
            )
        for tick in [140, 150, 160, 170, 180]:
            y = py(tick)
            body.extend(
                [
                    f'  <line x1="{left - 7}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#333630"/>',
                    f'  <text x="{left - 14}" y="{fmt(y + 5)}" text-anchor="end" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
                ]
            )
        body.extend(
            [
                f'  <text x="{left + panel_w / 2}" y="{top + panel_h + 56}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">体重（千克）</text>',
                f'  <text x="{left - 75}" y="{top + panel_h / 2}" transform="rotate(-90 {left - 75} {top + panel_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">身高（厘米）</text>',
            ]
        )

    body.extend(
        [
            f'  <text x="{width / 2}" y="1002" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#656963">每个面板绘制 20 条后验回归线；数据越多，回归关系越集中</text>',
            "</svg>",
            "",
        ]
    )
    out = MEDIA / "chapter-04-regression-line-clouds.svg"
    out.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {out}")


def generate_figure_48() -> None:
    width, height = 900, 540
    left, top, plot_w, plot_h = 125, 55, 660, 345
    xmin, xmax, ymin, ymax = 157.8, 160.6, 0.0, 1.25
    mean, sd = 159.13, 0.34

    def px(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_w

    def py(value: float) -> float:
        return top + plot_h - (value - ymin) / (ymax - ymin) * plot_h

    coords = []
    for index in range(241):
        x = xmin + (xmax - xmin) * index / 240
        density = math.exp(-0.5 * ((x - mean) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))
        coords.append(f"{fmt(px(x))},{fmt(py(density))}")

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>体重五十千克时平均身高的后验分布</title>",
        "  <desc>均值约一百五十九点一厘米的钟形密度曲线，表示体重五十千克时不同平均身高值的相对可信程度。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#ffffff" stroke="#333630" stroke-width="1.6"/>',
        f'  <polyline points="{" ".join(coords)}" fill="none" stroke="#5669ef" stroke-width="4" stroke-linejoin="round"/>',
    ]
    for tick in [158.0, 158.5, 159.0, 159.5, 160.0, 160.5]:
        x = px(tick)
        body.extend(
            [
                f'  <line x1="{fmt(x)}" y1="{top + plot_h}" x2="{fmt(x)}" y2="{top + plot_h + 8}" stroke="#333630"/>',
                f'  <text x="{fmt(x)}" y="{top + plot_h + 31}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{tick:.1f}</text>',
            ]
        )
    for tick in [0.0, 0.4, 0.8, 1.2]:
        y = py(tick)
        body.extend(
            [
                f'  <line x1="{left - 8}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#333630"/>',
                f'  <text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="17" fill="#30332e">{tick:.1f}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{left + plot_w / 2}" y="{top + plot_h + 76}" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">μ｜体重 = 50 千克</text>',
            f'  <text x="38" y="{top + plot_h / 2}" transform="rotate(-90 38 {top + plot_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">密度</text>',
            f'  <text x="{width / 2}" y="520" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">曲线表示不同平均身高值的相对可信程度</text>',
            "</svg>",
            "",
        ]
    )
    out = MEDIA / "chapter-04-mean-height-density.svg"
    out.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {out}")


def generate_figure_49(points: list[tuple[float, float]]) -> None:
    width, height = 1200, 650
    panel_w, panel_h = 440, 430
    lefts, top = [120, 680], 55
    xmin, xmax, ymin, ymax = 25.0, 70.0, 134.0, 181.0
    xbar = sum(x for x, _ in points) / len(points)
    ybar = sum(y for _, y in points) / len(points)
    sxx = sum((x - xbar) ** 2 for x, _ in points)
    slope = sum((x - xbar) * (y - ybar) for x, y in points) / sxx
    residuals = [y - (ybar + slope * (x - xbar)) for x, y in points]
    sigma = math.sqrt(sum(value * value for value in residuals) / (len(points) - 2))
    sd_a = sigma / math.sqrt(len(points))
    sd_b = sigma / math.sqrt(sxx)
    weights = list(range(25, 71))
    rng = random.Random(4909)

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>平均身高的后验分布与百分之八十九相容区间</title>",
        "  <desc>左图在每个体重值绘制一百个平均身高后验样本；右图在原始散点上叠加后验均值线与百分之八十九相容区间。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        "  <defs>",
    ]
    for index, left in enumerate(lefts):
        body.append(
            f'    <clipPath id="mean-panel-clip-{index}"><rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}"/></clipPath>'
        )
    body.append("  </defs>")

    def px(value: float, left: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * panel_w

    def py(value: float) -> float:
        return top + panel_h - (value - ymin) / (ymax - ymin) * panel_h

    # Left: the first 100 posterior values of mu at each weight.
    left = lefts[0]
    body.append(
        f'  <rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.6"/>'
    )
    for weight in weights:
        for _ in range(100):
            intercept = rng.gauss(ybar, sd_a)
            draw_slope = rng.gauss(slope, sd_b)
            mu = intercept + draw_slope * (weight - xbar)
            body.append(
                f'  <circle cx="{fmt(px(weight, left))}" cy="{fmt(py(mu))}" r="2.05" fill="#5669ef" opacity="0.17" clip-path="url(#mean-panel-clip-0)"/>'
            )

    # Right: raw data, posterior mean line, and 89% compatibility band.
    left = lefts[1]
    body.append(
        f'  <rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#ffffff" stroke="#333630" stroke-width="1.6"/>'
    )
    upper: list[str] = []
    lower: list[str] = []
    for weight in weights:
        mean = ybar + slope * (weight - xbar)
        sd_mu = math.sqrt(sd_a**2 + (weight - xbar) ** 2 * sd_b**2)
        upper.append(f"{fmt(px(weight, left))},{fmt(py(mean + 1.60 * sd_mu))}")
        lower.append(f"{fmt(px(weight, left))},{fmt(py(mean - 1.60 * sd_mu))}")
    polygon = " ".join(upper + list(reversed(lower)))
    body.append(
        f'  <polygon points="{polygon}" fill="#b9bdc6" opacity="0.75" clip-path="url(#mean-panel-clip-1)"/>'
    )
    for weight, stature in points:
        body.append(
            f'  <circle cx="{fmt(px(weight, left))}" cy="{fmt(py(stature))}" r="3.2" fill="#ffffff" stroke="#5669ef" stroke-width="1.15" opacity="0.62" clip-path="url(#mean-panel-clip-1)"/>'
        )
    mean_y1 = ybar + slope * (xmin - xbar)
    mean_y2 = ybar + slope * (xmax - xbar)
    body.append(
        f'  <line x1="{fmt(px(xmin, left))}" y1="{fmt(py(mean_y1))}" x2="{fmt(px(xmax, left))}" y2="{fmt(py(mean_y2))}" stroke="#1f211d" stroke-width="3" clip-path="url(#mean-panel-clip-1)"/>'
    )

    for index, left in enumerate(lefts):
        for tick in [30, 40, 50, 60, 70]:
            x = px(tick, left)
            body.extend(
                [
                    f'  <line x1="{fmt(x)}" y1="{top + panel_h}" x2="{fmt(x)}" y2="{top + panel_h + 8}" stroke="#333630"/>',
                    f'  <text x="{fmt(x)}" y="{top + panel_h + 31}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
                ]
            )
        for tick in [140, 150, 160, 170, 180]:
            y = py(tick)
            body.extend(
                [
                    f'  <line x1="{left - 8}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#333630"/>',
                    f'  <text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
                ]
            )
        body.extend(
            [
                f'  <text x="{left + panel_w / 2}" y="{top + panel_h + 76}" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">体重（千克）</text>',
                f'  <text x="{left - 76}" y="{top + panel_h / 2}" transform="rotate(-90 {left - 76} {top + panel_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">身高（厘米）</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{lefts[0] + panel_w / 2}" y="615" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">每个体重值的前 100 个 μ 后验样本</text>',
            f'  <text x="{lefts[1] + panel_w / 2}" y="615" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">黑线为均值；灰带为 89% 相容区间</text>',
            "</svg>",
            "",
        ]
    )
    out = MEDIA / "chapter-04-mean-height-interval.svg"
    out.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {out}")


def generate_figure_410(points: list[tuple[float, float]]) -> None:
    width, height = 900, 650
    left, top, plot_w, plot_h = 125, 55, 660, 465
    xmin, xmax, ymin, ymax = 30.0, 63.0, 134.0, 181.0
    xbar = sum(x for x, _ in points) / len(points)
    ybar = sum(y for _, y in points) / len(points)
    sxx = sum((x - xbar) ** 2 for x, _ in points)
    slope = sum((x - xbar) * (y - ybar) for x, y in points) / sxx
    residuals = [y - (ybar + slope * (x - xbar)) for x, y in points]
    sigma = math.sqrt(sum(value * value for value in residuals) / (len(points) - 2))
    sd_a = sigma / math.sqrt(len(points))
    sd_b = sigma / math.sqrt(sxx)
    weights = [xmin + (xmax - xmin) * index / 100 for index in range(101)]

    def px(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_w

    def py(value: float) -> float:
        return top + plot_h - (value - ymin) / (ymax - ymin) * plot_h

    def interval_polygon(include_observation_noise: bool) -> str:
        upper: list[str] = []
        lower: list[str] = []
        for weight in weights:
            mean = ybar + slope * (weight - xbar)
            variance = sd_a**2 + (weight - xbar) ** 2 * sd_b**2
            if include_observation_noise:
                variance += sigma**2
            half_width = 1.60 * math.sqrt(variance)
            upper.append(f"{fmt(px(weight))},{fmt(py(mean + half_width))}")
            lower.append(f"{fmt(px(weight))},{fmt(py(mean - half_width))}")
        return " ".join(upper + list(reversed(lower)))

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>身高的百分之八十九后验预测区间</title>",
        "  <desc>身高体重散点图叠加平均身高线、均值的窄相容区间，以及实际身高的宽后验预测区间。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <clipPath id="prediction-clip"><rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}"/></clipPath>',
        f'  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#ffffff" stroke="#333630" stroke-width="2"/>',
        f'  <polygon points="{interval_polygon(True)}" fill="#d9dce2" opacity="0.92" clip-path="url(#prediction-clip)"/>',
        f'  <polygon points="{interval_polygon(False)}" fill="#aeb4c0" opacity="0.95" clip-path="url(#prediction-clip)"/>',
    ]
    for weight, stature in points:
        body.append(
            f'  <circle cx="{fmt(px(weight))}" cy="{fmt(py(stature))}" r="3.4" fill="#ffffff" stroke="#5669ef" stroke-width="1.25" opacity="0.67" clip-path="url(#prediction-clip)"/>'
        )
    y1 = ybar + slope * (xmin - xbar)
    y2 = ybar + slope * (xmax - xbar)
    body.append(
        f'  <line x1="{fmt(px(xmin))}" y1="{fmt(py(y1))}" x2="{fmt(px(xmax))}" y2="{fmt(py(y2))}" stroke="#1f211d" stroke-width="3" clip-path="url(#prediction-clip)"/>'
    )
    for tick in [30, 35, 40, 45, 50, 55, 60]:
        x = px(tick)
        body.extend(
            [
                f'  <line x1="{fmt(x)}" y1="{top + plot_h}" x2="{fmt(x)}" y2="{top + plot_h + 8}" stroke="#333630"/>',
                f'  <text x="{fmt(x)}" y="{top + plot_h + 31}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
            ]
        )
    for tick in [140, 150, 160, 170, 180]:
        y = py(tick)
        body.extend(
            [
                f'  <line x1="{left - 8}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#333630"/>',
                f'  <text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{left + plot_w / 2}" y="{top + plot_h + 76}" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">体重（千克）</text>',
            f'  <text x="38" y="{top + plot_h / 2}" transform="rotate(-90 38 {top + plot_h / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">身高（厘米）</text>',
            f'  <text x="{width / 2}" y="632" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">深灰：μ 的 89% 区间；浅灰：实际身高的 89% 后验预测区间</text>',
            "</svg>",
            "",
        ]
    )
    out = MEDIA / "chapter-04-height-prediction-interval.svg"
    out.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {out}")


def main() -> int:
    MEDIA.mkdir(parents=True, exist_ok=True)
    points = height_weight_data()
    generate_figure_47(points)
    generate_figure_48()
    generate_figure_49(points)
    generate_figure_410(points)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
