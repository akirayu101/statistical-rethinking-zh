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
OUT5 = ROOT / "translations/zh/media/chapter-11-chimpanzee-posterior.svg"
OUT6 = ROOT / "translations/zh/media/chapter-11-ucb-posterior.svg"
OUT7 = ROOT / "translations/zh/media/chapter-11-ucb-dag-direct.svg"
OUT8 = ROOT / "translations/zh/media/chapter-11-ucb-dag-collider.svg"
OUT9 = ROOT / "translations/zh/media/chapter-11-poisson-intercept-priors.svg"
OUT10 = ROOT / "translations/zh/media/chapter-11-poisson-slope-priors.svg"
OUT11 = ROOT / "translations/zh/media/chapter-11-oceania-posterior.svg"
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


def chimpanzee_posterior_plot() -> None:
    """Rebuild Figure 11.4 from the published data and posterior summary."""
    width, height = 1200, 780
    observed = [
        [.3333333, .5, .2777778, .5555556],
        [1, 1, 1, 1],
        [.2777778, .6111111, .1666667, .3333333],
        [.3333333, .5, .1111111, .4444444],
        [.3333333, .5555556, .2777778, .5],
        [.7777778, .6111111, .5555556, .6111111],
        [.7777778, .8333333, .9444444, 1],
    ]
    actor_mean = [-.45, 3.86, -.75, -.74, -.44, .48, 1.95]
    actor_sd = [.32, .73, .33, .33, .32, .32, .40]
    treatment_mean = [-.04, .48, -.38, .37]
    treatment_sd = [.28, .28, .28, .27]
    predicted = []
    predicted_lower = []
    predicted_upper = []
    for am, ad in zip(actor_mean, actor_sd):
        row, low_row, high_row = [], [], []
        for bm, bd in zip(treatment_mean, treatment_sd):
            linear_mean = am + bm
            linear_sd = math.sqrt(ad * ad + bd * bd)
            row.append(inv_logit(linear_mean))
            low_row.append(inv_logit(linear_mean - 1.6 * linear_sd))
            high_row.append(inv_logit(linear_mean + 1.6 * linear_sd))
        predicted.append(row)
        predicted_lower.append(low_row)
        predicted_upper.append(high_row)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>黑猩猩观测比例与后验预测</title>',
        '<desc>上图按个体展示四种处理下拉左侧杠杆的观测比例；下图展示相应的后验均值与百分之八十九相容区间。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    left, right = 105, 1165
    group_width = (right - left) / 7
    treatments_x = lambda actor, treatment: left + actor * group_width + (treatment + .5) * group_width / 4

    def panel(y: float, panel_height: float, title_value: str, values: list[list[float]],
              lower_values: list[list[float]] | None = None,
              upper_values: list[list[float]] | None = None) -> None:
        top, bottom = y + 48, y + panel_height - 45
        sy = lambda value: bottom - value * (bottom - top)
        parts.extend([
            text((left + right) / 2, y + 5, title_value, size=22, anchor="middle", weight=700, fill="#263f86"),
            f'<rect x="{left}" y="{top}" width="{right - left}" height="{bottom - top}" fill="#fff" stroke="{GRID}"/>',
            f'<line x1="{left}" y1="{sy(.5):.1f}" x2="{right}" y2="{sy(.5):.1f}" stroke="{GRID}" stroke-width="2" stroke-dasharray="8 7"/>',
            text(left - 18, sy(1) + 6, "1", size=17, anchor="end"),
            text(left - 18, sy(.5) + 6, "0.5", size=17, anchor="end"),
            text(left - 18, sy(0) + 6, "0", size=17, anchor="end"),
            text(30, (top + bottom) / 2, "拉左侧杠杆的比例", size=19, anchor="middle", rotate=-90),
        ])
        for actor in range(7):
            if actor:
                xx = left + actor * group_width
                parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{bottom}" stroke="{GRID}"/>')
            parts.append(text(left + (actor + .5) * group_width, top - 12, f"个体 {actor + 1}", size=16, anchor="middle"))
            for pair in ((0, 2), (1, 3)):
                points = " ".join(
                    f"{treatments_x(actor, treatment):.1f},{sy(values[actor][treatment]):.1f}"
                    for treatment in pair
                )
                parts.append(f'<polyline points="{points}" fill="none" stroke="#6670ee" stroke-width="3"/>')
            for treatment in range(4):
                xx = treatments_x(actor, treatment)
                yy = sy(values[actor][treatment])
                if lower_values is not None and upper_values is not None:
                    parts.append(f'<line x1="{xx:.1f}" y1="{sy(lower_values[actor][treatment]):.1f}" x2="{xx:.1f}" y2="{sy(upper_values[actor][treatment]):.1f}" stroke="#30332e" stroke-width="2"/>')
                fill = "#6670ee" if treatment >= 2 else "#fff"
                parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="7" fill="{fill}" stroke="#6670ee" stroke-width="3"/>')

    panel(25, 340, "观测比例", observed)
    panel(400, 340, "后验预测", predicted, predicted_lower, predicted_upper)
    parts.extend([
        text(treatments_x(0, 0), 350, "R/N", size=14, anchor="middle"),
        text(treatments_x(0, 1), 350, "L/N", size=14, anchor="middle"),
        text(treatments_x(0, 2), 350, "R/P", size=14, anchor="middle"),
        text(treatments_x(0, 3), 350, "L/P", size=14, anchor="middle"),
        '</svg>',
    ])
    OUT5.write_text("\n".join(parts) + "\n", encoding="utf-8")


def ucb_posterior_plot() -> None:
    width, height = 1200, 620
    admit = [512, 89, 353, 17, 120, 202, 138, 131, 53, 94, 22, 24]
    applications = [825, 108, 560, 25, 325, 593, 417, 375, 191, 393, 373, 341]
    observed = [a / n for a, n in zip(admit, applications)]
    expected = [inv_logit(-.22 if index % 2 == 0 else -.83) for index in range(12)]
    linear_sd = [.04 if index % 2 == 0 else .05 for index in range(12)]
    lower = [inv_logit((-0.22 if index % 2 == 0 else -0.83) - 1.6 * linear_sd[index]) for index in range(12)]
    upper = [inv_logit((-0.22 if index % 2 == 0 else -0.83) + 1.6 * linear_sd[index]) for index in range(12)]
    predictive = [
        1.6 * math.sqrt(probability * (1 - probability) / n)
        for probability, n in zip(expected, applications)
    ]
    left, right, top, bottom = 95, 1160, 80, 535
    sx = lambda index: left + index * (right - left) / 11
    sy = lambda value: bottom - value * (bottom - top)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>UCB 录取模型的后验验证</title>',
        '<desc>蓝色点和连线表示六个院系男女申请者的观测录取比例；空心点、短黑线与十字分别表示模型期望、百分之八十九期望区间和模拟样本区间。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        text((left + right) / 2, 40, "后验验证检查", size=24, anchor="middle", weight=700, fill="#263f86"),
        f'<rect x="{left}" y="{top}" width="{right - left}" height="{bottom - top}" fill="#fff" stroke="{GRID}"/>',
        text(28, (top + bottom) / 2, "录取比例", size=20, anchor="middle", rotate=-90),
    ]
    for tick in (0, .2, .4, .6, .8, 1):
        yy = sy(tick)
        parts.extend([
            f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="5 6"/>',
            text(left - 14, yy + 6, f"{tick:.1f}", size=16, anchor="end"),
        ])
    for index in range(12):
        xx = sx(index)
        parts.extend([
            text(xx, bottom + 34, index + 1, size=16, anchor="middle"),
            f'<line x1="{xx:.1f}" y1="{sy(lower[index]):.1f}" x2="{xx:.1f}" y2="{sy(upper[index]):.1f}" stroke="#111" stroke-width="3"/>',
            f'<line x1="{xx - 7:.1f}" y1="{sy(expected[index] - predictive[index]):.1f}" x2="{xx + 7:.1f}" y2="{sy(expected[index] + predictive[index]):.1f}" stroke="#111" stroke-width="2"/>',
            f'<line x1="{xx - 7:.1f}" y1="{sy(expected[index] + predictive[index]):.1f}" x2="{xx + 7:.1f}" y2="{sy(expected[index] - predictive[index]):.1f}" stroke="#111" stroke-width="2"/>',
            f'<circle cx="{xx:.1f}" cy="{sy(expected[index]):.1f}" r="9" fill="#fff" stroke="#111" stroke-width="2"/>',
            f'<circle cx="{xx:.1f}" cy="{sy(observed[index]):.1f}" r="7" fill="#6670ee" stroke="#fff" stroke-width="2"/>',
        ])
    for dept in range(6):
        first, second = dept * 2, dept * 2 + 1
        parts.extend([
            f'<line x1="{sx(first):.1f}" y1="{sy(observed[first]):.1f}" x2="{sx(second):.1f}" y2="{sy(observed[second]):.1f}" stroke="#6670ee" stroke-width="4"/>',
            text((sx(first) + sx(second)) / 2, sy((observed[first] + observed[second]) / 2) - 18, chr(65 + dept), size=18, anchor="middle", weight=700, fill="#263f86"),
        ])
    parts.extend([text((left + right) / 2, height - 16, "数据行", size=19, anchor="middle"), '</svg>'])
    OUT6.write_text("\n".join(parts) + "\n", encoding="utf-8")


def dag(path: Path, *, collider: bool) -> None:
    width, height = 800, 360
    nodes = {"G": (120, 250), "D": (400, 80), "A": (680, 250)}
    if collider:
        nodes["U"] = (680, 80)
    arrows = [("G", "D"), ("D", "A"), ("G", "A")]
    if collider:
        arrows.extend([("U", "D"), ("U", "A")])
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f'<title>{"存在未观测混杂的院系录取 DAG" if collider else "性别、院系与录取的直接和间接路径"}</title>',
        f'<desc>{"性别和未观测能力共同影响院系，能力、院系与性别再影响录取。" if collider else "性别直接影响录取，也通过院系间接影响录取。"}</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#30332e"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    for start, end in arrows:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        parts.append(f'<line x1="{x1 + 40 * ux:.1f}" y1="{y1 + 40 * uy:.1f}" x2="{x2 - 44 * ux:.1f}" y2="{y2 - 44 * uy:.1f}" stroke="#30332e" stroke-width="4" marker-end="url(#arrow)"/>')
    labels = {"G": "性别 G", "D": "院系 D", "A": "录取 A", "U": "能力 U"}
    for key, (x, y) in nodes.items():
        parts.extend([
            f'<circle cx="{x}" cy="{y}" r="42" fill="#fff" stroke="#263f86" stroke-width="4"/>',
            text(x, y + 7, labels[key], size=19, anchor="middle", weight=700, fill="#263f86"),
        ])
    parts.append('</svg>')
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def lognormal_density(value: float, mean: float, standard_deviation: float) -> float:
    if value <= 0:
        return 0
    exponent = -((math.log(value) - mean) ** 2) / (2 * standard_deviation ** 2)
    return math.exp(exponent) / (value * standard_deviation * math.sqrt(2 * math.pi))


def poisson_intercept_priors() -> None:
    width, height = 1000, 560
    left, right, top, bottom = 105, 955, 70, 475
    sx = lambda value: left + value / 100 * (right - left)
    sy = lambda value: bottom - value / .08 * (bottom - top)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>简单 Poisson GLM 截距的先验预测分布</title>',
        '<desc>黑色曲线是截距服从均值零标准差十的宽先验，蓝色曲线是均值三标准差零点五的正则化先验。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="#fff" stroke="{GRID}"/>',
    ]
    for tick in range(0, 101, 20):
        xx = sx(tick)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+7}" stroke="{INK}"/>',
            text(xx, bottom + 30, tick, size=16, anchor="middle"),
        ])
    for tick in (0, .02, .04, .06, .08):
        yy = sy(tick)
        parts.extend([
            f'<line x1="{left-7}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
            text(left - 12, yy + 5, f"{tick:.2f}", size=16, anchor="end"),
            f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="4 6"/>',
        ])
    parts.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}" stroke-width="2"/>',
        text((left + right) / 2, height - 24, "工具数量的先验均值", size=19, anchor="middle"),
        text(28, (top + bottom) / 2, "密度", size=19, anchor="middle", rotate=-90),
    ])
    values = [index / 10 for index in range(1, 1001)]
    black = [(value, min(.08, lognormal_density(value, 0, 10))) for value in values]
    blue = [(value, lognormal_density(value, 3, .5)) for value in values]
    polyline(parts, black, sx, sy, color=INK, width=3)
    polyline(parts, blue, sx, sy, color=BLUE, width=4)
    parts.extend([
        text(sx(8), sy(.060), "α ∼ Normal(0, 10)", size=20, weight=700),
        text(sx(30), sy(.035), "α ∼ Normal(3, 0.5)", size=20, weight=700, fill=BLUE),
        '</svg>',
    ])
    OUT9.write_text("\n".join(parts) + "\n", encoding="utf-8")


def poisson_slope_priors() -> None:
    width, height = 1200, 1030
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>Poisson GLM 斜率先验的四种结果尺度视图</title>',
        '<desc>上排比较宽斜率先验与正则化斜率先验；下排把正则化先验分别画在人口对数和原始人口尺度上。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        '<defs>',
    ]
    panels = [
        (45, 45, 540, 430, -2, 2, 0, 100, "β ∼ Normal(0, 10)", "人口对数（标准化）", "工具总数"),
        (615, 45, 540, 430, -2, 2, 0, 100, "β ∼ Normal(0, 0.2)", "人口对数（标准化）", "工具总数"),
        (45, 540, 540, 430, math.log(100), math.log(200000), 0, 500, "α ∼ Normal(3, 0.5)，β ∼ Normal(0, 0.2)", "人口对数", "工具总数"),
        (615, 540, 540, 430, 100, 200000, 0, 500, "α ∼ Normal(3, 0.5)，β ∼ Normal(0, 0.2)", "人口", "工具总数"),
    ]
    geometries = []
    for index, (x, y, panel_width, panel_height, xmin, xmax, ymin, ymax, title_value, xlabel, ylabel) in enumerate(panels):
        left, right, top, bottom = x + 78, x + panel_width - 22, y + 48, y + panel_height - 68
        parts.append(f'<clipPath id="slope-panel-{index}"><rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}"/></clipPath>')
        geometries.append((left, right, top, bottom, xmin, xmax, ymin, ymax))
    parts.append('</defs>')
    for index, panel in enumerate(panels):
        x, y, panel_width, panel_height, xmin, xmax, ymin, ymax, title_value, xlabel, ylabel = panel
        left, right, top, bottom, *_ = geometries[index]
        parts.extend([
            f'<rect x="{x}" y="{y}" width="{panel_width}" height="{panel_height}" rx="8" fill="#fff" stroke="{GRID}"/>',
            text((left + right) / 2, y + 28, title_value, size=18, anchor="middle", weight=700, fill="#263f86"),
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.5"/>',
            f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}" stroke-width="1.5"/>',
            text((left + right) / 2, y + panel_height - 18, xlabel, size=17, anchor="middle"),
            text(x + 21, (top + bottom) / 2, ylabel, size=17, anchor="middle", rotate=-90),
        ])
        if index < 2:
            x_ticks = (-2, -1, 0, 1, 2)
        elif index == 2:
            x_ticks = (6, 8, 10, 12)
        else:
            x_ticks = (0, 50000, 100000, 150000, 200000)
        y_ticks = range(0, int(ymax) + 1, 20 if ymax == 100 else 100)
        for tick in x_ticks:
            xx = left + (tick - xmin) / (xmax - xmin) * (right - left)
            if left <= xx <= right:
                label = f"{tick // 10000}万" if index == 3 and tick else str(tick)
                parts.extend([f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+6}" stroke="{INK}"/>', text(xx, bottom + 25, label, size=14, anchor="middle")])
        for tick in y_ticks:
            yy = bottom - (tick - ymin) / (ymax - ymin) * (bottom - top)
            parts.extend([f'<line x1="{left-6}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>', text(left - 10, yy + 5, tick, size=14, anchor="end")])

    def add_curves(panel_index: int, curves: list[list[tuple[float, float]]]) -> None:
        left, right, top, bottom, xmin, xmax, ymin, ymax = geometries[panel_index]
        sx = lambda value: left + (value - xmin) / (xmax - xmin) * (right - left)
        sy = lambda value: bottom - (value - ymin) / (ymax - ymin) * (bottom - top)
        parts.append(f'<g clip-path="url(#slope-panel-{panel_index})">')
        for curve in curves:
            polyline(parts, curve, sx, sy, color="#343733", width=1.15)
        parts.append('</g>')

    standardized = [-2 + 4 * index / 99 for index in range(100)]
    wide_rng = random.Random(1141)
    wide_parameters = [(wide_rng.gauss(3, .5), wide_rng.gauss(0, 10)) for _ in range(100)]
    add_curves(0, [[(x, math.exp(a + b * x)) for x in standardized] for a, b in wide_parameters])

    regular_rng = random.Random(10)
    regular_parameters = [(regular_rng.gauss(3, .5), regular_rng.gauss(0, .2)) for _ in range(100)]
    add_curves(1, [[(x, math.exp(a + b * x)) for x in standardized] for a, b in regular_parameters])
    log_population = [math.log(100) + (math.log(200000) - math.log(100)) * index / 99 for index in range(100)]
    log_curves = [[(x, math.exp(a + b * x)) for x in log_population] for a, b in regular_parameters]
    add_curves(2, log_curves)
    add_curves(3, [[(math.exp(x), y) for x, y in curve] for curve in log_curves])
    parts.append('</svg>')
    OUT10.write_text("\n".join(parts) + "\n", encoding="utf-8")


def oceania_posterior_plot() -> None:
    names = ["Malekula", "Tikopia", "Santa Cruz", "Yap", "Lau Fiji", "Trobriand", "Chuuk", "Manus", "Tonga", "Hawaii"]
    population = [1100, 1500, 3600, 4791, 7400, 8000, 9200, 13000, 17500, 275000]
    contact = [1, 1, 1, 2, 2, 2, 2, 1, 2, 1]
    tools = [13, 22, 24, 43, 33, 19, 40, 28, 55, 71]
    log_population = [math.log(value) for value in population]
    log_mean = sum(log_population) / len(log_population)
    log_sd = math.sqrt(sum((value - log_mean) ** 2 for value in log_population) / (len(log_population) - 1))
    standardized = [(value - log_mean) / log_sd for value in log_population]

    def fit(group: int) -> tuple[float, float, tuple[float, float, float]]:
        intercept, slope = 3.0, 0.0
        indexes = [index for index, value in enumerate(contact) if value == group]
        for _ in range(30):
            expected = [math.exp(intercept + slope * standardized[index]) for index in indexes]
            gradient_a = sum(tools[index] - expected[pos] for pos, index in enumerate(indexes)) - (intercept - 3) / .25
            gradient_b = sum((tools[index] - expected[pos]) * standardized[index] for pos, index in enumerate(indexes)) - slope / .04
            m00 = sum(expected) + 4
            m01 = sum(expected[pos] * standardized[index] for pos, index in enumerate(indexes))
            m11 = sum(expected[pos] * standardized[index] ** 2 for pos, index in enumerate(indexes)) + 25
            determinant = m00 * m11 - m01 * m01
            step_a = (m11 * gradient_a - m01 * gradient_b) / determinant
            step_b = (-m01 * gradient_a + m00 * gradient_b) / determinant
            intercept += step_a
            slope += step_b
            if abs(step_a) + abs(step_b) < 1e-10:
                break
        expected = [math.exp(intercept + slope * standardized[index]) for index in indexes]
        m00 = sum(expected) + 4
        m01 = sum(expected[pos] * standardized[index] for pos, index in enumerate(indexes))
        m11 = sum(expected[pos] * standardized[index] ** 2 for pos, index in enumerate(indexes)) + 25
        determinant = m00 * m11 - m01 * m01
        return intercept, slope, (m11 / determinant, -m01 / determinant, m00 / determinant)

    fits = {group: fit(group) for group in (1, 2)}

    def prediction(group: int, predictor: float) -> tuple[float, float, float]:
        intercept, slope, (variance_a, covariance, variance_b) = fits[group]
        mean_linear = intercept + slope * predictor
        variance_linear = variance_a + 2 * predictor * covariance + predictor ** 2 * variance_b
        standard_error = math.sqrt(max(variance_linear, 0))
        mean = math.exp(mean_linear + variance_linear / 2)
        return mean, math.exp(mean_linear - 1.598 * standard_error), math.exp(mean_linear + 1.598 * standard_error)

    width, height = 1200, 620
    panels = [
        (35, 45, 550, 500, -1.5, 2.8, "人口对数（标准化）"),
        (615, 45, 550, 500, 0, 300000, "人口"),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>大洋洲工具模型的后验预测</title>',
        '<desc>左图以标准化人口对数为横轴，右图以原始人口为横轴；实心点表示高接触社会，空心点表示低接触社会，曲线和阴影表示后验均值与百分之八十九相容区间。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        '<defs>',
    ]
    geometries = []
    for index, (x, y, panel_width, panel_height, xmin, xmax, xlabel) in enumerate(panels):
        left, right, top, bottom = x + 78, x + panel_width - 22, y + 38, y + panel_height - 72
        geometries.append((left, right, top, bottom, xmin, xmax))
        parts.append(f'<clipPath id="oceania-panel-{index}"><rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}"/></clipPath>')
    parts.append('</defs>')

    for panel_index, panel in enumerate(panels):
        x, y, panel_width, panel_height, xmin, xmax, xlabel = panel
        left, right, top, bottom, *_ = geometries[panel_index]
        sx = lambda value, left=left, right=right, xmin=xmin, xmax=xmax: left + (value - xmin) / (xmax - xmin) * (right - left)
        sy = lambda value, top=top, bottom=bottom: bottom - value / 75 * (bottom - top)
        parts.extend([
            f'<rect x="{x}" y="{y}" width="{panel_width}" height="{panel_height}" rx="8" fill="#fff" stroke="{GRID}"/>',
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.5"/>',
            f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}" stroke-width="1.5"/>',
            text((left + right) / 2, y + panel_height - 20, xlabel, size=18, anchor="middle"),
            text(x + 23, (top + bottom) / 2, "工具总数", size=18, anchor="middle", rotate=-90),
        ])
        x_ticks = (-1, 0, 1, 2) if panel_index == 0 else (0, 50000, 150000, 250000)
        for tick in x_ticks:
            xx = sx(tick)
            label = str(tick) if panel_index == 0 else ("0" if tick == 0 else f"{tick // 10000}万")
            parts.extend([f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+6}" stroke="{INK}"/>', text(xx, bottom + 25, label, size=14, anchor="middle")])
        for tick in (0, 20, 40, 60):
            yy = sy(tick)
            parts.extend([
                f'<line x1="{left-6}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
                text(left - 10, yy + 5, tick, size=14, anchor="end"),
                f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="4 6"/>',
            ])

        predictor_sequence = [-1.5 + 4.5 * index / 119 for index in range(120)] if panel_index == 0 else [-5 + 8 * index / 119 for index in range(120)]
        display_x = predictor_sequence if panel_index == 0 else [math.exp(value * log_sd + log_mean) for value in predictor_sequence]
        parts.append(f'<g clip-path="url(#oceania-panel-{panel_index})">')
        for group, opacity in ((1, .18), (2, .28)):
            predictions = [prediction(group, value) for value in predictor_sequence]
            upper = [(display_x[index], values[2]) for index, values in enumerate(predictions)]
            lower = [(display_x[index], values[1]) for index, values in reversed(list(enumerate(predictions)))]
            polygon_points = upper + lower
            coords = " ".join(f"{sx(px):.1f},{sy(py):.1f}" for px, py in polygon_points)
            parts.append(f'<polygon points="{coords}" fill="#7b7b78" fill-opacity="{opacity}"/>')
        for group, dash in ((1, ' stroke-dasharray="9 7"'), (2, "")):
            curve = [(display_x[index], prediction(group, value)[0]) for index, value in enumerate(predictor_sequence)]
            coords = " ".join(f"{sx(px):.1f},{sy(py):.1f}" for px, py in curve)
            parts.append(f'<polyline points="{coords}" fill="none" stroke="{INK}" stroke-width="3"{dash}/>')

        pareto = [.24, .22, .28, .60, .31, .56, .33, .27, .69, 1.01]
        for index, value in enumerate(tools):
            px = standardized[index] if panel_index == 0 else population[index]
            radius = 6 + 5 * pareto[index]
            fill = BLUE if contact[index] == 2 else "#fff"
            parts.append(f'<circle cx="{sx(px):.1f}" cy="{sy(value):.1f}" r="{radius:.1f}" fill="{fill}" stroke="{BLUE}" stroke-width="3"/>')
        parts.append('</g>')
        if panel_index == 0:
            label_offsets = {3: (-12, -18, "end"), 5: (14, 22, "start"), 8: (-12, -18, "end"), 9: (-12, -18, "end")}
            for index, (dx, dy, anchor) in label_offsets.items():
                value = f"{names[index]} ({pareto[index]:.2f})".replace("0.", ".")
                parts.append(text(sx(standardized[index]) + dx, sy(tools[index]) + dy, value, size=15, anchor=anchor, fill=INK))
    parts.append('</svg>')
    OUT11.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    figure_11_3()
    parameter_plots()
    chimpanzee_posterior_plot()
    ucb_posterior_plot()
    dag(OUT7, collider=False)
    dag(OUT8, collider=True)
    poisson_intercept_priors()
    poisson_slope_priors()
    oceania_posterior_plot()
    for path in (OUT1, OUT2, OUT3, OUT4, OUT5, OUT6, OUT7, OUT8, OUT9, OUT10, OUT11):
        print(path)
