#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-03-point-estimates-loss.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def beta_pdf(x: float, alpha: int, beta: int) -> float:
    coefficient = math.gamma(alpha + beta) / (math.gamma(alpha) * math.gamma(beta))
    return coefficient * (x ** (alpha - 1)) * ((1 - x) ** (beta - 1))


def path(values: list[float], *, x: float, y: float, width: float, height: float, ymax: float) -> str:
    return " ".join(
        ("M" if index == 0 else "L")
        + f"{fmt(x + width * index / (len(values) - 1))} {fmt(y + height * (1 - value / ymax))}"
        for index, value in enumerate(values)
    )


def axes(*, x: float, y: float, width: float, height: float, xlabel: str, ylabel: str, ymax: float) -> list[str]:
    result = [
        f'  <rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(width)}" height="{fmt(height)}" fill="#fff" stroke="#363934" stroke-width="1.3"/>',
    ]
    for tick, label in ((0, "0"), (0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8"), (1, "1")):
        tx = x + width * tick
        result.extend(
            [
                f'  <line x1="{fmt(tx)}" y1="{fmt(y + height)}" x2="{fmt(tx)}" y2="{fmt(y + height + 7)}" stroke="#363934"/>',
                f'  <text x="{fmt(tx)}" y="{fmt(y + height + 27)}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="#30332e">{label}</text>',
            ]
        )
    for fraction in (0, 0.25, 0.5, 0.75, 1):
        ty = y + height * (1 - fraction)
        label = fmt(ymax * fraction)
        result.extend(
            [
                f'  <line x1="{fmt(x - 7)}" y1="{fmt(ty)}" x2="{fmt(x)}" y2="{fmt(ty)}" stroke="#363934"/>',
                f'  <text x="{fmt(x - 12)}" y="{fmt(ty + 5)}" text-anchor="end" font-family="{FONT}" font-size="14" fill="#30332e">{label}</text>',
            ]
        )
    result.extend(
        [
            f'  <text x="{fmt(x + width / 2)}" y="{fmt(y + height + 58)}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{xlabel}</text>',
            f'  <text x="{fmt(x - 55)}" y="{fmt(y + height / 2)}" transform="rotate(-90 {fmt(x - 55)} {fmt(y + height / 2)})" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{ylabel}</text>',
        ]
    )
    return result


def main() -> int:
    grid = [index / 1000 for index in range(1001)]
    density = [beta_pdf(p, 4, 1) for p in grid]
    step = grid[1] - grid[0]
    expected_loss = [
        sum(abs(decision - p) * weight for p, weight in zip(grid, density)) * step
        for decision in grid
    ]

    width, height = 1200, 470
    top, panel_height = 50, 300
    left_x, panel_width = 105, 430
    right_x = 700
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>点估计与损失函数</title>",
        "  <desc>左图标出偏斜后验的均值、中位数和众数；右图显示绝对距离规则下的期望损失，并在后验中位数处达到最小。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    body.extend(axes(x=left_x, y=top, width=panel_width, height=panel_height, xlabel="水域比例（p）", ylabel="密度", ymax=4.0))
    body.append(f'  <path d="{path(density, x=left_x, y=top, width=panel_width, height=panel_height, ymax=4.0)}" fill="none" stroke="#6670ee" stroke-width="3"/>')
    for value, label, label_y in ((0.8005558, "均值", 290), (0.8408408, "中位数", 245), (0.9985486, "众数", 200)):
        x = left_x + panel_width * value
        body.extend(
            [
                f'  <line x1="{fmt(x)}" y1="{top}" x2="{fmt(x)}" y2="{top + panel_height}" stroke="#292b27" stroke-width="1.6"/>',
                f'  <text x="{fmt(x - 7)}" y="{label_y}" transform="rotate(-90 {fmt(x - 7)} {label_y})" text-anchor="middle" font-family="{FONT}" font-size="15" font-weight="700" fill="#30332e">{label}</text>',
            ]
        )

    body.extend(axes(x=right_x, y=top, width=panel_width, height=panel_height, xlabel="决策值", ylabel="期望比例损失", ymax=0.85))
    body.append(f'  <path d="{path(expected_loss, x=right_x, y=top, width=panel_width, height=panel_height, ymax=0.85)}" fill="none" stroke="#6670ee" stroke-width="3"/>')
    median_index = min(range(len(expected_loss)), key=expected_loss.__getitem__)
    median_x = right_x + panel_width * median_index / (len(expected_loss) - 1)
    median_y = top + panel_height * (1 - expected_loss[median_index] / 0.85)
    body.extend(
        [
            f'  <circle cx="{fmt(median_x)}" cy="{fmt(median_y)}" r="6" fill="#fff" stroke="#263f86" stroke-width="2.5"/>',
            f'  <text x="{fmt(median_x)}" y="{fmt(median_y - 16)}" text-anchor="middle" font-family="{FONT}" font-size="15" font-weight="700" fill="#263f86">中位数</text>',
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
