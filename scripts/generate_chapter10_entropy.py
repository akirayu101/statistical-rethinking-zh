#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Chapter 10 entropy figures."""
from pathlib import Path
import math


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations/zh/media/chapter-10-pebble-entropy.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
BLUE = "#263f86"
BLUE_SOFT = "#dfe6f8"
GRID = "#d9d5c8"


def esc(text: object) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: float, y: float, value: object, *, size: int = 18, anchor: str = "start",
         weight: int = 400, fill: str = INK, rotate: int | None = None) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}"{transform}>'
        f'{esc(value)}</text>'
    )


def bar_panel(label: str, counts: list[int], ways: int, x: float, y: float) -> list[str]:
    width, height = 500, 250
    left, right, top, bottom = x + 62, x + width - 24, y + 50, y + height - 47
    plot_h = bottom - top
    parts = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="#fff" stroke="{GRID}"/>',
        text(x + 18, y + 31, label, size=24, weight=700, fill=BLUE),
        text(x + width - 18, y + 31, f"{ways:,} 种方式", size=18, anchor="end"),
    ]
    for tick in (0, 5, 10):
        yy = bottom - tick / 10 * plot_h
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(text(left - 12, yy + 6, tick, size=15, anchor="end", fill="#666862"))
    parts.append(text(x + 20, (top + bottom) / 2, "石子数", size=17, anchor="middle", fill=BLUE, rotate=-90))
    step = (right - left) / 5
    bar_w = 26
    for index, count in enumerate(counts, start=1):
        cx = left + (index - .5) * step
        bar_h = count / 10 * plot_h
        yy = bottom - bar_h
        parts.append(f'<rect x="{cx - bar_w / 2:.1f}" y="{yy:.1f}" width="{bar_w}" height="{bar_h:.1f}" rx="4" fill="{BLUE}"/>')
        if count:
            parts.append(text(cx, yy - 8, count, size=16, anchor="middle", weight=700))
        parts.append(text(cx, bottom + 25, index, size=16, anchor="middle"))
    parts.append(text((left + right) / 2, y + height - 10, "桶", size=17, anchor="middle", fill=BLUE))
    return parts


def scatter_panel(x: float, y: float) -> list[str]:
    width, height = 500, 250
    left, right, top, bottom = x + 68, x + width - 25, y + 35, y + height - 55
    xmax, ymax = 1.2, 1.7
    ways = [1, 90, 1260, 37800, 113400]
    entropy = [0.0, 0.6390319, 0.9502705, 1.4708085, 1.6094379]
    labels = list("ABCDE")
    xs = [math.log(value) / 10 for value in ways]
    sx = lambda value: left + value / xmax * (right - left)
    sy = lambda value: bottom - value / ymax * (bottom - top)
    parts = [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="#fff" stroke="{GRID}"/>']
    for tick in (0.0, 0.4, 0.8, 1.2):
        xx = sx(tick)
        parts.append(f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + 6}" stroke="{INK}"/>')
        parts.append(text(xx, bottom + 24, f"{tick:.1f}", size=14, anchor="middle", fill="#666862"))
    for tick in (0.0, 0.5, 1.0, 1.5):
        yy = sy(tick)
        parts.append(f'<line x1="{left - 6}" y1="{yy:.1f}" x2="{left}" y2="{yy:.1f}" stroke="{INK}"/>')
        parts.append(text(left - 11, yy + 5, f"{tick:.1f}", size=14, anchor="end", fill="#666862"))
    parts.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="{INK}"/>',
        text((left + right) / 2, y + height - 10, "每颗石子的 log(方式数)", size=16, anchor="middle", fill=BLUE),
        text(x + 20, (top + bottom) / 2, "熵", size=17, anchor="middle", fill=BLUE, rotate=-90),
    ])
    points = " ".join(f"{sx(px):.1f},{sy(py):.1f}" for px, py in zip(xs, entropy))
    parts.append(f'<polyline points="{points}" fill="none" stroke="#8c8e88" stroke-width="2" stroke-dasharray="7 6"/>')
    offsets = [(10, -10), (0, -13), (0, 23), (-9, 23), (-13, 23)]
    for label, px, py, (dx, dy) in zip(labels, xs, entropy, offsets):
        parts.append(f'<circle cx="{sx(px):.1f}" cy="{sy(py):.1f}" r="6" fill="{BLUE}" stroke="#fff" stroke-width="2"/>')
        parts.append(text(sx(px) + dx, sy(py) + dy, label, size=18, anchor="middle", weight=700))
    return parts


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1200, 930
    distributions = [
        ("A", [0, 0, 10, 0, 0], 1),
        ("B", [0, 1, 8, 1, 0], 90),
        ("C", [0, 2, 6, 2, 0], 1260),
        ("D", [1, 2, 4, 2, 1], 37800),
        ("E", [2, 2, 2, 2, 2], 113400),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>石子分布的方式数与信息熵</title>',
        '<desc>五个条形图展示十颗有编号石子落入五只桶的 A 到 E 五种分布及实现方式数；右下图比较各分布的信息熵与每颗石子的对数方式数。</desc>',
        '<rect width="100%" height="100%" fill="#fbfaf6"/>',
    ]
    positions = [(65, 35), (635, 35), (65, 330), (635, 330), (65, 625)]
    for (label, counts, ways), (x, y) in zip(distributions, positions):
        parts.extend(bar_panel(label, counts, ways, x, y))
    parts.extend(scatter_panel(635, 625))
    parts.append('</svg>')
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
