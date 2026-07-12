#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG for Chapter 7 Figure 7.6."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-07-train-test-deviance.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


PANELS = [
    {
        "title": "N = 20",
        "ylim": (43, 68),
        "ticks": [45, 50, 55, 60, 65],
        "inside": [55.4, 54.2, 50.7, 49.7, 48.8],
        "inside_sd": [6.2, 6.0, 4.9, 4.6, 4.6],
        "outside": [57.7, 58.4, 55.8, 57.1, 58.7],
        "outside_sd": [7.0, 6.8, 6.8, 7.3, 8.3],
    },
    {
        "title": "N = 100",
        "ylim": (248, 302),
        "ticks": [250, 260, 270, 280, 290, 300],
        "inside": [282.5, 278.2, 262.3, 261.8, 260.8],
        "inside_sd": [14.3, 13.6, 11.2, 11.5, 12.0],
        "outside": [285.0, 282.7, 267.5, 268.6, 269.0],
        "outside_sd": [14.5, 14.0, 11.8, 12.8, 12.4],
    },
]


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def main() -> int:
    width, height = 1200, 620
    top, plot_height, plot_width = 85, 390, 430
    panel_lefts = [125, 660]
    blue = "#6670ee"
    black = "#30332e"
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>训练样本内与测试样本外的离差</title>",
        "<desc>左图样本量二十，右图样本量一百。训练离差随参数增多持续下降；测试离差在三个参数附近最低，之后上升。点表示一万次模拟的均值，线段表示正负一个标准差。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]
    for left, panel in zip(panel_lefts, PANELS):
        ymin, ymax = panel["ylim"]

        def py(value: float) -> float:
            return top + plot_height - (value - ymin) / (ymax - ymin) * plot_height

        def px(index: int, offset: float = 0) -> float:
            return left + 35 + index * (plot_width - 70) / 4 + offset

        body.extend([
            f'<text x="{left + plot_width / 2}" y="48" text-anchor="middle" font-family="{FONT}" font-size="24" font-weight="700" fill="#263f86">{panel["title"]}</text>',
            f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
        ])
        for tick in panel["ticks"]:
            y = py(tick)
            body.extend([
                f'<line x1="{left - 7}" y1="{fmt(y)}" x2="{left}" y2="{fmt(y)}" stroke="#343732"/>',
                f'<text x="{left - 16}" y="{fmt(y + 6)}" text-anchor="end" font-family="{FONT}" font-size="17" fill="{black}">{tick}</text>',
            ])
        for index in range(5):
            x_in = px(index)
            x_out = px(index, 13)
            body.extend([
                f'<line x1="{fmt(x_in)}" y1="{fmt(py(panel["inside"][index] - panel["inside_sd"][index]))}" x2="{fmt(x_in)}" y2="{fmt(py(panel["inside"][index] + panel["inside_sd"][index]))}" stroke="{blue}" stroke-width="2"/>',
                f'<circle cx="{fmt(x_in)}" cy="{fmt(py(panel["inside"][index]))}" r="5.5" fill="{blue}"/>',
                f'<line x1="{fmt(x_out)}" y1="{fmt(py(panel["outside"][index] - panel["outside_sd"][index]))}" x2="{fmt(x_out)}" y2="{fmt(py(panel["outside"][index] + panel["outside_sd"][index]))}" stroke="{black}" stroke-width="2"/>',
                f'<circle cx="{fmt(x_out)}" cy="{fmt(py(panel["outside"][index]))}" r="5.5" fill="#fff" stroke="{black}" stroke-width="2"/>',
                f'<line x1="{fmt(px(index))}" y1="{top + plot_height}" x2="{fmt(px(index))}" y2="{top + plot_height + 7}" stroke="#343732"/>',
                f'<text x="{fmt(px(index))}" y="{top + plot_height + 31}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="{black}">{index + 1}</text>',
            ])
        body.extend([
            f'<text x="{left + plot_width / 2}" y="548" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">参数个数</text>',
            f'<text x="{left - 68}" y="{top + plot_height / 2}" transform="rotate(-90 {left - 68} {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">离差</text>',
        ])
    body.extend([
        f'<circle cx="505" cy="588" r="5.5" fill="{blue}"/><text x="520" y="595" font-family="{FONT}" font-size="18" fill="{blue}">样本内（训练）</text>',
        f'<circle cx="695" cy="588" r="5.5" fill="#fff" stroke="{black}" stroke-width="2"/><text x="710" y="595" font-family="{FONT}" font-size="18" fill="{black}">样本外（测试）</text>',
        "</svg>",
        "",
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
