#!/usr/bin/env python3
"""Generate deterministic SVG output for R code 7.29."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'translations/zh/media/chapter-07-waic-compare.svg'
FONT='PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif'
def main():
    rows=[('m6.7',354,362,14.3),('m6.8',397,403,11.3),('m6.6',401,406,11.7)]
    lo,hi=345,425; left,top,pw=150,65,650
    px=lambda v:left+(v-lo)/(hi-lo)*pw
    b=['<?xml version="1.0" encoding="UTF-8"?>','<svg xmlns="http://www.w3.org/2000/svg" width="900" height="360" viewBox="0 0 900 360" role="img">','<title>三个植物模型的 WAIC 比较</title>','<desc>实心点为样本内离差，空心点为 WAIC，线段为标准误；浅色三角线段表示前两个模型 WAIC 差值的标准误。</desc>','<rect width="100%" height="100%" fill="#fff"/>',f'<text x="475" y="35" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">WAIC</text>']
    for t in range(350,421,10): b += [f'<line x1="{px(t):.1f}" y1="250" x2="{px(t):.1f}" y2="258" stroke="#333"/>',f'<text x="{px(t):.1f}" y="282" text-anchor="middle" font-family="{FONT}" font-size="16">{t}</text>']
    b.append(f'<line x1="{left}" y1="250" x2="{left+pw}" y2="250" stroke="#333"/>')
    for i,(name,dev,waic,se) in enumerate(rows):
        y=85+i*70;b += [f'<text x="120" y="{y+6}" text-anchor="end" font-family="{FONT}" font-size="18">{name}</text>',f'<circle cx="{px(dev):.1f}" cy="{y}" r="5" fill="#30332e"/>',f'<line x1="{px(waic-se):.1f}" y1="{y}" x2="{px(waic+se):.1f}" y2="{y}" stroke="#30332e" stroke-width="2"/>',f'<circle cx="{px(waic):.1f}" cy="{y}" r="6" fill="#fff" stroke="#30332e" stroke-width="2"/>']
    b += [f'<line x1="{px(362):.1f}" y1="120" x2="{px(403):.1f}" y2="120" stroke="#a9aec0" stroke-width="3"/>',f'<polygon points="{px(382):.1f},112 {px(374):.1f},128 {px(390):.1f},128" fill="#6670ee"/>',f'<text x="475" y="325" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">离差</text>','</svg>','']
    OUT.write_text('\n'.join(b),encoding='utf-8');print(f'generated {OUT}')
if __name__=='__main__':main()
