#!/usr/bin/env python3
"""Generate the translated Figure 8.2 from the book's rugged data."""

from __future__ import annotations

import csv
import io
import math
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "work" / "chapter-08-260-262" / "rugged.csv"
OUT = ROOT / "translations" / "zh" / "media" / "chapter-08-ruggedness-gdp.svg"
DATA_URL = "https://raw.githubusercontent.com/rmcelreath/rethinking/ac1b3b2cda83f3e14096e2d997a6e30ad109eeee/data/rugged.csv"


def load_rows():
    if DATA.exists():
        source = DATA.read_text(encoding="utf-8-sig")
    else:
        with urllib.request.urlopen(DATA_URL) as response:
            source = response.read().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(source), delimiter=";"))
    complete = [row for row in rows if row["rgdppc_2000"].strip()]
    mean_log_gdp = sum(math.log(float(row["rgdppc_2000"])) for row in complete) / len(complete)
    max_rugged = max(float(row["rugged"]) for row in complete)
    return [
        {
            "country": row["country"],
            "africa": row["cont_africa"] == "1",
            "x": float(row["rugged"]) / max_rugged,
            "y": math.log(float(row["rgdppc_2000"])) / mean_log_gdp,
        }
        for row in complete
    ]


def regression(rows):
    xs = [row["x"] for row in rows]
    ys = [row["y"] for row in rows]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    sxx = sum((x - xbar) ** 2 for x in xs)
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sxx
    intercept = ybar - slope * xbar
    residual_sd = math.sqrt(sum((y - intercept - slope * x) ** 2 for x, y in zip(xs, ys)) / (len(xs) - 2))
    return intercept, slope, residual_sd, xbar, sxx, len(xs)


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def panel(rows, x0, y0, width, height, title, ymin, ymax, filled, labels):
    left, right, top, bottom = 72, 18, 48, 66
    pw, ph = width - left - right, height - top - bottom
    sx = lambda x: x0 + left + x / 1.05 * pw
    sy = lambda y: y0 + top + (ymax - y) / (ymax - ymin) * ph
    parts = [f'<text class="title" x="{x0 + width/2:.1f}" y="{y0 + 25}" text-anchor="middle">{title}</text>']
    parts.append(f'<rect class="plot" x="{x0+left}" y="{y0+top}" width="{pw}" height="{ph}"/>')
    for tick in [0, .2, .4, .6, .8, 1.0]:
        x = sx(tick)
        parts.append(f'<line class="tick" x1="{x:.1f}" y1="{y0+top+ph}" x2="{x:.1f}" y2="{y0+top+ph+6}"/>')
        parts.append(f'<text class="axis" x="{x:.1f}" y="{y0+top+ph+24}" text-anchor="middle">{tick:.1f}</text>')
    step = .1
    tick = math.ceil(ymin / step) * step
    while tick <= ymax + 1e-8:
        y = sy(tick)
        parts.append(f'<line class="grid" x1="{x0+left}" y1="{y:.1f}" x2="{x0+left+pw}" y2="{y:.1f}"/>')
        parts.append(f'<text class="axis" x="{x0+left-11}" y="{y+5:.1f}" text-anchor="end">{tick:.1f}</text>')
        tick += step
    parts.append(f'<text class="label" x="{x0+left+pw/2:.1f}" y="{y0+height-12}" text-anchor="middle">崎岖度（标准化）</text>')
    parts.append(f'<text class="label" transform="translate({x0+18},{y0+top+ph/2}) rotate(-90)" text-anchor="middle">对数 GDP（占均值比例）</text>')
    a, b, sd, xbar, sxx, n = regression(rows)
    samples = [i / 80 * 1.05 for i in range(81)]
    upper, lower = [], []
    for x in samples:
        mean = a + b * x
        se = sd * math.sqrt(1 / n + (x - xbar) ** 2 / sxx)
        upper.append((sx(x), sy(mean + 1.60 * se)))
        lower.append((sx(x), sy(mean - 1.60 * se)))
    path = " ".join([f'{x:.1f},{y:.1f}' for x, y in upper + list(reversed(lower))])
    parts.append(f'<polygon class="band" points="{path}"/>')
    parts.append(f'<line class="fit" x1="{sx(0):.1f}" y1="{sy(a):.1f}" x2="{sx(1.05):.1f}" y2="{sy(a+b*1.05):.1f}"/>')
    for row in rows:
        cls = "point filled" if filled else "point"
        parts.append(f'<circle class="{cls}" cx="{sx(row["x"]):.1f}" cy="{sy(row["y"]):.1f}" r="4.2"/>')
    zh = {"Seychelles": "塞舌尔", "Lesotho": "莱索托", "Switzerland": "瑞士", "Tajikistan": "塔吉克斯坦"}
    offsets = {"Seychelles": (-7, 18, "middle"), "Lesotho": (-8, -9, "end"), "Switzerland": (13, 5, "start"), "Tajikistan": (-8, -10, "end")}
    for row in rows:
        if row["country"] in labels:
            dx, dy, anchor = offsets[row["country"]]
            parts.append(f'<text class="annotation" x="{sx(row["x"])+dx:.1f}" y="{sy(row["y"])+dy:.1f}" text-anchor="{anchor}">{esc(zh[row["country"]])}</text>')
    return "".join(parts)


def main():
    rows = load_rows()
    africa = [row for row in rows if row["africa"]]
    elsewhere = [row for row in rows if not row["africa"]]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520" role="img" aria-labelledby="title desc">
<title id="title">非洲内外地形崎岖度与对数 GDP 的回归</title>
<desc id="desc">左图非洲国家斜率为正，右图非非洲国家斜率为负；灰带表示回归均值的不确定性。</desc>
<style>.title{{font:700 22px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#29302d}}.axis,.annotation{{font:16px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#30332e}}.label{{font:18px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#30332e}}.plot{{fill:#fff;stroke:#4b4e49;stroke-width:1.2}}.grid{{stroke:#e3e3df;stroke-width:1}}.tick{{stroke:#4b4e49;stroke-width:1.2}}.band{{fill:#d7d9d8;opacity:.95}}.fit{{stroke:#141613;stroke-width:3}}.point{{fill:#fff;stroke:#171915;stroke-width:1.4}}.point.filled{{fill:#777df4;stroke:#777df4}}</style>
{panel(africa, 20, 15, 560, 480, "非洲国家", .70, 1.15, True, {"Seychelles", "Lesotho"})}
{panel(elsewhere, 620, 15, 560, 480, "非非洲国家", .78, 1.30, False, {"Switzerland", "Tajikistan"})}
</svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
