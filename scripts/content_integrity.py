#!/usr/bin/env python3
"""Verify that important public blog content is rendered and current."""
from pathlib import Path

EDITORIAL = "/2026/07/shift-report-growing-sleep-tech-newsroom.html"
CPSGT_POST = "/2026/07/free-cpsgt-study-app-released.html"
CPSGT_APP = "https://sleeppathwaysguild.com/cpsgt-study-app.html"
CURRENT_EMAIL = "admin@sleeppathwaysguild.com"
OLD_EMAIL = "admin@sleeppathsguild.com"

home = Path("index.html").read_text(encoding="utf-8", errors="replace")
archive = Path("archive/index.html").read_text(encoding="utf-8", errors="replace")
sitemap = Path("sitemap.xml").read_text(encoding="utf-8", errors="replace")
feed = Path("feed.xml").read_text(encoding="utf-8", errors="replace")
editorial_page = Path(EDITORIAL.lstrip("/")).read_text(encoding="utf-8", errors="replace")

errors: list[str] = []
for label, text, required in (
    ("homepage editorial", home, EDITORIAL),
    ("homepage CPSGT release", home, CPSGT_POST),
    ("homepage CPSGT app", home, CPSGT_APP),
    ("homepage current email", home, CURRENT_EMAIL),
    ("archive editorial", archive, EDITORIAL),
    ("archive CPSGT release", archive, CPSGT_POST),
    ("sitemap editorial", sitemap, EDITORIAL),
    ("sitemap CPSGT release", sitemap, CPSGT_POST),
    ("feed editorial", feed, EDITORIAL),
    ("feed CPSGT release", feed, CPSGT_POST),
    ("editorial Shift Report link", editorial_page, "https://shift.sleeppathwaysguild.com/"),
):
    if required not in text:
        errors.append(f"Missing {label}: {required}")

for label, text in (("homepage", home), ("archive", archive), ("editorial", editorial_page)):
    if OLD_EMAIL.casefold() in text.casefold():
        errors.append(f"{label} still contains obsolete email {OLD_EMAIL}")

for forbidden in (
    "More Than a Scraper",
    "A scraper can collect headlines",
    "publishing system now does a better job",
    "feeds returned items",
):
    if forbidden.casefold() in editorial_page.casefold():
        errors.append(f"Editorial still exposes internal implementation language: {forbidden}")

if errors:
    print("Blog content-integrity check failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("Blog content-integrity check passed: release, editorial, contact, sitemap, and feed are current.")
