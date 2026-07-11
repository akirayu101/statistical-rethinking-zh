#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-prior-predictive.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def polyline(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def normal_pdf(value: float, mean: float, sd: float) -> float:
    return math.exp(-0.5 * ((value - mean) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))


def kde(values: list[float], xs: list[float]) -> list[float]:
    count = len(values)
    mean = sum(values) / count
    variance = sum((value - mean) ** 2 for value in values) / (count - 1)
    bandwidth = max(1.5, 1.06 * math.sqrt(variance) * count ** (-0.2))
    scale = 1 / (count * bandwidth * math.sqrt(2 * math.pi))
    return [scale * sum(math.exp(-0.5 * ((x - value) / bandwidth) ** 2) for value in values) for x in xs]


def plot_panel(
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    xlabel: str,
    xmin: float,
    xmax: float,
    xs: list[float],
    ys: list[float],
    ticks: list[tuple[float, str]],
    marker_lines: list[tuple[float, str, str]] | None = None,
) -> list[str]:
    ymax = max(ys) * 1.08

    def px(value: float) -> float:
        return x + width * (value - xmin) / (xmax - xmin)

    def py(value: float) -> float:
        return y + height * (1 - value / ymax)

    body = [
        f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#fff" stroke="#363934" stroke-width="1.2"/>',
        f'  <text x="{fmt(x + width / 2)}" y="{y - 18}" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="#263f86">{title}</text>',
        f'  <polyline points="{polyline([(px(xv), py(yv)) for xv, yv in zip(xs, ys)])}" fill="none" stroke="#6670ee" stroke-width="3"/>',
    ]
    for value, label in ticks:
        tx = px(value)
        body.extend(
            [
                f'  <line x1="{fmt(tx)}" y1="{y + height}" x2="{fmt(tx)}" y2="{y + height + 7}" stroke="#363934"/>',
                f'  <text x="{fmt(tx)}" y="{y + height + 28}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="#30332e">{label}</text>',
            ]
        )
    if marker_lines:
        for value, dash, color in marker_lines:
            tx = px(value)
            body.append(
                f'  <line x1="{fmt(tx)}" y1="{y}" x2="{fmt(tx)}" y2="{y + height}" stroke="{color}" stroke-width="1.8"{f" stroke-dasharray=\"{dash}\"" if dash else ""}/>'
            )
    body.extend(
        [
            f'  <text x="{fmt(x + width / 2)}" y="{y + height + 58}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">{xlabel}</text>',
            f'  <text x="{x - 35}" y="{fmt(y + height / 2)}" transform="rotate(-90 {x - 35} {fmt(y + height / 2)})" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#30332e">密度</text>',
        ]
    )
    return body


def main() -> int:
    rng = random.Random(4303)
    count = 8_000
    sample_sigma = [rng.uniform(0, 50) for _ in range(count)]
    sample_mu = [rng.gauss(178, 20) for _ in range(count)]
    prior_h = [rng.gauss(mu, sigma) for mu, sigma in zip(sample_mu, sample_sigma)]
    wide_mu = [rng.gauss(178, 100) for _ in range(count)]
    wide_h = [rng.gauss(mu, sigma) for mu, sigma in zip(wide_mu, sample_sigma)]

    width, height = 1200, 850
    panel_width, panel_height = 390, 250
    left_x, right_x = 145, 675
    top_y, bottom_y = 90, 515
    mu_xs = [100 + 150 * index / 240 for index in range(241)]
    sigma_xs = [-10 + 70 * index / 240 for index in range(241)]
    height_xs = [-50 + 450 * index / 240 for index in range(241)]
    wide_xs = [-150 + 700 * index / 240 for index in range(241)]

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "  <title>身高模型的先验预测模拟</title>",
        "  <desc>顶部显示均值与标准差先验，左下显示合理先验产生的身高先验预测，右下显示过宽均值先验产生负身高和异常高身高。</desc>",
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    body.extend(
        plot_panel(
            x=left_x,
            y=top_y,
            width=panel_width,
            height=panel_height,
            title="μ ∼ Normal(178, 20)",
            xlabel="μ",
            xmin=100,
            xmax=250,
            xs=mu_xs,
            ys=[normal_pdf(value, 178, 20) for value in mu_xs],
            ticks=[(100, "100"), (178, "178"), (250, "250")],
        )
    )
    uniform_ys = [0.02 if 0 <= value <= 50 else 0 for value in sigma_xs]
    body.extend(
        plot_panel(
            x=right_x,
            y=top_y,
            width=panel_width,
            height=panel_height,
            title="σ ∼ Uniform(0, 50)",
            xlabel="σ",
            xmin=-10,
            xmax=60,
            xs=sigma_xs,
            ys=uniform_ys,
            ticks=[(0, "0"), (50, "50")],
        )
    )
    body.extend(
        plot_panel(
            x=left_x,
            y=bottom_y,
            width=panel_width,
            height=panel_height,
            title="h ∼ Normal(μ, σ)",
            xlabel="身高（厘米）",
            xmin=-50,
            xmax=400,
            xs=height_xs,
            ys=kde(prior_h, height_xs),
            ticks=[(0, "0"), (73, "73"), (178, "178"), (283, "283")],
        )
    )
    body.extend(
        plot_panel(
            x=right_x,
            y=bottom_y,
            width=panel_width,
            height=panel_height,
            title="h ∼ Normal(μ, σ)，μ ∼ Normal(178, 100)",
            xlabel="身高（厘米）",
            xmin=-150,
            xmax=550,
            xs=wide_xs,
            ys=kde(wide_h, wide_xs),
            ticks=[(-128, "-128"), (0, "0"), (178, "178"), (272, "272"), (484, "484")],
            marker_lines=[(0, "7 6", "#30332e"), (272, "", "#30332e")],
        )
    )
    integration_points = 10_000
    negative = 0.0
    giant = 0.0
    for index in range(integration_points):
        sigma = 50 * (index + 0.5) / integration_points
        marginal_sd = math.sqrt(100**2 + sigma**2)
        negative += 0.5 * math.erfc(178 / (marginal_sd * math.sqrt(2)))
        giant += 0.5 * math.erfc((272 - 178) / (marginal_sd * math.sqrt(2)))
    negative /= integration_points
    giant /= integration_points
    body.extend(
        [
            f'  <text x="{width / 2}" y="828" text-anchor="middle" font-family="{FONT}" font-size="15" fill="#656963">过宽先验模拟中：约 {negative:.0%} 为负身高，约 {giant:.0%} 高于 272 厘米。</text>',
            "</svg>",
            "",
        ]
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
