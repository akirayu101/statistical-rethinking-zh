#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG for Chapter 6 Figure 6.4."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-06-happiness-marriage.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def main() -> int:
    rng = random.Random(1977)
    people: list[tuple[int, float, bool]] = []
    happiness_grid = [-2 + 4 * i / 19 for i in range(20)]
    for age in range(65):
        happiness = happiness_grid[:]
        rng.shuffle(happiness)
        for happy in happiness:
            married = False
            annual_probability = min(0.18, 0.028 * math.exp(0.72 * happy))
            for _ in range(max(0, age - 17)):
                if rng.random() < annual_probability:
                    married = True
                    break
            people.append((age, happy, married))

    width, height = 1000, 650
    left, top, plot_width, plot_height = 105, 90, 820, 440

    def px(age: int) -> float:
        return left + age / 65 * plot_width

    def py(happiness: float) -> float:
        return top + plot_height - (happiness + 2.15) / 4.3 * plot_height

    married_share = sum(married for _, _, married in people) / len(people)
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>年龄、幸福感与婚姻状态的模拟数据</title>",
        f"<desc>一千三百人的幸福感终生不变；已婚者约占 {married_share:.0%}，年龄越大且幸福感越高，结婚概率越高。</desc>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
    ]
    for age, happy, married in people:
        if married:
            body.append(f'<circle cx="{px(age):.2f}" cy="{py(happy):.2f}" r="3.7" fill="#6670ee" opacity="0.9"/>')
        else:
            body.append(f'<circle cx="{px(age):.2f}" cy="{py(happy):.2f}" r="3.7" fill="#fff" stroke="#777b76" stroke-width="1.2"/>')
    for tick in range(0, 61, 10):
        x = px(tick)
        body.extend([
            f'<line x1="{x:.2f}" y1="{top + plot_height}" x2="{x:.2f}" y2="{top + plot_height + 7}" stroke="#343732"/>',
            f'<text x="{x:.2f}" y="{top + plot_height + 30}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
        ])
    for tick in [-2, -1, 0, 1, 2]:
        y = py(tick)
        body.extend([
            f'<line x1="{left - 7}" y1="{y:.2f}" x2="{left}" y2="{y:.2f}" stroke="#343732"/>',
            f'<text x="{left - 16}" y="{y + 6:.2f}" text-anchor="end" font-family="{FONT}" font-size="17" fill="#30332e">{tick}</text>',
        ])
    body.extend([
        f'<text x="{left + plot_width / 2}" y="605" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">年龄</text>',
        f'<text x="42" y="{top + plot_height / 2}" transform="rotate(-90 42 {top + plot_height / 2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">幸福感</text>',
        f'<circle cx="360" cy="45" r="5" fill="#fff" stroke="#777b76" stroke-width="1.5"/><text x="375" y="51" font-family="{FONT}" font-size="18" fill="#30332e">未婚</text>',
        f'<circle cx="520" cy="45" r="5" fill="#6670ee"/><text x="535" y="51" font-family="{FONT}" font-size="18" fill="#6670ee">已婚</text>',
        "</svg>",
        "",
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT} ({married_share:.1%} married)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
