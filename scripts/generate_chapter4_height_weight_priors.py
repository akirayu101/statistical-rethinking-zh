#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG used for Figure 4.5."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-height-weight-priors.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def panel(*, x: int, title: str, slopes: list[float], intercepts: list[float], annotate: bool) -> list[str]:
    top, width, height = 90, 430, 390
    xmin, xmax, ymin, ymax = 30.0, 62.0, -100.0, 400.0
    xbar = 45.0

    def px(value: float) -> float:
        return x + (value - xmin) / (xmax - xmin) * width

    def py(value: float) -> float:
        return top + height - (value - ymin) / (ymax - ymin) * height

    body = [
        f'  <text x="{x + width / 2}" y="42" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">{title}</text>',
        f'  <defs><clipPath id="clip-{x}"><rect x="{x}" y="{top}" width="{width}" height="{height}"/></clipPath></defs>',
        f'  <rect x="{x}" y="{top}" width="{width}" height="{height}" fill="#ffffff" stroke="#333630" stroke-width="2"/>',
    ]
    for a, b in zip(intercepts, slopes):
        y1 = a + b * (xmin - xbar)
        y2 = a + b * (xmax - xbar)
        body.append(
            f'  <line x1="{fmt(px(xmin))}" y1="{fmt(py(y1))}" x2="{fmt(px(xmax))}" y2="{fmt(py(y2))}" stroke="#20231f" stroke-width="1.15" opacity="0.18" clip-path="url(#clip-{x})"/>'
        )
    body.extend(
        [
            f'  <line x1="{x}" y1="{fmt(py(0))}" x2="{x + width}" y2="{fmt(py(0))}" stroke="#333630" stroke-width="1.6" stroke-dasharray="7 6"/>',
            f'  <line x1="{x}" y1="{fmt(py(272))}" x2="{x + width}" y2="{fmt(py(272))}" stroke="#333630" stroke-width="1.4"/>',
        ]
    )
    for tick in [30, 35, 40, 45, 50, 55, 60]:
        tx = px(tick)
        body.extend(
            [
                f'  <line x1="{fmt(tx)}" y1="{top + height}" x2="{fmt(tx)}" y2="{top + height + 7}" stroke="#333630"/>',
                f'  <text x="{fmt(tx)}" y="{top + height + 27}" text-anchor="middle" font-family="{FONT}" font-size="15" fill="#30332e">{tick}</text>',
            ]
        )
    for tick in [-100, 0, 100, 200, 300, 400]:
        ty = py(tick)
        body.extend(
            [
                f'  <line x1="{x - 7}" y1="{fmt(ty)}" x2="{x}" y2="{fmt(ty)}" stroke="#333630"/>',
                f'  <text x="{x - 14}" y="{fmt(ty + 5)}" text-anchor="end" font-family="{FONT}" font-size="15" fill="#30332e">{tick}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{x + width / 2}" y="{top + height + 62}" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">体重（千克）</text>',
            f'  <text x="{x - 62}" y="{top + height / 2}" transform="rotate(-90 {x - 62} {top + height / 2})" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">身高（厘米）</text>',
        ]
    )
    if annotate:
        body.extend(
            [
                f'  <text x="{x + 14}" y="{fmt(py(272) - 9)}" font-family="{FONT}" font-size="14" fill="#30332e">最高个体（272 厘米）</text>',
                f'  <text x="{x + 14}" y="{fmt(py(0) + 20)}" font-family="{FONT}" font-size="14" fill="#30332e">胚胎</text>',
            ]
        )
    return body


def main() -> int:
    left_rng = random.Random(2971)
    left_a = [left_rng.gauss(178, 20) for _ in range(100)]
    left_b = [left_rng.gauss(0, 10) for _ in range(100)]

    right_rng = random.Random(2971)
    right_a = [right_rng.gauss(178, 20) for _ in range(100)]
    right_b = [math.exp(right_rng.gauss(0, 1)) for _ in range(100)]

    width, height = 1200, 650
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>身高和体重模型的先验预测模拟</title>",
        "  <desc>左图使用正态斜率先验，产生大量荒谬的正负关系；右图使用对数正态斜率先验，绝大多数关系落在人类合理范围内。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    body.extend(panel(x=130, title="β ∼ Normal(0, 10)", slopes=left_b, intercepts=left_a, annotate=False))
    body.extend(panel(x=700, title="log(β) ∼ Normal(0, 1)", slopes=right_b, intercepts=right_a, annotate=True))
    body.extend(
        [
            f'  <text x="{width / 2}" y="632" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">每个面板绘制由 α 与 β 先验共同产生的 100 条身高-体重关系线</text>',
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
