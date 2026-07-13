#!/usr/bin/env python3
"""Generate translated Figure 8.6, the reverse view of the GDP interaction."""
from pathlib import Path
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'translations/zh/media/chapter-08-africa-delta.svg'

def main():
    W,H=820,500;L,R,T,B=95,45,45,75;pw=W-L-R;ph=H-T-B
    xmin,xmax=-.2,1.2;ymin,ymax=-.35,.23
    sx=lambda x:L+(x-xmin)/(xmax-xmin)*pw
    sy=lambda y:T+(ymax-y)/(ymax-ymin)*ph
    xs=[xmin+i/100*(xmax-xmin) for i in range(101)];up=[];lo=[];means=[]
    for x in xs:
        m=(.89-1.05)+(.13-(-.14))*(x-.215)
        se=math.sqrt(.02**2+.01**2+(x-.215)**2*(.07**2+.05**2))
        means.append((sx(x),sy(m)));up.append((sx(x),sy(m+1.88*se)));lo.append((sx(x),sy(m-1.88*se)))
    s=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="820" height="500" viewBox="0 0 820 500" role="img" aria-labelledby="title desc"><title id="title">非洲与非非洲预期对数 GDP 差值</title><desc id="desc">低崎岖度时非洲国家预期 GDP 较低，高崎岖度时差值接近或略高于零。</desc><style>.axis,.ann{{font:16px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#30332e}}.label{{font:19px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}.plot{{fill:#fff;stroke:#444}}.grid{{stroke:#e5e5e1}}.zero{{stroke:#444;stroke-width:1.5;stroke-dasharray:8 7}}.band{{fill:#cfd2d1}}.fit{{fill:none;stroke:#171917;stroke-width:3}}</style><rect class="plot" x="{L}" y="{T}" width="{pw}" height="{ph}"/>''']
    for t in [0,.2,.4,.6,.8,1.0]:s += [f'<text class="axis" x="{sx(t):.1f}" y="{H-43}" text-anchor="middle">{t:.1f}</text>']
    for t in [-.3,-.2,-.1,0,.1,.2]:s += [f'<line class="grid" x1="{L}" y1="{sy(t):.1f}" x2="{W-R}" y2="{sy(t):.1f}"/><text class="axis" x="{L-12}" y="{sy(t)+5:.1f}" text-anchor="end">{t:.1f}</text>']
    s += ['<polygon class="band" points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in up+list(reversed(lo)))+'"/>',f'<line class="zero" x1="{L}" y1="{sy(0):.1f}" x2="{W-R}" y2="{sy(0):.1f}"/>','<polyline class="fit" points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in means)+'"/>',f'<text class="ann" x="{L+20}" y="{sy(0)-12:.1f}">非洲 GDP 较高</text>',f'<text class="ann" x="{L+20}" y="{sy(0)+24:.1f}">非洲 GDP 较低</text>',f'<text class="label" x="{L+pw/2}" y="{H-8}" text-anchor="middle">崎岖度</text>',f'<text class="label" transform="translate(24,{T+ph/2}) rotate(-90)" text-anchor="middle">预期对数 GDP 差值</text></svg>']
    OUT.write_text(''.join(s),encoding='utf-8');print(OUT)
if __name__=='__main__':main()
