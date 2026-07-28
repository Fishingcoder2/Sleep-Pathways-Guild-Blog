#!/usr/bin/env python3
"""Refine generated reference sections using only each article's actual body content."""

from __future__ import annotations

import re
from pathlib import Path

import link_article_references as linker


def article_body(source: str, path: Path) -> str:
    match = re.search(r'<div class="post-content">(.*?)</article>', source, re.I | re.S)
    if not match:
        raise SystemExit(f"Could not locate article body: {path}")
    return match.group(1)


def process(path: Path) -> bool:
    original = path.read_text(encoding="utf-8", errors="replace")
    source = linker.remove_block(original)
    body = article_body(source, path)
    text = linker.visible_text(body)
    existing_urls = set(re.findall(r'href=["\']([^"\']+)["\']', body, flags=re.I))
    entries: list[tuple[str, str, str, str]] = []
    seen = set(existing_urls)

    for pattern, label, search_title in linker.BOOKS:
        if re.search(pattern, text, re.I):
            linker.add_entry(
                entries,
                seen,
                f"{label} — view available editions on Amazon",
                linker.amazon_search(search_title),
                "Verify the title, author, and edition before purchasing.",
                "affiliate",
            )

    for pattern, label, url, note in linker.OFFICIAL:
        if re.search(pattern, text, re.I):
            linker.add_entry(entries, seen, label, url, note, "official")

    rel = path.relative_to(linker.ROOT).as_posix()
    for label, url, note in linker.POST_SPECIFIC.get(rel, []):
        linker.add_entry(entries, seen, label, url, note, "scholarly")

    if entries:
        source = linker.insert_block(source, linker.build_block(entries), path)

    if source != original:
        path.write_text(source, encoding="utf-8")
        print(f"REFINED {rel}: {len(entries)} body-supported links")
        return True
    return False


def main() -> None:
    changed = sum(process(path) for path in sorted(linker.ROOT.glob(linker.POST_GLOB)))
    linker.update_store_disclosure()
    print(f"Body-only reference refinement completed; changed {changed} articles.")


if __name__ == "__main__":
    main()
