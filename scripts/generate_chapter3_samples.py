#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-03-posterior-samples.svg"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def main() -> int:
    rng = random.Random(30301)
    grid = [index / 999 for index in range(1000)]
    weights = [(p**6) * ((1 - p) ** 3) for p in grid]
    samples = rng.choices(grid, weights=weights, k=10_000)

    width, height = 1200, 520
    plot_top, plot_height = 42, 330
    left_x, left_width = 95, 445
    right_x, right_width = 700, 405
    font = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"

    scatter: list[str] = []
    for index, sample in enumerate(samples):
        x = left_x + left_width * index / (len(samples) - 1)
        y = plot_top + plot_height * (1 - sample)
        scatter.append(f"M{fmt(x)} {fmt(y)}h.01")

    bandwidth = 0.035
    density_x = [index / 200 for index in range(201)]
    scale = 1 / (len(samples) * bandwidth * math.sqrt(2 * math.pi))
    density = [
        scale * sum(math.exp(-0.5 * ((x - sample) / bandwidth) ** 2) for sample in samples)
        for x in density_x
    ]
    density_max = 3.2
    density_path = " ".join(
        ("M" if index == 0 else "L")
        + f"{fmt(right_x + right_width * x)} {fmt(plot_top + plot_height * (1 - value / density_max))}"
        for index, (x, value) in enumerate(zip(density_x, density))
    )

    body: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>从地球仪投掷模型的后验分布中抽样</title>",
        "  <desc>左图按抽取顺序显示一万个水域比例样本，右图显示这些样本在各参数值处的密度估计。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <rect x="{left_x}" y="{plot_top}" width="{left_width}" height="{plot_height}" fill="#fff" stroke="#363934" stroke-width="1.3"/>',
        f'  <path d="{" ".join(scatter)}" fill="none" stroke="#5867ed" stroke-width="1.7" stroke-linecap="round" opacity="0.48"/>',
        f'  <rect x="{right_x}" y="{plot_top}" width="{right_width}" height="{plot_height}" fill="#fff" stroke="#363934" stroke-width="1.3"/>',
        f'  <path d="{density_path}" fill="none" stroke="#5867ed" stroke-width="3"/>',
    ]

    for value, label in ((0, "0"), (2500, "2500"), (5000, "5000"), (7500, "7500"), (9999, "10000")):
        x = left_x + left_width * value / 9999
        body.extend(
            [
                f'  <line x1="{fmt(x)}" y1="{plot_top + plot_height}" x2="{fmt(x)}" y2="{plot_top + plot_height + 8}" stroke="#363934"/>',
                f'  <text x="{fmt(x)}" y="{plot_top + plot_height + 30}" text-anchor="middle" font-family="{font}" font-size="14" fill="#30332e">{label}</text>',
            ]
        )
    for value, label in ((0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1, "1")):
        y = plot_top + plot_height * (1 - value)
        body.extend(
            [
                f'  <line x1="{left_x - 8}" y1="{fmt(y)}" x2="{left_x}" y2="{fmt(y)}" stroke="#363934"/>',
                f'  <text x="{left_x - 13}" y="{fmt(y + 5)}" text-anchor="end" font-family="{font}" font-size="14" fill="#30332e">{label}</text>',
            ]
        )
    for value, label in ((0, "0"), (0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8"), (1, "1")):
        x = right_x + right_width * value
        body.extend(
            [
                f'  <line x1="{fmt(x)}" y1="{plot_top + plot_height}" x2="{fmt(x)}" y2="{plot_top + plot_height + 8}" stroke="#363934"/>',
                f'  <text x="{fmt(x)}" y="{plot_top + plot_height + 30}" text-anchor="middle" font-family="{font}" font-size="14" fill="#30332e">{label}</text>',
            ]
        )
    for value in (0, 1, 2, 3):
        y = plot_top + plot_height * (1 - value / density_max)
        body.extend(
            [
                f'  <line x1="{right_x - 8}" y1="{fmt(y)}" x2="{right_x}" y2="{fmt(y)}" stroke="#363934"/>',
                f'  <text x="{right_x - 13}" y="{fmt(y + 5)}" text-anchor="end" font-family="{font}" font-size="14" fill="#30332e">{value}</text>',
            ]
        )

    body.extend(
        [
            f'  <text x="{fmt(left_x + left_width / 2)}" y="430" text-anchor="middle" font-family="{font}" font-size="18" fill="#30332e">样本序号</text>',
            f'  <text x="35" y="{fmt(plot_top + plot_height / 2)}" transform="rotate(-90 35 {fmt(plot_top + plot_height / 2)})" text-anchor="middle" font-family="{font}" font-size="18" fill="#30332e">水域比例（p）</text>',
            f'  <text x="{fmt(right_x + right_width / 2)}" y="430" text-anchor="middle" font-family="{font}" font-size="18" fill="#30332e">水域比例（p）</text>',
            f'  <text x="635" y="{fmt(plot_top + plot_height / 2)}" transform="rotate(-90 635 {fmt(plot_top + plot_height / 2)})" text-anchor="middle" font-family="{font}" font-size="18" fill="#30332e">密度</text>',
            f'  <text x="{fmt(left_x + left_width / 2)}" y="482" text-anchor="middle" font-family="{font}" font-size="17" font-weight="700" fill="#263f86">10,000 个后验样本</text>',
            f'  <text x="{fmt(right_x + right_width / 2)}" y="482" text-anchor="middle" font-family="{font}" font-size="17" font-weight="700" fill="#263f86">样本密度估计</text>',
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
