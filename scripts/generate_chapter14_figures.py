#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 14."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-14-cafe-waits.svg"
OUT2 = ROOT / "translations" / "zh" / "media" / "chapter-14-cafe-population.svg"
OUT3 = ROOT / "translations" / "zh" / "media" / "chapter-14-lkj-priors.svg"
OUT4 = ROOT / "translations" / "zh" / "media" / "chapter-14-correlation-posterior.svg"
OUT5 = ROOT / "translations" / "zh" / "media" / "chapter-14-cafe-shrinkage.svg"
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


def main() -> None:
    figure_14_1()
    figure_14_2()
    figure_14_3()
    figure_14_4()
    figure_14_5()
    print(OUT1)
    print(OUT2)
    print(OUT3)
    print(OUT4)
    print(OUT5)


if __name__ == "__main__":
    main()
