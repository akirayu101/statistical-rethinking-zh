#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 15."""

from __future__ import annotations

import math
from pathlib import Path

from generate_chapter5_waffle_divorce import rows


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-15-measurement-error.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
GRID = "#ddd9ce"
DIVORCE_SE = [
    0.79, 2.05, 0.74, 1.22, 0.24, 0.94, 0.77, 1.39, 1.89, 0.32,
    0.58, 1.27, 1.05, 0.45, 0.63, 0.91, 1.09, 0.75, 0.89, 1.48,
    0.69, 0.52, 0.53, 0.60, 1.01, 0.67, 1.71, 0.94, 1.61, 0.46,
    1.11, 0.31, 0.48, 1.44, 0.45, 1.01, 0.80, 0.43, 1.79, 0.70,
    2.50, 0.75, 0.35, 0.93, 1.87, 0.52, 0.65, 1.34, 0.57, 1.90,
]


def label(x: float, y: float, value: str, *, size: int = 18,
          anchor: str = "start", weight: int = 400,
          rotate: int | None = None) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
        f'fill="{INK}"{transform}>{value}</text>'
    )


def figure_15_1() -> None:
    width, height = 1200, 620
    panels = [(90.0, 55.0, 570.0, 520.0), (665.0, 55.0, 1145.0, 520.0)]
    data = rows()

    # Exact Divorce.SE values from the official rethinking WaffleDivorce dataset.
    errors = DIVORCE_SE

    def map_left(age: float, divorce: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[0]
        return x0 + (age - 22.5) / 7.5 * (x1 - x0), y1 - (divorce - 4.0) / 11.5 * (y1 - y0)

    def map_right(log_population: float, divorce: float) -> tuple[float, float]:
        x0, y0, x1, y1 = panels[1]
        return x0 + (log_population + 1.0) / 5.0 * (x1 - x0), y1 - (divorce - 4.0) / 11.5 * (y1 - y0)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>图 15.1：各州离婚率的测量误差</title>',
        '<desc>左图以结婚年龄中位数预测离婚率，右图以人口对数为横轴；每个空心点的竖线表示离婚率测量的一倍标准误，小州的不确定性更大。</desc>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
    ]
    for x0, y0, x1, y1 in panels:
        svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
        for divorce in [4, 6, 8, 10, 12, 14]:
            y = y1 - (divorce - 4.0) / 11.5 * (y1 - y0)
            svg.extend([
                f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>',
                f'<line x1="{x0-7}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.4"/>',
                label(x0 - 14, y + 6, str(divorce), size=16, anchor="end"),
            ])

    for age in [23, 24, 25, 26, 27, 28, 29, 30]:
        x, _ = map_left(float(age), 4.0)
        svg.extend([f'<line x1="{x:.1f}" y1="520" x2="{x:.1f}" y2="527" stroke="{INK}"/>', label(x, 552, str(age), size=16, anchor="middle")])
    for log_population in [-1, 0, 1, 2, 3, 4]:
        x, _ = map_right(float(log_population), 4.0)
        svg.extend([f'<line x1="{x:.1f}" y1="520" x2="{x:.1f}" y2="527" stroke="{INK}"/>', label(x, 552, str(log_population), size=16, anchor="middle")])

    for row, error in zip(data, errors):
        divorce = float(row["divorce"])
        age = float(row["age"])
        log_population = math.log(float(row["population"]))
        for mapper, x_value in [(map_left, age), (map_right, log_population)]:
            x, y = mapper(x_value, divorce)
            _, y_low = mapper(x_value, max(4.0, divorce - error))
            _, y_high = mapper(x_value, min(15.5, divorce + error))
            svg.extend([
                f'<line x1="{x:.1f}" y1="{y_high:.1f}" x2="{x:.1f}" y2="{y_low:.1f}" stroke="{INK}" stroke-width="1.25"/>',
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.2" fill="#fff" stroke="{INK}" stroke-width="1.6"/>',
            ])

    svg.extend([
        label(330, 598, "结婚年龄中位数", size=19, anchor="middle", weight=600),
        label(905, 598, "人口对数", size=19, anchor="middle", weight=600),
        label(28, 287, "离婚率", size=19, anchor="middle", weight=600, rotate=-90),
        label(603, 287, "离婚率", size=19, anchor="middle", weight=600, rotate=-90),
        '</svg>',
    ])
    OUT1.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    figure_15_1()
    print(OUT1)


if __name__ == "__main__":
    main()
