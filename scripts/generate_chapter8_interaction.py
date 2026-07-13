#!/usr/bin/env python3
"""Generate translated Figure 8.5 for the ruggedness-by-continent interaction."""
from pathlib import Path
import math
from generate_chapter8_ruggedness import load_rows, regression

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'translations/zh/media/chapter-08-ruggedness-interaction.svg'
ZH={'Equatorial Guinea':'赤道几内亚','South Africa':'南非','Swaziland':'斯威士兰','Rwanda':'卢旺达','Burundi':'布隆迪','Seychelles':'塞舌尔','Lesotho':'莱索托','Luxembourg':'卢森堡','Switzerland':'瑞士','Greece':'希腊','Lebanon':'黎巴嫩','Nepal':'尼泊尔','Yemen':'也门','Tajikistan':'塔吉克斯坦'}

def panel(rows,x0,title,ymin,ymax,filled,labels):
    y0,w,h=10,570,510;L,R,T,B=78,18,55,68;pw=w-L-R;ph=h-T-B
    sx=lambda x:x0+L+x/1.05*pw;sy=lambda y:y0+T+(ymax-y)/(ymax-ymin)*ph
    a,b,sd,xb,sxx,n=regression(rows);parts=[f'<text class="title" x="{x0+w/2}" y="34" text-anchor="middle">{title}</text>',f'<rect class="plot" x="{x0+L}" y="{y0+T}" width="{pw}" height="{ph}"/>']
    for t in [0,.2,.4,.6,.8,1.0]:parts += [f'<text class="axis" x="{sx(t):.1f}" y="{y0+T+ph+25}" text-anchor="middle">{t:.1f}</text>']
    t=math.ceil(ymin*10)/10
    while t<=ymax+.001:parts += [f'<line class="grid" x1="{x0+L}" y1="{sy(t):.1f}" x2="{x0+L+pw}" y2="{sy(t):.1f}"/><text class="axis" x="{x0+L-11}" y="{sy(t)+5:.1f}" text-anchor="end">{t:.1f}</text>'];t+=.1
    xs=[i/80*1.05 for i in range(81)];up=[];lo=[]
    for x in xs:
        m=a+b*x;se=sd*math.sqrt(1/n+(x-xb)**2/sxx);up.append((sx(x),sy(m+2.17*se)));lo.append((sx(x),sy(m-2.17*se)))
    parts.append('<polygon class="band" points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in up+list(reversed(lo)))+'"/>')
    parts.append(f'<line class="fit" x1="{sx(0):.1f}" y1="{sy(a):.1f}" x2="{sx(1.05):.1f}" y2="{sy(a+b*1.05):.1f}"/>')
    for r in rows:parts.append(f'<circle class="point {"filled" if filled else ""}" cx="{sx(r["x"]):.1f}" cy="{sy(r["y"]):.1f}" r="3.8"/>')
    offsets={'Equatorial Guinea':(-8,18,'end'),'South Africa':(-8,-8,'end'),'Swaziland':(8,-7,'start'),'Rwanda':(8,16,'start'),'Burundi':(-8,16,'end'),'Seychelles':(-8,17,'end'),'Lesotho':(-8,-8,'end'),'Luxembourg':(8,18,'start'),'Switzerland':(8,4,'start'),'Greece':(8,-7,'start'),'Lebanon':(8,15,'start'),'Nepal':(-8,-8,'end'),'Yemen':(8,-9,'start'),'Tajikistan':(-8,-9,'end')}
    for r in rows:
        if r['country'] in labels:
            dx,dy,anchor=offsets[r['country']];parts.append(f'<text class="ann" x="{sx(r["x"])+dx:.1f}" y="{sy(r["y"])+dy:.1f}" text-anchor="{anchor}">{ZH[r["country"]]}</text>')
    parts += [f'<text class="label" x="{x0+L+pw/2}" y="{h-5}" text-anchor="middle">崎岖度（标准化）</text>',f'<text class="label" transform="translate({x0+20},{y0+T+ph/2}) rotate(-90)" text-anchor="middle">对数 GDP（占均值比例）</text>']
    return ''.join(parts)

def main():
    rows=load_rows();af=[r for r in rows if r['africa']];na=[r for r in rows if not r['africa']]
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="530" viewBox="0 0 1200 530" role="img" aria-labelledby="title desc"><title id="title">非洲与非非洲崎岖度交互模型后验预测</title><desc id="desc">非洲国家回归斜率为正，非非洲国家为负，阴影表示均值的百分之九十七后验区间。</desc><style>.title{{font:700 21px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}.axis,.ann{{font:14px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#30332e}}.label{{font:17px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}.plot{{fill:#fff;stroke:#444}}.grid{{stroke:#e5e5e1}}.band{{fill:#cfd2d1;opacity:.85}}.fit{{stroke:#151715;stroke-width:2.8}}.point{{fill:#fff;stroke:#171917;stroke-width:1.2}}.point.filled{{fill:#6874ef;stroke:#6874ef}}</style>{panel(af,10,'非洲国家',.70,1.15,True,set(ZH)&{r['country'] for r in af})}{panel(na,610,'非非洲国家',.78,1.30,False,set(ZH)&{r['country'] for r in na})}</svg>'''
    OUT.write_text(svg,encoding='utf-8');print(OUT)
if __name__=='__main__':main()
