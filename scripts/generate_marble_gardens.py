#!/usr/bin/env python3
from __future__ import annotations

import itertools
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media"
OBSERVED = ("blue", "white", "blue")


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def palette(n_blue: int) -> tuple[str, ...]:
    return tuple(["blue"] * n_blue + ["white"] * (4 - n_blue))


def active(colors: tuple[str, ...], prefix: tuple[int, ...], highlight: bool) -> bool:
    if not highlight:
        return True
    return tuple(colors[index] for index in prefix) == OBSERVED[: len(prefix)]


def line(x1: float, y1: float, x2: float, y2: float, enabled: bool) -> str:
    stroke = "#282a26" if enabled else "#b9bab5"
    opacity = "1" if enabled else "0.42"
    width = "1.7" if enabled else "1.1"
    return (
        f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
        f'stroke="{stroke}" stroke-width="{width}" opacity="{opacity}"/>'
    )


def node(x: float, y: float, color: str, enabled: bool, radius: float) -> str:
    if color == "blue":
        fill = "#315bd7" if enabled else "#c5cceb"
        stroke = "#172860" if enabled else "#a4a8bd"
    else:
        fill = "#ffffff" if enabled else "#f5f5f2"
        stroke = "#242620" if enabled else "#b8b9b4"
    return (
        f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(radius)}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
    )


def tree_elements(
    n_blue: int,
    *,
    x0: float,
    y0: float,
    width: float,
    height: float,
    highlight: bool,
) -> list[str]:
    colors = palette(n_blue)
    root = (x0 + width / 2, y0 + height - 18)
    y1 = y0 + height * 0.72
    y2 = y0 + height * 0.43
    y3 = y0 + height * 0.10
    p1 = [x0 + width * (i + 0.5) / 4 for i in range(4)]
    p2 = [x0 + width * (i + 0.5) / 16 for i in range(16)]
    p3 = [x0 + width * (i + 0.5) / 64 for i in range(64)]
    lines: list[str] = []
    nodes: list[str] = [f'<circle cx="{fmt(root[0])}" cy="{fmt(root[1])}" r="4" fill="#30322d"/>']

    for i in range(4):
        prefix1 = (i,)
        enabled1 = active(colors, prefix1, highlight)
        lines.append(line(root[0], root[1], p1[i], y1, enabled1))
        nodes.append(node(p1[i], y1, colors[i], enabled1, 7.5))
        for j in range(4):
            index2 = i * 4 + j
            prefix2 = (i, j)
            enabled2 = active(colors, prefix2, highlight)
            lines.append(line(p1[i], y1, p2[index2], y2, enabled2))
            nodes.append(node(p2[index2], y2, colors[j], enabled2, 5.5))
            for k in range(4):
                index3 = index2 * 4 + k
                prefix3 = (i, j, k)
                enabled3 = active(colors, prefix3, highlight)
                lines.append(line(p2[index2], y2, p3[index3], y3, enabled3))
                nodes.append(node(p3[index3], y3, colors[k], enabled3, 3.8))
    return lines + nodes


def svg_document(title: str, description: str, width: int, height: int, body: list[str]) -> str:
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">',
            f"  <title>{title}</title>",
            f"  <desc>{description}</desc>",
            '  <rect width="100%" height="100%" fill="#ffffff"/>',
            *[f"  {element}" for element in body],
            "</svg>",
            "",
        ]
    )


def write(name: str, text: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(text, encoding="utf-8")


def main() -> int:
    full = tree_elements(1, x0=30, y0=20, width=940, height=430, highlight=False)
    write(
        "chapter-02-garden-64.svg",
        svg_document("一蓝三白猜想的 64 条路径", "三次有放回抽取，每次有四种可能，因此共有六十四条路径。", 1000, 470, full),
    )

    pruned = tree_elements(1, x0=30, y0=20, width=940, height=430, highlight=True)
    write(
        "chapter-02-garden-pruned.svg",
        svg_document("观测蓝白蓝后的三条剩余路径", "不符合蓝白蓝颜色顺序的路径均被灰化，剩下三条深色路径。", 1000, 470, pruned),
    )

    body: list[str] = []
    panel_width = 370
    for panel, n_blue in enumerate((1, 2, 3)):
        x0 = 20 + panel * 390
        count = n_blue * (4 - n_blue) * n_blue
        body.append(
            f'<text x="{fmt(x0 + panel_width / 2)}" y="30" text-anchor="middle" '
            f'font-family="-apple-system,BlinkMacSystemFont,PingFang SC,sans-serif" font-size="18" fill="#263f86">'
            f'{n_blue} 蓝 {4 - n_blue} 白：{count} 条相容路径</text>'
        )
        body.extend(tree_elements(n_blue, x0=x0, y0=42, width=panel_width, height=390, highlight=True))
        if panel < 2:
            divider = x0 + panel_width + 10
            body.append(f'<line x1="{divider}" y1="18" x2="{divider}" y2="440" stroke="#d9d5c8"/>')
    write(
        "chapter-02-garden-comparison.svg",
        svg_document(
            "三个弹珠组成猜想的相容路径比较",
            "一蓝三白、二蓝二白、三蓝一白三个猜想分别留下三条、八条和九条与蓝白蓝数据相容的路径。",
            1190,
            455,
            body,
        ),
    )
    print(f"generated marble-garden SVGs in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
