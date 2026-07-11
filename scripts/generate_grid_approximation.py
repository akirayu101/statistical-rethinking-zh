#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-02-grid-approximation.svg"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def posterior_grid(count: int) -> tuple[list[float], list[float]]:
    points = [index / (count - 1) for index in range(count)]
    weights = [math.comb(9, 6) * (p**6) * ((1 - p) ** 3) for p in points]
    total = sum(weights)
    return points, [weight / total for weight in weights]


def main() -> int:
    width, height = 1080, 500
    panel_width, panel_height = 440, 330
    gap = 80
    origin_x, origin_y = 60, 75
    plot_left, plot_top = 75, 35
    plot_width, plot_height = 325, 225
    font = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"

    body: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>五点与二十点网格近似比较</title>",
        "  <desc>左图使用五个均匀网格点近似后验，形状粗糙；右图使用二十个网格点，已形成平滑而准确的后验轮廓。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    for panel, count in enumerate((5, 20)):
        x0 = origin_x + panel * (panel_width + gap)
        y0 = origin_y
        x_plot = x0 + plot_left
        y_plot = y0 + plot_top
        points, posterior = posterior_grid(count)
        maximum = max(posterior) * 1.08

        coordinates: list[tuple[float, float]] = []
        for p, value in zip(points, posterior):
            px = x_plot + p * plot_width
            py = y_plot + plot_height - value / maximum * plot_height
            coordinates.append((px, py))
        path = " ".join(("M" if index == 0 else "L") + f"{fmt(px)} {fmt(py)}" for index, (px, py) in enumerate(coordinates))

        body.extend(
            [
                f'  <g id="grid-{count}">',
                f'    <text x="{fmt(x_plot + plot_width / 2)}" y="{fmt(y0)}" text-anchor="middle" font-family="{font}" font-size="22" font-weight="700" fill="#263f86">{count} 个点</text>',
                f'    <line x1="{fmt(x_plot)}" y1="{fmt(y_plot + plot_height)}" x2="{fmt(x_plot + plot_width)}" y2="{fmt(y_plot + plot_height)}" stroke="#363934" stroke-width="1.3"/>',
                f'    <line x1="{fmt(x_plot)}" y1="{fmt(y_plot)}" x2="{fmt(x_plot)}" y2="{fmt(y_plot + plot_height)}" stroke="#363934" stroke-width="1.3"/>',
                f'    <path d="{path}" fill="none" stroke="#172860" stroke-width="2.4"/>',
            ]
        )
        for px, py in coordinates:
            body.append(f'    <circle cx="{fmt(px)}" cy="{fmt(py)}" r="4.1" fill="#ffffff" stroke="#172860" stroke-width="2"/>')
        for tick, label in ((0.0, "0"), (0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8"), (1.0, "1")):
            tx = x_plot + tick * plot_width
            body.extend(
                [
                    f'    <line x1="{fmt(tx)}" y1="{fmt(y_plot + plot_height)}" x2="{fmt(tx)}" y2="{fmt(y_plot + plot_height + 8)}" stroke="#363934"/>',
                    f'    <text x="{fmt(tx)}" y="{fmt(y_plot + plot_height + 28)}" text-anchor="middle" font-family="{font}" font-size="14" fill="#30332e">{label}</text>',
                ]
            )
        body.extend(
            [
                f'    <text x="{fmt(x_plot + plot_width / 2)}" y="{fmt(y_plot + plot_height + 62)}" text-anchor="middle" font-family="{font}" font-size="17" fill="#30332e">水域概率</text>',
                f'    <text x="{fmt(x0 + 20)}" y="{fmt(y_plot + plot_height / 2)}" transform="rotate(-90 {fmt(x0 + 20)} {fmt(y_plot + plot_height / 2)})" text-anchor="middle" font-family="{font}" font-size="17" fill="#30332e">后验概率</text>',
                "  </g>",
            ]
        )

    body.extend(["</svg>", ""])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
