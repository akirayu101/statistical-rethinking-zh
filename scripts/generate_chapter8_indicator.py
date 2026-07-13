#!/usr/bin/env python3
"""Generate translated Figure 8.4: a continent indicator changes intercept, not slope."""
from pathlib import Path
from generate_chapter8_ruggedness import load_rows

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'translations/zh/media/chapter-08-indicator-parallel.svg'

def solve3(a,b):
    m=[a[i][:]+[b[i]] for i in range(3)]
    for k in range(3):
        p=max(range(k,3),key=lambda i:abs(m[i][k]));m[k],m[p]=m[p],m[k]
        z=m[k][k];m[k]=[v/z for v in m[k]]
        for i in range(3):
            if i!=k:
                z=m[i][k];m[i]=[m[i][j]-z*m[k][j] for j in range(4)]
    return [m[i][3] for i in range(3)]

def main():
    rows=load_rows(); X=[]; y=[]
    for r in rows:
        X.append([1 if r['africa'] else 0,0 if r['africa'] else 1,r['x']-.215]);y.append(r['y'])
    xtx=[[sum(x[i]*x[j] for x in X) for j in range(3)] for i in range(3)]
    xty=[sum(x[i]*v for x,v in zip(X,y)) for i in range(3)]
    a1,a2,b=solve3(xtx,xty)
    W,H=900,560; L,R,T,B=105,55,55,80; pw=W-L-R;ph=H-T-B
    sx=lambda x:L+x/1.05*pw;sy=lambda v:T+(1.32-v)/.64*ph
    s=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560" role="img" aria-labelledby="title desc"><title id="title">非洲指示变量只改变截距</title><desc id="desc">非洲国家为蓝色，其他国家为空心点；两条回归线平行，说明指示变量未改变斜率。</desc><style>.axis,.label,.ann{{font:17px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#30332e}}.label{{font-size:19px}}.plot{{fill:#fff;stroke:#4b4e49}}.grid{{stroke:#e5e5e1}}.na{{fill:#fff;stroke:#222;stroke-width:1.2}}.af{{fill:#6874ef}}.line{{stroke:#171917;stroke-width:3}}.blue{{stroke:#5968e7}}.band{{opacity:.14;fill:#20231f}}.band.blue{{fill:#5968e7;stroke:none}}</style><rect class="plot" x="{L}" y="{T}" width="{pw}" height="{ph}"/>''']
    for t in [0,.2,.4,.6,.8,1.0]:s.append(f'<text class="axis" x="{sx(t):.1f}" y="{H-45}" text-anchor="middle">{t:.1f}</text>')
    for t in [.7,.8,.9,1,1.1,1.2,1.3]:s.append(f'<line class="grid" x1="{L}" y1="{sy(t):.1f}" x2="{W-R}" y2="{sy(t):.1f}"/><text class="axis" x="{L-12}" y="{sy(t)+5:.1f}" text-anchor="end">{t:.1f}</text>')
    for r in rows:s.append(f'<circle class="{"af" if r["africa"] else "na"}" cx="{sx(r["x"]):.1f}" cy="{sy(r["y"]):.1f}" r="4"/>')
    for a,cl in [(a2,'line'),(a1,'line blue')]:
        y0=a+b*(0-.215);y1=a+b*(1.05-.215);s.append(f'<polygon class="band {"blue" if a==a1 else ""}" points="{sx(0):.1f},{sy(y0+.025):.1f} {sx(1.05):.1f},{sy(y1+.025):.1f} {sx(1.05):.1f},{sy(y1-.025):.1f} {sx(0):.1f},{sy(y0-.025):.1f}"/><line class="{cl}" x1="{sx(0):.1f}" y1="{sy(y0):.1f}" x2="{sx(1.05):.1f}" y2="{sy(y1):.1f}"/>')
    s+= [f'<text class="ann" x="{W-R-8}" y="{sy(a2+b*(.9-.215))-12:.1f}" text-anchor="end">非非洲</text>',f'<text class="ann" x="{W-R-8}" y="{sy(a1+b*(.9-.215))+24:.1f}" text-anchor="end" fill="#5968e7">非洲</text>',f'<text class="label" x="{L+pw/2}" y="{H-12}" text-anchor="middle">崎岖度（标准化）</text>',f'<text class="label" transform="translate(24,{T+ph/2}) rotate(-90)" text-anchor="middle">对数 GDP（占均值比例）</text></svg>']
    OUT.write_text(''.join(s),encoding='utf-8');print(OUT)
if __name__=='__main__':main()
