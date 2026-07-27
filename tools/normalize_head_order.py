#!/usr/bin/env python3
"""Keep charset/viewport declarations ahead of the generated SEO block."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- SPG SEO START -->"
END = "<!-- SPG SEO END -->"


def normalize(path: Path) -> None:
    original = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(re.escape(START) + r".*?" + re.escape(END), original, re.S)
    if not match:
        return
    block = match.group(0)
    text = original[:match.start()] + original[match.end():]
    text = re.sub(r"\s*<!--\s*Google tag \(gtag\.js\)\s*-->\s*", "\n", text, flags=re.I)
    head = re.search(r"<head\b[^>]*>", text, re.I)
    if not head:
        return
    head_end = re.search(r"</head\s*>", text[head.end():], re.I)
    boundary = head.end() + (head_end.start() if head_end else 4096)
    position = head.end()
    for pattern in (
        r'<meta\s+charset=["\'][^"\']+["\'][^>]*>',
        r'<meta\s+name=["\']viewport["\'][^>]*>',
    ):
        item = re.search(pattern, text[head.end():boundary], re.I)
        if item:
            position = max(position, head.end() + item.end())
    text = text[:position] + "\n" + block + "\n" + text[position:]
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"NORMALIZED {path.relative_to(ROOT)}")


def main() -> None:
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" not in path.parts and "node_modules" not in path.parts:
            normalize(path)


if __name__ == "__main__":
    main()
