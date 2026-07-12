#!/usr/bin/env python3
"""Generate the deterministic Chinese SVG for Chapter 7 Figure 7.9."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations/zh/media/chapter-07-criteria-comparison.svg"
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"
BLUE, BLACK = "#6670ee", "#30332e"

PANELS = [
    ("N = 20", "平均离差", (55.7,59.6),
     [[57.8,58.1,55.9,57.7,58.6],[57.1,58.0,56.3,57.9,59.4],[57.1,58.0,56.6,57.5,59.2],[57.1,57.9,56.1,56.5,57.4]]),
    ("N = 20", "平均误差（测试离差）", (5.8,7.4),
     [[6.8,7.1,6.2,6.4,6.8],[7.4,7.0,6.2,6.4,6.7],[7.4,7.1,6.2,6.4,6.75],[6.8,7.05,5.9,6.0,6.3]]),
    ("N = 100", "平均离差", (268,286),
     [[284.7,283.6,268.5,269.2,270.4],[284.8,284.7,268.9,269.4,270.5],[284.8,284.7,268.8,269.4,270.5],[284.6,283.4,268.7,269.2,270.4]]),
    ("N = 100", "平均误差（测试离差）", (12.8,15.9),
     [[15.8,15.0,13.4,13.1,13.6],[15.8,15.4,13.5,13.6,13.0],[15.8,15.4,13.5,13.6,13.0],[15.8,15.0,13.4,13.1,13.6]]),
]

def f(v): return f"{v:.2f}".rstrip("0").rstrip(".")

def main():
    w,h=1200,900; pw,ph=430,300; lefts=[105,650]; tops=[75,485]
    body=['<?xml version="1.0" encoding="UTF-8"?>',f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">','<title>WAIC 与交叉验证对样本外离差的估计</title>','<desc>四个面板比较样本量二十和一百时，CV、PSIS、WAIC 对平坦和正则化先验模型测试离差及误差的估计。</desc>','<rect width="100%" height="100%" fill="#fff"/>']
    for idx,(title,ylabel,ylim,series) in enumerate(PANELS):
        left=lefts[idx%2]; top=tops[idx//2]; ymin,ymax=ylim
        px=lambda i:left+28+i*(pw-56)/4
        py=lambda v:top+ph-(v-ymin)/(ymax-ymin)*ph
        body += [f'<text x="{left+pw/2}" y="{top-30}" text-anchor="middle" font-family="{FONT}" font-size="23" font-weight="700" fill="#263f86">{title}</text>',f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="#343732" stroke-width="1.4"/>']
        for i in range(5):
            body += [f'<line x1="{f(px(i))}" y1="{top+ph}" x2="{f(px(i))}" y2="{top+ph+6}" stroke="#343732"/>',f'<text x="{f(px(i))}" y="{top+ph+28}" text-anchor="middle" font-family="{FONT}" font-size="16">{i+1}</text>']
        styles=[(BLACK,"",2.5),(BLUE,"",2.2),(BLUE,"7 6",2.2),(BLACK,"",1.7)]
        for vals,(color,dash,sw) in zip(series,styles):
            pts=' '.join(f'{f(px(i))},{f(py(v))}' for i,v in enumerate(vals)); da=f' stroke-dasharray="{dash}"' if dash else ''
            body.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{sw}"{da}/>')
        if idx in (0,2):
            for i,v in enumerate(series[0]): body.append(f'<circle cx="{f(px(i))}" cy="{f(py(v))}" r="4.5" fill="#fff" stroke="{BLACK}" stroke-width="1.7"/>')
            for i,v in enumerate(series[3]): body.append(f'<circle cx="{f(px(i))}" cy="{f(py(v))}" r="4.5" fill="{BLACK}"/>')
        body += [f'<text x="{left+pw/2}" y="{top+ph+57}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#263f86">参数个数</text>',f'<text x="{left-62}" y="{top+ph/2}" transform="rotate(-90 {left-62} {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="#263f86">{ylabel}</text>']
    y=870
    for x,label,color,dash in [(245,"CV",BLUE,""),(390,"PSIS",BLUE,"7 6"),(555,"WAIC",BLACK,""),(720,"测试离差",BLACK,"")]:
        da=f' stroke-dasharray="{dash}"' if dash else ''; body += [f'<line x1="{x}" y1="{y}" x2="{x+48}" y2="{y}" stroke="{color}" stroke-width="2.4"{da}/>',f'<text x="{x+58}" y="{y+6}" font-family="{FONT}" font-size="17">{label}</text>']
    body += ['</svg>','']; OUT.write_text('\n'.join(body),encoding='utf-8'); print(f'generated {OUT}')
if __name__=='__main__': main()
