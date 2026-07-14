#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-02-quadratic-accuracy.svg"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def beta_pdf(x: float, alpha: int, beta: int) -> float:
    coefficient = math.gamma(alpha + beta) / (math.gamma(alpha) * math.gamma(beta))
    return coefficient * (x ** (alpha - 1)) * ((1 - x) ** (beta - 1))


def normal_pdf(x: float, mean: float, sd: float) -> float:
    return math.exp(-0.5 * ((x - mean) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))


def path_for(values: list[float], *, x: float, y: float, width: float, height: float, scale: float) -> str:
    commands: list[str] = []
    for index, value in enumerate(values):
        px = x + width * index / (len(values) - 1)
        py = y + height - (height - 8) * value / scale
        commands.append(("M" if index == 0 else "L") + f"{fmt(px)} {fmt(py)}")
    return " ".join(commands)


def main() -> int:
    width, height = 1200, 470
    panel_width, panel_height = 330, 315
    gap = 40
    origin_x, origin_y = 65, 55
    plot_left, plot_top = 58, 42
    plot_width, plot_height = 245, 205
    font = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
    samples = [index / 200 for index in range(201)]

    body: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>二次近似随样本量增加而改善</title>",
        "  <desc>三个面板比较样本量为九、十八和三十六时的精确后验与高斯二次近似。样本越多，两条曲线越接近。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    for panel, (n, waters) in enumerate(((9, 6), (18, 12), (36, 24))):
        lands = n - waters
        exact = [beta_pdf(p, waters + 1, lands + 1) for p in samples]
        mode = waters / n
        sd = math.sqrt(mode * (1 - mode) / n)
        approximate = [normal_pdf(p, mode, sd) for p in samples]
        scale = max(max(exact), max(approximate)) * 1.06

        x0 = origin_x + panel * (panel_width + gap)
        y0 = origin_y
        x_plot = x0 + plot_left
        y_plot = y0 + plot_top
        body.extend(
            [
                f'  <g id="sample-{n}">',
                f'    <text x="{fmt(x_plot + plot_width / 2)}" y="{fmt(y0)}" text-anchor="middle" font-family="{font}" font-size="21" font-weight="700" fill="#263f86">n = {n}，w = {waters}</text>',
                f'    <line x1="{fmt(x_plot)}" y1="{fmt(y_plot + plot_height)}" x2="{fmt(x_plot + plot_width)}" y2="{fmt(y_plot + plot_height)}" stroke="#363934" stroke-width="1.3"/>',
                f'    <line x1="{fmt(x_plot)}" y1="{fmt(y_plot)}" x2="{fmt(x_plot)}" y2="{fmt(y_plot + plot_height)}" stroke="#363934" stroke-width="1.3"/>',
                f'    <path d="{path_for(exact, x=x_plot, y=y_plot, width=plot_width, height=plot_height, scale=scale)}" fill="none" stroke="#315bd7" stroke-width="2.8"/>',
                f'    <path d="{path_for(approximate, x=x_plot, y=y_plot, width=plot_width, height=plot_height, scale=scale)}" fill="none" stroke="#30332e" stroke-width="2" stroke-dasharray="7 5"/>',
            ]
        )
        for tick, label in ((0.0, "0"), (0.5, "0.5"), (1.0, "1")):
            tx = x_plot + tick * plot_width
            body.extend(
                [
                    f'    <line x1="{fmt(tx)}" y1="{fmt(y_plot + plot_height)}" x2="{fmt(tx)}" y2="{fmt(y_plot + plot_height + 8)}" stroke="#363934"/>',
                    f'    <text x="{fmt(tx)}" y="{fmt(y_plot + plot_height + 28)}" text-anchor="middle" font-family="{font}" font-size="14" fill="#30332e">{label}</text>',
                ]
            )
        body.extend(
            [
                f'    <text x="{fmt(x_plot + plot_width / 2)}" y="{fmt(y_plot + plot_height + 61)}" text-anchor="middle" font-family="{font}" font-size="17" fill="#30332e">水域比例</text>',
                f'    <text x="{fmt(x0 + 17)}" y="{fmt(y_plot + plot_height / 2)}" transform="rotate(-90 {fmt(x0 + 17)} {fmt(y_plot + plot_height / 2)})" text-anchor="middle" font-family="{font}" font-size="17" fill="#30332e">概率密度</text>',
                "  </g>",
            ]
        )

    legend_y = 440
    body.extend(
        [
            f'  <line x1="380" y1="{legend_y}" x2="445" y2="{legend_y}" stroke="#315bd7" stroke-width="2.8"/>',
            f'  <text x="458" y="{legend_y + 6}" font-family="{font}" font-size="16" fill="#30332e">精确后验</text>',
            f'  <line x1="650" y1="{legend_y}" x2="715" y2="{legend_y}" stroke="#30332e" stroke-width="2" stroke-dasharray="7 5"/>',
            f'  <text x="728" y="{legend_y + 6}" font-family="{font}" font-size="16" fill="#30332e">二次近似</text>',
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
