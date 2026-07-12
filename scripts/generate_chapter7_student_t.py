#!/usr/bin/env python3
"""Generate deterministic Chinese SVG for Chapter 7 Figure 7.11."""
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'translations/zh/media/chapter-07-student-t.svg'
FONT='PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif';BLUE='#6670ee';BLACK='#30332e'
def normal(x): return math.exp(-x*x/2)/math.sqrt(2*math.pi)
def student(x,nu=2): return math.gamma((nu+1)/2)/(math.sqrt(nu*math.pi)*math.gamma(nu/2))*(1+x*x/nu)**(-(nu+1)/2)
def f(v):return f'{v:.2f}'.rstrip('0').rstrip('.')
def main():
    w,h=1200,580;lefts=[110,665];top=70;pw,ph=430,390
    b=['<?xml version="1.0" encoding="UTF-8"?>',f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">','<title>薄尾分布与高影响力观测</title>','<desc>左图比较高斯与自由度二的 Student-t 密度，右图比较负对数密度；Student-t 尾部下降更慢。</desc>','<rect width="100%" height="100%" fill="#fff"/>']
    for j,left in enumerate(lefts):
        xmin,xmax=(-5,5) if j==0 else (-7,7);ymin,ymax=(0,.72) if j==0 else (0,32)
        px=lambda x:left+(x-xmin)/(xmax-xmin)*pw;py=lambda y:top+ph-(y-ymin)/(ymax-ymin)*ph
        b.append(f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="#343732" stroke-width="1.5"/>')
        for fn,color in [(normal,BLUE),(student,BLACK)]:
            vals=[]
            for i in range(321):
                x=xmin+(xmax-xmin)*i/320;y=fn(x) if j==0 else -math.log(fn(x));vals.append(f'{f(px(x))},{f(py(y))}')
            b.append(f'<polyline points="{" ".join(vals)}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x in range(math.ceil(xmin),math.floor(xmax)+1,2):b += [f'<line x1="{f(px(x))}" y1="{top+ph}" x2="{f(px(x))}" y2="{top+ph+7}" stroke="#333"/>',f'<text x="{f(px(x))}" y="{top+ph+29}" text-anchor="middle" font-family="{FONT}" font-size="16">{x}</text>']
        ylabel='密度' if j==0 else '负对数密度';b += [f'<text x="{left+pw/2}" y="525" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">数值</text>',f'<text x="{left-62}" y="{top+ph/2}" transform="rotate(-90 {left-62} {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="#263f86">{ylabel}</text>']
    b += [f'<line x1="430" y1="555" x2="480" y2="555" stroke="{BLUE}" stroke-width="3"/><text x="490" y="561" font-family="{FONT}" font-size="17">高斯</text>',f'<line x1="625" y1="555" x2="675" y2="555" stroke="{BLACK}" stroke-width="3"/><text x="685" y="561" font-family="{FONT}" font-size="17">Student-t（ν=2）</text>','</svg>',''];OUT.write_text('\n'.join(b),encoding='utf-8');print(f'generated {OUT}')
if __name__=='__main__':main()
