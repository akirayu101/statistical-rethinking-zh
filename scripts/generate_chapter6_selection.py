#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG for Chapter 6 Figure 6.1."""

from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-06-selection-distortion.svg"
LEGS_OUT = ROOT / "translations" / "zh" / "media" / "chapter-06-multicollinear-legs.svg"
MILK_PAIRS_OUT = ROOT / "translations" / "zh" / "media" / "chapter-06-milk-pairs.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"


def main() -> int:
    rng = random.Random(1234)
    count = 200
    news = [rng.gauss(0, 1) for _ in range(count)]
    trust = [rng.gauss(0, 1) for _ in range(count)]
    selected = set(sorted(range(count), key=lambda i: news[i] + trust[i])[-20:])
    sx = [news[i] for i in selected]
    sy = [trust[i] for i in selected]
    xbar, ybar = sum(sx) / len(sx), sum(sy) / len(sy)
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(sx, sy)) / sum((x - xbar) ** 2 for x in sx)
    intercept = ybar - slope * xbar
    corr = sum((x - xbar) * (y - ybar) for x, y in zip(sx, sy)) / math.sqrt(
        sum((x - xbar) ** 2 for x in sx) * sum((y - ybar) ** 2 for y in sy)
    )
    width, height = 900, 650
    left, top, pw, ph = 125, 55, 690, 475
    low, high = -3.2, 3.2

    def px(value: float) -> float:
        return left + (value - low) / (high - low) * pw

    def py(value: float) -> float:
        return top + ph - (value - low) / (high - low) * ph

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>科研资助筛选造成的选择扭曲</title>",
        f"  <desc>两百份提案在筛选前可信度与新闻价值不相关；获选的百分之十内部出现约 {corr:.2f} 的负相关。</desc>",
        '  <rect width="100%" height="100%" fill="#fff"/>',
        f'  <rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',
    ]
    for i, (x, y) in enumerate(zip(news, trust)):
        chosen = i in selected
        body.append(
            f'  <circle cx="{px(x):.2f}" cy="{py(y):.2f}" r="{5 if chosen else 3.5}" fill="{"#6670ee" if chosen else "#a9aca8"}" opacity="{0.9 if chosen else 0.55}"/>'
        )
    x1, x2 = min(sx), max(sx)
    body.append(f'  <line x1="{px(x1):.2f}" y1="{py(intercept+slope*x1):.2f}" x2="{px(x2):.2f}" y2="{py(intercept+slope*x2):.2f}" stroke="#263f86" stroke-width="3"/>')
    for tick in range(-3, 4):
        body.extend([
            f'  <text x="{px(tick):.2f}" y="560" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
            f'  <text x="105" y="{py(tick)+5:.2f}" text-anchor="end" font-family="{FONT}" font-size="16" fill="#30332e">{tick}</text>',
        ])
    body.extend([
        f'  <text x="470" y="606" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">新闻价值</text>',
        f'  <text x="48" y="292" transform="rotate(-90 48 292)" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">可信度</text>',
        f'  <circle cx="640" cy="620" r="5" fill="#6670ee"/><text x="654" y="626" font-family="{FONT}" font-size="16" fill="#30332e">获选</text>',
        f'  <circle cx="720" cy="620" r="4" fill="#a9aca8"/><text x="734" y="626" font-family="{FONT}" font-size="16" fill="#30332e">落选</text>',
        "</svg>", "",
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    LEGS_OUT.write_text(multicollinear_legs(), encoding="utf-8")
    print(f"generated {LEGS_OUT}")
    MILK_PAIRS_OUT.write_text(milk_pairs(), encoding="utf-8")
    print(f"generated {MILK_PAIRS_OUT}")
    return 0


def multicollinear_legs() -> str:
    rng = random.Random(909)
    samples = []
    for _ in range(1200):
        total = rng.gauss(2.0, 0.065)
        difference = rng.gauss(-1.55, 5.0)
        samples.append(((total + difference) / 2, (total - difference) / 2))
    width, height = 1200, 620
    body = ['<?xml version="1.0" encoding="UTF-8"?>', f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">', '<title>共线双腿模型的联合后验与参数和</title>', '<desc>左图显示 bl 与 br 的狭长负相关后验脊，右图显示二者之和集中在 2 附近。</desc>', '<rect width="100%" height="100%" fill="#fff"/>']
    lx, top, pw, ph = 95, 60, 440, 430
    rx = 700
    def sx(v): return lx + (v + 6) / 12 * pw
    def sy(v): return top + ph - (v + 6) / 12 * ph
    body.append(f'<rect x="{lx}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="#343732"/>')
    for bl, br in samples:
        body.append(f'<circle cx="{sx(br):.2f}" cy="{sy(bl):.2f}" r="2.2" fill="#6670ee" opacity="0.12"/>')
    for t in [-6,-4,-2,0,2,4,6]:
        body.extend([f'<text x="{sx(t):.2f}" y="520" text-anchor="middle" font-family="{FONT}" font-size="15">{t}</text>',f'<text x="75" y="{sy(t)+5:.2f}" text-anchor="end" font-family="{FONT}" font-size="15">{t}</text>'])
    body.extend([f'<text x="315" y="565" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">br</text>',f'<text x="38" y="275" transform="rotate(-90 38 275)" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">bl</text>'])
    def px(v): return rx + (v - 1.75) / 0.5 * 390
    def py(v): return top + ph - v / 6.5 * ph
    grid=[1.75+i*0.5/160 for i in range(161)]
    pts=[]
    sd=.065
    for v in grid:
        d=math.exp(-0.5*((v-2)/sd)**2)/(sd*math.sqrt(2*math.pi))
        pts.append(f'{px(v):.2f},{py(d):.2f}')
    body.extend([f'<rect x="{rx}" y="{top}" width="390" height="{ph}" fill="#fff" stroke="#343732"/>',f'<polyline points="{" ".join(pts)}" fill="none" stroke="#263f86" stroke-width="4"/>'])
    for t in [1.8,1.9,2.0,2.1,2.2]: body.append(f'<text x="{px(t):.2f}" y="520" text-anchor="middle" font-family="{FONT}" font-size="15">{t:.1f}</text>')
    body.extend([f'<text x="895" y="565" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">bl 与 br 之和</text>',f'<text x="650" y="275" transform="rotate(-90 650 275)" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">概率密度</text>','</svg>',''])
    return "\n".join(body)


def milk_pairs() -> str:
    rng = random.Random(613)
    rows = []
    for _ in range(29):
        fat = rng.uniform(5, 58)
        lactose = 77 - 0.82 * fat + rng.gauss(0, 4)
        kcal = 0.38 + 0.010 * fat - 0.002 * lactose + rng.gauss(0, 0.055)
        rows.append((kcal, fat, lactose))
    names = ["每克乳汁千卡", "脂肪百分比", "乳糖百分比"]
    ranges = [(0.35, 1.0), (0, 60), (25, 80)]
    width, height = 1000, 920
    body = ['<?xml version="1.0" encoding="UTF-8"?>', f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">', '<title>灵长类乳汁能量、脂肪和乳糖的变量对图</title>', '<desc>脂肪与乳糖强烈负相关，并分别与乳汁能量正相关和负相关。</desc>', '<rect width="100%" height="100%" fill="#fff"/>']
    starts = [75, 375, 675]
    size = 245
    for row in range(3):
        for col in range(3):
            x, y = starts[col], starts[row]
            body.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="#fff" stroke="#d0d2cf"/>')
            if row == col:
                body.append(f'<text x="{x+size/2}" y="{y+size/2}" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">{names[row]}</text>')
                continue
            xmin, xmax = ranges[col]; ymin, ymax = ranges[row]
            for values in rows:
                px = x + 12 + (values[col]-xmin)/(xmax-xmin)*(size-24)
                py = y + size - 12 - (values[row]-ymin)/(ymax-ymin)*(size-24)
                body.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="4.2" fill="#fff" stroke="#6670ee" stroke-width="1.8"/>')
    body.extend(['</svg>', ''])
    return "\n".join(body)


if __name__ == "__main__":
    raise SystemExit(main())
