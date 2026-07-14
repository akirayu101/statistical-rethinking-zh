#!/usr/bin/env python3
"""Extract Figure 14.13 from the local Statistical Rethinking PDF."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = Path.home() / "Downloads" / "Statistical Rethinking 2nd Edition.pdf"
OUTPUT = ROOT / "translations" / "zh" / "media" / "chapter-14-primate-phylogeny.png"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="chapter14-phylogeny-") as temp_dir:
        page_prefix = Path(temp_dir) / "page-509"
        subprocess.run(
            [
                "pdftoppm", "-f", "509", "-l", "509", "-r", "264",
                "-png", "-singlefile", str(args.pdf), str(page_prefix),
            ],
            check=True,
        )
        subprocess.run(
            [
                "magick", str(page_prefix.with_suffix(".png")),
                "-crop", "1400x1300+310+230", "+repage", "-trim", "+repage",
                str(OUTPUT),
            ],
            check=True,
        )
    print(OUTPUT)


if __name__ == "__main__":
    main()
