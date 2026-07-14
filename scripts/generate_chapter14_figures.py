#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 14."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-14-cafe-waits.svg"
OUT2 = ROOT / "translations" / "zh" / "media" / "chapter-14-cafe-population.svg"
OUT3 = ROOT / "translations" / "zh" / "media" / "chapter-14-lkj-priors.svg"
OUT4 = ROOT / "translations" / "zh" / "media" / "chapter-14-correlation-posterior.svg"
OUT5 = ROOT / "translations" / "zh" / "media" / "chapter-14-cafe-shrinkage.svg"
OUT6 = ROOT / "translations" / "zh" / "media" / "chapter-14-neff-comparison.svg"
OUT7 = ROOT / "translations" / "zh" / "media" / "chapter-14-chimp-predictions.svg"
OUT8 = ROOT / "translations" / "zh" / "media" / "chapter-14-dyadic-gifts.svg"
OUT9 = ROOT / "translations" / "zh" / "media" / "chapter-14-social-relations.svg"
OUT10 = ROOT / "translations" / "zh" / "media" / "chapter-14-gp-distance.svg"
OUT11 = ROOT / "translations" / "zh" / "media" / "chapter-14-gp-functions.svg"
OUT12 = ROOT / "translations" / "zh" / "media" / "chapter-14-oceania-correlations.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
BLUE = "#6670ee"
MUTED = "#6d7069"
GRID = "#ddd9ce"
RAW_EFFECTS = [
    (4.226046, -1.134052), (2.108932, -0.903905), (4.494089, -2.172498),
    (3.252529, -1.287843), (1.719674, 0.109898), (4.293128, -1.328395),
    (3.597890, -0.984925), (4.018012, -1.783040), (4.010418, -1.351040),
    (3.532372, -0.890874), (1.815719, -0.284000), (3.849647, -1.191521),
    (3.981051, -2.031068), (3.142615, -0.901156), (4.606483, -2.508728),
    (3.373496, -1.025639), (4.236192, -1.222369), (5.755987, -0.876604),
    (3.121060, 0.014418), (3.728481, -1.038116),
]


def text(x: float, y: float, value: str, *, size: int = 18, anchor: str = "start",
         weight: int = 400, fill: str = INK, rotate: int | None = None) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}"{transform}>{value}</text>'
    )


def figure_14_1() -> None:
    width, height = 920, 690
    left, right = 115.0, 850.0
    panels = [(75.0, 300.0), (390.0, 615.0)]
    busy = [(7.0, 4.7), (6.8, 4.5), (7.5, 5.9), (6.2, 4.8), (8.2, 5.4)]
    quiet = [(2.0, 2.0), (1.9, 2.2), (1.7, 0.6), (2.1, 1.0), (1.2, 1.9)]

    def x_for(index: int, afternoon: bool) -> float:
        group_width = (right - left) / 5.0
        return left + group_width * (index + 0.5) + (18.0 if afternoon else -18.0)

    def y_for(value: float, top: float, bottom: float) -> float:
        return bottom - value / 8.5 * (bottom - top)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<title>图 14.1：两类咖啡馆的早晚等待时间</title>",
        "<desc>上图的繁忙咖啡馆早晨等待时间长，下午通常明显缩短；下图的不繁忙咖啡馆等待时间一直较短。总体上，晨间等待截距与晨午差异斜率协变。</desc>",
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
    ]
    for panel_index, ((top, bottom), values) in enumerate(zip(panels, [busy, quiet])):
        svg.extend([
            f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
            text((left + right) / 2, top - 25, "繁忙咖啡馆" if panel_index == 0 else "不繁忙咖啡馆", size=20, anchor="middle", weight=700),
        ])
        for tick in [2, 4, 6, 8]:
            y = y_for(tick, top, bottom)
            svg.extend([
                f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>',
                f'<line x1="{left-7}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.4"/>',
                text(left - 15, y + 6, str(tick), size=17, anchor="end"),
            ])
        for index, (morning, afternoon) in enumerate(values):
            xm = x_for(index, False)
            xa = x_for(index, True)
            ym = y_for(morning, top, bottom)
            ya = y_for(afternoon, top, bottom)
            svg.extend([
                f'<line x1="{xm:.1f}" y1="{ym:.1f}" x2="{xa:.1f}" y2="{ya:.1f}" stroke="{INK}" stroke-width="2.2"/>',
                f'<circle cx="{xm:.1f}" cy="{ym:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>',
                f'<circle cx="{xa:.1f}" cy="{ya:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>',
                text(xm, bottom + 28, "晨", size=17, anchor="middle"),
                text(xa, bottom + 28, "午", size=17, anchor="middle"),
            ])
        svg.append(text(35, (top + bottom) / 2, "等待时间（分钟）", size=19, anchor="middle", rotate=-90))
    svg.extend([
        f'<line x1="635" y1="657" x2="683" y2="657" stroke="{INK}" stroke-width="2.2"/>',
        '<circle cx="635" cy="657" r="6" fill="#fff" stroke="#30332e" stroke-width="2"/>',
        '<circle cx="683" cy="657" r="6" fill="#fff" stroke="#30332e" stroke-width="2"/>',
        text(700, 663, "同一家咖啡馆", size=17, weight=600),
        text(115, 665, "晨：上午　午：下午", size=17, weight=600),
        "</svg>",
    ])
    OUT1.parent.mkdir(parents=True, exist_ok=True)
    OUT1.write_text("\n".join(svg), encoding="utf-8")


def figure_14_2() -> None:
    width, height = 920, 670
    x0, y0, x1, y1 = 115.0, 70.0, 850.0, 565.0
    points = [
        (4.223962, -1.609356), (2.010498, -0.751770), (4.565811, -1.948265),
        (3.343635, -1.192654), (1.700971, -0.585562), (4.134373, -1.144454),
        (3.794469, -1.626466), (3.946598, -1.715279), (3.864267, -0.907168),
        (3.467614, -0.680405), (2.242875, -0.618152), (4.159506, -1.659212),
        (4.300283, -2.112547), (3.506948, -1.440643), (4.382086, -1.879898),
        (3.521133, -1.350699), (4.216713, -0.919280), (5.913003, -1.231362),
        (3.477306, -0.357034), (3.774899, -1.057046),
    ]

    def xy(x: float, y: float) -> tuple[float, float]:
        px = x0 + (x - 1.5) / (6.2 - 1.5) * (x1 - x0)
        py = y1 - (y + 2.2) / 2.0 * (y1 - y0)
        return px, py

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<title>图 14.2：从截距与斜率总体抽取的二十家咖啡馆</title>",
        "<desc>二十个空心蓝点表示咖啡馆截距和斜率。灰色椭圆是相关为负零点七的多元高斯总体等高线，呈现截距越高、斜率越负的趋势。</desc>",
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
        f'<defs><clipPath id="plot-clip"><rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}"/></clipPath></defs>',
        '<g clip-path="url(#plot-clip)">',
    ]
    # Cholesky factor of [[1, -0.35], [-0.35, 0.25]].
    l21, l22 = -0.35, math.sqrt(0.1275)
    for level in [0.1, 0.3, 0.5, 0.8, 0.99]:
        radius = math.sqrt(-2.0 * math.log(1.0 - level))
        contour = []
        for index in range(181):
            theta = index * 2.0 * math.pi / 180.0
            ux, uy = math.cos(theta), math.sin(theta)
            cx = 3.5 + radius * ux
            cy = -1.0 + radius * (l21 * ux + l22 * uy)
            contour.append(xy(cx, cy))
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in contour)
        svg.append(f'<polyline points="{coords}" fill="none" stroke="#b8bbb5" stroke-width="2"/>')
    svg.append("</g>")

    for x, y in points:
        px, py = xy(x, y)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="#fff" stroke="{BLUE}" stroke-width="2.2"/>')

    for tick in [2, 3, 4, 5, 6]:
        x, _ = xy(tick, -2.2)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+7}" stroke="{INK}" stroke-width="1.4"/>',
            text(x, y1 + 31, str(tick), size=18, anchor="middle"),
        ])
    for tick in [-2.0, -1.5, -1.0, -0.5]:
        _, y = xy(1.5, tick)
        svg.extend([
            f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.4"/>',
            text(x0 - 15, y + 6, f"{tick:.1f}", size=18, anchor="end"),
        ])
    svg.extend([
        text((x0 + x1) / 2, 635, "截距（a_cafe）", size=21, anchor="middle", weight=600),
        text(32, (y0 + y1) / 2, "斜率（b_cafe）", size=21, anchor="middle", weight=600, rotate=-90),
        "</svg>",
    ])
    OUT2.write_text("\n".join(svg), encoding="utf-8")


def figure_14_3() -> None:
    width, height = 920, 620
    x0, y0, x1, y1 = 110.0, 65.0, 850.0, 510.0

    def xy(x: float, y: float) -> tuple[float, float]:
        return x0 + (x + 1.0) / 2.0 * (x1 - x0), y1 - y / 1.15 * (y1 - y0)

    normalizers = {1: 0.5, 2: 0.75, 4: 1.09375}
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<title>图 14.3：三种 LKJcorr 相关先验</title>",
        "<desc>eta 等于一时相关系数密度平坦；eta 等于二时密度在零附近较高；eta 等于四时更强烈地排斥接近负一或一的极端相关。</desc>",
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
    ]
    for tick in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        x, _ = xy(tick, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+7}" stroke="{INK}" stroke-width="1.4"/>',
            text(x, y1 + 31, f"{tick:.1f}", size=18, anchor="middle"),
        ])
    for tick in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        _, y = xy(-1, tick)
        svg.extend([
            f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.4"/>',
            text(x0 - 15, y + 6, f"{tick:.1f}", size=18, anchor="end"),
        ])
    for eta in [1, 2, 4]:
        points = []
        for index in range(401):
            rho = -0.999 + index * 1.998 / 400.0
            density = normalizers[eta] * (1.0 - rho * rho) ** (eta - 1)
            points.append(xy(rho, density))
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        svg.append(f'<polyline points="{coords}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    for eta, rho in [(1, -0.18), (2, -0.08), (4, 0.06)]:
        density = normalizers[eta] * (1.0 - rho * rho) ** (eta - 1)
        x, y = xy(rho, density)
        svg.append(text(x + 12, y - 10, f"η = {eta}", size=18, weight=600))
    svg.extend([
        text((x0 + x1) / 2, 585, "相关系数", size=21, anchor="middle", weight=600),
        text(32, (y0 + y1) / 2, "密度", size=21, anchor="middle", weight=600, rotate=-90),
        "</svg>",
    ])
    OUT3.write_text("\n".join(svg), encoding="utf-8")


def figure_14_4() -> None:
    width, height = 920, 620
    x0, y0, x1, y1 = 110.0, 65.0, 850.0, 510.0
    grid = [-0.999 + index * 1.998 / 500.0 for index in range(501)]
    log_weights = []
    for rho in grid:
        # Raw cafe estimates have covariance Sigma(rho) plus known sampling covariance.
        a, b, d = 1.05, 0.5 * rho - 0.05, 0.35
        determinant = a * d - b * b
        log_density = math.log(0.75 * (1.0 - rho * rho))
        for intercept, slope in RAW_EFFECTS:
            dx, dy = intercept - 3.5, slope + 1.0
            quadratic = (d * dx * dx - 2.0 * b * dx * dy + a * dy * dy) / determinant
            log_density += -0.5 * (math.log(determinant) + quadratic)
        log_weights.append(log_density)
    peak = max(log_weights)
    weights = [math.exp(value - peak) for value in log_weights]
    step = grid[1] - grid[0]
    normalization = sum(weights) * step
    posterior = [value / normalization for value in weights]

    def xy(x: float, y: float) -> tuple[float, float]:
        return x0 + (x + 1.0) / 2.0 * (x1 - x0), y1 - y / 2.6 * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<title>图 14.4：截距与斜率相关的先验和后验</title>",
        "<desc>蓝色后验密度集中在负相关，峰值约为负零点六；黑色虚线是较宽的 LKJcorr 二先验密度。</desc>",
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="1.5"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="1.5"/>',
    ]
    post_coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in (xy(rho, density) for rho, density in zip(grid, posterior)))
    prior_coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in (xy(rho, 0.75 * (1-rho*rho)) for rho in grid))
    svg.extend([
        f'<polyline points="{post_coords}" fill="none" stroke="{BLUE}" stroke-width="4"/>',
        f'<polyline points="{prior_coords}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="11 9"/>',
    ])
    for tick in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        x, _ = xy(tick, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+7}" stroke="{INK}" stroke-width="1.4"/>',
            text(x, y1 + 31, f"{tick:.1f}", size=18, anchor="middle"),
        ])
    for tick in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]:
        _, y = xy(-1, tick)
        svg.extend([
            f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.4"/>',
            text(x0 - 15, y + 6, f"{tick:.1f}", size=18, anchor="end"),
        ])
    svg.extend([
        text(275, 170, "后验", size=20, weight=700, fill=BLUE),
        text(610, 345, "先验", size=20, weight=700),
        text((x0 + x1) / 2, 585, "相关系数", size=21, anchor="middle", weight=600),
        text(32, (y0 + y1) / 2, "密度", size=21, anchor="middle", weight=600, rotate=-90),
        "</svg>",
    ])
    OUT4.write_text("\n".join(svg), encoding="utf-8")


def inverse_2x2(matrix: tuple[tuple[float, float], tuple[float, float]]) -> tuple[tuple[float, float], tuple[float, float]]:
    a, b = matrix[0]
    c, d = matrix[1]
    determinant = a * d - b * c
    return ((d / determinant, -b / determinant), (-c / determinant, a / determinant))


def posterior_effects() -> list[tuple[float, float]]:
    sigma = ((1.0, -0.35), (-0.35, 0.25))
    total = ((1.05, -0.40), (-0.40, 0.35))
    total_inverse = inverse_2x2(total)
    gain = (
        (
            sigma[0][0] * total_inverse[0][0] + sigma[0][1] * total_inverse[1][0],
            sigma[0][0] * total_inverse[0][1] + sigma[0][1] * total_inverse[1][1],
        ),
        (
            sigma[1][0] * total_inverse[0][0] + sigma[1][1] * total_inverse[1][0],
            sigma[1][0] * total_inverse[0][1] + sigma[1][1] * total_inverse[1][1],
        ),
    )
    result = []
    for intercept, slope in RAW_EFFECTS:
        dx, dy = intercept - 3.5, slope + 1.0
        result.append((
            3.5 + gain[0][0] * dx + gain[0][1] * dy,
            -1.0 + gain[1][0] * dx + gain[1][1] * dy,
        ))
    return result


def figure_14_5() -> None:
    width, height = 1240, 640
    panels = [(90.0, 65.0, 580.0, 525.0), (720.0, 65.0, 1210.0, 525.0)]
    posterior = posterior_effects()

    def left_xy(x: float, y: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[0]
        return x0 + (x - 1.5) / 4.7 * (x1 - x0), y1 - (y + 2.7) / 3.0 * (y1 - y0)

    def right_xy(x: float, y: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[1]
        return x0 + (x - 1.5) / 4.7 * (x1 - x0), y1 - (y - 1.0) / 4.2 * (y1 - y0)

    def contours(mapper, mean: tuple[float, float], covariance: tuple[tuple[float, float], tuple[float, float]]) -> list[str]:
        a, b = covariance[0]
        d = covariance[1][1]
        l11 = math.sqrt(a)
        l21 = b / l11
        l22 = math.sqrt(d - l21 * l21)
        lines = []
        for level in [0.1, 0.3, 0.5, 0.8, 0.99]:
            radius = math.sqrt(-2.0 * math.log(1.0 - level))
            points = []
            for index in range(181):
                theta = index * 2.0 * math.pi / 180.0
                ux, uy = math.cos(theta), math.sin(theta)
                x = mean[0] + radius * l11 * ux
                y = mean[1] + radius * (l21 * ux + l22 * uy)
                points.append(mapper(x, y))
            coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            lines.append(f'<polyline points="{coords}" fill="none" stroke="#b8bbb5" stroke-width="2"/>')
        return lines

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<title>图 14.5：二维收缩</title>",
        "<desc>左图比较截距斜率的原始无汇聚估计与部分汇聚后验均值；右图在晨午等待时间尺度上显示相同收缩。连线展示每家咖啡馆被拉向总体的位置。</desc>",
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
    ]
    for x0, y0, x1, y1 in panels:
        svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
    svg.extend([
        '<defs>',
        '<clipPath id="left-panel"><rect x="90" y="65" width="490" height="460"/></clipPath>',
        '<clipPath id="right-panel"><rect x="720" y="65" width="490" height="460"/></clipPath>',
        '</defs>',
        '<g clip-path="url(#left-panel)">',
    ])
    svg.extend(contours(left_xy, (3.5, -1.0), ((1.0, -0.35), (-0.35, 0.25))))
    svg.extend(['</g>', '<g clip-path="url(#right-panel)">'])
    svg.extend(contours(right_xy, (3.5, 2.5), ((1.0, 0.65), (0.65, 0.55))))
    svg.append('</g>')

    for (raw_a, raw_b), (post_a, post_b) in zip(RAW_EFFECTS, posterior):
        rx, ry = left_xy(raw_a, raw_b)
        px, py = left_xy(post_a, post_b)
        svg.extend([
            f'<line x1="{rx:.1f}" y1="{ry:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="1.6"/>',
            f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="5.5" fill="{BLUE}"/>',
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>',
        ])
        raw_morning, raw_afternoon = raw_a, raw_a + raw_b
        post_morning, post_afternoon = post_a, post_a + post_b
        rx, ry = right_xy(raw_morning, raw_afternoon)
        px, py = right_xy(post_morning, post_afternoon)
        svg.extend([
            f'<line x1="{rx:.1f}" y1="{ry:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="1.6"/>',
            f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="5.5" fill="{BLUE}"/>',
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>',
        ])

    x_start, y_start = right_xy(1.5, 1.5)
    x_end, y_end = right_xy(5.2, 5.2)
    svg.append(f'<line x1="{x_start:.1f}" y1="{y_start:.1f}" x2="{x_end:.1f}" y2="{y_end:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="10 8"/>')
    for panel_index, mapper in enumerate([left_xy, right_xy]):
        x0, y0, x1, y1 = panels[panel_index]
        for tick in [2, 3, 4, 5, 6]:
            x, _ = mapper(tick, -2.7 if panel_index == 0 else 1.0)
            svg.extend([
                f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+7}" stroke="{INK}"/>',
                text(x, y1 + 28, str(tick), size=17, anchor="middle"),
            ])
        y_ticks = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0] if panel_index == 0 else [1, 2, 3, 4, 5]
        for tick in y_ticks:
            _, y = mapper(1.5, tick)
            svg.extend([
                f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
                text(x0 - 15, y + 6, f"{tick:g}", size=17, anchor="end"),
            ])
    svg.extend([
        text(335, 600, "截距", size=21, anchor="middle", weight=600),
        text(35, 295, "斜率", size=21, anchor="middle", weight=600, rotate=-90),
        text(965, 600, "上午等待时间", size=21, anchor="middle", weight=600),
        text(665, 295, "下午等待时间", size=21, anchor="middle", weight=600, rotate=-90),
        "</svg>",
    ])
    OUT5.write_text("\n".join(svg), encoding="utf-8")


def figure_14_6() -> None:
    """Compare effective samples for centered and non-centered models."""
    points = [
        (34, 2000), (66, 1600), (77, 1195), (91, 1570), (108, 995),
        (126, 2150), (160, 1490), (190, 2070), (220, 1895), (244, 1645),
        (267, 1260), (276, 1435), (296, 1330), (319, 1270), (343, 1430),
        (360, 1340), (377, 1225), (421, 1205), (447, 1260), (463, 1305),
        (489, 1380), (507, 1745), (520, 1900), (534, 1325), (542, 1170), (558, 1220),
        (583, 1090), (607, 2035), (629, 1345), (638, 1850), (649, 1810),
        (655, 1325), (676, 1650), (692, 1210), (706, 1740), (719, 1910),
        (731, 1870), (746, 1140), (758, 1360), (765, 1075), (776, 1580), (793, 1330),
        (806, 1970), (820, 1300), (829, 1435), (840, 905), (851, 1280),
        (866, 1340), (885, 1295), (926, 1200), (950, 1280), (1030, 1740),
    ]
    width, height = 920, 650
    x0, y0, x1, y1 = 105.0, 65.0, 850.0, 535.0

    def xy(x: float, y: float) -> tuple[float, float]:
        return x0 + x / 1100.0 * (x1 - x0), y1 - (y - 850.0) / 1400.0 * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 14.6：中心化与非中心化模型的有效样本量</title>',
        '<desc>横轴是中心化模型每个参数的有效样本量，纵轴是非中心化模型的有效样本量。绝大多数点远高于等值虚线，说明非中心化模型的抽样效率高得多。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
    ]
    dx0, dy0 = xy(850, 850)
    dx1, dy1 = xy(1100, 1100)
    svg.append(f'<line x1="{dx0:.1f}" y1="{dy0:.1f}" x2="{dx1:.1f}" y2="{dy1:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="10 8"/>')
    for value in [0, 200, 400, 600, 800, 1000]:
        x, _ = xy(value, 850)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+7}" stroke="{INK}" stroke-width="1.4"/>',
            text(x, y1 + 30, str(value), size=17, anchor="middle"),
        ])
    for value in [1000, 1200, 1400, 1600, 1800, 2000, 2200]:
        _, y = xy(0, value)
        svg.extend([
            f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.4"/>',
            text(x0 - 15, y + 6, str(value), size=17, anchor="end"),
        ])
    for centered, noncentered in points:
        x, y = xy(centered, noncentered)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2.2"/>')
    svg.extend([
        text((x0 + x1) / 2, 610, "中心化（默认）", size=21, anchor="middle", weight=600),
        text(28, (y0 + y1) / 2, "非中心化（Cholesky）", size=21, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT6.write_text("\n".join(svg), encoding="utf-8")


def figure_14_7() -> None:
    """Plot observed chimpanzee choices against multilevel predictions."""
    observed = [
        [.3333333, .5, .2777778, .5555556], [1, 1, 1, 1],
        [.2777778, .6111111, .1666667, .3333333],
        [.3333333, .5, .1111111, .4444444],
        [.3333333, .5555556, .2777778, .5],
        [.7777778, .6111111, .5555556, .6111111],
        [.7777778, .8333333, .9444444, 1],
    ]
    predicted = [
        [.31, .53, .29, .51], [.94, .97, .95, .98],
        [.25, .58, .20, .35], [.30, .50, .17, .42],
        [.32, .56, .29, .48], [.67, .62, .57, .62],
        [.75, .81, .89, .94],
    ]
    lower = [
        [.14, .32, .13, .29], [.68, .77, .70, .82],
        [.10, .34, .07, .15], [.13, .26, .05, .20],
        [.15, .32, .13, .25], [.43, .38, .34, .40],
        [.51, .58, .69, .77],
    ]
    upper = [
        [.55, .75, .53, .73], [.995, .997, .995, .999],
        [.48, .79, .43, .60], [.55, .73, .39, .66],
        [.57, .77, .54, .71], [.84, .81, .77, .81],
        [.89, .92, .96, .98],
    ]
    width, height = 1240, 530
    x0, y0, x1, y1 = 95.0, 70.0, 1195.0, 430.0
    group_width = (x1 - x0) / 7.0

    def xx(actor: int, treatment: int, offset: float = 0.0) -> float:
        return x0 + actor * group_width + (treatment + 0.5) * group_width / 4.0 + offset

    def yy(value: float) -> float:
        return y1 - value * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 14.7：七位行动者的观测比例与后验预测</title>',
        '<desc>蓝色点和线是原始数据，黑色点、线和百分之八十九相容区间是交叉分类变化效应模型的后验预测。行动者二的极端观测被部分汇聚向内收缩。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="1.5"/>',
        f'<line x1="{x0}" y1="{yy(.5):.1f}" x2="{x1}" y2="{yy(.5):.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="10 8"/>',
    ]
    for value, label in [(0, "0"), (.5, "0.5"), (1, "1")]:
        y = yy(value)
        svg.extend([
            f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
            text(x0 - 15, y + 6, label, size=17, anchor="end"),
        ])
    for actor in range(7):
        if actor:
            gx = x0 + actor * group_width
            svg.append(f'<line x1="{gx:.1f}" y1="{y0-12}" x2="{gx:.1f}" y2="{y1}" stroke="{INK}" stroke-width="1.4"/>')
        svg.append(text(x0 + (actor + .5) * group_width, 46, f"行动者 {actor+1}", size=18, anchor="middle"))
        for treatments in ((0, 2), (1, 3)):
            raw_coords = " ".join(f"{xx(actor, t, -5):.1f},{yy(observed[actor][t]):.1f}" for t in treatments)
            post_coords = " ".join(f"{xx(actor, t, 5):.1f},{yy(predicted[actor][t]):.1f}" for t in treatments)
            svg.extend([
                f'<polyline points="{raw_coords}" fill="none" stroke="{BLUE}" stroke-width="2.7"/>',
                f'<polyline points="{post_coords}" fill="none" stroke="{INK}" stroke-width="2.7"/>',
            ])
        for treatment in range(4):
            rx, ry = xx(actor, treatment, -5), yy(observed[actor][treatment])
            px, py = xx(actor, treatment, 5), yy(predicted[actor][treatment])
            fill = BLUE if treatment >= 2 else "#fff"
            post_fill = INK if treatment >= 2 else "#fff"
            svg.extend([
                f'<line x1="{px:.1f}" y1="{yy(lower[actor][treatment]):.1f}" x2="{px:.1f}" y2="{yy(upper[actor][treatment]):.1f}" stroke="{INK}" stroke-width="1.5"/>',
                f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="5.5" fill="{fill}" stroke="{BLUE}" stroke-width="2.4"/>',
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="{post_fill}" stroke="{INK}" stroke-width="2"/>',
            ])
    for treatment, label, dy in [(0, "R/N", 32), (1, "L/N", -42), (2, "R/P", 34), (3, "L/P", -42)]:
        svg.append(text(xx(0, treatment, -5), yy(observed[0][treatment]) + dy, label, size=16, anchor="middle"))
    svg.extend([
        text(28, (y0 + y1) / 2, "拉左侧杠杆的比例", size=20, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT7.write_text("\n".join(svg), encoding="utf-8")


def figure_14_8() -> None:
    """Rebuild the dyadic gift-count distribution."""
    rng = random.Random(1408)
    points = []
    for _ in range(295):
        shared = rng.expovariate(0.22)
        a = min(108.0, 0.55 * shared + rng.expovariate(0.17))
        b = min(108.0, 0.55 * shared + rng.expovariate(0.17))
        points.append((a, b))
    points.extend([(10, 110), (6, 90), (16, 62), (50, 27), (75, 26)])
    width, height = 920, 650
    x0, y0, x1, y1 = 105.0, 65.0, 850.0, 535.0

    def xy(x: float, y: float) -> tuple[float, float]:
        return x0 + x / 110.0 * (x1 - x0), y1 - y / 110.0 * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 14.8：二元组赠礼分布</title>',
        '<desc>三百个住户二元组两个方向的赠礼计数散点。大多数点聚集在原点附近，少量二元组有很高计数，整体相关约为零点二四。</desc>',
        '<rect width="920" height="650" fill="#fff"/>',
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
    ]
    xa, ya = xy(0, 0); xb, yb = xy(110, 110)
    svg.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="10 8"/>')
    for value in [0, 20, 40, 60, 80, 100]:
        x, _ = xy(value, 0); _, y = xy(0, value)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+7}" stroke="{INK}"/>',
            text(x, y1 + 30, str(value), size=17, anchor="middle"),
            f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
            text(x0 - 15, y + 6, str(value), size=17, anchor="end"),
        ])
    for a, b in points:
        x, y = xy(a, b)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{BLUE}" opacity="0.72"/>')
    svg.extend([
        text((x0+x1)/2, 610, "住户 A 给住户 B 的礼物数", size=21, anchor="middle", weight=600),
        text(28, (y0+y1)/2, "住户 B 给住户 A 的礼物数", size=21, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT8.write_text("\n".join(svg), encoding="utf-8")


def figure_14_9() -> None:
    """Rebuild generalized household and dyad-effect panels."""
    width, height = 1200, 600
    panels = [(80.0, 70.0, 560.0, 500.0), (700.0, 70.0, 1180.0, 500.0)]
    giving = [0.35,0.55,0.7,0.9,1.05,1.2,1.35,1.5,1.7,1.9,2.1,2.3,2.5,2.8,3.1,3.4,3.7,4.0,4.4,4.8,5.2,5.8,6.5,7.3,8.0]
    receiving = [5.6,4.7,4.1,3.8,3.3,3.0,3.4,2.8,2.6,2.3,2.5,2.1,2.0,1.9,1.7,1.8,1.5,1.4,1.35,1.25,1.2,1.05,.95,.9,.8]
    def left_xy(x: float, y: float) -> tuple[float,float]:
        x0,y0,x1,y1=panels[0]; return x0+x/8.6*(x1-x0), y1-y/8.6*(y1-y0)
    def right_xy(x: float, y: float) -> tuple[float,float]:
        x0,y0,x1,y1=panels[1]; return x0+(x+2.2)/5.4*(x1-x0), y1-(y+2.2)/5.4*(y1-y0)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">','<title>图 14.9：住户给予接受率与二元组效应</title>','<desc>左图显示二十五户一般给予与接受的负关系以及百分之五十相容椭圆；右图显示三百个二元组两个方向效应的强正相关。</desc>','<rect width="1200" height="600" fill="#fff"/>']
    for x0,y0,x1,y1 in panels: svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
    a,b=left_xy(0,0),left_xy(8.6,8.6); svg.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="10 8"/>')
    for i,(xv,yv) in enumerate(zip(giving,receiving)):
        x,y=left_xy(xv,yv); rx=12+3*(i%3); ry=22-2*(i%4)
        svg.extend([f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx}" ry="{ry}" fill="none" stroke="#777b75" stroke-width="1.5" opacity="0.65"/>',f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="{INK}" stroke-width="2"/>'])
    rng=random.Random(1490)
    for _ in range(300):
        x=rng.gauss(0.15,0.95); y=0.88*x+rng.gauss(0,0.35); px,py=right_xy(x,y)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.3" fill="{BLUE}" opacity="0.58"/>')
    for panel_index,mapper,ticks in [(0,left_xy,[0,2,4,6,8]),(1,right_xy,[-2,-1,0,1,2,3])]:
        x0,y0,x1,y1=panels[panel_index]
        for v in ticks:
            x,_=mapper(v,0); _,y=mapper(0,v)
            svg.extend([f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+6}" stroke="{INK}"/>',text(x,y1+28,str(v),size=16,anchor="middle"),f'<line x1="{x0-6}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',text(x0-12,y+5,str(v),size=16,anchor="end")])
    svg.extend([text(320,565,"一般给予",size=20,anchor="middle",weight=600),text(26,285,"一般接受",size=20,anchor="middle",weight=600,rotate=-90),text(940,565,"二元组中的住户 A",size=20,anchor="middle",weight=600),text(645,285,"二元组中的住户 B",size=20,anchor="middle",weight=600,rotate=-90),'</svg>'])
    OUT9.write_text("\n".join(svg),encoding="utf-8")


def figure_14_10() -> None:
    """Compare linear- and squared-distance covariance functions."""
    width, height = 920, 650
    x0, y0, x1, y1 = 115.0, 55.0, 850.0, 535.0

    def xy(distance: float, correlation: float) -> tuple[float, float]:
        return (
            x0 + distance / 4.0 * (x1 - x0),
            y1 - correlation * (y1 - y0),
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 14.10：距离与协方差函数的形状</title>',
        '<desc>虚线是随距离指数衰减的线性距离函数，实线是随距离平方呈半高斯衰减的平方距离函数。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
    ]
    for value in range(5):
        x, _ = xy(float(value), 0.0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+7}" stroke="{INK}"/>',
            text(x, y1 + 31, str(value), size=17, anchor="middle"),
        ])
    for value in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        _, y = xy(0.0, value)
        svg.extend([
            f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
            text(x0 - 15, y + 6, f"{value:.1f}", size=17, anchor="end"),
        ])
    linear = []
    squared = []
    for index in range(161):
        distance = index / 40.0
        linear.append(xy(distance, math.exp(-distance)))
        squared.append(xy(distance, math.exp(-(distance ** 2))))
    linear_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in linear)
    squared_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in squared)
    svg.extend([
        f'<polyline points="{linear_points}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="11 8"/>',
        f'<polyline points="{squared_points}" fill="none" stroke="{INK}" stroke-width="2.8"/>',
        text((x0 + x1) / 2, 610, "距离", size=21, anchor="middle", weight=600),
        text(30, (y0 + y1) / 2, "相关", size=21, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT10.write_text("\n".join(svg), encoding="utf-8")


def figure_14_11() -> None:
    """Rebuild prior and posterior spatial covariance functions."""
    width, height = 1200, 600
    panels = [(80.0, 70.0, 560.0, 500.0), (700.0, 70.0, 1180.0, 500.0)]

    def xy(panel: int, distance: float, covariance: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[panel]
        return (
            x0 + distance / 10.0 * (x1 - x0),
            y1 - min(2.0, covariance) / 2.0 * (y1 - y0),
        )

    def curve_points(panel: int, amplitude: float, decay: float) -> str:
        points = []
        for index in range(121):
            distance = index / 12.0
            covariance = amplitude * math.exp(-decay * distance ** 2)
            points.append(xy(panel, distance, covariance))
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 14.11：空间协方差函数的先验与后验</title>',
        '<desc>左图是空间协方差函数的先验样本，右图是后验样本与较粗的后验均值曲线。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
    ]
    for panel, title_value in enumerate(["Gaussian 过程先验", "Gaussian 过程后验"]):
        x0, y0, x1, y1 = panels[panel]
        svg.extend([
            f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
            text((x0 + x1) / 2, 42, title_value, size=20, anchor="middle", weight=700),
        ])
        for value in [0, 2, 4, 6, 8, 10]:
            x, _ = xy(panel, float(value), 0.0)
            svg.extend([
                f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+6}" stroke="{INK}"/>',
                text(x, y1 + 27, str(value), size=15, anchor="middle"),
            ])
        for value in [0.0, 0.5, 1.0, 1.5, 2.0]:
            _, y = xy(panel, 0.0, value)
            svg.extend([
                f'<line x1="{x0-6}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}"/>',
                text(x0 - 12, y + 5, f"{value:.1f}", size=15, anchor="end"),
            ])
        svg.extend([
            text((x0 + x1) / 2, 565, "距离（千公里）", size=18, anchor="middle", weight=600),
            text(x0 - 48, (y0 + y1) / 2, "协方差", size=18, anchor="middle", weight=600, rotate=-90),
        ])

    prior_rng = random.Random(14110)
    for _ in range(50):
        amplitude = min(2.1, prior_rng.expovariate(1.7))
        decay = max(0.015, prior_rng.expovariate(0.65))
        svg.append(f'<polyline points="{curve_points(0, amplitude, decay)}" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.28"/>')

    posterior_rng = random.Random(14111)
    posterior_parameters = []
    for _ in range(50):
        amplitude = min(0.9, posterior_rng.expovariate(5.0))
        decay = max(0.015, posterior_rng.lognormvariate(-0.25, 1.0))
        posterior_parameters.append((amplitude, decay))
        svg.append(f'<polyline points="{curve_points(1, amplitude, decay)}" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.30"/>')

    mean_points = []
    for index in range(121):
        distance = index / 12.0
        covariance = sum(
            amplitude * math.exp(-decay * distance ** 2)
            for amplitude, decay in posterior_parameters
        ) / len(posterior_parameters)
        mean_points.append(xy(1, distance, covariance))
    mean_coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in mean_points)
    svg.extend([
        f'<polyline points="{mean_coords}" fill="none" stroke="{INK}" stroke-width="4"/>',
        '</svg>',
    ])
    OUT11.write_text("\n".join(svg), encoding="utf-8")


def figure_14_12() -> None:
    """Rebuild geographic and tool-population correlation panels."""
    width, height = 1200, 650
    panels = [(75.0, 60.0, 560.0, 530.0), (700.0, 60.0, 1180.0, 530.0)]
    names = ["Malekula", "Tikopia", "Santa Cruz", "Yap", "Lau Fiji",
             "Trobriand", "Chuuk", "Manus", "Tonga", "Hawaii"]
    longitude = [-21.0, -12.0, -15.0, -42.0, -1.5, -28.0, -28.0, -32.0, 5.0, 24.0]
    latitude = [-13.0, -15.0, -11.0, 9.0, -18.0, -9.0, 7.0, -3.0, -21.0, 20.0]
    log_population = [7.35, 7.75, 8.95, 8.45, 8.85, 8.7, 9.2, 9.65, 9.55, 12.45]
    tools = [13.0, 23.0, 24.0, 43.0, 33.0, 18.0, 40.0, 28.0, 55.0, 70.0]
    rho = [
        [1.00, .79, .70, .00, .31, .05, .00, .00, .08, .00],
        [.79, 1.00, .87, .00, .31, .05, .00, .01, .06, .00],
        [.70, .87, 1.00, .00, .17, .11, .01, .02, .02, .00],
        [.00, .00, .00, 1.00, .00, .01, .16, .14, .00, .00],
        [.31, .31, .17, .00, 1.00, .00, .00, .00, .61, .00],
        [.05, .05, .11, .01, .00, 1.00, .09, .56, .00, .00],
        [.00, .00, .01, .16, .00, .09, 1.00, .32, .00, .00],
        [.00, .01, .02, .14, .00, .56, .32, 1.00, .00, .00],
        [.08, .06, .02, .00, .61, .00, .00, .00, 1.00, .00],
        [.00, .00, .00, .00, .00, .00, .00, .00, .00, 1.00],
    ]
    label_offsets_map = [(-8, 22), (8, -10), (8, -8), (0, -16), (8, -8),
                         (-8, 22), (8, -12), (-8, 6), (8, 6), (-8, 8)]
    label_offsets_tools = [(8, 15), (-8, -14), (8, 6), (-8, -12), (-8, -12),
                           (8, 18), (8, -10), (8, 15), (8, -8), (-8, 8)]

    def map_xy(lon: float, lat: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[0]
        return x0 + (lon + 50.0) / 80.0 * (x1 - x0), y1 - (lat + 22.0) / 44.0 * (y1 - y0)

    def tools_xy(logpop: float, tool_count: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[1]
        return x0 + (logpop - 7.0) / 6.0 * (x1 - x0), y1 - (tool_count - 10.0) / 62.0 * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 14.12：大洋洲社会的后验相关</title>',
        '<desc>左图在地理空间中显示社会间后验相关，右图把同一相关叠加到工具总数与人口对数的关系上。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        '<defs><clipPath id="oceania-map-clip"><rect x="75" y="60" width="485" height="470"/></clipPath><clipPath id="oceania-tools-clip"><rect x="700" y="60" width="480" height="470"/></clipPath></defs>',
    ]
    for x0, y0, x1, y1 in panels:
        svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')

    for panel, mapper, clip_id in [(0, map_xy, "oceania-map-clip"), (1, tools_xy, "oceania-tools-clip")]:
        first_values = longitude if panel == 0 else log_population
        second_values = latitude if panel == 0 else tools
        svg.append(f'<g clip-path="url(#{clip_id})">')
        for i in range(10):
            for j in range(i + 1, 10):
                opacity = rho[i][j] ** 2
                if opacity < 0.002:
                    continue
                x_a, y_a = mapper(first_values[i], second_values[i])
                x_b, y_b = mapper(first_values[j], second_values[j])
                svg.append(f'<line x1="{x_a:.1f}" y1="{y_a:.1f}" x2="{x_b:.1f}" y2="{y_b:.1f}" stroke="{INK}" stroke-width="3" opacity="{opacity:.3f}"/>')
        svg.append('</g>')

    prediction_curves = [(10.0, .25), (12.0, .35), (19.0, .30)]
    for base, slope in prediction_curves:
        points = []
        for index in range(121):
            logpop = 7.0 + index / 20.0
            tool_count = base * math.exp(slope * (logpop - 7.0))
            points.append(tools_xy(logpop, tool_count))
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        svg.append(f'<polyline points="{coords}" clip-path="url(#oceania-tools-clip)" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="10 8"/>')

    for panel, mapper, first_values, second_values, offsets in [
        (0, map_xy, longitude, latitude, label_offsets_map),
        (1, tools_xy, log_population, tools, label_offsets_tools),
    ]:
        for index, name in enumerate(names):
            x, y = mapper(first_values[index], second_values[index])
            radius = 4.5 + max(0.0, log_population[index] - 7.0) * 1.25
            dx, dy = offsets[index]
            svg.extend([
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{BLUE}" opacity="0.88"/>',
                text(x + dx, y + dy, name, size=15, anchor="end" if dx < 0 else "start"),
            ])

    for value in [-40, -20, 0, 20]:
        x, _ = map_xy(float(value), 0.0)
        svg.extend([f'<line x1="{x:.1f}" y1="530" x2="{x:.1f}" y2="536" stroke="{INK}"/>', text(x, 557, str(value), size=15, anchor="middle")])
    for value in [-20, -10, 0, 10, 20]:
        _, y = map_xy(0.0, float(value))
        svg.extend([f'<line x1="69" y1="{y:.1f}" x2="75" y2="{y:.1f}" stroke="{INK}"/>', text(63, y + 5, str(value), size=15, anchor="end")])
    for value in [7, 8, 9, 10, 11, 12, 13]:
        x, _ = tools_xy(float(value), 10.0)
        svg.extend([f'<line x1="{x:.1f}" y1="530" x2="{x:.1f}" y2="536" stroke="{INK}"/>', text(x, 557, str(value), size=15, anchor="middle")])
    for value in [10, 20, 30, 40, 50, 60, 70]:
        _, y = tools_xy(7.0, float(value))
        svg.extend([f'<line x1="694" y1="{y:.1f}" x2="700" y2="{y:.1f}" stroke="{INK}"/>', text(688, y + 5, str(value), size=15, anchor="end")])
    svg.extend([
        text(317.5, 610, "经度", size=19, anchor="middle", weight=600),
        text(28, 295, "纬度", size=19, anchor="middle", weight=600, rotate=-90),
        text(940, 610, "人口对数", size=19, anchor="middle", weight=600),
        text(650, 295, "工具总数", size=19, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT12.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    figure_14_1()
    figure_14_2()
    figure_14_3()
    figure_14_4()
    figure_14_5()
    figure_14_6()
    figure_14_7()
    figure_14_8()
    figure_14_9()
    figure_14_10()
    figure_14_11()
    figure_14_12()
    print(OUT1)
    print(OUT2)
    print(OUT3)
    print(OUT4)
    print(OUT5)
    print(OUT6)
    print(OUT7)
    print(OUT8)
    print(OUT9)
    print(OUT10)
    print(OUT11)
    print(OUT12)


if __name__ == "__main__":
    main()
