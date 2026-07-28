#!/usr/bin/env python3
"""Keep generated reference panels inside the first HTML body in legacy imported posts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- SPG LINKED REFERENCES START -->"
END = "<!-- SPG LINKED REFERENCES END -->"


def process(path: Path) -> bool:
    original = path.read_text(encoding="utf-8", errors="replace")
    start = original.find(START)
    body_close = original.lower().find("</body>")
    if start < 0 or body_close < 0 or start < body_close:
        return False

    match = re.search(re.escape(START) + r".*?" + re.escape(END) + r"\s*", original, re.S)
    if not match:
        raise SystemExit(f"Unbalanced generated reference block: {path}")
    block = match.group(0).rstrip() + "\n"
    source = original[:match.start()] + original[match.end():]
    body_close = source.lower().find("</body>")
    source = source[:body_close] + "\n" + block + source[body_close:]
    path.write_text(source, encoding="utf-8")
    print(f"RELOCATED {path.relative_to(ROOT)}")
    return True


def main() -> None:
    changed = sum(process(path) for path in sorted(ROOT.glob("20[0-9][0-9]/*/*.html")))
    print(f"Relocated reference panels in {changed} legacy articles.")


if __name__ == "__main__":
    main()
