#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "translations" / "zh" / "media"
OUT_32 = MEDIA / "chapter-03-posterior-intervals.svg"
OUT_33 = MEDIA / "chapter-03-percentile-vs-hpdi.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def beta_pdf(x: float, alpha: int, beta: int) -> float:
    coefficient = math.gamma(alpha + beta) / (math.gamma(alpha) * math.gamma(beta))
    return coefficient * (x ** (alpha - 1)) * ((1 - x) ** (beta - 1))


def line_path(values: list[float], *, x: float, y: float, width: float, height: float, ymax: float) -> str:
    return " ".join(
        ("M" if index == 0 else "L")
        + f"{fmt(x + width * index / (len(values) - 1))} {fmt(y + height * (1 - value / ymax))}"
        for index, value in enumerate(values)
    )


def area_path(values: list[float], *, lower: float, upper: float, x: float, y: float, width: float, height: float, ymax: float) -> str:
    points = [
        (index / (len(values) - 1), value)
        for index, value in enumerate(values)
        if lower <= index / (len(values) - 1) <= upper
    ]
    commands = [f"M{fmt(x + width * lower)} {fmt(y + height)}"]
    commands.extend(
        f"L{fmt(x + width * px)} {fmt(y + height * (1 - value / ymax))}" for px, value in points
    )
    commands.append(f"L{fmt(x + width * upper)} {fmt(y + height)} Z")
    return " ".join(commands)


def panel(
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    values: list[float],
    ymax: float,
    lower: float,
    upper: float,
    title: str,
) -> list[str]:
    result = [
        f'  <g aria-label="{title}">',
        f'    <text x="{fmt(x + width / 2)}" y="{fmt(y - 18)}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">{title}</text>',
        f'    <rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(width)}" height="{fmt(height)}" fill="#fff" stroke="#363934" stroke-width="1.3"/>',
        f'    <path d="{area_path(values, lower=lower, upper=upper, x=x, y=y, width=width, height=height, ymax=ymax)}" fill="#6670ee" opacity="0.82"/>',
        f'    <path d="{line_path(values, x=x, y=y, width=width, height=height, ymax=ymax)}" fill="none" stroke="#292b27" stroke-width="2"/>',
    ]
    for tick, label in ((0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1, "1")):
        tx = x + width * tick
        result.extend(
            [
                f'    <line x1="{fmt(tx)}" y1="{fmt(y + height)}" x2="{fmt(tx)}" y2="{fmt(y + height + 7)}" stroke="#363934"/>',
                f'    <text x="{fmt(tx)}" y="{fmt(y + height + 26)}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#30332e">{label}</text>',
            ]
        )
    result.extend(
        [
            f'    <text x="{fmt(x + width / 2)}" y="{fmt(y + height + 52)}" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">水域比例（p）</text>',
            f'    <text x="{fmt(x - 43)}" y="{fmt(y + height / 2)}" transform="rotate(-90 {fmt(x - 43)} {fmt(y + height / 2)})" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">概率密度</text>',
            "  </g>",
        ]
    )
    return result


def generate_figure_32() -> None:
    samples = [index / 400 for index in range(401)]
    values = [beta_pdf(p, 7, 4) for p in samples]
    width, height = 1200, 790
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>两类后验区间</title>",
        "  <desc>四个面板展示边界已知的后验区间和概率质量已知的后验区间。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    specs = (
        (100, 55, 430, 245, 0.0, 0.5, "低于 p = 0.5"),
        (690, 55, 430, 245, 0.5, 0.75, "p = 0.5 至 0.75"),
        (100, 435, 430, 245, 0.0, 0.7607608, "较低的 80%"),
        (690, 435, 430, 245, 0.4464464, 0.8118118, "中间的 80%"),
    )
    for x, y, panel_width, panel_height, lower, upper, title in specs:
        body.extend(panel(x=x, y=y, width=panel_width, height=panel_height, values=values, ymax=3.0, lower=lower, upper=upper, title=title))
    body.extend(["</svg>", ""])
    OUT_32.write_text("\n".join(body), encoding="utf-8")


def generate_figure_33() -> None:
    samples = [index / 400 for index in range(401)]
    values = [beta_pdf(p, 4, 1) for p in samples]
    width, height = 1200, 470
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>百分位区间与最高后验密度区间</title>",
        "  <desc>左图为百分位区间，排除了最可能的参数值一；右图为更窄且包含参数值一的最高后验密度区间。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    specs = (
        (100, 60, 430, 270, 0.7037037, 0.9329329, "50% 百分位区间"),
        (690, 60, 430, 270, 0.8408408, 1.0, "50% HPDI"),
    )
    for x, y, panel_width, panel_height, lower, upper, title in specs:
        body.extend(panel(x=x, y=y, width=panel_width, height=panel_height, values=values, ymax=4.1, lower=lower, upper=upper, title=title))
    body.extend(["</svg>", ""])
    OUT_33.write_text("\n".join(body), encoding="utf-8")


def main() -> int:
    MEDIA.mkdir(parents=True, exist_ok=True)
    generate_figure_32()
    generate_figure_33()
    print(f"generated {OUT_32}")
    print(f"generated {OUT_33}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
