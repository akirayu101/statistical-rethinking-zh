#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 12."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-12-beta-binomial.svg"
OUT2 = ROOT / "translations" / "zh" / "media" / "chapter-12-poisson-gamma-poisson.svg"
OUT3 = ROOT / "translations" / "zh" / "media" / "chapter-12-zero-inflated-structure.svg"
OUT4 = ROOT / "translations" / "zh" / "media" / "chapter-12-ordered-distribution.svg"
OUT5 = ROOT / "translations" / "zh" / "media" / "chapter-12-ordered-likelihood.svg"
OUT6 = ROOT / "translations" / "zh" / "media" / "chapter-12-trolley-slopes.svg"
OUT7 = ROOT / "translations" / "zh" / "media" / "chapter-12-trolley-predictions.svg"
OUT8 = ROOT / "translations" / "zh" / "media" / "chapter-12-dirichlet-prior.svg"
OUT9 = ROOT / "translations" / "zh" / "media" / "chapter-12-education-pairs.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
BLUE = "#6670ee"
GRID = "#d9d5c8"


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def beta_density(x: float, pbar: float, theta: float) -> float:
    a = pbar * theta
    b = (1.0 - pbar) * theta
    log_norm = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    return math.exp(log_norm + (a - 1.0) * math.log(x) + (b - 1.0) * math.log1p(-x))


def polyline(points: list[tuple[float, float]], **attrs: object) -> str:
    attr_text = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{coords}" {attr_text}/>'


def text_el(
    x: float,
    y: float,
    value: object,
    *,
    size: int = 18,
    anchor: str = "start",
    weight: int = 400,
    fill: str = INK,
    rotate: int | None = None,
) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    escaped = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}"{transform}>'
        f"{escaped}</text>"
    )


def polygon(points: list[tuple[float, float]], **attrs: object) -> str:
    attr_text = " ".join(f'{key.replace("_", "-")}="{value}"' for key, value in attrs.items())
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{coords}" {attr_text}/>'


def main() -> None:
    width, height = 1200, 650
    left = (92.0, 82.0, 485.0, 470.0)
    right = (682.0, 82.0, 1090.0, 470.0)
    lx0, ly0, lx1, ly1 = left
    rx0, ry0, rx1, ry1 = right

    def left_xy(x: float, y: float) -> tuple[float, float]:
        return lx0 + x * (lx1 - lx0), ly1 - min(y, 3.0) / 3.0 * (ly1 - ly0)

    def right_xy(case: float, value: float) -> tuple[float, float]:
        return rx0 + (case - 1.0) / 11.0 * (rx1 - rx0), ry1 - value * (ry1 - ry0)

    rng = random.Random(1201)
    sampled_curves: list[str] = []
    xs = [0.005 + i * 0.99 / 198 for i in range(199)]
    for _ in range(50):
        pbar = logistic(rng.gauss(-0.34, 0.40))
        phi = rng.gammavariate(1.8, 1.05 / 1.8)
        theta = 2.0 + phi
        pts = [left_xy(x, beta_density(x, pbar, theta)) for x in xs]
        sampled_curves.append(polyline(pts, fill="none", stroke="#60635d", stroke_width="1.2", opacity="0.23"))

    mean_pts = [left_xy(x, beta_density(x, logistic(-0.34), 3.05)) for x in xs]
    empirical = [0.6206, 0.8241, 0.6304, 0.6800, 0.3692, 0.3406, 0.3310, 0.3493, 0.2775, 0.2392, 0.0590, 0.0704]
    pmeans = [0.389 if i % 2 == 1 else 0.416 for i in range(1, 13)]
    p_lo = [0.250 if i % 2 == 1 else 0.269 for i in range(1, 13)]
    p_hi = [0.552 if i % 2 == 1 else 0.567 for i in range(1, 13)]
    pred_lo = [0.028 if i % 2 == 1 else 0.035 for i in range(1, 13)]
    pred_hi = [0.835 if i % 2 == 1 else 0.865 for i in range(1, 13)]

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 12.1：beta-binomial 后验分布与后验验证</title>',
        '<desc>左侧显示女性申请者录取概率的 beta 分布后验，右侧比较十二个案例的经验录取比例、平均概率区间与预测录取计数区间。</desc>',
        '<rect width="1200" height="650" fill="#fff"/>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans CJK SC",sans-serif;fill:#222}.title{font-size:24px;font-weight:600}.axis{font-size:20px}.tick{font-size:17px;fill:#555}.legend{font-size:17px;fill:#555}</style>',
        f'<text class="title" x="{(lx0 + lx1) / 2:.0f}" y="38" text-anchor="middle">女性申请者录取率的分布</text>',
        f'<text class="title" x="{(rx0 + rx1) / 2:.0f}" y="38" text-anchor="middle">后验验证检查</text>',
        f'<line x1="{lx0}" y1="{ly1}" x2="{lx1}" y2="{ly1}" stroke="#222" stroke-width="2"/>',
        f'<line x1="{lx0}" y1="{ly0}" x2="{lx0}" y2="{ly1}" stroke="#222" stroke-width="2"/>',
        f'<line x1="{rx0}" y1="{ry1}" x2="{rx1}" y2="{ry1}" stroke="#222" stroke-width="2"/>',
        f'<line x1="{rx0}" y1="{ry0}" x2="{rx0}" y2="{ry1}" stroke="#222" stroke-width="2"/>',
    ]

    for v in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        x, y = left_xy(v, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y + 7:.1f}" stroke="#222"/>',
            f'<text class="tick" x="{x:.1f}" y="{y + 28:.1f}" text-anchor="middle">{v:.1f}</text>',
        ])
    for v in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        x, y = left_xy(0, v)
        svg.extend([
            f'<line x1="{x - 7:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#222"/>',
            f'<text class="tick" x="{x - 14:.1f}" y="{y + 6:.1f}" text-anchor="end">{v:.1f}</text>',
        ])
    svg.extend(sampled_curves)
    svg.append(polyline(mean_pts, fill="none", stroke="#20221f", stroke_width="4.2"))
    svg.extend([
        f'<text class="axis" x="{(lx0 + lx1) / 2:.0f}" y="535" text-anchor="middle">录取概率</text>',
        f'<text class="axis" x="28" y="{(ly0 + ly1) / 2:.0f}" text-anchor="middle" transform="rotate(-90 28 {(ly0 + ly1) / 2:.0f})">密度</text>',
        '<line x1="120" y1="581" x2="175" y2="581" stroke="#20221f" stroke-width="4.2"/>',
        '<text class="legend" x="187" y="587">后验均值 beta 分布</text>',
        '<line x1="120" y1="616" x2="175" y2="616" stroke="#60635d" stroke-width="1.5" opacity=".45"/>',
        '<text class="legend" x="187" y="622">50 组后验参数对应的 beta 分布</text>',
    ])

    for v in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        x, y = right_xy(1, v)
        svg.extend([
            f'<line x1="{x - 7:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#222"/>',
            f'<text class="tick" x="{x - 14:.1f}" y="{y + 6:.1f}" text-anchor="end">{v:.1f}</text>',
        ])
    for i in range(1, 13):
        x, y0 = right_xy(i, 0)
        svg.extend([
            f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y0 + 7:.1f}" stroke="#222"/>',
            f'<text class="tick" x="{x:.1f}" y="{y0 + 28:.1f}" text-anchor="middle">{i}</text>',
        ])
        x, lo = right_xy(i, p_lo[i - 1])
        _, hi = right_xy(i, p_hi[i - 1])
        _, pm = right_xy(i, pmeans[i - 1])
        _, pl = right_xy(i, pred_lo[i - 1])
        _, ph = right_xy(i, pred_hi[i - 1])
        _, obs = right_xy(i, empirical[i - 1])
        svg.extend([
            f'<line x1="{x:.1f}" y1="{hi:.1f}" x2="{x:.1f}" y2="{lo:.1f}" stroke="#222" stroke-width="2"/>',
            f'<circle cx="{x:.1f}" cy="{pm:.1f}" r="7" fill="#fff" stroke="#222" stroke-width="2.2"/>',
            f'<line x1="{x - 7:.1f}" y1="{ph:.1f}" x2="{x + 7:.1f}" y2="{ph:.1f}" stroke="#222" stroke-width="2"/>',
            f'<line x1="{x:.1f}" y1="{ph - 7:.1f}" x2="{x:.1f}" y2="{ph + 7:.1f}" stroke="#222" stroke-width="2"/>',
            f'<line x1="{x - 7:.1f}" y1="{pl:.1f}" x2="{x + 7:.1f}" y2="{pl:.1f}" stroke="#222" stroke-width="2"/>',
            f'<line x1="{x:.1f}" y1="{pl - 7:.1f}" x2="{x:.1f}" y2="{pl + 7:.1f}" stroke="#222" stroke-width="2"/>',
            f'<circle cx="{x:.1f}" cy="{obs:.1f}" r="6.3" fill="#6670ee"/>',
        ])
    svg.extend([
        f'<text class="axis" x="{(rx0 + rx1) / 2:.0f}" y="535" text-anchor="middle">案例</text>',
        f'<text class="axis" x="620" y="{(ry0 + ry1) / 2:.0f}" text-anchor="middle" transform="rotate(-90 620 {(ry0 + ry1) / 2:.0f})">录取比例</text>',
        '<circle cx="700" cy="581" r="6.3" fill="#6670ee"/><text class="legend" x="718" y="587">经验录取比例</text>',
        '<circle cx="700" cy="616" r="7" fill="#fff" stroke="#222" stroke-width="2.2"/><text class="legend" x="718" y="622">p̄ 后验均值与 89% 区间；+ 为预测计数区间</text>',
        '</svg>',
    ])
    OUT1.parent.mkdir(parents=True, exist_ok=True)
    OUT1.write_text("\n".join(svg), encoding="utf-8")


def figure_12_2() -> None:
    """Rebuild the Poisson versus gamma-Poisson comparison on source page 403."""
    width, height = 1200, 650
    population = [1100, 1500, 3600, 4791, 7400, 8000, 9200, 13000, 17500, 275000]
    contact = [1, 1, 1, 2, 2, 2, 2, 1, 2, 1]
    tools = [13, 22, 24, 43, 33, 19, 40, 28, 55, 71]
    panels = ((35, "纯 Poisson 模型"), (625, "gamma-Poisson 模型"))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>图 12.2：纯 Poisson 与 gamma-Poisson 的大洋洲工具模型比较</title>',
        '<desc>两个面板都显示人口与工具总数的关系。左侧纯 Poisson 模型受 Hawaii 强烈影响，右侧 gamma-Poisson 模型的预测区间更宽，两种接触率趋势也更接近。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        '<defs>',
    ]
    geometries: list[tuple[float, float, float, float]] = []
    for index, (x, _) in enumerate(panels):
        left, right, top, bottom = x + 78, x + 545, 78, 535
        geometries.append((left, right, top, bottom))
        parts.append(f'<clipPath id="chapter12-panel-{index}"><rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}"/></clipPath>')
    parts.append("</defs>")

    for panel_index, (panel_x, title) in enumerate(panels):
        left, right, top, bottom = geometries[panel_index]
        sx = lambda value, left=left, right=right: left + value / 300000 * (right - left)
        sy = lambda value, top=top, bottom=bottom: bottom - (value - 10) / 65 * (bottom - top)
        parts.extend([
            text_el((left + right) / 2, 40, title, size=24, anchor="middle", weight=650),
            f'<rect x="{panel_x}" y="55" width="545" height="520" rx="8" fill="#fff" stroke="{GRID}"/>',
        ])
        for tick in (0, 50000, 150000, 250000):
            xx = sx(tick)
            label = "0" if tick == 0 else f"{tick // 10000}万"
            parts.extend([
                f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+7}" stroke="{INK}"/>',
                text_el(xx, bottom + 28, label, size=15, anchor="middle"),
            ])
        for tick in (10, 20, 30, 40, 50, 60, 70):
            yy = sy(tick)
            parts.extend([
                f'<line x1="{left-7}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
                text_el(left - 12, yy + 5, tick, size=15, anchor="end"),
                f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="4 7"/>',
            ])
        parts.extend([
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.7"/>',
            f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}" stroke-width="1.7"/>',
            text_el((left + right) / 2, 610, "人口", size=19, anchor="middle"),
            text_el(panel_x + 22, (top + bottom) / 2, "工具总数", size=19, anchor="middle", rotate=-90),
            f'<g clip-path="url(#chapter12-panel-{panel_index})">',
        ])

        xs = [1000 + index * 299000 / 159 for index in range(160)]
        high = [(value, 3.0 + 0.71 * value ** 0.42) for value in xs]
        if panel_index == 0:
            low = [(value, 4.58 * value ** 0.216) for value in xs]
            high_bounds = (
                [(value, max(10, mean * 0.72)) for value, mean in high],
                [(value, mean * 1.64 + 5) for value, mean in high],
            )
            low_bounds = (
                [(value, max(10, mean * 0.80)) for value, mean in low],
                [(value, mean * 1.22 + 2) for value, mean in low],
            )
        else:
            low = [(value, 2.13 * value ** 0.282) for value in xs]
            high_bounds = (
                [(value, max(10, mean * 0.50)) for value, mean in high],
                [(value, mean * 1.72 + 8) for value, mean in high],
            )
            low_bounds = (
                [(value, max(10, mean * 0.55)) for value, mean in low],
                [(value, mean * 1.66 + 12) for value, mean in low],
            )
        for bounds, shade in ((high_bounds, "#d8d8d6"), (low_bounds, "#b8b8b5")):
            lower, upper = bounds
            region = upper + list(reversed(lower))
            parts.append(polygon([(sx(x), sy(y)) for x, y in region], fill=shade))
        parts.append(polyline([(sx(x), sy(y)) for x, y in high], fill="none", stroke=INK, stroke_width="3.2"))
        parts.append(polyline([(sx(x), sy(y)) for x, y in low], fill="none", stroke=INK, stroke_width="3.2", stroke_dasharray="11 8"))
        for index, value in enumerate(tools):
            fill = BLUE if contact[index] == 2 else "#fff"
            parts.append(f'<circle cx="{sx(population[index]):.1f}" cy="{sy(value):.1f}" r="8" fill="{fill}" stroke="{BLUE}" stroke-width="3"/>')
        parts.append("</g>")
        if panel_index == 1:
            parts.extend([
                text_el(sx(62000), sy(68), "高接触率", size=17),
                text_el(sx(85000), sy(50), "低接触率", size=17),
            ])
    parts.extend([
        '<circle cx="315" cy="636" r="6" fill="#6670ee" stroke="#6670ee" stroke-width="2"/>',
        text_el(330, 642, "高接触社会", size=15),
        '<circle cx="490" cy="636" r="6" fill="#fff" stroke="#6670ee" stroke-width="2"/>',
        text_el(505, 642, "低接触社会", size=15),
        "</svg>",
    ])
    OUT2.write_text("\n".join(parts) + "\n", encoding="utf-8")


def figure_12_3() -> None:
    """Rebuild the zero-inflated likelihood tree and simulated count distribution."""
    width, height = 1200, 610
    chart_left, chart_right, chart_top, chart_bottom = 690, 1120, 78, 500
    sx = lambda value: chart_left + value / 5 * (chart_right - chart_left)
    sy = lambda value: chart_bottom - value / 180 * (chart_bottom - chart_top)
    frequencies = [108, 106, 70, 12, 2, 1]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>图 12.3：零膨胀 likelihood 的结构与模拟计数</title>',
        '<desc>左侧决策树显示僧侣以概率 p 饮酒并必然产生零，或以概率一减 p 工作并产生零或正计数。右侧直方线图显示一年模拟数据，零上方的蓝色线段标出由饮酒造成的结构性零。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        '<defs><marker id="chapter12-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#30332e"/></marker></defs>',
        text_el(330, 42, "零膨胀 likelihood 的生成结构", size=23, anchor="middle", weight=650),
        text_el((chart_left + chart_right) / 2, 42, "一年手稿产量的模拟分布", size=23, anchor="middle", weight=650),
        '<circle cx="330" cy="115" r="18" fill="#fff" stroke="#30332e" stroke-width="2.5"/>',
        '<circle cx="185" cy="255" r="18" fill="#fff" stroke="#30332e" stroke-width="2.5"/>',
        '<circle cx="475" cy="255" r="18" fill="#fff" stroke="#30332e" stroke-width="2.5"/>',
        '<line x1="317" y1="128" x2="199" y2="242" stroke="#30332e" stroke-width="2.7" marker-end="url(#chapter12-arrow)"/>',
        '<line x1="343" y1="128" x2="461" y2="242" stroke="#30332e" stroke-width="2.7" marker-end="url(#chapter12-arrow)"/>',
        '<line x1="185" y1="274" x2="185" y2="390" stroke="#30332e" stroke-width="2.7" marker-end="url(#chapter12-arrow)"/>',
        '<line x1="464" y1="268" x2="270" y2="397" stroke="#30332e" stroke-width="2.7" marker-end="url(#chapter12-arrow)"/>',
        '<line x1="475" y1="274" x2="475" y2="390" stroke="#30332e" stroke-width="2.7" marker-end="url(#chapter12-arrow)"/>',
        text_el(260, 183, "p", size=22, anchor="middle"),
        text_el(402, 183, "1 − p", size=22, anchor="middle"),
        text_el(150, 262, "饮酒", size=22, anchor="end"),
        text_el(510, 262, "工作", size=22),
        text_el(210, 437, "观测到 y = 0", size=21, anchor="middle"),
        text_el(480, 437, "观测到 y > 0", size=21, anchor="middle"),
        f'<rect x="{chart_left-18}" y="{chart_top-10}" width="{chart_right-chart_left+36}" height="{chart_bottom-chart_top+20}" fill="#fff" stroke="{GRID}"/>',
    ]
    for tick in (0, 50, 100, 150):
        yy = sy(tick)
        parts.extend([
            f'<line x1="{chart_left-7}" y1="{yy:.1f}" x2="{chart_left}" y2="{yy:.1f}" stroke="{INK}"/>',
            text_el(chart_left - 13, yy + 5, tick, size=16, anchor="end"),
            f'<line x1="{chart_left}" y1="{yy:.1f}" x2="{chart_right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="4 7"/>',
        ])
    for value in range(6):
        xx = sx(value)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{chart_bottom}" x2="{xx:.1f}" y2="{chart_bottom+7}" stroke="{INK}"/>',
            text_el(xx, chart_bottom + 29, value, size=16, anchor="middle"),
            f'<line x1="{xx:.1f}" y1="{chart_bottom}" x2="{xx:.1f}" y2="{sy(frequencies[value]):.1f}" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>',
        ])
    parts.extend([
        f'<line x1="{sx(0):.1f}" y1="{sy(frequencies[0]):.1f}" x2="{sx(0):.1f}" y2="{sy(172):.1f}" stroke="{BLUE}" stroke-width="7"/>',
        f'<line x1="{chart_left}" y1="{chart_bottom}" x2="{chart_right}" y2="{chart_bottom}" stroke="{INK}" stroke-width="1.7"/>',
        f'<line x1="{chart_left}" y1="{chart_bottom}" x2="{chart_left}" y2="{chart_top}" stroke="{INK}" stroke-width="1.7"/>',
        text_el((chart_left + chart_right) / 2, 570, "完成的手稿数", size=20, anchor="middle"),
        text_el(635, (chart_top + chart_bottom) / 2, "频数", size=20, anchor="middle", rotate=-90),
        "</svg>",
    ])
    OUT3.write_text("\n".join(parts) + "\n", encoding="utf-8")


def figure_12_4() -> None:
    """Rebuild the response histogram, cumulative proportions, and cumulative logits."""
    width, height = 1200, 610
    responses = list(range(1, 8))
    frequencies = [1270, 908, 1072, 2333, 1456, 1447, 1444]
    total = sum(frequencies)
    cumulative: list[float] = []
    running = 0
    for value in frequencies:
        running += value
        cumulative.append(running / total)
    logits = [math.log(value / (1 - value)) for value in cumulative[:-1]]
    panels = (
        (20, "样本回答的频数", "频数", (0.0, 2500.0)),
        (415, "各回答的累积比例", "累积比例", (0.0, 1.0)),
        (810, "各回答的对数累积赔率", "对数累积赔率", (-2.0, 2.0)),
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>图 12.4：用对数累积赔率重新描述离散分布</title>',
        '<desc>左图显示一至七档道德许可回答的频数，中图显示累积比例，右图显示前六档回答的对数累积赔率；第七档为正无穷而未画出。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    for panel_index, (panel_x, title, ylabel, yrange) in enumerate(panels):
        left, right, top, bottom = panel_x + 78, panel_x + 370, 92, 520
        ymin, ymax = yrange
        sx = lambda value, left=left, right=right: left + (value - 1) / 6 * (right - left)
        sy = lambda value, top=top, bottom=bottom, ymin=ymin, ymax=ymax: bottom - (value - ymin) / (ymax - ymin) * (bottom - top)
        parts.extend([
            text_el((left + right) / 2, 40, title, size=21, anchor="middle", weight=650),
            f'<rect x="{panel_x}" y="62" width="370" height="500" rx="8" fill="#fff" stroke="{GRID}"/>',
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.7"/>',
            f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}" stroke-width="1.7"/>',
            text_el((left + right) / 2, 552, "回答", size=18, anchor="middle"),
            text_el(panel_x + 22, (top + bottom) / 2, ylabel, size=18, anchor="middle", rotate=-90),
        ])
        for value in responses:
            xx = sx(value)
            parts.extend([
                f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+6}" stroke="{INK}"/>',
                text_el(xx, bottom + 27, value, size=15, anchor="middle"),
            ])
        if panel_index == 0:
            yticks = (0, 500, 1000, 1500, 2000, 2500)
            values = frequencies
        elif panel_index == 1:
            yticks = (0, .2, .4, .6, .8, 1.0)
            values = cumulative
        else:
            yticks = (-2, -1, 0, 1, 2)
            values = logits
        for value in yticks:
            yy = sy(value)
            label = f"{value:.1f}" if panel_index == 1 else f"{value:g}"
            parts.extend([
                f'<line x1="{left-6}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
                text_el(left - 11, yy + 5, label, size=14, anchor="end"),
                f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="4 7"/>',
            ])
        if panel_index == 0:
            for response, value in zip(responses, values):
                xx = sx(response)
                parts.append(f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{sy(value):.1f}" stroke="{INK}" stroke-width="6"/>')
        else:
            sequence = responses if panel_index == 1 else responses[:-1]
            points = [(sx(response), sy(value)) for response, value in zip(sequence, values)]
            parts.append(polyline(points, fill="none", stroke=INK, stroke_width="2.5"))
            for xx, yy in points:
                parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    parts.extend([
        text_el(996, 588, "第 7 档的对数累积赔率为 +∞，未绘制", size=14, anchor="middle", fill="#666860"),
        "</svg>",
    ])
    OUT4.write_text("\n".join(parts) + "\n", encoding="utf-8")


def figure_12_5() -> None:
    """Rebuild cumulative probabilities and the ordered likelihood differences."""
    width, height = 900, 610
    frequencies = [1270, 908, 1072, 2333, 1456, 1447, 1444]
    total = sum(frequencies)
    probabilities = [value / total for value in frequencies]
    cumulative: list[float] = []
    running = 0.0
    for value in probabilities:
        running += value
        cumulative.append(running)
    left, right, top, bottom = 115, 845, 70, 505
    sx = lambda value: left + (value - 1) / 6 * (right - left)
    sy = lambda value: bottom - value * (bottom - top)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>图 12.5：累积概率与有序 likelihood</title>',
        '<desc>灰色竖线表示一至七档结果的累积概率，蓝色竖线段表示相邻累积概率之差，也就是各档结果的离散 likelihood。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        f'<rect x="45" y="35" width="825" height="535" rx="8" fill="#fff" stroke="{GRID}"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.7"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}" stroke-width="1.7"/>',
    ]
    for value in range(1, 8):
        xx = sx(value)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+7}" stroke="{INK}"/>',
            text_el(xx, bottom + 30, value, size=17, anchor="middle"),
        ])
    for value in (0, .2, .4, .6, .8, 1.0):
        yy = sy(value)
        parts.extend([
            f'<line x1="{left-7}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
            text_el(left - 13, yy + 5, f"{value:.1f}", size=16, anchor="end"),
            f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="4 7"/>',
        ])
    cumulative_points = [(sx(response), sy(value)) for response, value in zip(range(1, 8), cumulative)]
    parts.append(polyline(cumulative_points, fill="none", stroke=INK, stroke_width="2.5", stroke_dasharray="12 9"))
    previous = 0.0
    for response, value in enumerate(cumulative, 1):
        xx, yy = sx(response), sy(value)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{yy:.1f}" stroke="#bcbdb9" stroke-width="7"/>',
            f'<line x1="{xx+13:.1f}" y1="{sy(previous):.1f}" x2="{xx+13:.1f}" y2="{yy:.1f}" stroke="{BLUE}" stroke-width="7"/>',
            f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>',
            text_el(xx + 22, (sy(previous) + yy) / 2 + 6, response, size=17, fill=BLUE),
        ])
        previous = value
    parts.extend([
        text_el((left + right) / 2, 585, "回答", size=20, anchor="middle"),
        text_el(25, (top + bottom) / 2, "累积比例", size=20, anchor="middle", rotate=-90),
        '<line x1="205" y1="548" x2="250" y2="548" stroke="#bcbdb9" stroke-width="7"/><text x="265" y="554" font-family="-apple-system,BlinkMacSystemFont,PingFang SC,sans-serif" font-size="16" fill="#30332e">累积概率</text>',
        f'<line x1="430" y1="548" x2="475" y2="548" stroke="{BLUE}" stroke-width="7"/><text x="490" y="554" font-family="-apple-system,BlinkMacSystemFont,PingFang SC,sans-serif" font-size="16" fill="#30332e">离散概率（likelihood）</text>',
        "</svg>",
    ])
    OUT5.write_text("\n".join(parts) + "\n", encoding="utf-8")


def trolley_slope_plot() -> None:
    """Rebuild the marginal posterior plot produced by code 12.25."""
    width, height = 900, 460
    rows = [
        ("bIC", -1.23, -1.38, -1.09),
        ("bIA", -0.43, -0.55, -0.31),
        ("bC", -0.35, -0.45, -0.24),
        ("bI", -0.29, -0.38, -0.20),
        ("bA", -0.47, -0.56, -0.39),
    ]
    left, right, top, bottom = 150, 840, 70, 375
    sx = lambda value: left + (value + 1.4) / 1.4 * (right - left)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>代码 12.25：电车模型斜率的边际后验分布</title>',
        '<desc>五个斜率的后验均值和百分之八十九相容区间全部位于零以下，其中意图与接触的交互 bIC 最负。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        f'<rect x="45" y="35" width="825" height="375" rx="8" fill="#fff" stroke="{GRID}"/>',
    ]
    for tick_index in range(8):
        value = -1.4 + .2 * tick_index
        xx = sx(value)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{bottom}" stroke="{GRID}" stroke-dasharray="4 7"/>',
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+7}" stroke="{INK}"/>',
            text_el(xx, bottom + 29, f"{value:.1f}", size=15, anchor="middle"),
        ])
    for index, (label, mean, low, high) in enumerate(rows):
        yy = top + 35 + index * 55
        parts.extend([
            text_el(left - 24, yy + 6, label, size=18, anchor="end", weight=650),
            f'<line x1="{sx(low):.1f}" y1="{yy}" x2="{sx(high):.1f}" y2="{yy}" stroke="{INK}" stroke-width="4"/>',
            f'<circle cx="{sx(mean):.1f}" cy="{yy}" r="7" fill="{BLUE}" stroke="#fff" stroke-width="2"/>',
        ])
    parts.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.7"/>',
        text_el((left + right) / 2, 444, "参数值（89% 相容区间）", size=19, anchor="middle"),
        "</svg>",
    ])
    OUT6.write_text("\n".join(parts) + "\n", encoding="utf-8")


def trolley_prediction_plot() -> None:
    """Rebuild the six-panel posterior prediction display in Figure 12.6."""
    width, height = 1200, 760
    scenarios = [
        ("action=0, contact=0", [64, 61, 83, 204, 159, 170, 191], [73, 69, 112, 200, 157, 159, 217]),
        ("action=1, contact=0", [100, 72, 109, 230, 128, 120, 127], [179, 92, 148, 247, 92, 87, 83]),
        ("action=0, contact=1", [91, 80, 105, 225, 122, 157, 156], [330, 151, 126, 213, 61, 44, 39]),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>图 12.6：含交互项的有序类别模型后验预测</title>',
        '<desc>上排三个面板显示不同的行动与接触组合下，意图从零变为一时六条累积概率边界的变化；下排用黑色与蓝色线段比较相应的模拟回答频数。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    columns = [70, 430, 790]
    panel_width = 300
    top_y0, top_y1 = 80, 320
    bottom_y0, bottom_y1 = 450, 675

    for panel_index, (title, count0, count1) in enumerate(scenarios):
        panel_left = columns[panel_index]
        axis_left, axis_right = panel_left + 54, panel_left + panel_width
        sx = lambda value, left=axis_left, right=axis_right: left + value * (right - left)
        sy = lambda value, top=top_y0, bottom=top_y1: bottom - value * (bottom - top)
        totals = (sum(count0), sum(count1))
        cumulative0 = [sum(count0[:index]) / totals[0] for index in range(1, 7)]
        cumulative1 = [sum(count1[:index]) / totals[1] for index in range(1, 7)]
        parts.extend([
            text_el((axis_left + axis_right) / 2, 42, title, size=19, anchor="middle", weight=650),
            f'<rect x="{panel_left}" y="55" width="{panel_width + 20}" height="310" rx="8" fill="#fff" stroke="{GRID}"/>',
        ])
        for tick in (0.0, 0.5, 1.0):
            yy = sy(tick)
            parts.extend([
                f'<line x1="{axis_left-6}" y1="{yy:.1f}" x2="{axis_left}" y2="{yy:.1f}" stroke="{INK}"/>',
                text_el(axis_left - 11, yy + 5, f"{tick:.1f}", size=14, anchor="end"),
            ])
        for tick in (0, 1):
            xx = sx(tick)
            parts.extend([
                f'<line x1="{xx:.1f}" y1="{top_y1}" x2="{xx:.1f}" y2="{top_y1+6}" stroke="{INK}"/>',
                text_el(xx, top_y1 + 25, tick, size=14, anchor="middle"),
            ])
        parts.extend([
            f'<line x1="{axis_left}" y1="{top_y1}" x2="{axis_right}" y2="{top_y1}" stroke="{INK}" stroke-width="1.6"/>',
            f'<line x1="{axis_left}" y1="{top_y1}" x2="{axis_left}" y2="{top_y0}" stroke="{INK}" stroke-width="1.6"/>',
            text_el((axis_left + axis_right) / 2, 356, "意图", size=17, anchor="middle"),
            text_el(panel_left + 17, (top_y0 + top_y1) / 2, "累积概率", size=17, anchor="middle", rotate=-90),
        ])
        for boundary, (p0, p1) in enumerate(zip(cumulative0, cumulative1)):
            for variation in (-0.012, -0.006, 0.006, 0.012):
                sign = -1 if boundary % 2 else 1
                y0 = sy(max(0, min(1, p0 + variation * sign)))
                y1 = sy(max(0, min(1, p1 + variation)))
                parts.append(f'<line x1="{sx(0):.1f}" y1="{y0:.1f}" x2="{sx(1):.1f}" y2="{y1:.1f}" stroke="#777a74" stroke-width="1" opacity=".22"/>')
            parts.extend([
                f'<line x1="{sx(0):.1f}" y1="{sy(p0):.1f}" x2="{sx(1):.1f}" y2="{sy(p1):.1f}" stroke="{INK}" stroke-width="3"/>',
                f'<circle cx="{sx(0):.1f}" cy="{sy(p0):.1f}" r="5" fill="{BLUE}"/>',
                f'<circle cx="{sx(1):.1f}" cy="{sy(p1):.1f}" r="5" fill="{BLUE}"/>',
            ])

        hist_left, hist_right = axis_left, axis_right
        hx = lambda value, left=hist_left, right=hist_right: left + (value - 1) / 6 * (right - left)
        hy = lambda value, top=bottom_y0, bottom=bottom_y1: bottom - value / 350 * (bottom - top)
        parts.extend([
            text_el((hist_left + hist_right) / 2, 415, title, size=19, anchor="middle", weight=650),
            f'<rect x="{panel_left}" y="425" width="{panel_width + 20}" height="310" rx="8" fill="#fff" stroke="{GRID}"/>',
        ])
        for tick in (0, 100, 200, 300):
            yy = hy(tick)
            parts.extend([
                f'<line x1="{hist_left-6}" y1="{yy:.1f}" x2="{hist_left}" y2="{yy:.1f}" stroke="{INK}"/>',
                text_el(hist_left - 11, yy + 5, tick, size=14, anchor="end"),
            ])
        for category in range(1, 8):
            xx = hx(category)
            parts.extend([
                f'<line x1="{xx:.1f}" y1="{bottom_y1}" x2="{xx:.1f}" y2="{bottom_y1+6}" stroke="{INK}"/>',
                text_el(xx, bottom_y1 + 24, category, size=14, anchor="middle"),
                f'<line x1="{xx-4:.1f}" y1="{bottom_y1}" x2="{xx-4:.1f}" y2="{hy(count0[category-1]):.1f}" stroke="{INK}" stroke-width="4"/>',
                f'<line x1="{xx+4:.1f}" y1="{bottom_y1}" x2="{xx+4:.1f}" y2="{hy(count1[category-1]):.1f}" stroke="{BLUE}" stroke-width="4"/>',
            ])
        parts.extend([
            f'<line x1="{hist_left}" y1="{bottom_y1}" x2="{hist_right}" y2="{bottom_y1}" stroke="{INK}" stroke-width="1.6"/>',
            f'<line x1="{hist_left}" y1="{bottom_y1}" x2="{hist_left}" y2="{bottom_y0}" stroke="{INK}" stroke-width="1.6"/>',
            text_el((hist_left + hist_right) / 2, 724, "回答", size=17, anchor="middle"),
            text_el(panel_left + 17, (bottom_y0 + bottom_y1) / 2, "频数", size=17, anchor="middle", rotate=-90),
        ])

    parts.extend([
        '<line x1="890" y1="746" x2="925" y2="746" stroke="#30332e" stroke-width="4"/>',
        text_el(934, 752, "意图 = 0", size=14),
        '<line x1="1035" y1="746" x2="1070" y2="746" stroke="#6670ee" stroke-width="4"/>',
        text_el(1079, 752, "意图 = 1", size=14),
        "</svg>",
    ])
    OUT7.write_text("\n".join(parts) + "\n", encoding="utf-8")


def dirichlet_prior_plot() -> None:
    """Rebuild Figure 12.7 with deterministic Dirichlet(2, ..., 2) draws."""
    width, height = 900, 560
    left, right, top, bottom = 110, 830, 55, 455
    sx = lambda index: left + (index - 1) / 6 * (right - left)
    sy = lambda value: bottom - value / 0.4 * (bottom - top)
    rng = random.Random(1805)
    draws: list[list[float]] = []
    for _ in range(10):
        while True:
            values = [rng.gammavariate(2.0, 1.0) for _ in range(7)]
            total = sum(values)
            draw = [value / total for value in values]
            if max(draw) <= 0.36:
                draws.append(draw)
                break
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>图 12.7：Dirichlet 先验的模拟抽样</title>',
        '<desc>十个由七个概率组成的 Dirichlet 先验向量，每个向量之和为一；第三个向量以粗黑线突出显示。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        '<rect x="45" y="25" width="825" height="500" rx="8" fill="#fff" stroke="#d9d5c8"/>',
    ]
    for tick in (0.0, 0.1, 0.2, 0.3, 0.4):
        yy = sy(tick)
        parts.extend([
            f'<line x1="{left-7}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>',
            f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="4 7"/>',
            text_el(left - 14, yy + 5, f"{tick:.1f}", size=15, anchor="end"),
        ])
    for index in range(1, 8):
        xx = sx(index)
        parts.extend([
            f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom+7}" stroke="{INK}"/>',
            text_el(xx, bottom + 28, index, size=15, anchor="middle"),
        ])
    parts.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.7"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}" stroke-width="1.7"/>',
        text_el((left + right) / 2, 520, "索引", size=19, anchor="middle"),
        text_el(28, (top + bottom) / 2, "概率", size=19, anchor="middle", rotate=-90),
    ])
    for draw_index, values in enumerate(draws):
        if draw_index == 2:
            continue
        points = [(sx(index + 1), sy(value)) for index, value in enumerate(values)]
        parts.append(polyline(points, fill="none", stroke="#555852", stroke_width="1.7", opacity="0.72"))
        for xx, yy in points:
            parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4.5" fill="#fff" stroke="#555852" stroke-width="1.5"/>')
    highlighted = [(sx(index + 1), sy(value)) for index, value in enumerate(draws[2])]
    parts.append(polyline(highlighted, fill="none", stroke=INK, stroke_width="4.2"))
    for xx, yy in highlighted:
        parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="5.5" fill="{INK}" stroke="#fff" stroke-width="1.5"/>')
    parts.append("</svg>")
    OUT8.write_text("\n".join(parts) + "\n", encoding="utf-8")


def education_pairs_plot() -> None:
    """Rebuild the posterior pairs display for incremental education effects."""
    width, height = 1200, 1040
    labels = ["Elem", "MidSch", "SHS", "HSG", "SCol", "Bach", "Mast"]
    means = [0.23, 0.14, 0.19, 0.17, 0.04, 0.10, 0.12]
    concentration = 8.0
    rng = random.Random(1208)
    draws: list[list[float]] = []
    for _ in range(320):
        values = [rng.gammavariate(max(mean * concentration, 0.12), 1.0) for mean in means]
        total = sum(values)
        draws.append([value / total for value in values])

    def correlation(x: list[float], y: list[float]) -> float:
        mx, my = sum(x) / len(x), sum(y) / len(y)
        numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
        denominator = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
        return numerator / denominator

    margin, cell, gap = 92, 126, 5
    grid = 7 * cell + 6 * gap
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>图 12.8：教育增量效应的后验配对图</title>',
        '<desc>七个教育增量效应的边际密度、两两散点与相关系数。由于这些参数之和为一，绝大多数两两相关为负。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
        f'<rect x="40" y="25" width="{grid + 104}" height="{grid + 86}" rx="10" fill="#fff" stroke="{GRID}"/>',
    ]
    columns = [[draw[index] for draw in draws] for index in range(7)]
    max_values = [max(column) * 1.04 for column in columns]

    for row in range(7):
        for col in range(7):
            x0 = margin + col * (cell + gap)
            y0 = 55 + row * (cell + gap)
            parts.append(f'<rect x="{x0}" y="{y0}" width="{cell}" height="{cell}" fill="#fff" stroke="#5f625c" stroke-width="1.1"/>')
            if row == col:
                values = columns[row]
                limit = max_values[row]
                bins = 18
                counts = [0] * bins
                for value in values:
                    counts[min(bins - 1, int(value / limit * bins))] += 1
                peak = max(counts)
                points = [(x0 + index / (bins - 1) * cell, y0 + cell - 10 - count / peak * (cell - 42)) for index, count in enumerate(counts)]
                parts.extend([
                    polygon([(x0, y0 + cell - 10), *points, (x0 + cell, y0 + cell - 10)], fill="#dce8f4", opacity=".85"),
                    polyline(points, fill="none", stroke=INK, stroke_width="2.2"),
                    text_el(x0 + 9, y0 + 23, labels[row], size=17, weight=650),
                ])
            elif row < col:
                x_limit, y_limit = max_values[col], max_values[row]
                for draw in draws[::2]:
                    xx = x0 + 7 + draw[col] / x_limit * (cell - 14)
                    yy = y0 + cell - 7 - draw[row] / y_limit * (cell - 14)
                    parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="2.4" fill="#43a0d5" opacity=".28"/>')
            else:
                value = correlation(columns[col], columns[row])
                parts.append(text_el(x0 + cell / 2, y0 + cell / 2 + 8, f"{value:.2f}", size=22, anchor="middle", weight=600))

    parts.extend([
        text_el(margin + grid / 2, 1008, "教育增量参数", size=20, anchor="middle", weight=650),
        text_el(24, 55 + grid / 2, "后验分布与两两相关", size=20, anchor="middle", weight=650, rotate=-90),
        "</svg>",
    ])
    OUT9.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
    figure_12_2()
    figure_12_3()
    figure_12_4()
    figure_12_5()
    trolley_slope_plot()
    trolley_prediction_plot()
    dirichlet_prior_plot()
    education_pairs_plot()
    for path in (OUT1, OUT2, OUT3, OUT4, OUT5, OUT6, OUT7, OUT8, OUT9):
        print(path)
