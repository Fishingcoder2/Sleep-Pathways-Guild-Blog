#!/usr/bin/env python3
"""Add current release and editorial cards to the generated blog listings."""
from pathlib import Path

EDITORIAL_PATH = "/2026/07/shift-report-growing-sleep-tech-newsroom.html"
CPSGT_PATH = "/2026/07/free-cpsgt-study-app-released.html"
CPSGT_APP = "https://sleeppathwaysguild.com/cpsgt-study-app.html"
GRID_MARKER = '<section class="wrap grid">'

EDITORIAL_HOME_CARD = (
    '<article class="card" data-spg-post="shift-report-editorial">'
    '<div class="meta">July 30, 2026</div>'
    '<h2>The Shift Report Is Growing: A Sleep-Tech Newsroom Takes Shape</h2>'
    '<p class="summary">A founder editorial on how The Shift Report is becoming a practical newsroom for sleep technologists, expanding free CEC coverage, strengthening editorial standards, and preparing to move closer to Sleep Pathways Guild.</p>'
    f'<a class="read" href="{EDITORIAL_PATH}">Read article</a>'
    '</article>'
)

CPSGT_HOME_CARD = (
    '<article class="card" data-spg-post="cpsgt-release">'
    '<div class="meta">July 28, 2026</div>'
    '<h2>Free CPSGT Study App Released</h2>'
    '<p class="summary">The free CPSGT Study Launchpad is live with 600 original practice questions, a 75-question mock-style exam, flashcards, Math Coach, equipment review, missed-question repair, and personalized progress reports.</p>'
    f'<a class="read" href="{CPSGT_PATH}">Read the release announcement</a>'
    '</article>'
)

RELEASE_BANNER = (
    '<aside class="spg-release-announcement" data-spg-release="cpsgt" '
    'aria-labelledby="spg-cpsgt-release-title">'
    '<span class="spg-release-kicker">Now released</span>'
    '<h2 id="spg-cpsgt-release-title">The free CPSGT Study Launchpad is live.</h2>'
    '<p>Start with 600 original practice questions, a 75-question mock-style exam, flashcards, Math Coach, equipment review, missed-question repair, and personalized progress reports. No purchase or account is required.</p>'
    '<div class="spg-release-actions">'
    f'<a class="primary" href="{CPSGT_APP}">Launch the Free CPSGT Webapp</a>'
    f'<a class="secondary" href="{CPSGT_PATH}">Read the release announcement</a>'
    '</div></aside>'
)

EDITORIAL_ARCHIVE_CARD = (
    '<article class="card" data-spg-post="shift-report-editorial">'
    '<div class="meta">July 30, 2026</div>'
    f'<h2><a href="{EDITORIAL_PATH}">The Shift Report Is Growing: A Sleep-Tech Newsroom Takes Shape</a></h2>'
    '</article>'
)

CPSGT_ARCHIVE_CARD = (
    '<article class="card" data-spg-post="cpsgt-release">'
    '<div class="meta">July 28, 2026</div>'
    f'<h2><a href="{CPSGT_PATH}">Free CPSGT Study App Released</a></h2>'
    '</article>'
)


def inject_home() -> None:
    path = Path("index.html")
    text = path.read_text(encoding="utf-8")
    if GRID_MARKER not in text:
        raise RuntimeError("Could not find article-grid marker in index.html")

    prefix = ""
    if 'data-spg-release="cpsgt"' not in text:
        prefix += RELEASE_BANNER
    if 'data-spg-post="shift-report-editorial"' not in text:
        prefix += EDITORIAL_HOME_CARD
    if 'data-spg-post="cpsgt-release"' not in text:
        prefix += CPSGT_HOME_CARD

    if prefix:
        text = text.replace(GRID_MARKER, prefix + GRID_MARKER, 1)
        path.write_text(text, encoding="utf-8")


def inject_archive() -> None:
    path = Path("archive/index.html")
    text = path.read_text(encoding="utf-8")
    if GRID_MARKER not in text:
        raise RuntimeError("Could not find article-grid marker in archive/index.html")

    cards = ""
    if 'data-spg-post="shift-report-editorial"' not in text:
        cards += EDITORIAL_ARCHIVE_CARD
    if 'data-spg-post="cpsgt-release"' not in text:
        cards += CPSGT_ARCHIVE_CARD

    if cards:
        text = text.replace(GRID_MARKER, GRID_MARKER + cards, 1)
        path.write_text(text, encoding="utf-8")


inject_home()
inject_archive()
print("Current CPSGT release and Shift Report editorial added to blog listings.")
