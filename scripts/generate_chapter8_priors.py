#!/usr/bin/env python3
"""Generate the translated prior-predictive panels for Figure 8.3."""

from __future__ import annotations

import random
from pathlib import Path

from generate_chapter8_ruggedness import load_rows


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-08-ruggedness-priors.svg"


def panel(x0, title_a, title_b, a_sd, b_sd, ymin_obs, ymax_obs, seed):
    y0, width, height = 10, 560, 480
    left, right, top, bottom = 76, 18, 72, 62
    pw, ph = width - left - right, height - top - bottom
    sx = lambda x: x0 + left + (x + .1) / 1.2 * pw
    sy = lambda y: y0 + top + (1.5 - y) * ph
    rng = random.Random(seed)
    draws = [(rng.gauss(1, a_sd), rng.gauss(0, b_sd)) for _ in range(50)]
    parts = [f'<text class="prior" x="{x0+width/2}" y="30" text-anchor="middle">{title_a}</text>', f'<text class="prior" x="{x0+width/2}" y="55" text-anchor="middle">{title_b}</text>']
    parts.append(f'<rect class="plot" x="{x0+left}" y="{y0+top}" width="{pw}" height="{ph}"/>')
    for tick in [0, .2, .4, .6, .8, 1.0]:
        x = sx(tick); parts += [f'<line class="tick" x1="{x:.1f}" y1="{y0+top+ph}" x2="{x:.1f}" y2="{y0+top+ph+6}"/>', f'<text class="axis" x="{x:.1f}" y="{y0+top+ph+24}" text-anchor="middle">{tick:.1f}</text>']
    for tick in [.6,.8,1.0,1.2,1.4]:
        y=sy(tick); parts += [f'<line class="grid" x1="{x0+left}" y1="{y:.1f}" x2="{x0+left+pw}" y2="{y:.1f}"/>',f'<text class="axis" x="{x0+left-11}" y="{y+5:.1f}" text-anchor="end">{tick:.1f}</text>']
    parts += [f'<line class="observed" x1="{x0+left}" y1="{sy(ymin_obs):.1f}" x2="{x0+left+pw}" y2="{sy(ymin_obs):.1f}"/>',f'<line class="observed" x1="{x0+left}" y1="{sy(ymax_obs):.1f}" x2="{x0+left+pw}" y2="{sy(ymax_obs):.1f}"/>']
    extreme = max(range(len(draws)), key=lambda i: abs(draws[i][1])) if b_sd > .5 else -1
    for i,(a,b) in enumerate(draws):
        cls="line highlight" if i==extreme else "line"
        parts.append(f'<line class="{cls}" clip-path="url(#clip-{x0})" x1="{sx(-.1):.1f}" y1="{sy(a+b*(-.315)):.1f}" x2="{sx(1.1):.1f}" y2="{sy(a+b*(.885)):.1f}"/>')
    parts += [f'<text class="label" x="{x0+left+pw/2}" y="{y0+height-8}" text-anchor="middle">崎岖度</text>',f'<text class="label" transform="translate({x0+20},{y0+top+ph/2}) rotate(-90)" text-anchor="middle">对数 GDP（占均值比例）</text>',f'<clipPath id="clip-{x0}"><rect x="{x0+left}" y="{y0+top}" width="{pw}" height="{ph}"/></clipPath>']
    return "".join(parts)


def main():
    ys=[row["y"] for row in load_rows()]
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520" role="img" aria-labelledby="title desc"><title id="title">地形崎岖度模型的先验预测模拟</title><desc id="desc">左图宽松先验产生许多不合理直线；右图收紧截距与斜率先验后，直线大多落在观测范围附近。</desc><style>.prior{{font:17px ui-monospace,monospace;fill:#29302d}}.axis{{font:15px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#30332e}}.label{{font:18px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#30332e}}.plot{{fill:#fff;stroke:#4b4e49;stroke-width:1.2}}.grid{{stroke:#e6e6e2}}.tick{{stroke:#4b4e49}}.observed{{stroke:#353833;stroke-width:1.5;stroke-dasharray:8 7}}.line{{stroke:#1e211e;stroke-width:1.4;opacity:.22}}.highlight{{stroke:#5666df;stroke-width:3;opacity:.85}}</style>{panel(20,"a ~ Normal(1, 1)","b ~ Normal(0, 1)",1,1,min(ys),max(ys),7)}{panel(620,"a ~ Normal(1, 0.1)","b ~ Normal(0, 0.3)",.1,.3,min(ys),max(ys),8)}</svg>'''
    OUT.write_text(svg,encoding="utf-8")
    print(OUT)


if __name__ == "__main__": main()
