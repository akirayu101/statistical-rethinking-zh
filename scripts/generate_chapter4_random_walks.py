#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-random-walks.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def polyline(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def kde(values: list[float], xs: list[float]) -> list[float]:
    count = len(values)
    mean = sum(values) / count
    variance = sum((value - mean) ** 2 for value in values) / (count - 1)
    bandwidth = max(0.15, 1.06 * math.sqrt(variance) * count ** (-0.2))
    scale = 1 / (count * bandwidth * math.sqrt(2 * math.pi))
    return [scale * sum(math.exp(-0.5 * ((x - value) / bandwidth) ** 2) for value in values) for x in xs]


def density_panel(
    values: list[float],
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    normal_steps: int | None = None,
) -> list[str]:
    xs = [-6 + 12 * index / 240 for index in range(241)]
    density = kde(values, xs)
    normal = []
    if normal_steps is not None:
        sd = math.sqrt(normal_steps / 3)
        normal = [math.exp(-0.5 * (value / sd) ** 2) / (sd * math.sqrt(2 * math.pi)) for value in xs]
    ymax = max(density + normal) * 1.08

    def px(value: float) -> float:
        return x + width * (value + 6) / 12

    def py(value: float) -> float:
        return y + height * (1 - value / ymax)

    body = [
        f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#fff" stroke="#363934" stroke-width="1.2"/>',
        f'  <text x="{fmt(x + width / 2)}" y="{y - 16}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">{label}</text>',
        f'  <polyline points="{polyline([(px(xv), py(yv)) for xv, yv in zip(xs, density)])}" fill="none" stroke="#6670ee" stroke-width="3"/>',
    ]
    if normal:
        body.append(
            f'  <polyline points="{polyline([(px(xv), py(yv)) for xv, yv in zip(xs, normal)])}" fill="none" stroke="#30332e" stroke-width="2.2"/>'
        )
    for tick in (-6, -3, 0, 3, 6):
        tx = px(tick)
        body.extend(
            [
                f'  <line x1="{fmt(tx)}" y1="{y + height}" x2="{fmt(tx)}" y2="{y + height + 7}" stroke="#363934"/>',
                f'  <text x="{fmt(tx)}" y="{y + height + 28}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="#30332e">{tick}</text>',
            ]
        )
    body.extend(
        [
            f'  <text x="{fmt(x + width / 2)}" y="{y + height + 58}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">位置</text>',
            f'  <text x="{x - 34}" y="{fmt(y + height / 2)}" transform="rotate(-90 {x - 34} {fmt(y + height / 2)})" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">概率密度</text>',
        ]
    )
    return body


def main() -> int:
    rng = random.Random(4102)
    paths: list[list[float]] = []
    for _ in range(100):
        values = [0.0]
        for _ in range(16):
            values.append(values[-1] + rng.uniform(-1, 1))
        paths.append(values)

    density_samples: dict[int, list[float]] = {}
    for steps in (4, 8, 16):
        density_samples[steps] = [sum(rng.uniform(-1, 1) for _ in range(steps)) for _ in range(3000)]

    width, height = 1200, 850
    top_x, top_y, top_width, top_height = 110, 65, 1020, 285

    def top_px(step: int) -> float:
        return top_x + top_width * step / 16

    def top_py(position: float) -> float:
        return top_y + top_height * (1 - (position + 6) / 12)

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>足球场随机游走逐渐形成正态分布</title>",
        "  <desc>上图显示一百条十六步随机游走；下方三个面板显示四步、八步和十六步后位置的经验概率密度，十六步面板叠加理想正态曲线。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        f'  <rect x="{top_x}" y="{top_y}" width="{top_width}" height="{top_height}" fill="#fff" stroke="#363934" stroke-width="1.2"/>',
    ]
    for index, path in enumerate(paths):
        points = [(top_px(step), top_py(value)) for step, value in enumerate(path)]
        body.append(
            f'  <polyline points="{polyline(points)}" fill="none" stroke="{"#30332e" if index == 0 else "#6670ee"}" stroke-width="{"2.5" if index == 0 else "1"}" opacity="{"1" if index == 0 else "0.25"}"/>'
        )
    for step in (4, 8, 16):
        tx = top_px(step)
        body.append(f'  <line x1="{fmt(tx)}" y1="{top_y}" x2="{fmt(tx)}" y2="{top_y + top_height}" stroke="#30332e" stroke-width="1.3" stroke-dasharray="7 6"/>')
    for tick in (0, 4, 8, 12, 16):
        tx = top_px(tick)
        body.append(f'  <text x="{fmt(tx)}" y="{top_y + top_height + 29}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="#30332e">{tick}</text>')
    for tick in (-6, -3, 0, 3, 6):
        ty = top_py(tick)
        body.append(f'  <text x="{top_x - 16}" y="{fmt(ty + 5)}" text-anchor="end" font-family="{FONT}" font-size="14" fill="#30332e">{tick}</text>')
    body.extend(
        [
            f'  <text x="{width / 2}" y="{top_y + top_height + 58}" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">步数</text>',
            f'  <text x="42" y="{top_y + top_height / 2}" transform="rotate(-90 42 {top_y + top_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#30332e">位置</text>',
        ]
    )

    panel_y, panel_width, panel_height = 500, 285, 210
    for index, steps in enumerate((4, 8, 16)):
        panel_x = 85 + index * 385
        body.extend(
            density_panel(
                density_samples[steps],
                x=panel_x,
                y=panel_y,
                width=panel_width,
                height=panel_height,
                label=f"{steps} 步",
                normal_steps=steps if steps == 16 else None,
            )
        )
    body.extend(
        [
            f'  <line x1="850" y1="805" x2="890" y2="805" stroke="#30332e" stroke-width="2.2"/>',
            f'  <text x="902" y="811" font-family="{FONT}" font-size="15" fill="#30332e">理想正态概率密度</text>',
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
