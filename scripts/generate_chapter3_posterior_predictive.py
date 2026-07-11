#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-03-posterior-predictive.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def beta_pdf(x: float, alpha: int, beta: int) -> float:
    coefficient = math.gamma(alpha + beta) / (math.gamma(alpha) * math.gamma(beta))
    return coefficient * (x ** (alpha - 1)) * ((1 - x) ** (beta - 1))


def binomial_pmf(k: int, n: int, p: float) -> float:
    return math.comb(n, k) * (p**k) * ((1 - p) ** (n - k))


def beta_binomial_pmf(k: int, n: int, alpha: int, beta: int) -> float:
    log_value = (
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
        + math.lgamma(k + alpha)
        + math.lgamma(n - k + beta)
        - math.lgamma(n + alpha + beta)
        - (math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta))
    )
    return math.exp(log_value)


def curve_path(values: list[float], *, x: float, y: float, width: float, height: float, ymax: float) -> str:
    return " ".join(
        ("M" if index == 0 else "L")
        + f"{fmt(x + width * index / (len(values) - 1))} {fmt(y + height * (1 - value / ymax))}"
        for index, value in enumerate(values)
    )


def bars(
    values: list[float], *, x: float, y: float, width: float, height: float, color: str, opacity: float = 1
) -> list[str]:
    maximum = max(values)
    slot = width / len(values)
    bar_width = slot * 0.58
    result: list[str] = []
    for index, value in enumerate(values):
        bar_height = height * value / maximum
        bx = x + index * slot + (slot - bar_width) / 2
        by = y + height - bar_height
        result.append(
            f'  <rect x="{fmt(bx)}" y="{fmt(by)}" width="{fmt(bar_width)}" height="{fmt(bar_height)}" fill="{color}" opacity="{opacity}"/>'
        )
    return result


def main() -> int:
    width, height = 1200, 820
    alpha, beta, trials = 7, 4, 9
    p_values = [index / 10 for index in range(1, 10)]
    posterior_x = [index / 400 for index in range(401)]
    posterior_y = [beta_pdf(p, alpha, beta) for p in posterior_x]
    posterior_max = max(posterior_y) * 1.04

    top_x, top_y, top_width, top_height = 150, 65, 930, 175
    middle_y, middle_width, middle_height, gap = 355, 96, 105, 24
    middle_start = (width - (len(p_values) * middle_width + (len(p_values) - 1) * gap)) / 2
    bottom_x, bottom_y, bottom_width, bottom_height = 365, 590, 470, 145

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>从完整后验模拟预测</title>",
        "  <desc>顶部为水域比例后验，中部为九个参数值对应的抽样分布，底部为按后验概率加权合成的后验预测分布。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <text x="32" y="45" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">后验概率</text>',
        f'  <rect x="{top_x}" y="{top_y}" width="{top_width}" height="{top_height}" fill="#fff" stroke="#363934" stroke-width="1.3"/>',
        f'  <path d="{curve_path(posterior_y, x=top_x, y=top_y, width=top_width, height=top_height, ymax=posterior_max)}" fill="none" stroke="#30332e" stroke-width="2.4"/>',
    ]

    for tick, label in ((0, "0"), (0.5, "0.5"), (1, "1")):
        tx = top_x + top_width * tick
        body.extend(
            [
                f'  <line x1="{fmt(tx)}" y1="{top_y + top_height}" x2="{fmt(tx)}" y2="{top_y + top_height + 8}" stroke="#363934"/>',
                f'  <text x="{fmt(tx)}" y="{top_y + top_height + 29}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="#30332e">{label}</text>',
            ]
        )
    body.append(f'  <text x="{width / 2}" y="{top_y + top_height + 57}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">水域概率</text>')

    body.append(f'  <text x="32" y="325" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">抽样分布</text>')
    line_specs: list[tuple[float, float, float]] = []
    for index, p in enumerate(p_values):
        panel_x = middle_start + index * (middle_width + gap)
        panel_center = panel_x + middle_width / 2
        posterior_value = beta_pdf(p, alpha, beta)
        top_point_x = top_x + top_width * p
        top_point_y = top_y + top_height * (1 - posterior_value / posterior_max)
        stroke_width = 0.8 + 4.4 * posterior_value / posterior_max
        line_specs.append((panel_center, top_point_x, stroke_width))
        body.extend(
            [
                f'  <line x1="{fmt(top_point_x)}" y1="{fmt(top_point_y)}" x2="{fmt(panel_center)}" y2="{middle_y}" stroke="#59605a" stroke-width="{fmt(stroke_width)}" opacity="0.65"/>',
                f'  <line x1="{fmt(top_point_x)}" y1="{top_y + top_height}" x2="{fmt(top_point_x)}" y2="{fmt(top_point_y)}" stroke="#263f86" stroke-width="{fmt(stroke_width)}"/>',
                f'  <circle cx="{fmt(top_point_x)}" cy="{fmt(top_point_y)}" r="3" fill="#263f86"/>',
                f'  <rect x="{fmt(panel_x)}" y="{middle_y}" width="{middle_width}" height="{middle_height}" fill="#fff" stroke="#363934" stroke-width="1.1"/>',
                f'  <text x="{fmt(panel_center)}" y="{middle_y - 9}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="700" fill="#30332e">p = {p:.1f}</text>',
            ]
        )
        body.extend(
            bars(
                [binomial_pmf(k, trials, p) for k in range(trials + 1)],
                x=panel_x + 5,
                y=middle_y + 8,
                width=middle_width - 10,
                height=middle_height - 15,
                color="#6670ee",
                opacity=0.8,
            )
        )

    body.extend(
        [
            f'  <text x="32" y="570" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">后验预测分布</text>',
            f'  <rect x="{bottom_x}" y="{bottom_y}" width="{bottom_width}" height="{bottom_height}" fill="#fff" stroke="#363934" stroke-width="1.3"/>',
        ]
    )
    for panel_center, _, stroke_width in line_specs:
        body.append(
            f'  <line x1="{fmt(panel_center)}" y1="{middle_y + middle_height}" x2="{width / 2}" y2="{bottom_y}" stroke="#59605a" stroke-width="{fmt(stroke_width)}" opacity="0.45"/>'
        )
    predictive = [beta_binomial_pmf(k, trials, alpha, beta) for k in range(trials + 1)]
    body.extend(bars(predictive, x=bottom_x + 12, y=bottom_y + 10, width=bottom_width - 24, height=bottom_height - 20, color="#263f86"))
    slot = (bottom_width - 24) / len(predictive)
    for index in range(10):
        tick_x = bottom_x + 12 + (index + 0.5) * slot
        body.append(f'  <text x="{fmt(tick_x)}" y="{bottom_y + bottom_height + 24}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#30332e">{index}</text>')
    body.extend(
        [
            f'  <text x="{width / 2}" y="{bottom_y + bottom_height + 55}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">水域样本数</text>',
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
