#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-02-globe-learning.svg"
SEQUENCE = "WLWWWLWLW"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def beta_pdf(x: float, alpha: int, beta: int) -> float:
    coefficient = math.gamma(alpha + beta) / (math.gamma(alpha) * math.gamma(beta))
    return coefficient * (x ** (alpha - 1)) * ((1 - x) ** (beta - 1))


def curve_path(
    values: list[float],
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    scale: float,
) -> str:
    points: list[str] = []
    for index, value in enumerate(values):
        px = x + width * index / (len(values) - 1)
        py = y + height - height * value / scale
        points.append(("M" if index == 0 else "L") + f"{fmt(px)} {fmt(py)}")
    return " ".join(points)


def main() -> int:
    width, height = 1200, 1040
    panel_width, panel_height = 320, 275
    gap_x, gap_y = 36, 46
    origin_x, origin_y = 105, 55
    plot_left, plot_top = 58, 52
    plot_width, plot_height = 238, 172
    font = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"

    body: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">',
        "  <title>贝叶斯模型随九次地球仪投掷逐步学习</title>",
        "  <desc>九个面板依次加入水域或陆地观测。虚线表示更新前的可信程度，实线表示纳入最新观测后的可信程度。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    waters = 0
    lands = 0
    samples = [index / 120 for index in range(121)]

    for panel, observation in enumerate(SEQUENCE, start=1):
        row, col = divmod(panel - 1, 3)
        x0 = origin_x + col * (panel_width + gap_x)
        y0 = origin_y + row * (panel_height + gap_y)
        x_plot = x0 + plot_left
        y_plot = y0 + plot_top

        prior_alpha, prior_beta = waters + 1, lands + 1
        if observation == "W":
            waters += 1
        else:
            lands += 1
        post_alpha, post_beta = waters + 1, lands + 1

        prior_values = [beta_pdf(value, prior_alpha, prior_beta) for value in samples]
        posterior_values = [beta_pdf(value, post_alpha, post_beta) for value in samples]
        scale = max(max(prior_values), max(posterior_values)) * 1.06

        body.append(f'  <g id="step-{panel}">')
        for index, label in enumerate(SEQUENCE, start=1):
            color = "#20231f" if index <= panel else "#b7b8b3"
            weight = "700" if index == panel else "400"
            body.append(
                f'    <text x="{fmt(x_plot + (index - 1) * 24)}" y="{fmt(y0 + 24)}" '
                f'font-family="{font}" font-size="18" font-weight="{weight}" fill="{color}">{label}</text>'
            )
        body.extend(
            [
                f'    <rect x="{fmt(x_plot)}" y="{fmt(y_plot)}" width="{plot_width}" height="{plot_height}" fill="none" stroke="#353832" stroke-width="1.2"/>',
                f'    <text x="{fmt(x_plot + 12)}" y="{fmt(y_plot + 28)}" font-family="{font}" font-size="17" fill="#20231f">n = {panel}</text>',
            ]
        )

        for tick, label in ((0.0, "0"), (0.5, "0.5"), (1.0, "1")):
            tx = x_plot + tick * plot_width
            body.extend(
                [
                    f'    <line x1="{fmt(tx)}" y1="{fmt(y_plot + plot_height)}" x2="{fmt(tx)}" y2="{fmt(y_plot + plot_height + 10)}" stroke="#353832"/>',
                    f'    <text x="{fmt(tx)}" y="{fmt(y_plot + plot_height + 31)}" text-anchor="middle" font-family="{font}" font-size="15" fill="#30332e">{label}</text>',
                ]
            )

        body.extend(
            [
                f'    <path d="{curve_path(prior_values, x=x_plot, y=y_plot + 8, width=plot_width, height=plot_height - 16, scale=scale)}" fill="none" stroke="#666962" stroke-width="1.6" stroke-dasharray="7 6"/>',
                f'    <path d="{curve_path(posterior_values, x=x_plot, y=y_plot + 8, width=plot_width, height=plot_height - 16, scale=scale)}" fill="none" stroke="#172860" stroke-width="2.6"/>',
            ]
        )

        if col == 0:
            body.append(
                f'    <text x="{fmt(x0 + 18)}" y="{fmt(y_plot + plot_height / 2)}" transform="rotate(-90 {fmt(x0 + 18)} {fmt(y_plot + plot_height / 2)})" '
                f'text-anchor="middle" font-family="{font}" font-size="17" fill="#30332e">可信程度</text>'
            )
        if row == 2:
            body.append(
                f'    <text x="{fmt(x_plot + plot_width / 2)}" y="{fmt(y_plot + plot_height + 60)}" text-anchor="middle" '
                f'font-family="{font}" font-size="17" fill="#30332e">水域比例</text>'
            )
        body.append("  </g>")

    legend_y = 1010
    body.extend(
        [
            f'  <line x1="390" y1="{legend_y}" x2="455" y2="{legend_y}" stroke="#666962" stroke-width="1.6" stroke-dasharray="7 6"/>',
            f'  <text x="468" y="{legend_y + 6}" font-family="{font}" font-size="16" fill="#30332e">更新前</text>',
            f'  <line x1="610" y1="{legend_y}" x2="675" y2="{legend_y}" stroke="#172860" stroke-width="2.6"/>',
            f'  <text x="688" y="{legend_y + 6}" font-family="{font}" font-size="16" fill="#30332e">更新后</text>',
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
