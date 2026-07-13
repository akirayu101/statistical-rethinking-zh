#!/usr/bin/env python3
"""Generate deterministic Chinese SVGs for Chapter 9 Figures 9.2 and 9.3."""
from pathlib import Path
import math
import random

ROOT = Path(__file__).resolve().parents[1]
OUT2 = ROOT / "translations/zh/media/chapter-09-metropolis-king.svg"
OUT3 = ROOT / "translations/zh/media/chapter-09-correlated-chains.svg"
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


def main() -> None:
    figure_9_2()
    figure_9_3()
    print(OUT2)
    print(OUT3)


if __name__ == "__main__":
    main()
