#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG for Chapter 6 Figure 6.5."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-06-grandparents-collider.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def standardize(values: list[float]) -> list[float]:
    mean = sum(values) / len(values)
    sd = math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))
    return [(value - mean) / sd for value in values]


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def main() -> int:
    rng = random.Random(1)
    count = 200
    u = [1 if rng.random() < 0.5 else -1 for _ in range(count)]
    g = [rng.gauss(0, 1) for _ in range(count)]
    p = [rng.gauss(g[i] + 2 * u[i], 1) for i in range(count)]
    c = [rng.gauss(p[i] + 2 * u[i], 1) for i in range(count)]
    gs, ps, cs = standardize(g), standardize(p), standardize(c)
    low, high = percentile(ps, 0.45), percentile(ps, 0.60)
    selected = [i for i, value in enumerate(ps) if low <= value <= high]
    xbar = sum(gs[i] for i in selected) / len(selected)
    ybar = sum(cs[i] for i in selected) / len(selected)
    slope = sum((gs[i] - xbar) * (cs[i] - ybar) for i in selected) / sum((gs[i] - xbar) ** 2 for i in selected)
    intercept = ybar - slope * xbar

    width, height = 900, 680
    left, top, plot_width, plot_height = 115, 90, 700, 470
    xmin, xmax, ymin, ymax = -3.2, 2.8, -2.8, 2.5

    def px(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_width

    def py(value: float) -> float:
        return top + plot_height - (value - ymin) / (ymax - ymin) * plot_height

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>未观测社区因素与三代教育成就中的碰撞点偏差</title>",
        f"<desc>好社区与差社区各形成正向点云，但在父母教育第45至60百分位内，祖父母与孙辈教育的斜率为 {slope:.2f}。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
    ]
    for i, (x, y) in enumerate(zip(gs, cs)):
        color = "#6670ee" if u[i] == 1 else "#30332e"
        if i in selected:
            body.append(f'<circle cx="{px(x):.2f}" cy="{py(y):.2f}" r="6.2" fill="{color}" opacity="0.95"/>')
        else:
            body.append(f'<circle cx="{px(x):.2f}" cy="{py(y):.2f}" r="4.7" fill="#fff" stroke="{color}" stroke-width="1.7"/>')
    selected_x = [gs[i] for i in selected]
    line_start, line_end = min(selected_x), max(selected_x)
    body.append(f'<line x1="{px(line_start):.2f}" y1="{py(intercept + slope * line_start):.2f}" x2="{px(line_end):.2f}" y2="{py(intercept + slope * line_end):.2f}" stroke="#263f86" stroke-width="3"/>')
    for tick in [-3, -2, -1, 0, 1, 2]:
        x = px(tick)
        body.extend([f'<line x1="{x:.2f}" y1="{top + plot_height}" x2="{x:.2f}" y2="{top + plot_height + 7}" stroke="#343732"/>', f'<text x="{x:.2f}" y="{top + plot_height + 30}" text-anchor="middle" font-family="{FONT}" font-size="17">{tick}</text>'])
    for tick in [-2, -1, 0, 1, 2]:
        y = py(tick)
        body.extend([f'<line x1="{left - 7}" y1="{y:.2f}" x2="{left}" y2="{y:.2f}" stroke="#343732"/>', f'<text x="{left - 16}" y="{y + 6:.2f}" text-anchor="end" font-family="{FONT}" font-size="17">{tick}</text>'])
    body.extend([
        f'<text x="{left + plot_width / 2}" y="635" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">祖父母教育程度（G）</text>',
        f'<text x="43" y="{top + plot_height / 2}" transform="rotate(-90 43 {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">孙辈教育程度（C）</text>',
        f'<text x="135" y="45" font-family="{FONT}" font-size="19" font-weight="700" fill="#30332e">父母教育第 45–60 百分位</text>',
        f'<circle cx="555" cy="42" r="5" fill="#6670ee"/><text x="570" y="48" font-family="{FONT}" font-size="17" fill="#6670ee">好社区</text>',
        f'<circle cx="690" cy="42" r="5" fill="#30332e"/><text x="705" y="48" font-family="{FONT}" font-size="17" fill="#30332e">差社区</text>',
        "</svg>",
        "",
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT} (selected slope {slope:.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
