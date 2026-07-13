#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Chapter 10 entropy figures."""
from pathlib import Path
import math


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations/zh/media/chapter-10-pebble-entropy.svg"
OUT2 = ROOT / "translations/zh/media/chapter-10-gaussian-maxent.svg"
OUT3 = ROOT / "translations/zh/media/chapter-10-binomial-candidates.svg"
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
        '<desc>左图比较方差均为一的高斯与三种广义正态密度；右图显示广义正态的熵在形状参数贝塔等于二时达到最大。</desc>',
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
        text(28, top + plot_h / 2, "密度", size=19, anchor="middle", fill=BLUE, rotate=-90),
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
        text(left + 72, top + 30, "高斯 β=2", size=16, fill=BLUE),
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
        text(sx2(2) + 12, sy2(generalized_normal_entropy(2)) - 12, "最大值 β=2", size=17, fill=BLUE, weight=700),
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
    print(f"generated {OUT1}")
    print(f"generated {OUT2}")
    print(f"generated {OUT3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
