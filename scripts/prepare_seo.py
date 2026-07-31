#!/usr/bin/env python3
"""Normalize critical metadata in the generated static blog before audit/deploy."""
from __future__ import annotations

import re
from pathlib import Path

META_DESCRIPTION = re.compile(
    r"<meta\b(?=[^>]*\bname\s*=\s*([\"'])description\1)[^>]*>",
    flags=re.IGNORECASE,
)
CONTENT_ATTR = re.compile(r"\bcontent\s*=\s*([\"'])(.*?)\1", flags=re.IGNORECASE | re.DOTALL)

DESCRIPTION_OVERRIDES = {
    "2026/07/shift-report-growing-sleep-tech-newsroom.html": (
        "A founder editorial on The Shift Report, expanded free CEC coverage, "
        "sleep-technology news, and its future with Sleep Pathways Guild."
    ),
    "2026/07/free-cpsgt-study-app-released.html": (
        "The free CPSGT Study Launchpad is live with 600 practice questions, "
        "a mock-style exam, flashcards, Math Coach, and progress reports."
    ),
    "2026/07/obesity-hypoventilation-polysomnography-rpsgt.html": (
        "Practical RPSGT review of obesity hypoventilation on polysomnography, "
        "including CO2 scoring, REM findings, PAP, oxygen, and treatment clues."
    ),
    "downloads/mini-lessons/sleep-related-hypoventilation/index.html": (
        "A concise sleep-technology lesson on sleep-related hypoventilation, "
        "CO2 monitoring, scoring concepts, and practical PSG review."
    ),
}


def replace_content(tag: str, value: str) -> str:
    escaped = value.replace("&", "&amp;").replace('"', "&quot;")
    if CONTENT_ATTR.search(tag):
        return CONTENT_ATTR.sub(lambda _m: f'content="{escaped}"', tag, count=1)
    return tag[:-1] + f' content="{escaped}">' if tag.endswith(">") else tag


def normalize(path: Path) -> tuple[bool, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(META_DESCRIPTION.finditer(text))
    if not matches:
        return False, 0

    changed = False
    removed = 0
    if len(matches) > 1:
        for match in reversed(matches[1:]):
            text = text[: match.start()] + text[match.end() :]
            removed += 1
        changed = True

    override = DESCRIPTION_OVERRIDES.get(path.as_posix())
    if override:
        first = META_DESCRIPTION.search(text)
        if first:
            replacement = replace_content(first.group(0), override)
            if replacement != first.group(0):
                text = text[: first.start()] + replacement + text[first.end() :]
                changed = True

    if changed:
        path.write_text(text, encoding="utf-8")
    return changed, removed


def main() -> None:
    changed_files = 0
    removed_tags = 0
    for path in sorted(Path(".").rglob("*.html")):
        if ".git" in path.parts:
            continue
        changed, removed = normalize(path)
        changed_files += int(changed)
        removed_tags += removed
    print(
        f"SEO metadata normalized in {changed_files} file(s); "
        f"removed {removed_tags} duplicate description tag(s)."
    )


if __name__ == "__main__":
    main()
