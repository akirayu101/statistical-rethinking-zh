#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Chapter 10 entropy figures."""
from pathlib import Path
import math
import random


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations/zh/media/chapter-10-pebble-entropy.svg"
OUT2 = ROOT / "translations/zh/media/chapter-10-gaussian-maxent.svg"
OUT3 = ROOT / "translations/zh/media/chapter-10-binomial-candidates.svg"
OUT4 = ROOT / "translations/zh/media/chapter-10-binomial-entropy.svg"
OUT5 = ROOT / "translations/zh/media/chapter-10-link-functions.svg"
OUT6 = ROOT / "translations/zh/media/chapter-10-exponential-family.svg"
OUT7 = ROOT / "translations/zh/media/chapter-10-logit-link.svg"
OUT8 = ROOT / "translations/zh/media/chapter-10-log-link.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
BLUE = "#263f86"
BLUE_SOFT = "#dfe6f8"
GRID = "#d9d5c8"


def esc(text: object) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: float, y: float, value: object, *, size: int = 18, anchor: str = "start",
         weight: int = 400, fill: str = INK, rotate: int | None = None) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}"{transform}>'
        f'{esc(value)}</text>'
    )


def bar_panel(label: str, counts: list[int], ways: int, x: float, y: float) -> list[str]:
    width, height = 500, 250
    left, right, top, bottom = x + 62, x + width - 24, y + 50, y + height - 47
    plot_h = bottom - top
    parts = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="#fff" stroke="{GRID}"/>',
        text(x + 18, y + 31, label, size=24, weight=700, fill=BLUE),
        text(x + width - 18, y + 31, f"{ways:,} 种方式", size=18, anchor="end"),
    ]
    for tick in (0, 5, 10):
        yy = bottom - tick / 10 * plot_h
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(text(left - 12, yy + 6, tick, size=15, anchor="end", fill="#666862"))
    parts.append(text(x + 20, (top + bottom) / 2, "石子数", size=17, anchor="middle", fill=BLUE, rotate=-90))
    step = (right - left) / 5
    bar_w = 26
    for index, count in enumerate(counts, start=1):
        cx = left + (index - .5) * step
        bar_h = count / 10 * plot_h
        yy = bottom - bar_h
        parts.append(f'<rect x="{cx - bar_w / 2:.1f}" y="{yy:.1f}" width="{bar_w}" height="{bar_h:.1f}" rx="4" fill="{BLUE}"/>')
        if count:
            parts.append(text(cx, yy - 8, count, size=16, anchor="middle", weight=700))
        parts.append(text(cx, bottom + 25, index, size=16, anchor="middle"))
    parts.append(text((left + right) / 2, y + height - 10, "桶", size=17, anchor="middle", fill=BLUE))
    return parts


def scatter_panel(x: float, y: float) -> list[str]:
    width, height = 500, 250
    left, right, top, bottom = x + 68, x + width - 25, y + 35, y + height - 55
    xmax, ymax = 1.2, 1.7
    ways = [1, 90, 1260, 37800, 113400]
    entropy = [0.0, 0.6390319, 0.9502705, 1.4708085, 1.6094379]
    labels = list("ABCDE")
    xs = [math.log(value) / 10 for value in ways]
    sx = lambda value: left + value / xmax * (right - left)
    sy = lambda value: bottom - value / ymax * (bottom - top)
    parts = [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="#fff" stroke="{GRID}"/>']
    for tick in (0.0, 0.4, 0.8, 1.2):
        xx = sx(tick)
        parts.append(f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + 6}" stroke="{INK}"/>')
        parts.append(text(xx, bottom + 24, f"{tick:.1f}", size=14, anchor="middle", fill="#666862"))
    for tick in (0.0, 0.5, 1.0, 1.5):
        yy = sy(tick)
        parts.append(f'<line x1="{left - 6}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>')
        parts.append(text(left - 11, yy + 5, f"{tick:.1f}", size=14, anchor="end", fill="#666862"))
    parts.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}"/>',
        text((left + right) / 2, y + height - 10, "每颗石子的 log(方式数)", size=16, anchor="middle", fill=BLUE),
        text(x + 20, (top + bottom) / 2, "熵", size=17, anchor="middle", fill=BLUE, rotate=-90),
    ])
    points = " ".join(f"{sx(px):.1f},{sy(py):.1f}" for px, py in zip(xs, entropy))
    parts.append(f'<polyline points="{points}" fill="none" stroke="#8c8e88" stroke-width="2" stroke-dasharray="7 6"/>')
    offsets = [(10, -10), (0, -13), (0, 23), (-9, 23), (-13, 23)]
    for label, px, py, (dx, dy) in zip(labels, xs, entropy, offsets):
        parts.append(f'<circle cx="{sx(px):.1f}" cy="{sy(py):.1f}" r="6" fill="{BLUE}" stroke="#fff" stroke-width="2"/>')
        parts.append(text(sx(px) + dx, sy(py) + dy, label, size=18, anchor="middle", weight=700))
    return parts


def generalized_normal_density(value: float, beta: float) -> float:
    """Generalized normal density standardized to variance one."""
    alpha = math.sqrt(math.gamma(1 / beta) / math.gamma(3 / beta))
    return beta / (2 * alpha * math.gamma(1 / beta)) * math.exp(-((abs(value) / alpha) ** beta))


def generalized_normal_entropy(beta: float) -> float:
    """Differential entropy of a variance-one generalized normal."""
    alpha = math.sqrt(math.gamma(1 / beta) / math.gamma(3 / beta))
    return math.log(2 * alpha * math.gamma(1 / beta) / beta) + 1 / beta


def figure_10_2() -> None:
    width, height = 1200, 600
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>最大熵与高斯分布</title>',
        '<desc>左图比较方差均为一的高斯分布与三种广义正态分布的概率密度曲线；右图显示形状参数贝塔等于二、曲线呈高斯形状时，广义正态分布的熵达到最大。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]

    left, top, plot_w, plot_h = 90, 55, 470, 430
    sx = lambda value: left + (value + 4.2) / 8.4 * plot_w
    sy = lambda value: top + (0.75 - value) / 0.75 * plot_h
    parts.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fff" stroke="{GRID}"/>')
    for tick in (-4, -2, 0, 2, 4):
        xx = sx(tick)
        parts.extend([f'<line x1="{xx:.1f}" y1="{top + plot_h}" x2="{xx:.1f}" y2="{top + plot_h + 7}" stroke="{INK}"/>', text(xx, top + plot_h + 31, tick, size=16, anchor="middle")])
    for tick in (0.0, 0.2, 0.4, 0.6):
        yy = sy(tick)
        parts.extend([f'<line x1="{left - 7}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>', text(left - 13, yy + 5, f"{tick:.1f}", size=15, anchor="end")])
    parts.extend([
        text(left + plot_w / 2, height - 35, "取值", size=19, anchor="middle", fill=BLUE),
        text(28, top + plot_h / 2, "概率密度", size=19, anchor="middle", fill=BLUE, rotate=-90),
    ])
    styles = [(1.0, "#111", 2.2), (1.5, "#777872", 2.2), (4.0, "#111", 2.2), (2.0, "#6670ee", 4.0)]
    for beta, color, stroke_width in styles:
        points = []
        for index in range(701):
            value = -4.2 + 8.4 * index / 700
            points.append(f"{sx(value):.1f},{sy(generalized_normal_density(value, beta)):.1f}")
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>')
    parts.extend([
        f'<line x1="{left + 22}" y1="{top + 24}" x2="{left + 62}" y2="{top + 24}" stroke="#6670ee" stroke-width="4"/>',
        text(left + 72, top + 30, "高斯分布（β = 2）", size=16, fill=BLUE),
    ])

    left2, top2, plot_w2, plot_h2 = 690, 55, 420, 430
    sx2 = lambda value: left2 + (value - 1) / 3 * plot_w2
    sy2 = lambda value: top2 + (1.425 - value) / (1.425 - 1.345) * plot_h2
    parts.append(f'<rect x="{left2}" y="{top2}" width="{plot_w2}" height="{plot_h2}" fill="#fff" stroke="{GRID}"/>')
    for tick in (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0):
        xx = sx2(tick)
        parts.extend([f'<line x1="{xx:.1f}" y1="{top2 + plot_h2}" x2="{xx:.1f}" y2="{top2 + plot_h2 + 7}" stroke="{INK}"/>', text(xx, top2 + plot_h2 + 31, f"{tick:.1f}", size=15, anchor="middle")])
    for tick in (1.35, 1.37, 1.39, 1.41):
        yy = sy2(tick)
        parts.extend([f'<line x1="{left2 - 7}" y1="{yy:.1f}" x2="{left2}" y2="{yy:.1f}" stroke="{INK}"/>', text(left2 - 13, yy + 5, f"{tick:.2f}", size=15, anchor="end")])
    entropy_points = []
    for index in range(601):
        beta = 1 + 3 * index / 600
        entropy_points.append(f"{sx2(beta):.1f},{sy2(generalized_normal_entropy(beta)):.1f}")
    parts.extend([
        f'<polyline points="{" ".join(entropy_points)}" fill="none" stroke="#6670ee" stroke-width="4"/>',
        f'<line x1="{sx2(2):.1f}" y1="{top2}" x2="{sx2(2):.1f}" y2="{top2 + plot_h2}" stroke="{INK}" stroke-width="2" stroke-dasharray="8 7"/>',
        text(left2 + plot_w2 / 2, height - 35, "形状参数 β", size=19, anchor="middle", fill=BLUE),
        text(628, top2 + plot_h2 / 2, "熵", size=19, anchor="middle", fill=BLUE, rotate=-90),
        text(sx2(2) + 12, sy2(generalized_normal_entropy(2)) - 12, "最大值（β = 2）", size=17, fill=BLUE, weight=700),
        '</svg>',
    ])
    OUT2.write_text("\n".join(parts) + "\n", encoding="utf-8")


def figure_10_3() -> None:
    """Draw the four candidate distributions from Figure 10.3."""
    width, height = 1200, 650
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>期望值相同的四种候选分布</title>',
        '<desc>A 到 D 四种分布都表示两次抽取平均得到一颗蓝色弹珠，但四个结果序列上的概率配置不同。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    candidates = [
        ("A", [1 / 4, 1 / 4, 1 / 4, 1 / 4]),
        ("B", [2 / 6, 1 / 6, 1 / 6, 2 / 6]),
        ("C", [1 / 6, 2 / 6, 2 / 6, 1 / 6]),
        ("D", [1 / 8, 4 / 8, 2 / 8, 1 / 8]),
    ]
    outcomes = ["ww", "bw", "wb", "bb"]
    positions = [(60, 35), (630, 35), (60, 335), (630, 335)]
    for (label, probabilities), (x, y) in zip(candidates, positions):
        panel_w, panel_h = 510, 255
        left, right, top, bottom = x + 72, x + panel_w - 30, y + 50, y + panel_h - 54
        sx = lambda index: left + index * (right - left) / 3
        sy = lambda value: bottom - value / 0.55 * (bottom - top)
        parts.extend([
            f'<rect x="{x}" y="{y}" width="{panel_w}" height="{panel_h}" rx="8" fill="#fff" stroke="{GRID}"/>',
            text(x + 18, y + 34, label, size=26, weight=700, fill=BLUE),
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}"/>',
        ])
        points = " ".join(f"{sx(index):.1f},{sy(value):.1f}" for index, value in enumerate(probabilities))
        parts.append(f'<polyline points="{points}" fill="none" stroke="#737cff" stroke-width="4"/>')
        for index, (outcome, value) in enumerate(zip(outcomes, probabilities)):
            xx, yy = sx(index), sy(value)
            parts.extend([
                f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="7" fill="#737cff" stroke="#fff" stroke-width="2"/>',
                text(xx, bottom + 31, outcome, size=18, anchor="middle"),
                text(xx, yy - 14, f"{value:.3f}".rstrip("0").rstrip("."), size=15, anchor="middle", fill="#666862"),
            ])
    parts.append('</svg>')
    OUT3.write_text("\n".join(parts) + "\n", encoding="utf-8")


def simulated_distribution(rng: random.Random, expected: float = 1.4) -> tuple[list[float], float]:
    """Replicate sim.p from Code 10.9 with a deterministic random generator."""
    x123 = [rng.random() for _ in range(3)]
    x4 = (expected * sum(x123) - x123[1] - x123[2]) / (2 - expected)
    total = sum(x123) + x4
    probabilities = [value / total for value in [*x123, x4]]
    entropy = -sum(value * math.log(value) for value in probabilities)
    return probabilities, entropy


def figure_10_4() -> None:
    """Draw the simulated entropy distribution and four representative candidates."""
    width, height = 1200, 700
    rng = random.Random(104)
    simulations = [simulated_distribution(rng) for _ in range(100000)]
    entropies = [entropy for _, entropy in simulations]
    targets = [max(entropies), 1.0, 0.85, 0.67]
    labels = list("ABCD")
    candidates = [
        min(simulations, key=lambda item, target=target: abs(item[1] - target))
        for target in targets
    ]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>期望值为 1.4 的模拟分布及其熵</title>',
        '<desc>左图显示十万次随机模拟所得熵值的概率密度；右侧 A 到 D 展示熵逐渐降低时概率分布越来越不均匀。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]

    x, y, plot_w, plot_h = 75, 70, 480, 500
    left, right, top, bottom = x + 70, x + plot_w - 25, y + 25, y + plot_h - 60
    xmin, xmax, bins = 0.62, 1.225, 150
    counts = [0.0] * bins
    for value in entropies:
        index = min(bins - 1, max(0, int((value - xmin) / (xmax - xmin) * bins)))
        counts[index] += 1
    smooth = []
    sigma = 3.0
    for index in range(bins):
        numerator = denominator = 0.0
        for offset in range(-10, 11):
            other = index + offset
            if 0 <= other < bins:
                weight = math.exp(-(offset ** 2) / (2 * sigma ** 2))
                numerator += counts[other] * weight
                denominator += weight
        smooth.append(numerator / denominator)
    peak = max(smooth)
    sx = lambda value: left + (value - xmin) / (xmax - xmin) * (right - left)
    sy = lambda value: bottom - value / peak * (bottom - top)
    parts.extend([
        f'<rect x="{x}" y="{y}" width="{plot_w}" height="{plot_h}" rx="8" fill="#fff" stroke="{GRID}"/>',
        text(x + 20, y + 34, "模拟熵值的概率密度", size=22, weight=700, fill=BLUE),
    ])
    for tick in (0.7, 0.8, 0.9, 1.0, 1.1, 1.2):
        xx = sx(tick)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + 7}" stroke="{INK}"/>',
            text(xx, bottom + 29, f"{tick:.1f}", size=15, anchor="middle"),
        ])
    parts.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}"/>',
        text((left + right) / 2, y + plot_h - 12, "熵", size=18, anchor="middle", fill=BLUE),
        text(x + 25, (top + bottom) / 2, "概率密度", size=18, anchor="middle", fill=BLUE, rotate=-90),
    ])
    density_points = []
    for index, value in enumerate(smooth):
        entropy = xmin + (index + 0.5) / bins * (xmax - xmin)
        density_points.append(f"{sx(entropy):.1f},{sy(value):.1f}")
    parts.append(f'<polyline points="{" ".join(density_points)}" fill="none" stroke="#737cff" stroke-width="4"/>')
    for label, (_, entropy) in zip(labels, candidates):
        index = min(bins - 1, max(0, int((entropy - xmin) / (xmax - xmin) * bins)))
        xx, yy = sx(entropy), sy(smooth[index])
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{yy:.1f}" stroke="#8c8e88" stroke-width="2" stroke-dasharray="5 5"/>',
            text(xx, max(top + 22, yy - 12), label, size=22, anchor="middle", weight=700),
        ])

    outcomes = ["ww", "bw", "wb", "bb"]
    positions = [(630, 70), (910, 70), (630, 360), (910, 360)]
    for (label, (probabilities, entropy)), (px, py) in zip(zip(labels, candidates), positions):
        panel_w, panel_h = 245, 235
        pleft, pright, ptop, pbottom = px + 40, px + panel_w - 18, py + 50, py + panel_h - 47
        psx = lambda index: pleft + index * (pright - pleft) / 3
        psy = lambda value: pbottom - value / 0.82 * (pbottom - ptop)
        parts.extend([
            f'<rect x="{px}" y="{py}" width="{panel_w}" height="{panel_h}" rx="8" fill="#fff" stroke="{GRID}"/>',
            text(px + 15, py + 31, label, size=24, weight=700, fill=BLUE),
            text(px + panel_w - 15, py + 30, f"H={entropy:.3f}", size=14, anchor="end", fill="#666862"),
            f'<line x1="{pleft}" y1="{pbottom}" x2="{pright}" y2="{pbottom}" stroke="{INK}"/>',
        ])
        points = " ".join(f"{psx(index):.1f},{psy(value):.1f}" for index, value in enumerate(probabilities))
        parts.append(f'<polyline points="{points}" fill="none" stroke="#737cff" stroke-width="4"/>')
        for index, (outcome, value) in enumerate(zip(outcomes, probabilities)):
            xx, yy = psx(index), psy(value)
            parts.extend([
                f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="6" fill="#737cff" stroke="#fff" stroke-width="2"/>',
                text(xx, pbottom + 27, outcome, size=15, anchor="middle"),
            ])
    parts.append('</svg>')
    OUT4.write_text("\n".join(parts) + "\n", encoding="utf-8")


def figure_10_5() -> None:
    """Draw the bounded-probability motivation for link functions."""
    width, height = 1200, 650
    left, right, top, bottom = 130, 1090, 70, 530
    sx = lambda value: left + value / 2.1 * (right - left)
    sy = lambda value: bottom - value / 1.35 * (bottom - top)
    intercept, slope = 0.34, 0.5
    boundary_x = (1 - intercept) / slope
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>为什么需要 link 函数</title>',
        '<desc>线性预测随 x 增大时会越过概率一的上界；真实概率达到一后只能保持在边界上。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" rx="8" fill="#fff" stroke="{GRID}"/>',
    ]
    for tick in (0.0, 0.5, 1.0, 1.5, 2.0):
        xx = sx(tick)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + 8}" stroke="{INK}"/>',
            text(xx, bottom + 32, f"{tick:.1f}", size=17, anchor="middle"),
        ])
    for tick in (0.0, 0.5, 1.0):
        yy = sy(tick)
        parts.extend([
            f'<line x1="{left - 8}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
            text(left - 16, yy + 6, f"{tick:.1f}", size=17, anchor="end"),
        ])
    parts.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}"/>',
        f'<line x1="{left}" y1="{sy(1):.1f}" x2="{right}" y2="{sy(1):.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="9 8"/>',
        f'<line x1="{left}" y1="{sy(0):.1f}" x2="{right}" y2="{sy(0):.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="9 8"/>',
        text((left + right) / 2, height - 40, "预测变量 x", size=21, anchor="middle", fill=BLUE),
        text(42, (top + bottom) / 2, "概率", size=21, anchor="middle", fill=BLUE, rotate=-90),
        text(right - 12, sy(1) - 13, "概率上界 1", size=18, anchor="end", fill="#666862"),
    ])
    parts.extend([
        f'<line x1="{sx(0):.1f}" y1="{sy(intercept):.1f}" x2="{sx(boundary_x):.1f}" y2="{sy(1):.1f}" stroke="#737cff" stroke-width="5"/>',
        f'<line x1="{sx(boundary_x):.1f}" y1="{sy(1):.1f}" x2="{sx(2.05):.1f}" y2="{sy(intercept+slope*2.05):.1f}" stroke="#737cff" stroke-width="5" stroke-dasharray="13 10"/>',
        f'<line x1="{sx(boundary_x):.1f}" y1="{sy(1):.1f}" x2="{sx(2.05):.1f}" y2="{sy(1):.1f}" stroke="#263f86" stroke-width="6"/>',
        f'<circle cx="{sx(boundary_x):.1f}" cy="{sy(1):.1f}" r="8" fill="#263f86" stroke="#fff" stroke-width="3"/>',
        text(sx(0.35), sy(intercept + slope * 0.35) - 18, "线性模型", size=18, fill=BLUE, weight=700),
        text(sx(1.65), sy(intercept + slope * 1.65) - 16, "越过边界的外推", size=17, anchor="middle", fill="#666862"),
        text(sx(1.72), sy(1) + 34, "受约束的真实趋势", size=17, anchor="middle", fill=BLUE, weight=700),
        '</svg>',
    ])
    OUT5.write_text("\n".join(parts) + "\n", encoding="utf-8")


def distribution_panel(x: float, y: float, formula: str, function_name: str,
                       values: list[float], *, discrete: bool = False) -> list[str]:
    """Build a small labeled density or mass panel for Figure 10.6."""
    width, height = 340, 205
    left, right, top, bottom = x + 28, x + width - 20, y + 45, y + height - 35
    peak = max(values)
    parts = [
        text(x + width / 2, y + 25, formula, size=20, anchor="middle", fill=INK),
        f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="#fff" stroke="{INK}"/>',
    ]
    if discrete:
        step = (right - left) / len(values)
        for index, value in enumerate(values):
            xx = left + (index + 0.5) * step
            yy = bottom - value / peak * (bottom - top - 8)
            parts.append(f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{yy:.1f}" stroke="#737cff" stroke-width="4"/>')
    else:
        points = []
        for index, value in enumerate(values):
            xx = left + index / (len(values) - 1) * (right - left)
            yy = bottom - value / peak * (bottom - top - 8)
            points.append(f"{xx:.1f},{yy:.1f}")
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#737cff" stroke-width="4"/>')
    parts.append(text(x + width / 2, y + height - 7, function_name, size=17, anchor="middle", fill="#666862"))
    return parts


def figure_10_6() -> None:
    """Draw selected exponential-family distributions and generative links."""
    width, height = 1200, 930
    gamma_values = []
    normal_values = []
    exponential_values = []
    for index in range(180):
        value = 8 * index / 179
        gamma_values.append(value ** 2 * math.exp(-value))
        normal_x = -4 + 8 * index / 179
        normal_values.append(math.exp(-0.5 * normal_x ** 2))
        exponential_values.append(math.exp(-0.65 * value))
    poisson_values = [math.exp(-4) * 4 ** k / math.factorial(k) for k in range(11)]
    binomial_values = [math.comb(10, k) * 0.72 ** k * 0.28 ** (10 - k) for k in range(11)]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>指数族分布及其生成关系</title>',
        '<desc>Gamma、正态、指数、Poisson 与二项分布的代表性形状，以及求和、大均值、计数和低概率极限等关系。</desc>',
        '<defs><marker id="arrow10-6" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#a8aaa4"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    arrow = lambda path: f'<path d="{path}" fill="none" stroke="#a8aaa4" stroke-width="4" marker-end="url(#arrow10-6)"/>'
    parts.extend([
        arrow("M 430 185 C 560 75, 650 75, 760 185"),
        text(600, 76, "均值很大", size=18, anchor="middle", fill="#777872"),
        arrow("M 500 425 C 445 390, 425 350, 408 300"),
        text(432, 355, "求和", size=18, anchor="middle", fill="#777872"),
        arrow("M 470 510 C 430 600, 410 650, 372 690"),
        text(435, 610, "计数事件", size=18, anchor="middle", fill="#777872"),
        text(435, 635, "低发生率", size=17, anchor="middle", fill="#777872"),
        arrow("M 730 510 C 770 600, 790 650, 828 690"),
        text(765, 610, "计数事件", size=18, anchor="middle", fill="#777872"),
        arrow("M 790 835 C 660 905, 540 905, 410 835"),
        text(600, 870, "低概率、试验很多", size=18, anchor="middle", fill="#777872"),
    ])
    parts.extend(distribution_panel(70, 115, "y ∼ Gamma(λ, k)", "dgamma", gamma_values))
    parts.extend(distribution_panel(790, 115, "y ∼ Normal(μ, σ)", "dnorm", normal_values))
    parts.extend(distribution_panel(430, 365, "y ∼ Exponential(λ)", "dexp", exponential_values))
    parts.extend(distribution_panel(70, 665, "y ∼ Poisson(λ)", "dpois", poisson_values, discrete=True))
    parts.extend(distribution_panel(790, 665, "y ∼ Binomial(n, p)", "dbinom", binomial_values, discrete=True))
    parts.append('</svg>')
    OUT6.write_text("\n".join(parts) + "\n", encoding="utf-8")


def figure_10_7() -> None:
    """Draw the logit link from a linear predictor to probability."""
    width, height = 1200, 650
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>logit link 把线性模型变换为概率</title>',
        '<desc>左图为无界的对数赔率线性空间，右图为压缩到零与一之间的概率空间。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    panels = [(85, "对数赔率", -4.3, 4.3), (655, "概率", -0.02, 1.02)]
    for left, ylabel, ymin, ymax in panels:
        top, plot_w, plot_h = 65, 455, 455
        right, bottom = left + plot_w, top + plot_h
        sx = lambda value, l=left, r=right: l + (value + 1) / 2 * (r - l)
        sy = lambda value, t=top, b=bottom, lo=ymin, hi=ymax: b - (value - lo) / (hi - lo) * (b - t)
        parts.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fff" stroke="{GRID}"/>')
        for tick in (-1.0, -0.5, 0.0, 0.5, 1.0):
            xx = sx(tick)
            parts.extend([
                f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+7}" stroke="{INK}"/>',
                text(xx, bottom + 29, f"{tick:.1f}", size=15, anchor="middle"),
            ])
        guide_values = list(range(-4, 5))
        for guide in guide_values:
            value = guide if ylabel == "对数赔率" else 1 / (1 + math.exp(-guide))
            yy = sy(value)
            parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#b9bbb5" stroke-width="1.5"/>')
        y_ticks = (-4, -2, 0, 2, 4) if ylabel == "对数赔率" else (0.0, 0.5, 1.0)
        for tick in y_ticks:
            yy = sy(tick)
            parts.extend([
                f'<line x1="{left-7}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
                text(left - 13, yy + 5, f"{tick:.1f}" if ylabel == "概率" else tick, size=15, anchor="end"),
            ])
        points = []
        for index in range(301):
            xvalue = -1 + 2 * index / 300
            linear = 2.3 * xvalue
            yvalue = linear if ylabel == "对数赔率" else 1 / (1 + math.exp(-linear))
            points.append(f"{sx(xvalue):.1f},{sy(yvalue):.1f}")
        parts.extend([
            f'<polyline points="{" ".join(points)}" fill="none" stroke="#737cff" stroke-width="5"/>',
            text((left + right) / 2, height - 58, "预测变量 x", size=19, anchor="middle", fill=BLUE),
            text(left - 60, (top + bottom) / 2, ylabel, size=19, anchor="middle", fill=BLUE, rotate=-90),
        ])
    parts.extend([
        text(312, 38, "线性模型", size=22, anchor="middle", weight=700, fill=BLUE),
        text(882, 38, "logistic 变换", size=22, anchor="middle", weight=700, fill=BLUE),
        '</svg>',
    ])
    OUT7.write_text("\n".join(parts) + "\n", encoding="utf-8")


def figure_10_8() -> None:
    """Draw the log link from a linear predictor to a positive measurement."""
    width, height = 1200, 650
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>log link 把线性模型变换为严格为正的测量值</title>',
        '<desc>左图为 log 尺度上的线性模型，右图为指数变换后的正数尺度；等距水平线在原始尺度上逐渐拉开。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    panels = [
        (85, "log 测量值", -3.2, 3.2, "线性模型（log 尺度）"),
        (655, "原始测量值", -0.15, 10.2, "指数变换"),
    ]
    for left, ylabel, ymin, ymax, heading in panels:
        top, plot_w, plot_h = 65, 455, 455
        right, bottom = left + plot_w, top + plot_h
        sx = lambda value, l=left, r=right: l + (value + 1) / 2 * (r - l)
        sy = lambda value, t=top, b=bottom, lo=ymin, hi=ymax: b - (value - lo) / (hi - lo) * (b - t)
        parts.extend([
            text((left + right) / 2, 38, heading, size=22, anchor="middle", weight=700, fill=BLUE),
            f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fff" stroke="{GRID}"/>',
        ])
        for tick in (-1.0, -0.5, 0.0, 0.5, 1.0):
            xx = sx(tick)
            parts.extend([
                f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+7}" stroke="{INK}"/>',
                text(xx, bottom + 29, f"{tick:.1f}", size=15, anchor="middle"),
            ])
        for guide in (-3, -2, -1, 0, 1, 2):
            value = guide if ylabel == "log 测量值" else math.exp(guide)
            yy = sy(value)
            parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#b9bbb5" stroke-width="1.5"/>')
        y_ticks = (-3, -2, -1, 0, 1, 2, 3) if ylabel == "log 测量值" else (0, 2, 4, 6, 8, 10)
        for tick in y_ticks:
            yy = sy(tick)
            parts.extend([
                f'<line x1="{left-7}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
                text(left - 13, yy + 5, tick, size=15, anchor="end"),
            ])
        points = []
        for index in range(301):
            xvalue = -1 + 2 * index / 300
            linear = 2.3 * xvalue
            yvalue = linear if ylabel == "log 测量值" else math.exp(linear)
            points.append(f"{sx(xvalue):.1f},{sy(yvalue):.1f}")
        parts.extend([
            f'<polyline points="{" ".join(points)}" fill="none" stroke="#737cff" stroke-width="5"/>',
            text((left + right) / 2, height - 58, "预测变量 x", size=19, anchor="middle", fill=BLUE),
            text(left - 60, (top + bottom) / 2, ylabel, size=19, anchor="middle", fill=BLUE, rotate=-90),
        ])
    parts.append('</svg>')
    OUT8.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> int:
    OUT1.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1200, 930
    distributions = [
        ("A", [0, 0, 10, 0, 0], 1),
        ("B", [0, 1, 8, 1, 0], 90),
        ("C", [0, 2, 6, 2, 0], 1260),
        ("D", [1, 2, 4, 2, 1], 37800),
        ("E", [2, 2, 2, 2, 2], 113400),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>石子分布的方式数与信息熵</title>',
        '<desc>五个条形图展示十颗有编号石子落入五只桶的 A 到 E 五种分布及实现方式数；右下图比较各分布的信息熵与每颗石子的对数方式数。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    positions = [(65, 35), (635, 35), (65, 330), (635, 330), (65, 625)]
    for (label, counts, ways), (x, y) in zip(distributions, positions):
        parts.extend(bar_panel(label, counts, ways, x, y))
    parts.extend(scatter_panel(635, 625))
    parts.append('</svg>')
    OUT1.write_text("\n".join(parts) + "\n", encoding="utf-8")
    figure_10_2()
    figure_10_3()
    figure_10_4()
    figure_10_5()
    figure_10_6()
    figure_10_7()
    figure_10_8()
    print(f"generated {OUT1}")
    print(f"generated {OUT2}")
    print(f"generated {OUT3}")
    print(f"generated {OUT4}")
    print(f"generated {OUT5}")
    print(f"generated {OUT6}")
    print(f"generated {OUT7}")
    print(f"generated {OUT8}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
