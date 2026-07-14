#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Chapter 9 Figures 9.2 through 9.12."""
from pathlib import Path
import math
import random

ROOT = Path(__file__).resolve().parents[1]
OUT2 = ROOT / "translations/zh/media/chapter-09-metropolis-king.svg"
OUT3 = ROOT / "translations/zh/media/chapter-09-correlated-chains.svg"
OUT4 = ROOT / "translations/zh/media/chapter-09-concentration.svg"
OUT5 = ROOT / "translations/zh/media/chapter-09-royal-drive.svg"
OUT6 = ROOT / "translations/zh/media/chapter-09-hmc-trajectories.svg"
OUT7 = ROOT / "translations/zh/media/chapter-09-pairs-posterior.svg"
OUT8 = ROOT / "translations/zh/media/chapter-09-traceplot.svg"
OUT9 = ROOT / "translations/zh/media/chapter-09-trankplot.svg"
OUT10 = ROOT / "translations/zh/media/chapter-09-chain-diagnostics.svg"
OUT11 = ROOT / "translations/zh/media/chapter-09-weak-prior.svg"
OUT12 = ROOT / "translations/zh/media/chapter-09-nonidentifiable-chains.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"
BLUE = "#6670ee"
INK = "#30332e"


def king_positions(seed: int = 9, weeks: int = 100_000) -> list[int]:
    rng = random.Random(seed)
    current = 10
    positions: list[int] = []
    for _ in range(weeks):
        positions.append(current)
        proposal = current + rng.choice((-1, 1))
        if proposal < 1:
            proposal = 10
        if proposal > 10:
            proposal = 1
        if rng.random() < proposal / current:
            current = proposal
    return positions


def figure_9_2() -> None:
    positions = king_positions()
    counts = [positions.count(i) for i in range(1, 11)]
    w, h = 1200, 560
    panels = [(90, 70, 465, 390), (690, 70, 420, 390)]
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>好国王马尔可夫的 Metropolis 模拟结果</title>',
        '<desc>左图显示前一百周所在岛屿，右图显示十万周中各岛访问次数与人口近似成比例。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]
    left, top, pw, ph = panels[0]
    sx = lambda x: left + x / 100 * pw
    sy = lambda y: top + (10.5 - y) / 10 * ph
    body.append(f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="{INK}"/>')
    for x in range(0, 101, 20):
        body += [f'<line x1="{sx(x):.1f}" y1="{top+ph}" x2="{sx(x):.1f}" y2="{top+ph+7}" stroke="{INK}"/>', f'<text x="{sx(x):.1f}" y="{top+ph+31}" text-anchor="middle" font-family="{FONT}" font-size="17">{x}</text>']
    for y in range(2, 11, 2):
        body += [f'<line x1="{left-7}" y1="{sy(y):.1f}" x2="{left}" y2="{sy(y):.1f}" stroke="{INK}"/>', f'<text x="{left-14}" y="{sy(y)+6:.1f}" text-anchor="end" font-family="{FONT}" font-size="17">{y}</text>']
    for week, island in enumerate(positions[:100], start=1):
        body.append(f'<circle cx="{sx(week):.1f}" cy="{sy(island):.1f}" r="3.7" fill="#fff" stroke="{BLUE}" stroke-width="1.7"/>')
    body += [f'<text x="{left+pw/2}" y="{h-30}" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">周</text>', f'<text x="28" y="{top+ph/2}" transform="rotate(-90 28 {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">岛屿</text>']

    left, top, pw, ph = panels[1]
    ymax = max(counts) * 1.05
    sx2 = lambda x: left + (x - .5) / 10 * pw
    sy2 = lambda y: top + (ymax - y) / ymax * ph
    body.append(f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="{INK}"/>')
    for x in range(2, 11, 2):
        body += [f'<line x1="{sx2(x):.1f}" y1="{top+ph}" x2="{sx2(x):.1f}" y2="{top+ph+7}" stroke="{INK}"/>', f'<text x="{sx2(x):.1f}" y="{top+ph+31}" text-anchor="middle" font-family="{FONT}" font-size="17">{x}</text>']
    for y in (0, 5000, 10000, 15000):
        body += [f'<line x1="{left-7}" y1="{sy2(y):.1f}" x2="{left}" y2="{sy2(y):.1f}" stroke="{INK}"/>', f'<text x="{left-14}" y="{sy2(y)+6:.1f}" text-anchor="end" font-family="{FONT}" font-size="17">{y}</text>']
    for island, count in enumerate(counts, start=1):
        body.append(f'<line x1="{sx2(island):.1f}" y1="{sy2(0):.1f}" x2="{sx2(island):.1f}" y2="{sy2(count):.1f}" stroke="{BLUE}" stroke-width="3"/>')
    body += [f'<text x="{left+pw/2}" y="{h-30}" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">岛屿</text>', f'<text x="{left-70}" y="{top+ph/2}" transform="rotate(-90 {left-70} {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">周数</text>', '</svg>', '']
    OUT2.write_text('\n'.join(body), encoding="utf-8")


def metropolis_points(step: float, seed: int) -> tuple[list[tuple[float, float, bool]], int]:
    rng = random.Random(seed)
    rho = -0.98
    inv = 1 / (1 - rho * rho)
    logp = lambda x, y: -0.5 * inv * (x * x - 2 * rho * x * y + y * y)
    x, y = -1.2, 0.8
    points: list[tuple[float, float, bool]] = []
    accepted = 0
    for _ in range(50):
        nx, ny = x + rng.gauss(0, step), y + rng.gauss(0, step)
        accept = math.log(rng.random()) < logp(nx, ny) - logp(x, y)
        points.append((nx, ny, accept))
        if accept:
            x, y = nx, ny
            accepted += 1
    return points, accepted


def figure_9_3() -> None:
    w, h = 1200, 620
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>高相关下的 Metropolis 链</title>',
        '<desc>两个面板分别显示步长零点一和零点二五时的五十次提议，实心点为接受，空心点为拒绝。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]
    for idx, step in enumerate((0.1, 0.25)):
        left, top, pw, ph = 90 + idx * 585, 85, 450, 450
        sx = lambda x: left + (x + 1.6) / 3.2 * pw
        sy = lambda y: top + (1.6 - y) / 3.2 * ph
        points, accepted = metropolis_points(step, 44_160 if step == 0.1 else 96_054)
        rate = accepted / 50
        body += [f'<defs><clipPath id="clip{idx}"><rect x="{left}" y="{top}" width="{pw}" height="{ph}"/></clipPath></defs>', f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="{INK}"/>']
        cx, cy = sx(0), sy(0)
        for radius in range(55, 600, 38):
            body.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{radius:.1f}" ry="{radius*0.1:.1f}" transform="rotate(45 {cx:.1f} {cy:.1f})" fill="none" stroke="#9b9c97" stroke-width="1" clip-path="url(#clip{idx})"/>')
        for tick in (-1.5, -1, -.5, 0, .5, 1, 1.5):
            body += [f'<line x1="{sx(tick):.1f}" y1="{top+ph}" x2="{sx(tick):.1f}" y2="{top+ph+7}" stroke="{INK}"/>', f'<text x="{sx(tick):.1f}" y="{top+ph+29}" text-anchor="middle" font-family="{FONT}" font-size="15">{tick:g}</text>', f'<line x1="{left-7}" y1="{sy(tick):.1f}" x2="{left}" y2="{sy(tick):.1f}" stroke="{INK}"/>', f'<text x="{left-14}" y="{sy(tick)+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="15">{tick:g}</text>']
        for x, y, accept in points:
            body.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="5" fill="{INK if accept else "#fff"}" stroke="{INK}" stroke-width="1.6" clip-path="url(#clip{idx})"/>')
        body += [f'<text x="{left+pw/2}" y="42" text-anchor="middle" font-family="{FONT}" font-size="22" fill="#263f86">步长 {step:g}，接受率 {rate:.2f}</text>', f'<text x="{left+pw/2}" y="{h-26}" text-anchor="middle" font-family="{FONT}" font-size="20" fill="#263f86">a₁</text>', f'<text x="{left-63}" y="{top+ph/2}" transform="rotate(-90 {left-63} {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="20" fill="#263f86">a₂</text>']
    body += ['</svg>', '']
    OUT3.write_text('\n'.join(body), encoding="utf-8")


def figure_9_4() -> None:
    """Plot radial-distance densities for standard Gaussian distributions."""
    w, h = 1200, 560
    left, right, top, bottom = 100, 40, 65, 90
    pw, ph = w - left - right, h - top - bottom
    xmax, ymax = 35.0, 0.84
    sx = lambda x: left + x / xmax * pw
    sy = lambda y: top + (ymax - y) / ymax * ph

    def chi_density(radius: float, dims: int) -> float:
        if radius <= 0:
            return math.sqrt(2 / math.pi) if dims == 1 else 0.0
        log_density = (1 - dims / 2) * math.log(2) + (dims - 1) * math.log(radius) - radius * radius / 2 - math.lgamma(dims / 2)
        return math.exp(log_density)

    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>测度集中与高维诅咒</title>',
        '<desc>一维、十维、一百维和一千维标准高斯分布中，样本到后验众数的径向距离密度随维度增加而远离零。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="{INK}"/>',
    ]
    for x in range(0, 36, 5):
        body += [f'<line x1="{sx(x):.1f}" y1="{top+ph}" x2="{sx(x):.1f}" y2="{top+ph+7}" stroke="{INK}"/>', f'<text x="{sx(x):.1f}" y="{top+ph+31}" text-anchor="middle" font-family="{FONT}" font-size="17">{x}</text>']
    for y in (0, .2, .4, .6, .8):
        body += [f'<line x1="{left-7}" y1="{sy(y):.1f}" x2="{left}" y2="{sy(y):.1f}" stroke="{INK}"/>', f'<text x="{left-14}" y="{sy(y)+6:.1f}" text-anchor="end" font-family="{FONT}" font-size="17">{y:.1f}</text>']
    colors = ("#263f86", "#6670ee", "#8f63a4", "#b06b63")
    for dims, color in zip((1, 10, 100, 1000), colors):
        points = []
        for i in range(701):
            radius = i * xmax / 700
            points.append((sx(radius), sy(chi_density(radius, dims))))
        body.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="3"/>')
        mode = math.sqrt(max(dims - 1, 0))
        label_x = max(mode, .8)
        label_y = min(chi_density(label_x, dims) + .1, .79)
        body.append(f'<text x="{sx(label_x):.1f}" y="{sy(label_y):.1f}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="{color}">{dims}</text>')
    body += [f'<text x="{left+pw/2}" y="{h-24}" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">到众数的径向距离</text>', f'<text x="30" y="{top+ph/2}" transform="rotate(-90 30 {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">概率密度</text>', '</svg>', '']
    OUT4.write_text('\n'.join(body), encoding="utf-8")


def figure_9_5() -> None:
    """Reconstruct King Monty's variable-momentum drive through a valley."""
    w, h = 1200, 560
    left, right, top, bottom = 100, 45, 55, 90
    pw, ph = w - left - right, h - top - bottom
    sx = lambda t: left + t / 380 * pw
    sy = lambda p: top + (1.65 - p) / 3.3 * ph
    visits = [(0,0),(20,-.9),(42,0),(62,-.55),(82,-1.25),(102,.35),(122,-.25),(142,.4),(162,.25),(182,-.6),(202,-.3),(222,-.35),(242,.75),(262,0),(282,-.2),(302,1.35),(322,-1.1),(342,-.2),(362,-.25),(380,.15)]
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">','<title>蒙蒂国王的王室驾车之旅</title>','<desc>车辆在南北向山谷中随动量上坡减速、下坡加速，并在一系列访问地点停下。</desc>','<rect width="100%" height="100%" fill="#fff"/>']
    for p in [x/5 for x in range(-8,9)]:
        body.append(f'<line x1="{left}" y1="{sy(p):.1f}" x2="{w-right}" y2="{sy(p):.1f}" stroke="#b8b9b5" stroke-width="1"/>')
    body.append(f'<line x1="{left}" y1="{sy(0):.1f}" x2="{w-right}" y2="{sy(0):.1f}" stroke="{INK}" stroke-width="1.6"/>')
    for i,((t1,p1),(t2,p2)) in enumerate(zip(visits,visits[1:])):
        mid=(t1+t2)/2
        amp = (-.35 if i%2==0 else .35) * (1 + (i%4)/5)
        cy = (p1+p2)/2 + amp
        d=f'M {sx(t1):.1f},{sy(p1):.1f} Q {sx(mid):.1f},{sy(cy):.1f} {sx(t2):.1f},{sy(p2):.1f}'
        width=2.5 + abs(cy-(p1+p2)/2)*6
        body.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{width:.1f}" stroke-linecap="round"/>')
    for t,p in visits[1:]:
        body.append(f'<circle cx="{sx(t):.1f}" cy="{sy(p):.1f}" r="5.5" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    for t in (0,100,200,300):
        body += [f'<line x1="{sx(t):.1f}" y1="{top+ph}" x2="{sx(t):.1f}" y2="{top+ph+7}" stroke="{INK}"/>',f'<text x="{sx(t):.1f}" y="{top+ph+31}" text-anchor="middle" font-family="{FONT}" font-size="17">{t}</text>']
    body += [f'<text x="{left+pw/2}" y="{h-24}" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">时间</text>',f'<text x="31" y="{top+ph/2}" transform="rotate(-90 31 {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">位置</text>',f'<text x="{left-12}" y="{sy(1.45):.1f}" text-anchor="end" font-family="{FONT}" font-size="18">北</text>',f'<text x="{left-12}" y="{sy(-1.45):.1f}" text-anchor="end" font-family="{FONT}" font-size="18">南</text>','</svg>','']
    OUT5.write_text('\n'.join(body),encoding='utf-8')


def hmc_trajectory(q, rng, step, leapfrog_steps, rho=0.0, scale=1.0):
    """Return one two-dimensional leapfrog path and its accepted endpoint."""
    def gradient(point):
        x, y = point
        factor = 1 / (scale * scale * (1 - rho * rho))
        return ((x - rho * y) * factor, (y - rho * x) * factor)

    def energy(point, momentum):
        x, y = point
        px, py = momentum
        potential = (x * x - 2 * rho * x * y + y * y) / (2 * scale * scale * (1 - rho * rho))
        return potential + (px * px + py * py) / 2

    start = q
    p = (rng.gauss(0, 1), rng.gauss(0, 1))
    start_p = p
    gx, gy = gradient(q)
    p = (p[0] - step * gx / 2, p[1] - step * gy / 2)
    path = [q]
    momenta = [p]
    for i in range(leapfrog_steps):
        q = (q[0] + step * p[0], q[1] + step * p[1])
        path.append(q)
        if i != leapfrog_steps - 1:
            gx, gy = gradient(q)
            p = (p[0] - step * gx, p[1] - step * gy)
        momenta.append(p)
    gx, gy = gradient(q)
    p = (p[0] - step * gx / 2, p[1] - step * gy / 2)
    accept_probability = min(1.0, math.exp(energy(start, start_p) - energy(q, p)))
    accepted = rng.random() < accept_probability
    return (q if accepted else start), path, momenta, accepted


def figure_9_6() -> None:
    """Show HMC trajectories, U-turns, and efficient exploration of correlation."""
    w, h = 1200, 1030
    panel_w, panel_h = 455, 380
    panels = [(95, 85), (670, 85), (95, 565), (670, 565)]
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>哈密顿蒙特卡洛的四组轨迹</title>',
        '<desc>上排比较合适与过长的蛙跳路径，下排显示 HMC 在高度相关后验中的单条轨迹和五十个样本。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]

    def draw_axes(index, title, limit, rho):
        nonlocal body
        left, top = panels[index]
        sx = lambda x: left + (x + limit) / (2 * limit) * panel_w
        sy = lambda y: top + (limit - y) / (2 * limit) * panel_h
        body.append(f'<defs><clipPath id="hmc-clip-{index}"><rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}"/></clipPath></defs>')
        body.append(f'<rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#fff" stroke="{INK}"/>')
        for level in (limit * .28, limit * .52, limit * .76, limit, limit * 1.24):
            points = []
            for i in range(121):
                angle = i * 2 * math.pi / 120
                if rho == 0:
                    x, y = level * math.cos(angle), level * math.sin(angle)
                else:
                    long = level * math.sqrt(1 - rho)
                    short = level * math.sqrt(1 + rho)
                    x = (long * math.cos(angle) + short * math.sin(angle)) / math.sqrt(2)
                    y = (-long * math.cos(angle) + short * math.sin(angle)) / math.sqrt(2)
                points.append(f'{sx(x):.1f},{sy(y):.1f}')
            body.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#a4a6a0" stroke-width="1" clip-path="url(#hmc-clip-{index})"/>')
        ticks = (-limit, -limit / 2, 0, limit / 2, limit)
        for tick in ticks:
            label = f'{tick:.1f}'
            body += [
                f'<line x1="{sx(tick):.1f}" y1="{top+panel_h}" x2="{sx(tick):.1f}" y2="{top+panel_h+6}" stroke="{INK}"/>',
                f'<text x="{sx(tick):.1f}" y="{top+panel_h+27}" text-anchor="middle" font-family="{FONT}" font-size="15">{label}</text>',
                f'<line x1="{left-6}" y1="{sy(tick):.1f}" x2="{left}" y2="{sy(tick):.1f}" stroke="{INK}"/>',
                f'<text x="{left-12}" y="{sy(tick)+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="15">{label}</text>',
            ]
        body += [
            f'<text x="{left+panel_w/2}" y="{top-28}" text-anchor="middle" font-family="{FONT}" font-size="22" fill="#263f86">{title}</text>',
            f'<text x="{left+panel_w/2}" y="{top+panel_h+55}" text-anchor="middle" font-family="{FONT}" font-size="20" fill="#263f86">{("μₓ" if index < 2 else "a₁")}</text>',
            f'<text x="{left-62}" y="{top+panel_h/2}" transform="rotate(-90 {left-62} {top+panel_h/2})" text-anchor="middle" font-family="{FONT}" font-size="20" fill="#263f86">{("μᵧ" if index < 2 else "a₂")}</text>',
        ]
        return sx, sy

    sx0, sy0 = draw_axes(0, '二维高斯，L = 11', .3, 0)
    rng = random.Random(46)
    q = (-.1, .2)
    body.append(f'<text x="{sx0(q[0]):.1f}" y="{sy0(q[1])+6:.1f}" text-anchor="middle" font-family="{FONT}" font-size="25">×</text>')
    for sample in range(1, 5):
        q, path, momenta, _ = hmc_trajectory(q, rng, .03, 11, scale=.135)
        body.append(f'<polyline points="{" ".join(f"{sx0(x):.1f},{sy0(y):.1f}" for x,y in path)}" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" opacity=".62" clip-path="url(#hmc-clip-0)"/>')
        for x, y in path[1:-1]:
            body.append(f'<circle cx="{sx0(x):.1f}" cy="{sy0(y):.1f}" r="2.7" fill="#fff" stroke="{INK}" clip-path="url(#hmc-clip-0)"/>')
        body += [f'<circle cx="{sx0(q[0]):.1f}" cy="{sy0(q[1]):.1f}" r="5.3" fill="{INK}"/>', f'<text x="{sx0(q[0])+11:.1f}" y="{sy0(q[1])-8:.1f}" font-family="{FONT}" font-size="17">{sample}</text>']

    sx1, sy1 = draw_axes(1, '二维高斯，L = 28', .3, 0)
    rng = random.Random(1)
    q = (-.1, .2)
    body.append(f'<text x="{sx1(q[0]):.1f}" y="{sy1(q[1])+6:.1f}" text-anchor="middle" font-family="{FONT}" font-size="25">×</text>')
    for _ in range(4):
        q, path, _, _ = hmc_trajectory(q, rng, .03, 28, scale=.135)
        body.append(f'<polyline points="{" ".join(f"{sx1(x):.1f},{sy1(y):.1f}" for x,y in path)}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" opacity=".48" clip-path="url(#hmc-clip-1)"/>')
        body.append(f'<circle cx="{sx1(q[0]):.1f}" cy="{sy1(q[1]):.1f}" r="5" fill="{INK}"/>')

    sx2, sy2 = draw_axes(2, '后验相关 −0.9', 1.5, -.9)
    rng = random.Random(113)
    q = (-.9, .8)
    body.append(f'<text x="{sx2(q[0]):.1f}" y="{sy2(q[1])+6:.1f}" text-anchor="middle" font-family="{FONT}" font-size="25">×</text>')
    for sample in range(1, 5):
        q, path, _, _ = hmc_trajectory(q, rng, .09, 12, rho=-.9, scale=.65)
        body.append(f'<polyline points="{" ".join(f"{sx2(x):.1f},{sy2(y):.1f}" for x,y in path)}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" opacity=".6" clip-path="url(#hmc-clip-2)"/>')
        body += [f'<circle cx="{sx2(q[0]):.1f}" cy="{sy2(q[1]):.1f}" r="5.3" fill="{INK}"/>', f'<text x="{sx2(q[0])+11:.1f}" y="{sy2(q[1])-8:.1f}" font-family="{FONT}" font-size="17">{sample}</text>']

    sx3, sy3 = draw_axes(3, '50 条轨迹', 1.5, -.9)
    rng = random.Random(251)
    q = (-.9, .8)
    body.append(f'<text x="{sx3(q[0]):.1f}" y="{sy3(q[1])+6:.1f}" text-anchor="middle" font-family="{FONT}" font-size="25">×</text>')
    samples = []
    for _ in range(50):
        q, _, _, accepted = hmc_trajectory(q, rng, .09, 12, rho=-.9, scale=.65)
        samples.append((q[0], q[1], accepted))
    for i, (x, y, accepted) in enumerate(samples):
        fill = '#fff' if i == 31 or not accepted else INK
        body.append(f'<circle cx="{sx3(x):.1f}" cy="{sy3(y):.1f}" r="5" fill="{fill}" stroke="{INK}" stroke-width="1.8" clip-path="url(#hmc-clip-3)"/>')
    body += ['</svg>', '']
    OUT6.write_text('\n'.join(body), encoding='utf-8')


def figure_9_7() -> None:
    """Reconstruct the five-parameter pairs plot from the ulam posterior."""
    w, h = 1200, 1080
    left, top, cell = 150, 75, 180
    labels = ("a₁", "a₂", "b₁", "b₂", "sigma")
    ranges = ((.84, .94), (1.02, 1.08), (-.1, .3), (-.3, -.05), (.10, .13))
    correlations = [
        [1, -.01, .17, -.02, .02],
        [-.01, 1, -.06, -.09, -.03],
        [.17, -.06, 1, .02, -.03],
        [-.02, -.09, .02, 1, .01],
        [.02, -.03, -.03, .01, 1],
    ]

    def cholesky(matrix):
        n = len(matrix)
        lower = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1):
                subtotal = sum(lower[i][k] * lower[j][k] for k in range(j))
                if i == j:
                    lower[i][j] = math.sqrt(max(matrix[i][i] - subtotal, 1e-9))
                else:
                    lower[i][j] = (matrix[i][j] - subtotal) / lower[j][j]
        return lower

    lower = cholesky(correlations)
    rng = random.Random(907)
    samples = []
    for _ in range(240):
        independent = [rng.gauss(0, 1) for _ in labels]
        samples.append([sum(lower[i][k] * independent[k] for k in range(i + 1)) for i in range(len(labels))])

    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>ulam 后验样本的变量对图</title>',
        '<desc>五个参数构成的变量对矩阵，对角线显示各参数的边际后验概率密度，上三角显示样本散点，下三角显示相关系数。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]
    for row in range(5):
        for col in range(5):
            x0, y0 = left + col * cell, top + row * cell
            body.append(f'<rect x="{x0}" y="{y0}" width="{cell}" height="{cell}" fill="#fff" stroke="#d9dad5"/>')
            if row == col:
                points = []
                for n in range(81):
                    z = -3 + n * 6 / 80
                    if row == 4:
                        density = math.exp(-((z - .28) ** 2) / 1.45) * (1 + .18 * z)
                    else:
                        density = math.exp(-z * z / 2)
                    px = x0 + 12 + n / 80 * (cell - 24)
                    py = y0 + cell - 18 - density * (cell - 55)
                    points.append(f'{px:.1f},{py:.1f}')
                body.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
                body.append(f'<text x="{x0+cell/2}" y="{y0+cell/2+7}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="700" fill="#263f86">{labels[row]}</text>')
            elif row < col:
                for sample in samples:
                    px = x0 + 9 + min(max((sample[col] + 3) / 6, 0), 1) * (cell - 18)
                    py = y0 + cell - 9 - min(max((sample[row] + 3) / 6, 0), 1) * (cell - 18)
                    body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.25" fill="{BLUE}" opacity=".24"/>')
            else:
                corr = correlations[row][col]
                size = 26 + abs(corr) * 35
                body.append(f'<text x="{x0+cell/2}" y="{y0+cell/2+10}" text-anchor="middle" font-family="{FONT}" font-size="{size:.1f}" font-weight="700" fill="{INK}">{corr:.2f}</text>')

    for index, (label, value_range) in enumerate(zip(labels, ranges)):
        x0 = left + index * cell
        y_bottom = top + 5 * cell
        body += [
            f'<text x="{x0+cell/2}" y="{y_bottom+45}" text-anchor="middle" font-family="{FONT}" font-size="22" fill="#263f86">{label}</text>',
            f'<text x="{x0+8}" y="{y_bottom+22}" text-anchor="start" font-family="{FONT}" font-size="14" fill="{INK}">{value_range[0]:.2f}</text>',
            f'<text x="{x0+cell-8}" y="{y_bottom+22}" text-anchor="end" font-family="{FONT}" font-size="14" fill="{INK}">{value_range[1]:.2f}</text>',
            f'<text x="{left-28}" y="{top+index*cell+cell/2+7}" text-anchor="end" font-family="{FONT}" font-size="22" fill="#263f86">{label}</text>',
        ]
    body += [
        f'<text x="{left+2.5*cell}" y="{h-22}" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#60635d">对角线：密度　上三角：后验样本　下三角：相关系数</text>',
        '</svg>',
        '',
    ]
    OUT7.write_text('\n'.join(body), encoding='utf-8')


def figure_9_8() -> None:
    """Draw a healthy five-parameter trace plot with a shaded warmup region."""
    w, h = 1200, 920
    panel_w, panel_h = 470, 190
    panels = ((85, 75), (645, 75), (85, 355), (645, 355), (85, 635))
    specs = (
        ("a[1]", 2671, .89, .014),
        ("a[2]", 3109, 1.05, .010),
        ("b[1]", 2153, .13, .070),
        ("b[2]", 2027, -.14, .050),
        ("sigma", 2885, .11, .006),
    )
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>地形崎岖度模型的健康链轨迹图</title>',
        '<desc>五个参数的第一条链轨迹，前五百次预热区域为灰色，后五百次推断样本区域为白色。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]
    rng = random.Random(920)
    for index, ((label, n_eff, mean, sd), (left, top)) in enumerate(zip(specs, panels)):
        values = []
        previous = 0.0
        for draw in range(1000):
            innovation = rng.gauss(0, 1)
            previous = -.12 * previous + .88 * innovation
            warmup_shift = (1 - draw / 500) * .22 if draw < 500 else 0
            values.append(mean + sd * (previous + warmup_shift))
        low, high = min(values), max(values)
        span = max(high - low, sd * 4)
        low, high = mean - span * .58, mean + span * .58
        sx = lambda draw: left + draw / 999 * panel_w
        sy = lambda value: top + (high - value) / (high - low) * panel_h
        body += [
            f'<rect x="{left}" y="{top}" width="{panel_w/2}" height="{panel_h}" fill="#e2e3e0"/>',
            f'<rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="none" stroke="{INK}"/>',
            f'<text x="{left}" y="{top-14}" font-family="{FONT}" font-size="22" fill="{INK}">{label}</text>',
            f'<text x="{left+panel_w}" y="{top-14}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{INK}">n_eff = {n_eff}</text>',
            f'<polyline points="{" ".join(f"{sx(i):.1f},{sy(v):.1f}" for i,v in enumerate(values))}" fill="none" stroke="{BLUE}" stroke-width="1.2" opacity=".82"/>',
        ]
        for draw in (200, 400, 600, 800, 1000):
            x = left + draw / 1000 * panel_w
            body += [f'<line x1="{x:.1f}" y1="{top+panel_h}" x2="{x:.1f}" y2="{top+panel_h+6}" stroke="{INK}"/>', f'<text x="{x:.1f}" y="{top+panel_h+27}" text-anchor="middle" font-family="{FONT}" font-size="14">{draw}</text>']
    body += [
        f'<rect x="{w-310}" y="{h-82}" width="24" height="18" fill="#e2e3e0" stroke="#b7b9b4"/>',
        f'<text x="{w-275}" y="{h-68}" font-family="{FONT}" font-size="17" fill="{INK}">预热（1–500）</text>',
        f'<rect x="{w-155}" y="{h-82}" width="24" height="18" fill="#fff" stroke="#b7b9b4"/>',
        f'<text x="{w-120}" y="{h-68}" font-family="{FONT}" font-size="17" fill="{INK}">推断</text>',
        '</svg>',
        '',
    ]
    OUT8.write_text('\n'.join(body), encoding='utf-8')


def figure_9_9() -> None:
    """Draw uniform overlapping rank histograms for four healthy chains."""
    w, h = 1200, 900
    panel_w, panel_h = 470, 190
    panels = ((85, 70), (645, 70), (85, 345), (645, 345), (85, 620))
    specs = (("a[1]", 2671), ("a[2]", 3109), ("b[1]", 2153), ("b[2]", 2027), ("sigma", 2885))
    colors = (INK, BLUE, "#8c8e89", "#c6c8c3")
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>健康链的秩直方图</title>',
        '<desc>五个参数各有四条链的重叠秩直方图，形状近似均匀，没有某条链持续高于或低于其他链。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]
    rng = random.Random(921)
    for (label, n_eff), (left, top) in zip(specs, panels):
        body += [
            f'<line x1="{left}" y1="{top+panel_h}" x2="{left+panel_w}" y2="{top+panel_h}" stroke="{INK}"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+panel_h}" stroke="{INK}"/>',
            f'<text x="{left}" y="{top-14}" font-family="{FONT}" font-size="22" fill="{INK}">{label}</text>',
            f'<text x="{left+panel_w}" y="{top-14}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{INK}">n_eff = {n_eff}</text>',
        ]
        for chain, color in enumerate(colors):
            heights = [max(8, 38 + rng.gauss(0, 7) + (chain - 1.5) * rng.uniform(-2, 2)) for _ in range(24)]
            max_height = 62
            points = []
            bin_width = panel_w / len(heights)
            for bin_index, height in enumerate(heights):
                x1 = left + bin_index * bin_width
                x2 = x1 + bin_width
                y = top + panel_h - height / max_height * (panel_h - 18)
                if bin_index == 0:
                    points.append((x1, top + panel_h))
                points.extend(((x1, y), (x2, y)))
            points.append((left + panel_w, top + panel_h))
            body.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="2" opacity="{.95 if chain < 2 else .8}"/>')
    body += [
        f'<text x="{w-280}" y="{h-45}" font-family="{FONT}" font-size="17" fill="{INK}">四条链的秩直方图重叠</text>',
        '</svg>',
        '',
    ]
    OUT9.write_text('\n'.join(body), encoding='utf-8')


def figure_9_10() -> None:
    """Contrast sick and healed trace/rank plots for three chains."""
    w, h = 1200, 1050
    panel_w = 470
    lefts = (85, 645)
    colors = (INK, BLUE, "#aeb0ab")
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>病态与恢复健康的马尔可夫链诊断图</title>',
        '<desc>上半部为平坦先验模型的病态轨迹图与秩图，下半部为加入弱信息先验后的健康结果。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]

    def draw_trace(left, top, label, n_eff, series, low, high, clip_id):
        panel_h = 175
        sx = lambda index: left + index / 999 * panel_w
        sy = lambda value: top + (high - value) / (high - low) * panel_h
        body.extend([
            f'<defs><clipPath id="{clip_id}"><rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}"/></clipPath></defs>',
            f'<rect x="{left}" y="{top}" width="{panel_w/2}" height="{panel_h}" fill="#e2e3e0"/>',
            f'<rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="none" stroke="{INK}"/>',
            f'<text x="{left}" y="{top-13}" font-family="{FONT}" font-size="22" fill="{INK}">{label}</text>',
            f'<text x="{left+panel_w}" y="{top-13}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{INK}">n_eff = {n_eff}</text>',
        ])
        for chain, values in enumerate(series):
            points = " ".join(f"{sx(i):.1f},{sy(value):.1f}" for i, value in enumerate(values))
            body.append(f'<polyline points="{points}" fill="none" stroke="{colors[chain]}" stroke-width="1.35" opacity=".9" clip-path="url(#{clip_id})"/>')
        for draw in (200, 400, 600, 800, 1000):
            x = left + draw / 1000 * panel_w
            body.extend([
                f'<line x1="{x:.1f}" y1="{top+panel_h}" x2="{x:.1f}" y2="{top+panel_h+6}" stroke="{INK}"/>',
                f'<text x="{x:.1f}" y="{top+panel_h+27}" text-anchor="middle" font-family="{FONT}" font-size="14">{draw}</text>',
            ])
        for value in (low, (low + high) / 2, high):
            y = sy(value)
            label_value = f'{value:g}'
            body.extend([
                f'<line x1="{left-6}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="{INK}"/>',
                f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="14">{label_value}</text>',
            ])

    def draw_rank(left, top, label, n_eff, sick, seed):
        panel_h = 155
        body.extend([
            f'<line x1="{left}" y1="{top+panel_h}" x2="{left+panel_w}" y2="{top+panel_h}" stroke="{INK}"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+panel_h}" stroke="{INK}"/>',
            f'<text x="{left}" y="{top-13}" font-family="{FONT}" font-size="22" fill="{INK}">{label}</text>',
            f'<text x="{left+panel_w}" y="{top-13}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{INK}">n_eff = {n_eff}</text>',
        ])
        rng = random.Random(seed)
        bins = 20
        for chain, color in enumerate(colors):
            if sick:
                heights = []
                for index in range(bins):
                    phase = index / (bins - 1)
                    if chain == 0:
                        baseline = 18 + 45 * phase
                    elif chain == 1:
                        baseline = 64 - 48 * phase
                    else:
                        baseline = 39 + 18 * math.sin(phase * 3 * math.pi)
                    heights.append(max(8, baseline + rng.gauss(0, 7)))
            else:
                heights = [max(12, 42 + rng.gauss(0, 8)) for _ in range(bins)]
            points = []
            bin_width = panel_w / bins
            for index, height in enumerate(heights):
                x1 = left + index * bin_width
                x2 = x1 + bin_width
                y = top + panel_h - min(height, 72) / 72 * (panel_h - 12)
                if index == 0:
                    points.append((x1, top + panel_h))
                points.extend(((x1, y), (x2, y)))
            points.append((left + panel_w, top + panel_h))
            body.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="2" opacity=".92"/>')

    def sick_alpha(seed):
        rng = random.Random(seed)
        value = rng.uniform(-300, 300)
        values = []
        for index in range(1000):
            value = .992 * value + rng.gauss(0, 65)
            if index in (170 + seed % 40, 540 + seed % 50, 875 - seed % 35):
                value += rng.choice((-1, 1)) * rng.uniform(1000, 1800)
            values.append(value)
        return values

    def sick_sigma(seed):
        rng = random.Random(seed)
        value = rng.uniform(300, 900)
        values = []
        for index in range(1000):
            value = abs(.975 * value + rng.gauss(0, 180))
            if index in (130 + seed % 60, 515 + seed % 45, 790 + seed % 55):
                value += rng.uniform(4500, 10500)
            values.append(value)
        return values

    def healthy_alpha(seed):
        rng = random.Random(seed)
        previous = 0.0
        values = []
        for _ in range(1000):
            previous = -.12 * previous + rng.gauss(0, 1.05)
            values.append(.1 + previous)
        return values

    def healthy_sigma(seed):
        rng = random.Random(seed)
        previous = 0.0
        values = []
        for _ in range(1000):
            previous = .08 * previous + rng.gauss(0, .48)
            values.append(max(.15, math.exp(.28 + previous)))
        return values

    draw_trace(lefts[0], 60, "alpha", 116, [sick_alpha(912 + i * 19) for i in range(3)], -2400, 2400, "sick-alpha")
    draw_trace(lefts[1], 60, "sigma", 179, [sick_sigma(948 + i * 23) for i in range(3)], 0, 12000, "sick-sigma")
    draw_rank(lefts[0], 320, "alpha", 116, True, 961)
    draw_rank(lefts[1], 320, "sigma", 179, True, 962)
    body.append(f'<line x1="45" y1="530" x2="1155" y2="530" stroke="#888b85" stroke-width="1.5"/>')
    draw_trace(lefts[0], 590, "alpha", 478, [healthy_alpha(970 + i * 17) for i in range(3)], -7, 4, "healthy-alpha")
    draw_trace(lefts[1], 590, "sigma", 438, [healthy_sigma(990 + i * 13) for i in range(3)], 0, 8, "healthy-sigma")
    draw_rank(lefts[0], 850, "alpha", 478, False, 1011)
    draw_rank(lefts[1], 850, "sigma", 438, False, 1012)
    body.extend(['</svg>', ''])
    OUT10.write_text('\n'.join(body), encoding='utf-8')


def figure_9_11() -> None:
    """Plot weak priors and posteriors for alpha and sigma."""
    w, h = 1200, 600
    panels = ((90, 65, 470, 410), (680, 65, 430, 410))
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>弱信息先验与后验</title>',
        '<desc>左图比较 alpha 的正态先验与后验，右图比较 sigma 的指数先验与后验。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]

    def normal_density(x, mean, sd):
        return math.exp(-.5 * ((x - mean) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))

    left, top, pw, ph = panels[0]
    sx = lambda x: left + (x + 16) / 32 * pw
    sy = lambda y: top + (.42 - y) / .42 * ph
    body.append(f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="{INK}"/>')
    for tick in (-15, -10, -5, 0, 5, 10, 15):
        body.extend([f'<line x1="{sx(tick):.1f}" y1="{top+ph}" x2="{sx(tick):.1f}" y2="{top+ph+7}" stroke="{INK}"/>', f'<text x="{sx(tick):.1f}" y="{top+ph+29}" text-anchor="middle" font-family="{FONT}" font-size="16">{tick}</text>'])
    for tick in (0, .1, .2, .3, .4):
        body.extend([f'<line x1="{left-7}" y1="{sy(tick):.1f}" x2="{left}" y2="{sy(tick):.1f}" stroke="{INK}"/>', f'<text x="{left-13}" y="{sy(tick)+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="16">{tick:.1f}</text>'])
    prior_points = [(sx(-16 + i * 32 / 320), sy(normal_density(-16 + i * 32 / 320, 1, 10))) for i in range(321)]
    posterior_points = [(sx(-16 + i * 32 / 320), sy(normal_density(-16 + i * 32 / 320, .1, 1.13))) for i in range(321)]
    body.extend([
        f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in prior_points)}" fill="none" stroke="{INK}" stroke-width="2.3" stroke-dasharray="9 8"/>',
        f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in posterior_points)}" fill="none" stroke="{BLUE}" stroke-width="3.4"/>',
        f'<text x="{sx(8):.1f}" y="{sy(.055):.1f}" font-family="{FONT}" font-size="19" fill="{INK}">先验</text>',
        f'<text x="{sx(2.5):.1f}" y="{sy(.23):.1f}" font-family="{FONT}" font-size="19" fill="{BLUE}">后验</text>',
        f'<text x="{left+pw/2}" y="{h-45}" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">alpha</text>',
        f'<text x="30" y="{top+ph/2}" transform="rotate(-90 30 {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">概率密度</text>',
    ])

    left, top, pw, ph = panels[1]
    sx = lambda x: left + x / 10.5 * pw
    sy = lambda y: top + (.82 - y) / .82 * ph
    body.extend([
        f'<defs><clipPath id="weak-prior-sigma"><rect x="{left}" y="{top}" width="{pw}" height="{ph}"/></clipPath></defs>',
        f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fff" stroke="{INK}"/>',
    ])
    for tick in (0, 2, 4, 6, 8, 10):
        body.extend([f'<line x1="{sx(tick):.1f}" y1="{top+ph}" x2="{sx(tick):.1f}" y2="{top+ph+7}" stroke="{INK}"/>', f'<text x="{sx(tick):.1f}" y="{top+ph+29}" text-anchor="middle" font-family="{FONT}" font-size="16">{tick}</text>'])
    for tick in (0, .2, .4, .6, .8):
        body.extend([f'<line x1="{left-7}" y1="{sy(tick):.1f}" x2="{left}" y2="{sy(tick):.1f}" stroke="{INK}"/>', f'<text x="{left-13}" y="{sy(tick)+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="16">{tick:.1f}</text>'])
    def gamma_density(x, shape=5.0, rate=3.0):
        if x <= 0:
            return 0.0
        return rate ** shape / math.gamma(shape) * x ** (shape - 1) * math.exp(-rate * x)
    prior_points = [(sx(i * 10.5 / 320), sy(math.exp(-(i * 10.5 / 320)))) for i in range(1, 321)]
    posterior_points = [(sx(i * 10.5 / 320), sy(gamma_density(i * 10.5 / 320))) for i in range(1, 321)]
    body.extend([
        f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in prior_points)}" fill="none" stroke="{INK}" stroke-width="2.3" stroke-dasharray="9 8" clip-path="url(#weak-prior-sigma)"/>',
        f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in posterior_points)}" fill="none" stroke="{BLUE}" stroke-width="3.4" clip-path="url(#weak-prior-sigma)"/>',
        f'<text x="{sx(3.2):.1f}" y="{sy(.13):.1f}" font-family="{FONT}" font-size="19" fill="{INK}">先验</text>',
        f'<text x="{sx(2.2):.1f}" y="{sy(.46):.1f}" font-family="{FONT}" font-size="19" fill="{BLUE}">后验</text>',
        f'<text x="{left+pw/2}" y="{h-45}" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">sigma</text>',
        f'<text x="{left-60}" y="{top+ph/2}" transform="rotate(-90 {left-60} {top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="21" fill="#263f86">概率密度</text>',
        '</svg>',
        '',
    ])
    OUT11.write_text('\n'.join(body), encoding='utf-8')


def figure_9_12() -> None:
    """Contrast non-identifiable chains before and after weak priors."""
    w, h = 1200, 1480
    panel_w, panel_h = 470, 165
    lefts = (85, 645)
    row_tops = (55, 280, 505, 800, 1025, 1250)
    colors = (INK, BLUE, "#afb1ac")
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<title>不可识别参数的病态链与弱信息先验修复</title>',
        '<desc>上半部显示不可识别参数 a1 和 a2 的游荡轨迹及非均匀秩图，下半部显示弱信息先验修复后的健康结果。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ]

    def draw_trace(left, top, label, n_eff, series, low, high, clip_id):
        sx = lambda index: left + index / 999 * panel_w
        sy = lambda value: top + (high - value) / (high - low) * panel_h
        body.extend([
            f'<defs><clipPath id="{clip_id}"><rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}"/></clipPath></defs>',
            f'<rect x="{left}" y="{top}" width="{panel_w/2}" height="{panel_h}" fill="#e2e3e0"/>',
            f'<rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="none" stroke="{INK}"/>',
            f'<text x="{left}" y="{top-12}" font-family="{FONT}" font-size="22" fill="{INK}">{label}</text>',
            f'<text x="{left+panel_w}" y="{top-12}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{INK}">n_eff = {n_eff}</text>',
        ])
        for chain, values in enumerate(series):
            points = " ".join(f"{sx(i):.1f},{sy(value):.1f}" for i, value in enumerate(values))
            body.append(f'<polyline points="{points}" fill="none" stroke="{colors[chain]}" stroke-width="1.25" opacity=".9" clip-path="url(#{clip_id})"/>')
        for draw in (200, 400, 600, 800, 1000):
            x = left + draw / 1000 * panel_w
            body.extend([
                f'<line x1="{x:.1f}" y1="{top+panel_h}" x2="{x:.1f}" y2="{top+panel_h+6}" stroke="{INK}"/>',
                f'<text x="{x:.1f}" y="{top+panel_h+26}" text-anchor="middle" font-family="{FONT}" font-size="14">{draw}</text>',
            ])
        for value in (low, (low + high) / 2, high):
            y = sy(value)
            body.extend([
                f'<line x1="{left-6}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="{INK}"/>',
                f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="14">{value:g}</text>',
            ])

    def draw_rank(left, top, label, n_eff, sick, seed):
        rng = random.Random(seed)
        body.extend([
            f'<line x1="{left}" y1="{top+panel_h}" x2="{left+panel_w}" y2="{top+panel_h}" stroke="{INK}"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+panel_h}" stroke="{INK}"/>',
            f'<text x="{left}" y="{top-12}" font-family="{FONT}" font-size="22" fill="{INK}">{label}</text>',
            f'<text x="{left+panel_w}" y="{top-12}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{INK}">n_eff = {n_eff}</text>',
        ])
        bins = 20
        for chain, color in enumerate(colors):
            heights = []
            for index in range(bins):
                phase = index / (bins - 1)
                if sick:
                    if chain == 0:
                        baseline = 16 + 52 * phase
                    elif chain == 1:
                        baseline = 65 - 49 * phase
                    else:
                        baseline = 25 + 35 * abs(math.sin(phase * 1.5 * math.pi))
                    height = baseline + rng.gauss(0, 8)
                else:
                    height = 42 + rng.gauss(0, 9)
                heights.append(max(8, height))
            points = []
            bin_width = panel_w / bins
            for index, height in enumerate(heights):
                x1 = left + index * bin_width
                x2 = x1 + bin_width
                y = top + panel_h - min(height, 76) / 76 * (panel_h - 12)
                if index == 0:
                    points.append((x1, top + panel_h))
                points.extend(((x1, y), (x2, y)))
            points.append((left + panel_w, top + panel_h))
            body.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="2" opacity=".92"/>')

    sick_a1, sick_a2, sick_sigma = [], [], []
    for chain in range(3):
        rng = random.Random(9120 + chain * 31)
        value = rng.uniform(-350, 250)
        chain_a1, chain_a2, chain_sigma = [], [], []
        sigma_prev = 0.0
        for index in range(1000):
            value = .998 * value + rng.gauss(0, 24)
            if index in (310 + chain * 40, 650 - chain * 35):
                value += rng.choice((-1, 1)) * rng.uniform(260, 520)
            chain_a1.append(value)
            chain_a2.append(-value + rng.gauss(0, 42))
            sigma_prev = .62 * sigma_prev + rng.gauss(0, .035)
            chain_sigma.append(1.05 + sigma_prev)
        sick_a1.append(chain_a1)
        sick_a2.append(chain_a2)
        sick_sigma.append(chain_sigma)

    def healthy_series(seed, mean, sd, positive=False):
        rng = random.Random(seed)
        previous = 0.0
        values = []
        for _ in range(1000):
            previous = -.1 * previous + rng.gauss(0, sd)
            value = mean + previous
            values.append(max(.78, value) if positive else value)
        return values

    healthy_a1 = [healthy_series(9220 + i * 17, .01, 7.2) for i in range(3)]
    healthy_a2 = [healthy_series(9260 + i * 19, .18, 7.2) for i in range(3)]
    healthy_sigma = [healthy_series(9300 + i * 23, 1.03, .075, True) for i in range(3)]

    draw_trace(lefts[0], row_tops[0], "a1", 2, sick_a1, -1200, 600, "nonid-sick-a1")
    draw_rank(lefts[1], row_tops[0], "a1", 2, True, 9341)
    draw_trace(lefts[0], row_tops[1], "a2", 2, sick_a2, -600, 1200, "nonid-sick-a2")
    draw_rank(lefts[1], row_tops[1], "a2", 2, True, 9342)
    draw_trace(lefts[0], row_tops[2], "sigma", 2, sick_sigma, .82, 1.28, "nonid-sick-sigma")
    draw_rank(lefts[1], row_tops[2], "sigma", 2, True, 9343)
    body.append(f'<line x1="45" y1="735" x2="1155" y2="735" stroke="#888b85" stroke-width="1.5"/>')
    draw_trace(lefts[0], row_tops[3], "a1", 389, healthy_a1, -25, 25, "nonid-healthy-a1")
    draw_rank(lefts[1], row_tops[3], "a1", 389, False, 9351)
    draw_trace(lefts[0], row_tops[4], "a2", 389, healthy_a2, -25, 25, "nonid-healthy-a2")
    draw_rank(lefts[1], row_tops[4], "a2", 389, False, 9352)
    draw_trace(lefts[0], row_tops[5], "sigma", 448, healthy_sigma, .8, 1.3, "nonid-healthy-sigma")
    draw_rank(lefts[1], row_tops[5], "sigma", 448, False, 9353)
    body.extend(['</svg>', ''])
    OUT12.write_text('\n'.join(body), encoding='utf-8')


def main() -> None:
    figure_9_2()
    figure_9_3()
    figure_9_4()
    figure_9_5()
    figure_9_6()
    figure_9_7()
    figure_9_8()
    figure_9_9()
    figure_9_10()
    figure_9_11()
    figure_9_12()
    print(OUT2)
    print(OUT3)
    print(OUT4)
    print(OUT5)
    print(OUT6)
    print(OUT7)
    print(OUT8)
    print(OUT9)
    print(OUT10)
    print(OUT11)
    print(OUT12)


if __name__ == "__main__":
    main()
