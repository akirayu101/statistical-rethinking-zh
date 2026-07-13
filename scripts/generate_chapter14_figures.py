#!/usr/bin/env python3
"""Generate deterministic Chinese figures for Chapter 14."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT1 = ROOT / "translations" / "zh" / "media" / "chapter-14-cafe-waits.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
INK = "#30332e"
BLUE = "#6670ee"
MUTED = "#6d7069"
GRID = "#ddd9ce"


def text(x: float, y: float, value: str, *, size: int = 18, anchor: str = "start",
         weight: int = 400, rotate: int | None = None) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
        f'fill="{INK}"{transform}>{value}</text>'
    )


def figure_14_1() -> None:
    width, height = 920, 690
    left, right = 115.0, 850.0
    panels = [(75.0, 300.0), (390.0, 615.0)]
    busy = [(7.0, 4.7), (6.8, 4.5), (7.5, 5.9), (6.2, 4.8), (8.2, 5.4)]
    quiet = [(2.0, 2.0), (1.9, 2.2), (1.7, 0.6), (2.1, 1.0), (1.2, 1.9)]

    def x_for(index: int, afternoon: bool) -> float:
        group_width = (right - left) / 5.0
        return left + group_width * (index + 0.5) + (18.0 if afternoon else -18.0)

    def y_for(value: float, top: float, bottom: float) -> float:
        return bottom - value / 8.5 * (bottom - top)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<title>图 14.1：两类咖啡馆的早晚等待时间</title>",
        "<desc>上图的繁忙咖啡馆早晨等待时间长，下午通常明显缩短；下图的不繁忙咖啡馆等待时间一直较短。总体上，晨间等待截距与晨午差异斜率协变。</desc>",
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
    ]
    for panel_index, ((top, bottom), values) in enumerate(zip(panels, [busy, quiet])):
        svg.extend([
            f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
            text((left + right) / 2, top - 25, "繁忙咖啡馆" if panel_index == 0 else "不繁忙咖啡馆", size=20, anchor="middle", weight=700),
        ])
        for tick in [2, 4, 6, 8]:
            y = y_for(tick, top, bottom)
            svg.extend([
                f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>',
                f'<line x1="{left-7}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.4"/>',
                text(left - 15, y + 6, str(tick), size=17, anchor="end"),
            ])
        for index, (morning, afternoon) in enumerate(values):
            xm = x_for(index, False)
            xa = x_for(index, True)
            ym = y_for(morning, top, bottom)
            ya = y_for(afternoon, top, bottom)
            svg.extend([
                f'<line x1="{xm:.1f}" y1="{ym:.1f}" x2="{xa:.1f}" y2="{ya:.1f}" stroke="{INK}" stroke-width="2.2"/>',
                f'<circle cx="{xm:.1f}" cy="{ym:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>',
                f'<circle cx="{xa:.1f}" cy="{ya:.1f}" r="6" fill="#fff" stroke="{INK}" stroke-width="2"/>',
                text(xm, bottom + 28, "晨", size=17, anchor="middle"),
                text(xa, bottom + 28, "午", size=17, anchor="middle"),
            ])
        svg.append(text(35, (top + bottom) / 2, "等待时间（分钟）", size=19, anchor="middle", rotate=-90))
    svg.extend([
        f'<line x1="635" y1="657" x2="683" y2="657" stroke="{INK}" stroke-width="2.2"/>',
        '<circle cx="635" cy="657" r="6" fill="#fff" stroke="#30332e" stroke-width="2"/>',
        '<circle cx="683" cy="657" r="6" fill="#fff" stroke="#30332e" stroke-width="2"/>',
        text(700, 663, "同一家咖啡馆", size=17, weight=600),
        text(115, 665, "晨：上午　午：下午", size=17, weight=600),
        "</svg>",
    ])
    OUT1.parent.mkdir(parents=True, exist_ok=True)
    OUT1.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    figure_14_1()
    print(OUT1)


if __name__ == "__main__":
    main()
