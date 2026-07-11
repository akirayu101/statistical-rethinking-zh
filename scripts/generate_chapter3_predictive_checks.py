#!/usr/bin/env python3
from __future__ import annotations

import itertools
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-03-predictive-checks.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def beta(a: float, b: float) -> float:
    return math.exp(math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b))


def longest_run(sequence: tuple[int, ...]) -> int:
    longest = current = 1
    for previous, value in zip(sequence, sequence[1:]):
        current = current + 1 if value == previous else 1
        longest = max(longest, current)
    return longest


def switches(sequence: tuple[int, ...]) -> int:
    return sum(previous != value for previous, value in zip(sequence, sequence[1:]))


def distributions() -> tuple[list[float], list[float]]:
    alpha, beta_parameter, tosses = 7, 4, 9
    normalizer = beta(alpha, beta_parameter)
    run_counts: defaultdict[int, float] = defaultdict(float)
    switch_counts: defaultdict[int, float] = defaultdict(float)
    for sequence in itertools.product((0, 1), repeat=tosses):
        waters = sum(sequence)
        probability = beta(alpha + waters, beta_parameter + tosses - waters) / normalizer
        run_counts[longest_run(sequence)] += probability
        switch_counts[switches(sequence)] += probability
    return (
        [10_000 * run_counts[index] for index in range(1, tosses + 1)],
        [10_000 * switch_counts[index] for index in range(tosses)],
    )


def panel(
    values: list[float],
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    observed: int,
    xlabel: str,
    start: int,
) -> list[str]:
    ymax = 3_000
    slot = width / len(values)
    bar_width = slot * 0.52
    body = [
        f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#fff" stroke="#363934" stroke-width="1.3"/>',
    ]
    for index, count in enumerate(values):
        bar_height = min(height, height * count / ymax)
        bx = x + index * slot + (slot - bar_width) / 2
        by = y + height - bar_height
        body.append(
            f'  <rect x="{fmt(bx)}" y="{fmt(by)}" width="{fmt(bar_width)}" height="{fmt(bar_height)}" fill="#4d524e" opacity="0.82"/>'
        )
        tick_x = x + (index + 0.5) * slot
        body.extend(
            [
                f'  <line x1="{fmt(tick_x)}" y1="{y + height}" x2="{fmt(tick_x)}" y2="{y + height + 7}" stroke="#363934"/>',
                f'  <text x="{fmt(tick_x)}" y="{y + height + 29}" text-anchor="middle" font-family="{FONT}" font-size="15" fill="#30332e">{start + index}</text>',
            ]
        )
    observed_index = observed - start
    observed_x = x + (observed_index + 0.5) * slot
    observed_height = min(height, height * values[observed_index] / ymax)
    body.extend(
        [
            f'  <line x1="{fmt(observed_x)}" y1="{fmt(y + height)}" x2="{fmt(observed_x)}" y2="{fmt(y + height - observed_height)}" stroke="#179bd7" stroke-width="8" stroke-linecap="round"/>',
            f'  <circle cx="{fmt(observed_x)}" cy="{fmt(y + height - observed_height)}" r="5" fill="#179bd7"/>',
            f'  <text x="{fmt(x + width / 2)}" y="{y + height + 67}" text-anchor="middle" font-family="{FONT}" font-size="19" fill="#30332e">{xlabel}</text>',
        ]
    )
    for value in (0, 500, 1_500, 2_500):
        ty = y + height * (1 - value / ymax)
        body.extend(
            [
                f'  <line x1="{x - 7}" y1="{fmt(ty)}" x2="{x}" y2="{fmt(ty)}" stroke="#363934"/>',
                f'  <text x="{x - 13}" y="{fmt(ty + 5)}" text-anchor="end" font-family="{FONT}" font-size="14" fill="#30332e">{value:,}</text>',
            ]
        )
    return body


def main() -> int:
    run_values, switch_values = distributions()
    width, height = 1200, 570
    plot_y, plot_width, plot_height = 90, 440, 340
    left_x, right_x = 125, 690
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>同一后验预测分布的两种替代视图</title>",
        "  <desc>左图显示九次投掷中最长连续段的后验预测频数，观测值为三；右图显示水域与陆地切换次数的后验预测频数，观测值为六。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <text x="34" y="{plot_y + plot_height / 2}" transform="rotate(-90 34 {plot_y + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="19" fill="#30332e">频数</text>',
        f'  <text x="632" y="{plot_y + plot_height / 2}" transform="rotate(-90 632 {plot_y + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="19" fill="#30332e">频数</text>',
    ]
    body.extend(panel(run_values, x=left_x, y=plot_y, width=plot_width, height=plot_height, observed=3, xlabel="最长连续段长度", start=1))
    body.extend(panel(switch_values, x=right_x, y=plot_y, width=plot_width, height=plot_height, observed=6, xlabel="切换次数", start=0))
    body.extend(
        [
            f'  <circle cx="430" cy="535" r="6" fill="#179bd7"/>',
            f'  <text x="447" y="541" font-family="{FONT}" font-size="16" fill="#30332e">实际观测</text>',
            f'  <rect x="590" y="529" width="14" height="14" fill="#4d524e" opacity="0.82"/>',
            f'  <text x="614" y="541" font-family="{FONT}" font-size="16" fill="#30332e">后验预测</text>',
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
