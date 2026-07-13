#!/usr/bin/env python3
"""Generate translated Figures 8.7 and 8.8 for the tulip interaction example."""
from pathlib import Path
import csv, io, math, random, urllib.request

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'work/chapter-08-278-280/tulips.csv'
URL='https://raw.githubusercontent.com/rmcelreath/rethinking/ac1b3b2cda83f3e14096e2d997a6e30ad109eeee/data/tulips.csv'
POST=ROOT/'translations/zh/media/chapter-08-tulips-posterior.svg'
PRIOR=ROOT/'translations/zh/media/chapter-08-tulips-prior.svg'

def load():
    text=LOCAL.read_text() if LOCAL.exists() else urllib.request.urlopen(URL).read().decode()
    raw=list(csv.DictReader(io.StringIO(text),delimiter=';'));mx=max(float(r['blooms']) for r in raw)
    return [{'w':float(r['water'])-2,'s':float(r['shade'])-2,'y':float(r['blooms'])/mx} for r in raw]

def inverse(a):
    n=len(a);m=[a[i][:]+[1. if i==j else 0. for j in range(n)] for i in range(n)]
    for k in range(n):
        p=max(range(k,n),key=lambda i:abs(m[i][k]));m[k],m[p]=m[p],m[k];z=m[k][k];m[k]=[v/z for v in m[k]]
        for i in range(n):
            if i!=k:
                z=m[i][k];m[i]=[m[i][j]-z*m[k][j] for j in range(2*n)]
    return [r[n:] for r in m]

def matvec(a,v): return [sum(x*y for x,y in zip(r,v)) for r in a]
def chol(a):
    n=len(a);L=[[0.]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            z=a[i][j]-sum(L[i][k]*L[j][k] for k in range(j))
            L[i][j]=math.sqrt(max(z,1e-12)) if i==j else z/L[j][j]
    return L

def fit(rows,interaction):
    X=[[1,r['w'],r['s']]+([r['w']*r['s']] if interaction else []) for r in rows];y=[r['y'] for r in rows];p=len(X[0])
    xtx=[[sum(x[i]*x[j] for x in X) for j in range(p)] for i in range(p)];inv=inverse(xtx);b=matvec(inv,[sum(x[i]*v for x,v in zip(X,y)) for i in range(p)])
    sig2=sum((v-sum(bb*xx for bb,xx in zip(b,x)))**2 for x,v in zip(X,y))/(len(y)-p);L=chol([[sig2*inv[i][j] for j in range(p)] for i in range(p)])
    rng=random.Random(807+interaction);draws=[]
    for _ in range(20):
        z=[rng.gauss(0,1) for _ in range(p)];draws.append([b[i]+sum(L[i][j]*z[j] for j in range(i+1)) for i in range(p)])
    return draws

def priors(interaction):
    rng=random.Random(7+interaction);p=4 if interaction else 3
    return [[rng.gauss(.5,.25)]+[rng.gauss(0,.25) for _ in range(p-1)] for _ in range(20)]

def pred(b,w,s): return b[0]+b[1]*w+b[2]*s+(b[3]*w*s if len(b)>3 else 0)

def make(rows,top,bottom,out,prior=False):
    W,H=1400,780;pad=28;pw=430;ph=300;gap=28;left=65;top0=58
    ymin,ymax=(-.5,1.5) if prior else (0,1)
    sx=lambda c,x:left+c*(pw+gap)+(x+1)/2*pw
    sy=lambda r,y:top0+r*(ph+85)+(ymax-y)/(ymax-ymin)*ph
    s=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="780" viewBox="0 0 1400 780" role="img" aria-labelledby="title desc"><title id="title">郁金香花朵的{"先验" if prior else "后验"}预测三联图</title><desc id="desc">上排无交互作用，下排有水量与遮阴交互作用；三列分别固定遮阴为负一、零和一。</desc><style>.title,.axis{{font:15px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;fill:#30332e}}.title{{font-weight:700;font-size:16px}}.plot{{fill:#fff;stroke:#555}}.grid{{stroke:#e7e7e3}}.point{{fill:#6874ef}}.line{{stroke:#20231f;stroke-width:1.3;opacity:.22}}.bold{{stroke:#171917;stroke-width:3;opacity:.9}}.label{{font:17px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}</style>''']
    for r,draws in enumerate([top,bottom]):
        for c,shade in enumerate([-1,0,1]):
            x0=left+c*(pw+gap);y0=top0+r*(ph+85);model='m8.4' if r==0 else 'm8.5';kind='先验' if prior else '后验'
            s += [f'<text class="title" x="{x0+pw/2}" y="{y0-17}" text-anchor="middle">{model} {kind}：遮阴 = {shade}</text>',f'<rect class="plot" x="{x0}" y="{y0}" width="{pw}" height="{ph}"/>']
            for y in ([0,.5,1] if not prior else [-.5,0,.5,1,1.5]):s.append(f'<line class="grid" x1="{x0}" y1="{sy(r,y):.1f}" x2="{x0+pw}" y2="{sy(r,y):.1f}"/>')
            if not prior:
                for row in rows:
                    if row['s']==shade:s.append(f'<circle class="point" cx="{sx(c,row["w"]):.1f}" cy="{sy(r,row["y"]):.1f}" r="4"/>')
            for i,b in enumerate(draws):
                cls='bold' if prior and i==0 else 'line';s.append(f'<polyline class="{cls}" points="'+' '.join(f'{sx(c,w):.1f},{sy(r,pred(b,w,shade)):.1f}' for w in [-1,0,1])+'"/>')
            for x in [-1,0,1]:s.append(f'<text class="axis" x="{sx(c,x):.1f}" y="{y0+ph+23}" text-anchor="middle">{x}</text>')
            s += [f'<text class="label" x="{x0+pw/2}" y="{y0+ph+50}" text-anchor="middle">水量</text>',f'<text class="label" transform="translate({x0-35},{y0+ph/2}) rotate(-90)" text-anchor="middle">花朵</text>']
    s.append('</svg>');out.write_text(''.join(s),encoding='utf-8');print(out)

def main():
    rows=load();make(rows,fit(rows,False),fit(rows,True),POST);make(rows,priors(False),priors(True),PRIOR,True)
if __name__=='__main__':main()
