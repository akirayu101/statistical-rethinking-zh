#!/usr/bin/env python3
"""Generate deterministic Chinese SVG for Chapter 7 Figure 7.10."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'translations/zh/media/chapter-07-influence.svg'
FONT='PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif'
def main():
    w,h=900,620;left,top,pw,ph=120,70,690,430
    px=lambda x:left+x/1.15*pw;py=lambda y:top+ph-y/2.35*ph
    pts=[(.05,.05),(.12,.12),(.18,.20),(.22,.15),(.3,.26),(.35,.18),(.42,.32),(.48,.28),(.55,.37),(.62,.43),(.7,.48),(.26,.55),(.38,.62),(.6,.7),(.15,.35),(.1,.18),(.78,.52),(.9,.65)]
    b=['<?xml version="1.0" encoding="UTF-8"?>',f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">','<title>高影响力观测与样本外预测</title>','<desc>横轴是 PSIS 的 Pareto k，纵轴是 WAIC 惩罚项；爱达荷位于右上角，缅因也被标出。</desc>','<rect width="100%" height="100%" fill="#fff"/>',f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="#343732" stroke-width="1.5"/>',f'<line x1="{px(.5):.1f}" y1="{top}" x2="{px(.5):.1f}" y2="{top+ph}" stroke="#777" stroke-dasharray="7 6"/>']
    for x,y in pts:b.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="4.5" fill="#6670ee"/>')
    for x,y,label in [(.32,.65,'ME'),(1.05,2.15,'ID')]:
        b += [f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="6" fill="#6670ee"/>',f'<text x="{px(x)+10:.1f}" y="{py(y)-10:.1f}" font-family="{FONT}" font-size="19" font-weight="700">{label}</text>']
    for x in [0,.25,.5,.75,1.0]:b += [f'<line x1="{px(x):.1f}" y1="{top+ph}" x2="{px(x):.1f}" y2="{top+ph+7}" stroke="#333"/>',f'<text x="{px(x):.1f}" y="{top+ph+30}" text-anchor="middle" font-family="{FONT}" font-size="16">{x:.2g}</text>']
    for y in [0,.5,1,1.5,2]:b += [f'<line x1="{left-7}" y1="{py(y):.1f}" x2="{left}" y2="{py(y):.1f}" stroke="#333"/>',f'<text x="{left-15}" y="{py(y)+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="16">{y:.1f}</text>']
    b += [f'<text x="{left+pw/2}" y="570" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">PSIS Pareto k</text>',f'<text x="38" y="{top+ph/2}" transform="rotate(-90 38 {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#263f86">WAIC 惩罚项</text>','</svg>',''];OUT.write_text('\n'.join(b),encoding='utf-8');print(f'generated {OUT}')
if __name__=='__main__':main()
