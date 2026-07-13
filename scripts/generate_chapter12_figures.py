#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 12."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-12-beta-binomial.svg"


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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
