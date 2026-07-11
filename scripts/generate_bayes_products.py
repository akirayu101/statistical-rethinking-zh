#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-02-bayes-products.svg"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def path_for(values: list[float], *, x: float, y: float, width: float, height: float) -> str:
    maximum = max(values) or 1
    commands: list[str] = []
    for index, value in enumerate(values):
        px = x + width * index / (len(values) - 1)
        py = y + height - (height - 10) * value / maximum
        commands.append(("M" if index == 0 else "L") + f"{fmt(px)} {fmt(py)}")
    return " ".join(commands)


def main() -> int:
    width, height = 1160, 890
    panel_width, panel_height = 260, 185
    gap_x, gap_y = 110, 68
    origin_x, origin_y = 80, 105
    plot_left, plot_top = 20, 14
    plot_width, plot_height = 220, 140
    font = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
    samples = [index / 160 for index in range(161)]

    likelihood = [(p**6) * ((1 - p) ** 3) for p in samples]
    priors = [
        [1.0 for _ in samples],
        [0.0 if p < 0.5 else 1.0 for p in samples],
        [math.exp(-6 * abs(p - 0.5)) for p in samples],
    ]

    body: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>先验与似然相乘生成后验</title>",
        "  <desc>三行依次展示平坦先验、阶梯先验和尖峰先验与同一个似然相乘，得到不同后验分布。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    headings = ("先验", "似然", "后验")
    for col, heading in enumerate(headings):
        center = origin_x + col * (panel_width + gap_x) + panel_width / 2
        body.append(
            f'  <text x="{fmt(center)}" y="48" text-anchor="middle" font-family="{font}" font-size="23" font-weight="700" fill="#263f86">{heading}</text>'
        )

    for row, prior in enumerate(priors):
        posterior = [a * b for a, b in zip(prior, likelihood)]
        series = (prior, likelihood, posterior)
        y0 = origin_y + row * (panel_height + gap_y)

        for col, values in enumerate(series):
            x0 = origin_x + col * (panel_width + gap_x)
            x_plot = x0 + plot_left
            y_plot = y0 + plot_top
            body.append(f'  <g id="row-{row + 1}-col-{col + 1}">')
            body.append(
                f'    <rect x="{fmt(x_plot)}" y="{fmt(y_plot)}" width="{plot_width}" height="{plot_height}" fill="none" stroke="#41443e" stroke-width="1.2"/>'
            )
            for tick, label in ((0.0, "0"), (0.5, "0.5"), (1.0, "1")):
                tx = x_plot + tick * plot_width
                body.extend(
                    [
                        f'    <line x1="{fmt(tx)}" y1="{fmt(y_plot + plot_height)}" x2="{fmt(tx)}" y2="{fmt(y_plot + plot_height + 9)}" stroke="#41443e"/>',
                        f'    <text x="{fmt(tx)}" y="{fmt(y_plot + plot_height + 29)}" text-anchor="middle" font-family="{font}" font-size="15" fill="#30332e">{label}</text>',
                    ]
                )
            body.append(
                f'    <path d="{path_for(list(values), x=x_plot + 8, y=y_plot + 8, width=plot_width - 16, height=plot_height - 16)}" fill="none" stroke="#172860" stroke-width="2.2"/>'
            )
            body.append("  </g>")

        symbol_y = y0 + plot_top + plot_height / 2 + 8
        body.extend(
            [
                f'  <text x="{fmt(origin_x + panel_width + gap_x / 2)}" y="{fmt(symbol_y)}" text-anchor="middle" font-family="{font}" font-size="46" fill="#30332e">×</text>',
                f'  <text x="{fmt(origin_x + 2 * panel_width + gap_x * 1.5)}" y="{fmt(symbol_y)}" text-anchor="middle" font-family="{font}" font-size="46" fill="#30332e">∝</text>',
            ]
        )

    labels = (
        "平坦先验：后验与似然同形",
        "阶梯先验：排除 p &lt; 0.5",
        "尖峰先验：后验发生偏移与偏斜",
    )
    for row, label in enumerate(labels):
        y = origin_y + row * (panel_height + gap_y) + panel_height + 45
        body.append(
            f'  <text x="{width / 2}" y="{fmt(y)}" text-anchor="middle" font-family="{font}" font-size="17" fill="#5d6059">{label}</text>'
        )

    body.extend(["</svg>", ""])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
