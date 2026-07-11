#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-03-dummy-water-histogram.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def main() -> int:
    trials, probability, simulations = 9, 0.7, 100_000
    counts = [
        simulations
        * math.comb(trials, waters)
        * (probability**waters)
        * ((1 - probability) ** (trials - waters))
        for waters in range(trials + 1)
    ]

    width, height = 900, 500
    plot_x, plot_y = 105, 55
    plot_width, plot_height = 720, 335
    ymax = 30_000
    slot = plot_width / len(counts)
    bar_width = slot * 0.64
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>九次地球仪投掷的模拟水域次数</title>",
        "  <desc>十万次模拟中，水域次数集中在六次和七次，假设真实水域比例为零点七。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <rect x="{plot_x}" y="{plot_y}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#363934" stroke-width="1.3"/>',
    ]
    for index, count in enumerate(counts):
        bar_height = plot_height * count / ymax
        x = plot_x + index * slot + (slot - bar_width) / 2
        y = plot_y + plot_height - bar_height
        body.append(
            f'  <rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(bar_width)}" height="{fmt(bar_height)}" fill="#6670ee" opacity="0.88"/>'
        )
        tick_x = plot_x + (index + 0.5) * slot
        body.extend(
            [
                f'  <line x1="{fmt(tick_x)}" y1="{plot_y + plot_height}" x2="{fmt(tick_x)}" y2="{plot_y + plot_height + 7}" stroke="#363934"/>',
                f'  <text x="{fmt(tick_x)}" y="{plot_y + plot_height + 28}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="#30332e">{index}</text>',
            ]
        )
    for value in (0, 5_000, 10_000, 15_000, 20_000, 25_000, 30_000):
        y = plot_y + plot_height * (1 - value / ymax)
        body.extend(
            [
                f'  <line x1="{plot_x - 7}" y1="{fmt(y)}" x2="{plot_x}" y2="{fmt(y)}" stroke="#363934"/>',
                f'  <text x="{plot_x - 13}" y="{fmt(y + 5)}" text-anchor="end" font-family="{FONT}" font-size="14" fill="#30332e">{value:,}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{fmt(plot_x + plot_width / 2)}" y="455" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">模拟水域次数</text>',
            f'  <text x="34" y="{fmt(plot_y + plot_height / 2)}" transform="rotate(-90 34 {fmt(plot_y + plot_height / 2)})" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">频数</text>',
            "</svg>",
            "",
        ]
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
