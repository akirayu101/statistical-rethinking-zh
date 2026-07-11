#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "translations" / "zh" / "media" / "chapter-04-ptolemaic-universe.svg"
FONT = "-apple-system,BlinkMacSystemFont,PingFang SC,Noto Sans CJK SC,sans-serif"


def main() -> int:
    width, height = 900, 600
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <title>托勒密宇宙的本轮与均轮</title>
  <desc>地球偏离均轮中心，行星沿本轮运动，本轮中心再沿均轮运动；对应点位于均轮中心另一侧。</desc>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#30332e"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#ffffff"/>

  <circle cx="390" cy="355" r="205" fill="none" stroke="#30332e" stroke-width="2" stroke-dasharray="5 6"/>
  <path d="M 193 300 A 205 205 0 0 1 216 242" fill="none" stroke="#30332e" stroke-width="2.4" marker-end="url(#arrow)"/>

  <circle cx="385" cy="142" r="88" fill="none" stroke="#30332e" stroke-width="1.7" stroke-dasharray="4 5"/>
  <path d="M 322 82 A 88 88 0 0 1 371 55" fill="none" stroke="#30332e" stroke-width="2.4" marker-end="url(#arrow)"/>
  <line x1="390" y1="355" x2="385" y2="142" stroke="#6b706b" stroke-width="1.4"/>

  <circle cx="318" cy="355" r="24" fill="#edf2ff" stroke="#263f86" stroke-width="2.2"/>
  <path d="M 300 348 C 307 337, 319 340, 323 346 C 329 354, 337 352, 339 361 C 332 372, 321 378, 310 373 C 303 368, 299 359, 300 348 Z" fill="#6fa075" opacity="0.9"/>
  <text x="250" y="345" text-anchor="end" font-family="{FONT}" font-size="22" fill="#30332e">地球</text>

  <circle cx="390" cy="355" r="7" fill="#ffffff" stroke="#30332e" stroke-width="1.7"/>
  <text x="430" y="386" font-family="{FONT}" font-size="17" fill="#656963">均轮中心</text>

  <circle cx="466" cy="355" r="9" fill="#30332e"/>
  <text x="492" y="363" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">对应点</text>

  <circle cx="385" cy="142" r="9" fill="#30332e"/>
  <path d="M 385 142 C 315 118, 275 116, 220 150" fill="none" stroke="#30332e" stroke-width="2" stroke-dasharray="5 5" marker-end="url(#arrow)"/>
  <circle cx="335" cy="73" r="20" fill="#ffffff" stroke="#30332e" stroke-width="3"/>
  <text x="273" y="66" text-anchor="end" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">行星</text>

  <path d="M 462 115 L 513 80" stroke="#30332e" stroke-width="1.8" marker-end="url(#arrow)"/>
  <text x="525" y="82" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">本轮</text>

  <path d="M 555 220 L 603 185" stroke="#30332e" stroke-width="1.8" marker-end="url(#arrow)"/>
  <text x="618" y="186" font-family="{FONT}" font-size="22" font-weight="700" fill="#263f86">均轮</text>

  <text x="450" y="555" text-anchor="middle" font-family="{FONT}" font-size="16" fill="#656963">行星沿本轮转动，本轮中心沿均轮绕行；对应点用于校准角速度。</text>
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
