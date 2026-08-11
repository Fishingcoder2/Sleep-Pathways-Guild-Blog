#!/usr/bin/env python3
"""Normalize legacy static-blog SEO without changing public URLs or article meaning.

The blog was migrated from older publishing markup. Some posts contain a second
(or third) H1 inside the article body, and several inherited document titles are
longer than the Guild's SEO audit target. This script keeps the first H1 on each
page, demotes later H1 headings to H2, and applies a small reviewed mapping of
SEO titles/descriptions for legacy pages.

It is intentionally idempotent and is run before both GitHub Pages deployment
and the repository SEO audit.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TITLE_OVERRIDES = {
    "2026/08/whats-new-shift-report-august-2026.html": "The Shift Report: Sleep Technology Updates | August 2026",
    "2026/05/an-update-will-be-coming-in-near-future.html": "Sleep Pathways Guild Update: New Features Coming Soon",
    "2026/05/update-sleeppathwaysguildcom.html": "Sleep Pathways Guild Homepage Update & Founder Introduction",
    "2026/05/where-path-leads-sleep-pathways-guild.html": "Sleep Technologist Careers & Credentialing | Sleep Pathways Guild",
    "2026/06/breaking-cycle-how-sleep-deprivation.html": "Sleep Deprivation, Metabolism & Sleep Apnea | Sleep Guild",
    "2026/06/domain-3-ekgecg-artifact-recognition.html": "RPSGT Domain 3: EKG/ECG Artifact Recognition",
    "2026/06/how-to-study-for-rpsgt-exam-1-hour-per.html": "How to Study for the RPSGT Exam: 1 Hour a Day",
    "2026/06/rpsgt-exam-practice-recognizing-snore_01261318364.html": "RPSGT Practice: Recognizing Snore Artifact on PSG",
    "2026/06/rpsgt-study-exam-prep-domain-4-self.html": "RPSGT Domain 4 Self-Study Lesson | Sleep Pathways Guild",
    "2026/06/sleep-2026-guild-feature.html": "SLEEP 2026 Highlights for Sleep Technologists | Guild Feature",
    "2026/06/the-saturday-pulse-sleep-pathways-guild.html": "The Saturday Pulse: Sleep Technology Briefing | June 2026",
    "2026/06/the-tuesday-pulse-sleep-pathways-guild.html": "The Tuesday Pulse: Sleep Technology Briefing | June 2026",
    "2026/07/coach-bob-teaches-stage-n2-sleep-rpsgt_01114178945.html": "Stage N2 Sleep Scoring: RPSGT Practice with Coach Bob",
    "2026/07/free-rpsgt-exam-prep-blueprint_0739379817.html": "Free RPSGT Exam Prep: Blueprint Scenarios & UPPP Review",
    "2026/07/low-flow-vs-high-flow-oxygen.html": "Low-Flow vs High-Flow Oxygen: 4–5 L/min Explained",
    "2026/07/respiratory-events-rera-uars-and.html": "RERA, UARS & Pediatric Apnea Scoring | RPSGT Practice",
    "2026/07/rpsgt-review-test-previous-posts-sleep.html": "RPSGT Review: Sleep Staging & Brain Waves Practice",
    "2026/07/sleep-medicine-is-moving-fast-recent.html": "Sleep Medicine Updates for Sleep Technologists | July 2026",
}

DESCRIPTION_OVERRIDES = {
    "2026/08/whats-new-shift-report-august-2026.html": (
        "August 2026 sleep technology updates for RPSGT learners and working technologists, "
        "including recertification, CMS fact checks, CECs, and autoscoring review."
    ),
    "archive/index.html": (
        "Browse the Sleep Pathways Guild article archive for RPSGT and CPSGT exam prep, sleep "
        "scoring, PSG artifacts, PAP titration, EKG review, and professional updates."
    ),
    "2026/06/domain-3-ekgecg-artifact-recognition.html": (
        "RPSGT Domain 3 practice on EKG/ECG artifact recognition, signal quality, troubleshooting, "
        "and scoring awareness for sleep technologists and exam-prep learners."
    ),
}

TITLE_RE = re.compile(r"<title\b[^>]*>.*?</title>", re.IGNORECASE | re.DOTALL)
META_DESCRIPTION_RE = re.compile(
    r"<meta\b(?=[^>]*\bname\s*=\s*([\"'])description\1)[^>]*>",
    re.IGNORECASE | re.DOTALL,
)
H1_OPEN_RE = re.compile(r"<h1\b([^>]*)>", re.IGNORECASE)
H1_CLOSE_RE = re.compile(r"</h1\s*>", re.IGNORECASE)


def replace_title(text: str, title: str) -> str:
    escaped = title.replace("&", "&amp;")
    return TITLE_RE.sub(f"<title>{escaped}</title>", text, count=1)


def replace_description(text: str, description: str) -> str:
    escaped = (
        description.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    replacement = f'<meta name="description" content="{escaped}">' 
    return META_DESCRIPTION_RE.sub(replacement, text, count=1)


def demote_extra_h1(text: str) -> tuple[str, int]:
    opens = list(H1_OPEN_RE.finditer(text))
    if len(opens) <= 1:
        return text, 0

    open_count = 0
    close_count = 0

    def open_repl(match: re.Match[str]) -> str:
        nonlocal open_count
        open_count += 1
        if open_count == 1:
            return match.group(0)
        return f"<h2{match.group(1)}>"

    def close_repl(match: re.Match[str]) -> str:
        nonlocal close_count
        close_count += 1
        return match.group(0) if close_count == 1 else "</h2>"

    text = H1_OPEN_RE.sub(open_repl, text)
    text = H1_CLOSE_RE.sub(close_repl, text)
    return text, len(opens) - 1


def main() -> int:
    changed_files = 0
    demoted = 0

    # Sitemap-listed HTML is the public SEO surface; limit changes to it.
    html_files = sorted(
        p for p in ROOT.rglob("*.html")
        if ".git" not in p.parts and "tools" not in p.parts
    )

    for path in html_files:
        rel = path.relative_to(ROOT).as_posix()
        original = path.read_text(encoding="utf-8", errors="replace")
        text = original

        if rel in TITLE_OVERRIDES:
            text = replace_title(text, TITLE_OVERRIDES[rel])
        if rel in DESCRIPTION_OVERRIDES:
            text = replace_description(text, DESCRIPTION_OVERRIDES[rel])

        text, count = demote_extra_h1(text)
        demoted += count

        if text != original:
            path.write_text(text, encoding="utf-8")
            changed_files += 1

    print(f"Legacy SEO cleanup: changed {changed_files} files; demoted {demoted} extra H1 headings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
