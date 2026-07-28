#!/usr/bin/env python3
"""Inventory references, resource mentions, and outbound links in blog articles."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POST_GLOB = "20[0-9][0-9]/*/*.html"
REPORT = ROOT / "REFERENCE_LINK_AUDIT.md"

KNOWN_RESOURCES = (
    "Fundamentals of Sleep Technology",
    "Polysomnography for the Sleep Technologist",
    "Sleep Medicine Pearls",
    "Pediatric Sleep Medicine Pearls",
    "A Clinical Guide to Pediatric Sleep",
    "RPSGT Scoring Mastery",
    "Fundamentals for Sleep Professionals",
    "AASM Scoring Manual",
    "International Classification of Sleep Disorders",
    "ICSD-3",
    "ICSD-3-TR",
    "BRPT Candidate Handbook",
    "BRPT Exam Blueprint",
    "RPSGT Candidate Handbook",
    "AAST",
    "AASM",
    "BRPT",
)

REFERENCE_HEADINGS = re.compile(
    r"\b(references?|sources?|resources?|works cited|bibliography|further reading|recommended reading|study resources?)\b",
    re.I,
)


def article_html(text: str) -> str:
    match = re.search(r'<div class="post-content">(.*?)</article>', text, re.I | re.S)
    return match.group(1) if match else text


def plain_text(fragment: str) -> str:
    fragment = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<style\b.*?</style>", " ", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<!--.*?-->", " ", fragment, flags=re.S)
    fragment = re.sub(r"</?(?:p|div|section|article|li|ul|ol|h[1-6]|br|table|tr|blockquote)\b[^>]*>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    fragment = html.unescape(fragment)
    lines = [re.sub(r"\s+", " ", line).strip() for line in fragment.splitlines()]
    return "\n".join(line for line in lines if line)


def title_of(text: str, path: Path) -> str:
    for pattern in (
        r'<h1 class="post-title">(.*?)</h1>',
        r"<title>(.*?)</title>",
    ):
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return re.sub(r"<[^>]+>", "", html.unescape(match.group(1))).strip()
    return path.stem


def hrefs(fragment: str) -> list[str]:
    found = []
    for value in re.findall(r'href=["\']([^"\']+)["\']', fragment, re.I):
        if value.startswith(("#", "mailto:", "javascript:")):
            continue
        if value not in found:
            found.append(value)
    return found


def reference_excerpt(text: str) -> str:
    match = REFERENCE_HEADINGS.search(text)
    if match:
        return text[match.start(): match.start() + 5000]
    return text[-1800:]


def main() -> None:
    paths = sorted(ROOT.glob(POST_GLOB))
    rows = [
        "# Blog Article Reference-Link Audit",
        "",
        f"Articles scanned: **{len(paths)}**",
        "",
        "This report inventories resource names, identifiers, current links, and the reference-like ending of each article. It does not alter article content.",
        "",
    ]

    for path in paths:
        source = path.read_text(encoding="utf-8", errors="replace")
        fragment = article_html(source)
        text = plain_text(fragment)
        links = hrefs(fragment)
        mentions = [name for name in KNOWN_RESOURCES if re.search(re.escape(name), text, re.I)]
        dois = sorted(set(re.findall(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.I)))
        isbns = sorted(set(re.findall(r"\b(?:ISBN(?:-1[03])?:?\s*)?(?:97[89][- ]?)?\d[- 0-9]{8,16}[\dX]\b", text, re.I)))

        rows.extend(
            [
                f"## {title_of(source, path)}",
                "",
                f"- Path: `{path.relative_to(ROOT).as_posix()}`",
                f"- Known resource mentions: {', '.join(mentions) if mentions else 'None detected'}",
                f"- DOI candidates: {', '.join(dois) if dois else 'None detected'}",
                f"- ISBN candidates: {', '.join(isbns) if isbns else 'None detected'}",
                f"- Current outbound links: {len(links)}",
            ]
        )
        for link in links:
            rows.append(f"  - {link}")
        rows.extend(["", "Reference/end excerpt:", "", "```text", reference_excerpt(text), "```", ""])

    REPORT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)} for {len(paths)} articles")


if __name__ == "__main__":
    main()
