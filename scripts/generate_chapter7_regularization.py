#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Chapter 7 Figures 7.7 and 7.8."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "translations" / "zh" / "media"
PRIORS_OUT = MEDIA / "chapter-07-regularizing-priors.svg"
DEVIANCE_OUT = MEDIA / "chapter-07-regularized-deviance.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"
BLUE = "#6670ee"
BLACK = "#30332e"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def normal_density(value: float, sigma: float) -> float:
    return math.exp(-0.5 * (value / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def generate_priors() -> None:
    width, height = 900, 560
    left, top, plot_width, plot_height = 125, 65, 690, 390

    def px(value: float) -> float:
        return left + (value + 3.25) / 6.5 * plot_width

    def py(value: float) -> float:
        return top + plot_height - value / 2.15 * plot_height

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>强弱不同的三个正则化高斯先验</title>",
        "<desc>均值都为零，标准差分别为一、零点五和零点二。先验越强，密度越集中在零附近。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
    ]
    styles = [(1.0, "7 7", 2.2), (0.5, "", 2.2), (0.2, "", 4.5)]
    for sigma, dash, stroke_width in styles:
        points = " ".join(
            f"{fmt(px(x))},{fmt(py(normal_density(x, sigma)))}"
            for x in (-3.2 + 6.4 * step / 320 for step in range(321))
        )
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(
            f'<polyline points="{points}" fill="none" stroke="{BLACK}" stroke-width="{stroke_width}"{dash_attr}/>'
        )
    for tick in range(-3, 4):
        x = px(tick)
        body.extend([
            f'<line x1="{fmt(x)}" y1="{top + plot_height}" x2="{fmt(x)}" y2="{top + plot_height + 7}" stroke="#343732"/>',
            f'<text x="{fmt(x)}" y="{top + plot_height + 31}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="{BLACK}">{tick}</text>',
        ])
    for tick in [0, 0.5, 1.0, 1.5, 2.0]:
        y = py(tick)
        body.extend([
            f'<line x1="{left - 7}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#343732"/>',
            f'<text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="17" fill="{BLACK}">{tick:.1f}</text>',
        ])
    body.extend([
        f'<text x="{left + plot_width / 2}" y="525" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">参数值</text>',
        f'<text x="43" y="{top + plot_height / 2}" transform="rotate(-90 43 {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">概率密度</text>',
        "</svg>",
        "",
    ])
    PRIORS_OUT.write_text("\n".join(body), encoding="utf-8")


PANELS = [
    {
        "title": "N = 20",
        "ylim": (47.5, 60.8),
        "ticks": [48, 50, 52, 54, 56, 58, 60],
        "inside_points": [55.6, 54.3, 50.6, 49.8, 49.0],
        "outside_points": [57.7, 58.4, 56.0, 57.4, 58.7],
        "inside_lines": [
            [55.6, 54.0, 50.5, 49.8, 49.0],
            [55.6, 54.5, 50.9, 50.3, 49.8],
            [55.7, 55.0, 52.2, 51.8, 51.3],
        ],
        "outside_lines": [
            [57.6, 58.1, 55.4, 55.8, 56.0],
            [57.6, 57.9, 55.4, 55.8, 55.8],
            [57.7, 57.6, 55.3, 56.1, 56.7],
        ],
    },
    {
        "title": "N = 100",
        "ylim": (259, 286.5),
        "ticks": [260, 265, 270, 275, 280, 285],
        "inside_points": [282.5, 279.5, 263.0, 262.0, 261.3],
        "outside_points": [284.5, 282.9, 268.4, 269.0, 269.6],
        "inside_lines": [
            [282.5, 279.6, 263.0, 262.0, 261.3],
            [282.5, 279.7, 263.5, 262.9, 262.0],
            [282.5, 279.8, 264.0, 263.3, 262.8],
        ],
        "outside_lines": [
            [284.5, 282.8, 268.4, 269.0, 269.7],
            [284.5, 282.8, 268.3, 268.8, 269.4],
            [284.5, 282.7, 268.2, 268.7, 269.2],
        ],
    },
]


def generate_deviance() -> None:
    width, height = 1200, 650
    top, plot_height, plot_width = 75, 400, 430
    panel_lefts = [125, 660]
    line_styles = [("8 7", 2.2), ("", 2.2), ("", 4.2)]
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>正则化先验与样本外离差</title>",
        "<desc>两个样本量下，点表示平坦先验的训练与测试离差；虚线、细实线和粗实线分别表示标准差一、零点五和零点二的正则化先验。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]
    for left, panel in zip(panel_lefts, PANELS):
        ymin, ymax = panel["ylim"]

        def py(value: float) -> float:
            return top + plot_height - (value - ymin) / (ymax - ymin) * plot_height

        def px(index: int) -> float:
            return left + 35 + index * (plot_width - 70) / 4

        body.extend([
            f'<text x="{left + plot_width / 2}" y="43" text-anchor="middle" font-family="{FONT}" font-size="24" font-weight="700" fill="#263f86">{panel["title"]}</text>',
            f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
        ])
        for tick in panel["ticks"]:
            y = py(tick)
            body.extend([
                f'<line x1="{left - 7}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#343732"/>',
                f'<text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="17" fill="{BLACK}">{tick}</text>',
            ])
        for index in range(5):
            body.extend([
                f'<circle cx="{fmt(px(index))}" cy="{fmt(py(panel["inside_points"][index]))}" r="5.2" fill="{BLUE}"/>',
                f'<circle cx="{fmt(px(index))}" cy="{fmt(py(panel["outside_points"][index]))}" r="5.2" fill="#fff" stroke="{BLACK}" stroke-width="2"/>',
                f'<line x1="{fmt(px(index))}" y1="{top + plot_height}" x2="{fmt(px(index))}" y2="{top + plot_height + 7}" stroke="#343732"/>',
                f'<text x="{fmt(px(index))}" y="{top + plot_height + 31}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="{BLACK}">{index + 1}</text>',
            ])
        for color, key in [(BLUE, "inside_lines"), (BLACK, "outside_lines")]:
            for values, (dash, stroke_width) in zip(panel[key], line_styles):
                points = " ".join(f"{fmt(px(i))},{fmt(py(value))}" for i, value in enumerate(values))
                dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
                body.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{stroke_width}"{dash_attr}/>' )
        body.extend([
            f'<text x="{left + plot_width / 2}" y="550" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">参数个数</text>',
            f'<text x="{left - 68}" y="{top + plot_height / 2}" transform="rotate(-90 {left - 68} {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">离差</text>',
        ])
    legend_y = 598
    for x, label, dash, stroke_width in [(370, "Normal(0, 1)", "8 7", 2.2), (590, "Normal(0, 0.5)", "", 2.2), (835, "Normal(0, 0.2)", "", 4.2)]:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        body.extend([
            f'<line x1="{x}" y1="{legend_y}" x2="{x + 56}" y2="{legend_y}" stroke="{BLACK}" stroke-width="{stroke_width}"{dash_attr}/>',
            f'<text x="{x + 68}" y="{legend_y + 6}" font-family="{FONT}" font-size="18" fill="{BLACK}">{label}</text>',
        ])
    body.extend(["</svg>", ""])
    DEVIANCE_OUT.write_text("\n".join(body), encoding="utf-8")


def main() -> int:
    MEDIA.mkdir(parents=True, exist_ok=True)
    generate_priors()
    generate_deviance()
    print(f"generated {PRIORS_OUT}")
    print(f"generated {DEVIANCE_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
