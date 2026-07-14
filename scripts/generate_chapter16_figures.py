#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import math
import random
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-16-cylinder-posterior-fit.svg"
BOXES_OUT = ROOT / "translations" / "zh" / "media" / "chapter-16-boxes-strategy-posterior.svg"
NUT_PRIOR_OUT = ROOT / "translations" / "zh" / "media" / "chapter-16-nut-prior-predictive.svg"
NUT_POSTERIOR_OUT = ROOT / "translations" / "zh" / "media" / "chapter-16-nut-posterior-curves.svg"
LYNX_HARE_OUT = ROOT / "translations" / "zh" / "media" / "chapter-16-lynx-hare-series.svg"
DATA_URL = "https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Howell1.csv"
BOXES_DATA_URL = "https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Boxes.csv"
PANDA_DATA_URL = "https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Panda_nuts.csv"
LYNX_HARE_DATA_URL = "https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Lynx_Hare.csv"
FONT = '-apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif'


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def path(points: list[tuple[float, float]]) -> str:
    return " ".join(("M" if i == 0 else "L") + f"{fmt(x)},{fmt(y)}" for i, (x, y) in enumerate(points))


def load_data() -> list[tuple[float, float]]:
    raw = urllib.request.urlopen(DATA_URL, timeout=30).read().decode("utf-8")
    rows = csv.DictReader(io.StringIO(raw), delimiter=";")
    return [(float(row["height"]), float(row["weight"])) for row in rows]


def sample_posterior(theta_hat: float, sigma: float, n: int) -> list[tuple[float, float]]:
    grid = [0.105 + i * (0.45 - 0.105) / 1500 for i in range(1501)]
    log_density = [
        -math.log(p) + 17 * math.log1p(-p) - 0.5 * theta_hat / (p * p)
        for p in grid
    ]
    peak = max(log_density)
    weights = [math.exp(value - peak) for value in log_density]
    cumulative: list[float] = []
    total = 0.0
    for weight in weights:
        total += weight
        cumulative.append(total)

    rng = random.Random(1616)
    theta_sd = sigma / math.sqrt(544)
    samples: list[tuple[float, float]] = []
    for _ in range(n):
        target = rng.random() * total
        lo, hi = 0, len(cumulative) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cumulative[mid] < target:
                lo = mid + 1
            else:
                hi = mid
        p = grid[lo]
        theta = theta_hat * math.exp(rng.gauss(0, theta_sd))
        samples.append((p, theta / (p * p)))
    return samples


def density_curve(values: list[float], xmin: float, xmax: float, steps: int = 120) -> list[tuple[float, float]]:
    bandwidth = (xmax - xmin) / 35
    curve: list[tuple[float, float]] = []
    for i in range(steps + 1):
        x = xmin + (xmax - xmin) * i / steps
        y = sum(math.exp(-0.5 * ((x - value) / bandwidth) ** 2) for value in values)
        curve.append((x, y))
    return curve


def load_boxes() -> dict[tuple[int, int], int]:
    raw = urllib.request.urlopen(BOXES_DATA_URL, timeout=30).read().decode("utf-8")
    rows = csv.DictReader(io.StringIO(raw), delimiter=";")
    counts = {(choice, order): 0 for choice in (1, 2, 3) for order in (0, 1)}
    for row in rows:
        counts[(int(row["y"]), int(row["majority_first"]))] += 1
    return counts


def boxes_posterior(counts: dict[tuple[int, int], int]) -> list[list[float]]:
    def simplex(z: list[float]) -> list[float]:
        logits = z + [0.0]
        peak = max(logits)
        weights = [math.exp(value - peak) for value in logits]
        total = sum(weights)
        return [value / total for value in weights]

    def log_target(z: list[float]) -> float:
        majority, minority, maverick, random_choice, follow_first = simplex(z)
        probabilities = {
            (1, 0): maverick + random_choice / 3,
            (1, 1): maverick + random_choice / 3,
            (2, 0): majority + random_choice / 3,
            (2, 1): majority + random_choice / 3 + follow_first,
            (3, 0): minority + random_choice / 3 + follow_first,
            (3, 1): minority + random_choice / 3,
        }
        likelihood = sum(count * math.log(probabilities[key]) for key, count in counts.items())
        # Dirichlet([4,4,4,4,4]) plus the additive-log-ratio Jacobian.
        return likelihood + 4 * sum(math.log(value) for value in simplex(z))

    start = [0.259, 0.139, 0.148, 0.194, 0.259]
    z = [math.log(start[index] / start[4]) for index in range(4)]
    rng = random.Random(1602)
    current = log_target(z)
    draws: list[list[float]] = []
    for iteration in range(250_000):
        proposal = [value + rng.gauss(0, 0.16) for value in z]
        proposed = log_target(proposal)
        if math.log(rng.random()) < proposed - current:
            z, current = proposal, proposed
        if iteration >= 50_000 and iteration % 20 == 0:
            draws.append(simplex(z))
    return draws


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(probability * len(ordered)))]


def write_boxes_figure() -> None:
    draws = boxes_posterior(load_boxes())
    labels = ["1 跟随多数", "2 跟随少数", "3 特立独行", "4 随机", "5 跟随第一"]
    summaries = []
    for index in range(5):
        values = [draw[index] for draw in draws]
        summaries.append((sum(values) / len(values), quantile(values, 0.055), quantile(values, 0.945)))

    width, height = 900, 430
    left, right, top, bottom = 245, 835, 55, 340
    xmin, xmax = 0.075, 0.34

    def x(value: float) -> float:
        return left + (right - left) * (value - xmin) / (xmax - xmin)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">五种儿童选择策略的边际后验</title>',
        '<desc id="desc">五条水平线表示五种策略概率的百分之八十九相容区间，空心圆表示后验均值；跟随多数和跟随第一约各占四分之一。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<style>.axis{{font:16px {FONT};fill:#30332e}}.label{{font:19px {FONT};fill:#30332e}}.title{{font:700 22px {FONT};fill:#263f86}}.grid{{stroke:#c8c9c8;stroke-width:1;stroke-dasharray:3 5}}.interval{{stroke:#242824;stroke-width:4;stroke-linecap:round}}.mean{{fill:#fff;stroke:#242824;stroke-width:2.2}}</style>',
        '<text class="title" x="450" y="30" text-anchor="middle">隐藏策略概率的后验分布</text>',
    ]
    row_gap = (bottom - top) / 4
    for index, (label, summary) in enumerate(zip(labels, summaries)):
        y = top + index * row_gap
        mean, low, high = summary
        parts.append(f'<line class="grid" x1="{left}" y1="{fmt(y)}" x2="{right}" y2="{fmt(y)}"/>')
        parts.append(f'<text class="label" x="{left - 18}" y="{fmt(y + 6)}" text-anchor="end">{label}</text>')
        parts.append(f'<line class="interval" x1="{fmt(x(low))}" y1="{fmt(y)}" x2="{fmt(x(high))}" y2="{fmt(y)}"/>')
        parts.append(f'<circle class="mean" cx="{fmt(x(mean))}" cy="{fmt(y)}" r="6"/>')
    parts.append(f'<line x1="{left}" y1="{bottom + 30}" x2="{right}" y2="{bottom + 30}" stroke="#343732" stroke-width="2"/>')
    for value in (0.10, 0.15, 0.20, 0.25, 0.30):
        xpos = x(value)
        parts.append(f'<line x1="{fmt(xpos)}" y1="{bottom + 30}" x2="{fmt(xpos)}" y2="{bottom + 37}" stroke="#343732"/>')
        parts.append(f'<text class="axis" x="{fmt(xpos)}" y="{bottom + 58}" text-anchor="middle">{value:.2f}</text>')
    parts.append(f'<text class="label" x="{(left + right) / 2}" y="{height - 8}" text-anchor="middle">策略概率</text>')
    parts.append('</svg>')
    BOXES_OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {BOXES_OUT}")


def load_panda_nuts() -> list[tuple[float, int, float]]:
    raw = urllib.request.urlopen(PANDA_DATA_URL, timeout=30).read().decode("utf-8")
    rows = csv.DictReader(io.StringIO(raw), delimiter=";")
    return [(float(row["age"]), int(row["nuts_opened"]), float(row["seconds"])) for row in rows]


def load_lynx_hare() -> list[tuple[int, float, float]]:
    raw = urllib.request.urlopen(LYNX_HARE_DATA_URL, timeout=30).read().decode("utf-8")
    rows = csv.DictReader(io.StringIO(raw), delimiter=";")
    return [(int(row["Year"]), float(row["Lynx"]), float(row["Hare"])) for row in rows]


def panda_posterior(data: list[tuple[float, int, float]]) -> list[tuple[float, float, float]]:
    max_age = max(age for age, _, _ in data)
    normalized = [(age / max_age, opened, seconds) for age, opened, seconds in data]
    prior_means = [0.0, math.log(2), math.log(5)]
    prior_sds = [0.1, 0.25, 0.25]

    def log_target(z: list[float]) -> float:
        phi, k, theta = [math.exp(value) for value in z]
        value = -0.5 * sum(((z[index] - prior_means[index]) / prior_sds[index]) ** 2 for index in range(3))
        for age, opened, seconds in normalized:
            expected = seconds * phi * (1 - math.exp(-k * age)) ** theta
            value += opened * math.log(expected) - expected - math.lgamma(opened + 1)
        return value

    rng = random.Random(1612)
    z = [math.log(0.9), math.log(2), math.log(5)]
    current = log_target(z)
    steps = [0.025, 0.055, 0.06]
    draws: list[tuple[float, float, float]] = []
    for iteration in range(240_000):
        proposal = [z[index] + rng.gauss(0, steps[index]) for index in range(3)]
        proposed = log_target(proposal)
        if math.log(rng.random()) < proposed - current:
            z, current = proposal, proposed
        if iteration >= 40_000 and iteration % 40 == 0:
            draws.append(tuple(math.exp(value) for value in z))
    return draws


def write_nut_prior_figure() -> None:
    rng = random.Random(1610)
    samples = [
        (math.exp(rng.gauss(0, 0.1)), math.exp(rng.gauss(math.log(2), 0.25)), math.exp(rng.gauss(math.log(5), 0.25)))
        for _ in range(20)
    ]
    width, height = 1200, 620
    top, panel_h, panel_w = 70, 410, 455
    left_x, right_x = 85, 665

    def px(origin: float, age: float) -> float:
        return origin + panel_w * age / 24

    def py(maximum: float, value: float) -> float:
        return top + panel_h - panel_h * value / maximum

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">开坚果模型的先验预测模拟</title>',
        '<desc id="desc">左图为二十条相对体重生长先验曲线，右图为对应的开坚果速率先验曲线；曲线均随年龄增长并在成年前后逐渐趋平。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<style>.axis{{font:15px {FONT};fill:#30332e}}.label{{font:19px {FONT};fill:#30332e}}.title{{font:700 22px {FONT};fill:#263f86}}.panel{{fill:#fff;stroke:#3c403b;stroke-width:1.4}}.curve{{fill:none;stroke:#222722;stroke-width:2;opacity:.56}}</style>',
        '<text class="title" x="312" y="34" text-anchor="middle">相对体重的先验生长曲线</text>',
        '<text class="title" x="892" y="34" text-anchor="middle">开坚果速率的先验曲线</text>',
        f'<rect class="panel" x="{left_x}" y="{top}" width="{panel_w}" height="{panel_h}"/>',
        f'<rect class="panel" x="{right_x}" y="{top}" width="{panel_w}" height="{panel_h}"/>',
    ]
    ages = [24 * index / 120 for index in range(121)]
    for phi, k, theta in samples:
        growth = [(px(left_x, age), py(1.0, 1 - math.exp(-k * age / 16))) for age in ages]
        rate = [(px(right_x, age), py(1.2, phi * (1 - math.exp(-k * age / 16)) ** theta)) for age in ages]
        parts.append(f'<path class="curve" d="{path(growth)}"/>')
        parts.append(f'<path class="curve" d="{path(rate)}"/>')
    for origin in (left_x, right_x):
        for tick in range(0, 25, 4):
            xpos = px(origin, tick)
            parts.append(f'<line x1="{fmt(xpos)}" y1="{top + panel_h}" x2="{fmt(xpos)}" y2="{top + panel_h + 6}" stroke="#3c403b"/>')
            parts.append(f'<text class="axis" x="{fmt(xpos)}" y="{top + panel_h + 27}" text-anchor="middle">{tick}</text>')
        parts.append(f'<text class="label" x="{origin + panel_w / 2}" y="{height - 47}" text-anchor="middle">年龄</text>')
    for tick in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        ypos = py(1.0, tick)
        parts.append(f'<text class="axis" x="{left_x - 12}" y="{fmt(ypos + 5)}" text-anchor="end">{tick:.1f}</text>')
    for tick in (0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2):
        ypos = py(1.2, tick)
        parts.append(f'<text class="axis" x="{right_x - 12}" y="{fmt(ypos + 5)}" text-anchor="end">{tick:.1f}</text>')
    parts.append(f'<text class="label" x="28" y="{top + panel_h / 2}" text-anchor="middle" transform="rotate(-90 28 {top + panel_h / 2})">相对体重</text>')
    parts.append(f'<text class="label" x="608" y="{top + panel_h / 2}" text-anchor="middle" transform="rotate(-90 608 {top + panel_h / 2})">每秒坚果数</text>')
    parts.append('</svg>')
    NUT_PRIOR_OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {NUT_PRIOR_OUT}")


def write_nut_posterior_figure(data: list[tuple[float, int, float]]) -> None:
    draws = panda_posterior(data)
    selected = [draws[index * len(draws) // 30] for index in range(30)]
    width, height = 900, 600
    left, top, panel_w, panel_h = 100, 65, 735, 430

    def px(age: float) -> float:
        return left + panel_w * age / 16

    def py(value: float) -> float:
        return top + panel_h - panel_h * value / 1.5

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">黑猩猩开坚果技能的后验发展曲线</title>',
        '<desc id="desc">蓝色圆点为每次活动每秒打开的坚果数，圆点大小随活动持续时间变化；三十条黑色曲线来自后验分布。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<style>.axis{{font:16px {FONT};fill:#30332e}}.label{{font:20px {FONT};fill:#30332e}}.title{{font:700 23px {FONT};fill:#263f86}}.panel{{fill:#fff;stroke:#3c403b;stroke-width:1.4}}.curve{{fill:none;stroke:#202420;stroke-width:2;opacity:.5}}.point{{fill:none;stroke:#6874ef;stroke-width:2.4;opacity:.88}}</style>',
        '<text class="title" x="450" y="32" text-anchor="middle">开坚果技能的后验发展曲线</text>',
        f'<rect class="panel" x="{left}" y="{top}" width="{panel_w}" height="{panel_h}"/>',
    ]
    ages = [16 * index / 120 for index in range(121)]
    for phi, k, theta in selected:
        curve = [(px(age), py(phi * (1 - math.exp(-k * age / 16)) ** theta)) for age in ages]
        parts.append(f'<path class="curve" d="{path(curve)}"/>')
    seconds = [duration for _, _, duration in data]
    low_seconds, high_seconds = min(seconds), max(seconds)
    jitter = random.Random(1615)
    for age, opened, duration in data:
        rate = opened / duration
        radius = 3 + 8 * (duration - low_seconds) / (high_seconds - low_seconds)
        parts.append(f'<circle class="point" cx="{fmt(px(age + jitter.uniform(-0.12, 0.12)))}" cy="{fmt(py(rate))}" r="{fmt(radius)}"/>')
    for tick in (0, 4, 8, 12, 16):
        xpos = px(tick)
        parts.append(f'<text class="axis" x="{fmt(xpos)}" y="{top + panel_h + 28}" text-anchor="middle">{tick}</text>')
    for tick in (0, 0.5, 1.0, 1.5):
        ypos = py(tick)
        parts.append(f'<text class="axis" x="{left - 12}" y="{fmt(ypos + 5)}" text-anchor="end">{tick:.1f}</text>')
    parts.append(f'<text class="label" x="{left + panel_w / 2}" y="{height - 42}" text-anchor="middle">年龄</text>')
    parts.append(f'<text class="label" x="35" y="{top + panel_h / 2}" text-anchor="middle" transform="rotate(-90 35 {top + panel_h / 2})">每秒坚果数</text>')
    parts.append('</svg>')
    NUT_POSTERIOR_OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {NUT_POSTERIOR_OUT}")


def write_lynx_hare_figure(data: list[tuple[int, float, float]]) -> None:
    width, height = 1100, 600
    left, top, panel_w, panel_h = 100, 60, 930, 430

    def px(year: int) -> float:
        return left + panel_w * (year - 1900) / 20

    def py(value: float) -> float:
        return top + panel_h - panel_h * value / 90

    hare = [(px(year), py(value)) for year, _, value in data]
    lynx = [(px(year), py(value)) for year, value, _ in data]
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Hudson Bay Company 记录的猞猁与雪兔毛皮数量</title>',
        '<desc id="desc">一九零零至一九二零年，黑色雪兔和蓝色猞猁毛皮数量都周期波动，猞猁的峰值通常晚于雪兔。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<style>.axis{{font:16px {FONT};fill:#30332e}}.label{{font:20px {FONT};fill:#30332e}}.title{{font:700 23px {FONT};fill:#263f86}}.panel{{fill:#fff;stroke:#3c403b;stroke-width:1.4}}.hare{{fill:none;stroke:#202420;stroke-width:3}}.lynx{{fill:none;stroke:#6874ef;stroke-width:3}}.hare-point{{fill:#202420;stroke:#fff;stroke-width:1.5}}.lynx-point{{fill:#6874ef;stroke:#fff;stroke-width:1.5}}</style>',
        '<text class="title" x="550" y="31" text-anchor="middle">雪兔与猞猁毛皮数量，1900–1920</text>',
        f'<rect class="panel" x="{left}" y="{top}" width="{panel_w}" height="{panel_h}"/>',
        f'<path class="hare" d="{path(hare)}"/>',
        f'<path class="lynx" d="{path(lynx)}"/>',
    ]
    for point in hare:
        parts.append(f'<circle class="hare-point" cx="{fmt(point[0])}" cy="{fmt(point[1])}" r="6"/>')
    for point in lynx:
        parts.append(f'<circle class="lynx-point" cx="{fmt(point[0])}" cy="{fmt(point[1])}" r="6"/>')
    for tick in (1900, 1910, 1920):
        xpos = px(tick)
        parts.append(f'<text class="axis" x="{fmt(xpos)}" y="{top + panel_h + 28}" text-anchor="middle">{tick}</text>')
    for tick in (0, 20, 40, 60, 80):
        ypos = py(tick)
        parts.append(f'<text class="axis" x="{left - 12}" y="{fmt(ypos + 5)}" text-anchor="end">{tick}</text>')
    parts.append(f'<text class="label" x="{left + panel_w / 2}" y="{height - 42}" text-anchor="middle">年份</text>')
    parts.append(f'<text class="label" x="34" y="{top + panel_h / 2}" text-anchor="middle" transform="rotate(-90 34 {top + panel_h / 2})">毛皮数量（千张）</text>')
    parts.append(f'<text class="label" x="{fmt(px(1914))}" y="{fmt(py(78))}" fill="#202420">雪兔</text>')
    parts.append(f'<text class="label" x="{fmt(px(1916))}" y="{fmt(py(48))}" fill="#6874ef">猞猁</text>')
    parts.append('</svg>')
    LYNX_HARE_OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {LYNX_HARE_OUT}")


def main() -> int:
    raw = load_data()
    mean_h = sum(height for height, _ in raw) / len(raw)
    mean_w = sum(weight for _, weight in raw) / len(raw)
    data = [(height / mean_h, weight / mean_w) for height, weight in raw]
    residuals = [math.log(w) - math.log(math.pi) - 3 * math.log(h) for h, w in data]
    log_theta = sum(residuals) / len(residuals)
    theta_hat = math.exp(log_theta)
    sigma = math.sqrt(sum((value - log_theta) ** 2 for value in residuals) / len(residuals))
    samples = sample_posterior(theta_hat, sigma, 1000)
    p_values = [p for p, _ in samples]
    k_values = [k for _, k in samples]

    width, height = 1200, 620
    panel = 185
    left_x, top_y = 80, 65
    gap = 25
    right_x, right_y, right_w, right_h = 665, 70, 455, 410
    pmin, pmax = 0.1, 0.5
    kmin, kmax = 3.0, 18.0

    def px_p(value: float) -> float:
        return left_x + panel * (value - pmin) / (pmax - pmin)

    def py_p(value: float) -> float:
        return top_y + panel - panel * (value - pmin) / (pmax - pmin)

    joint_x = left_x + panel + gap
    joint_y = top_y

    def px_k(value: float) -> float:
        return joint_x + panel * (value - kmin) / (kmax - kmin)

    bottom_y = top_y + panel + gap
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">圆柱人体模型的参数后验与身高体重拟合</title>',
        '<desc id="desc">左侧显示 p 与 k 的边际后验、负相关弯曲脊和负零点八九相关；右侧显示缩放后身高体重数据、圆柱模型均值曲线与预测区间。</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<style>.axis{{font:14px {FONT};fill:#30332e}}.label{{font:18px {FONT};fill:#30332e}}.title{{font:700 21px {FONT};fill:#263f86}}.panel{{fill:#fff;stroke:#3c403b;stroke-width:1.4}}.density{{fill:none;stroke:#1d211d;stroke-width:2.2}}.ridge{{fill:#5ca7db;opacity:.44}}.point{{fill:none;stroke:#6874ef;stroke-width:1.2;opacity:.45}}.band{{fill:#cfd2d1;opacity:.9}}.fit{{fill:none;stroke:#1d211d;stroke-width:3}}</style>',
        f'<text class="title" x="275" y="34" text-anchor="middle">参数 <tspan font-style="italic">p</tspan> 与 <tspan font-style="italic">k</tspan> 的联合后验</text>',
        f'<text class="title" x="{right_x + right_w / 2}" y="34" text-anchor="middle">圆柱模型的后验预测</text>',
    ]

    for x, y in ((left_x, top_y), (joint_x, joint_y), (left_x, bottom_y), (joint_x, bottom_y)):
        parts.append(f'<rect class="panel" x="{x}" y="{y}" width="{panel}" height="{panel}"/>')

    p_density = density_curve(p_values, pmin, pmax)
    max_pd = max(y for _, y in p_density)
    p_points = [(px_p(x), top_y + panel - (panel - 18) * y / max_pd) for x, y in p_density]
    parts.append(f'<path class="density" d="{path(p_points)}"/>')
    parts.append(f'<text class="label" x="{left_x + panel / 2}" y="{top_y + 35}" text-anchor="middle" font-style="italic">p</text>')

    for p, k in samples[::2]:
        if kmin <= k <= kmax:
            parts.append(f'<circle class="ridge" cx="{fmt(px_k(k))}" cy="{fmt(py_p(p))}" r="2.2"/>')
    parts.append(f'<text class="axis" x="{joint_x + panel / 2}" y="{joint_y - 12}" text-anchor="middle"><tspan font-style="italic">k</tspan></text>')
    parts.append(f'<text class="axis" x="{joint_x - 18}" y="{joint_y + panel / 2}" text-anchor="middle" transform="rotate(-90 {joint_x - 18} {joint_y + panel / 2})"><tspan font-style="italic">p</tspan></text>')

    parts.append(f'<text x="{left_x + panel / 2}" y="{bottom_y + panel / 2 - 5}" text-anchor="middle" font-family="sans-serif" font-size="34" fill="#263f86">−0.89</text>')
    parts.append(f'<text class="axis" x="{left_x + panel / 2}" y="{bottom_y + panel / 2 + 25}" text-anchor="middle">后验相关</text>')

    k_density = density_curve(k_values, kmin, kmax)
    max_kd = max(y for _, y in k_density)
    k_points = [(joint_x + panel * (x - kmin) / (kmax - kmin), bottom_y + panel - (panel - 18) * y / max_kd) for x, y in k_density]
    parts.append(f'<path class="density" d="{path(k_points)}"/>')
    parts.append(f'<text class="label" x="{joint_x + panel / 2}" y="{bottom_y + 35}" text-anchor="middle" font-style="italic">k</text>')

    for value in (0.2, 0.3, 0.4, 0.5):
        x = px_p(value)
        parts.append(f'<text class="axis" x="{fmt(x)}" y="{bottom_y + panel + 23}" text-anchor="middle">{value:.1f}</text>')
    for value in (5, 10, 15):
        x = px_k(value)
        parts.append(f'<text class="axis" x="{fmt(x)}" y="{bottom_y + panel + 23}" text-anchor="middle">{value}</text>')

    parts.append(f'<rect class="panel" x="{right_x}" y="{right_y}" width="{right_w}" height="{right_h}"/>')
    xmax, ymax = 1.35, 1.9

    def rx(value: float) -> float:
        return right_x + right_w * value / xmax

    def ry(value: float) -> float:
        return right_y + right_h - right_h * value / ymax

    h_seq = [xmax * i / 100 for i in range(101)]
    median = [math.pi * theta_hat * h**3 for h in h_seq]
    low = [value * math.exp(-1.6 * sigma) for value in median]
    high = [value * math.exp(1.6 * sigma) for value in median]
    band = [(rx(h), ry(min(ymax, value))) for h, value in zip(h_seq, high)] + [
        (rx(h), ry(max(0, value))) for h, value in reversed(list(zip(h_seq, low)))
    ]
    parts.append(f'<polygon class="band" points="{" ".join(f"{fmt(x)},{fmt(y)}" for x, y in band)}"/>')
    for h, w in data:
        if h <= xmax and w <= ymax:
            parts.append(f'<circle class="point" cx="{fmt(rx(h))}" cy="{fmt(ry(w))}" r="3.2"/>')
    fit_points = [(rx(h), ry(min(ymax, value))) for h, value in zip(h_seq, median)]
    parts.append(f'<path class="fit" d="{path(fit_points)}"/>')

    for value in (0, 0.4, 0.8, 1.2):
        x = rx(value)
        parts.append(f'<line x1="{fmt(x)}" y1="{right_y + right_h}" x2="{fmt(x)}" y2="{right_y + right_h + 6}" stroke="#3c403b"/>')
        parts.append(f'<text class="axis" x="{fmt(x)}" y="{right_y + right_h + 25}" text-anchor="middle">{value:.1f}</text>')
    for value in (0, 0.5, 1.0, 1.5):
        y = ry(value)
        parts.append(f'<line x1="{right_x - 6}" y1="{fmt(y)}" x2="{right_x}" y2="{fmt(y)}" stroke="#3c403b"/>')
        parts.append(f'<text class="axis" x="{right_x - 12}" y="{fmt(y + 5)}" text-anchor="end">{value:.1f}</text>')
    parts.append(f'<text class="label" x="{right_x + right_w / 2}" y="{right_y + right_h + 57}" text-anchor="middle">身高（缩放后）</text>')
    parts.append(f'<text class="label" x="{right_x - 60}" y="{right_y + right_h / 2}" text-anchor="middle" transform="rotate(-90 {right_x - 60} {right_y + right_h / 2})">体重（缩放后）</text>')
    parts.append('</svg>')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT}")
    write_boxes_figure()
    panda_nuts = load_panda_nuts()
    write_nut_prior_figure()
    write_nut_posterior_figure(panda_nuts)
    write_lynx_hare_figure(load_lynx_hare())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
