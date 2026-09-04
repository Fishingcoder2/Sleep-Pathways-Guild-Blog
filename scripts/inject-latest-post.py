from pathlib import Path

POSTS = [
    {
        "id": "shift-report-editorial",
        "path": "/2026/07/shift-report-growing-sleep-tech-newsroom.html",
        "date": "July 30, 2026",
        "title": "The Shift Report Is Growing: A Sleep-Tech Newsroom Takes Shape",
        "summary": "A founder editorial on how The Shift Report is becoming a practical newsroom for sleep technologists, expanding free CEC coverage, strengthening editorial standards, and preparing to move closer to Sleep Pathways Guild.",
    },
    {
        "id": "back-to-school-guide-2026",
        "path": "/2026/08/back-to-school-guide-2026.html",
        "date": "August 10, 2026",
        "title": "Back-to-School Guide 2026: Sleep Technology Education Pathways",
        "summary": "A practical 2026 guide to ASTEP, STAR, BRPT credential eligibility, accredited sleep technology programs, degree options, professional memberships, and choosing an education path that fits your goals.",
    },
    {
        "id": "brpt-new-management-2026",
        "path": "/2026/08/brpt-new-management-rpsgt-candidates-2026.html",
        "date": "August 10, 2026",
        "title": "BRPT New Management: What RPSGT Candidates Should Know",
        "summary": "BRPT has selected Association Headquarters as its new management firm. Tracy Frazier explains what the 2026 transition means—and does not mean—for RPSGT candidates and sleep technologists.",
    },
    {
        "id": "shift-report-august-2026",
        "path": "/2026/08/whats-new-shift-report-august-2026.html",
        "date": "August 11, 2026",
        "title": "What's New on The Shift Report: August 2026",
        "summary": "New Shift Report resources for sleep technologists covering RPSGT recertification, a CMS sleep-study fact check, verified AAST member-free CEC opportunities, and autoscoring with human quality review.",
    },
    {
        "id": "central-sleep-apnea-practical-notes",
        "path": "/downloads/mini-lessons/central-sleep-apnea/",
        "date": "September 4, 2026",
        "title": "Central Sleep Apnea &amp; TECSA — Practical Notes in Polysomnography",
        "summary": "A free case-based Sleep Pathways Guild lesson on central sleep apnea, treatment-emergent central sleep apnea, mixed apnea, periodic breathing, Cheyne-Stokes breathing, PSG recognition, PAP response, and sleep technologist practice.",
    },
]

LATEST = POSTS[-1]
LATEST_URL = "https://blog.sleeppathwaysguild.com" + LATEST["path"]
LATEST_BUILD = "2026-09-04T12:00:00Z"
LATEST_LASTMOD = "2026-09-04"


def home_card(post):
    return (
        f'<article class="card" data-spg-post="{post["id"]}">'
        f'<div class="meta">{post["date"]}</div>'
        f'<h2>{post["title"]}</h2>'
        f'<p class="summary">{post["summary"]}</p>'
        f'<a class="read" href="{post["path"]}">Read article</a>'
        '</article>'
    )


def archive_card(post):
    return (
        f'<article class="card" data-spg-post="{post["id"]}">'
        f'<div class="meta">{post["date"]}</div>'
        f'<h2><a href="{post["path"]}">{post["title"]}</a></h2>'
        '</article>'
    )


def prepend_cards(path: str, card_factory) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    marker = '<section class="wrap grid">'
    if marker not in text:
        raise RuntimeError(f"Could not find article-grid marker in {path}")

    # Insert oldest first because each replacement prepends at the marker.
    # The final rendered order is therefore newest first.
    for post in POSTS:
        if post["path"] in text:
            continue
        text = text.replace(marker, marker + card_factory(post), 1)

    file_path.write_text(text, encoding="utf-8")


def update_feed() -> None:
    path = Path("feed.xml")
    text = path.read_text(encoding="utf-8")
    if LATEST_URL not in text:
        item = (
            "  <item>\n"
            f"    <title>{LATEST['title']} | Sleep Pathways Guild</title>\n"
            f"    <link>{LATEST_URL}</link>\n"
            f"    <guid isPermaLink=\"true\">{LATEST_URL}</guid>\n"
            f"    <pubDate>{LATEST_BUILD}</pubDate>\n"
            f"    <description>{LATEST['summary']}</description>\n"
            "  </item>\n"
        )
        marker = "  <item>\n"
        if marker not in text:
            raise RuntimeError("Could not find RSS item marker in feed.xml")
        text = text.replace(marker, item + marker, 1)

    import re
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{LATEST_BUILD}</lastBuildDate>", text, count=1)
    path.write_text(text, encoding="utf-8")


def update_sitemap() -> None:
    path = Path("sitemap.xml")
    text = path.read_text(encoding="utf-8")
    if LATEST_URL not in text:
        marker = "  <url><loc>https://blog.sleeppathwaysguild.com/</loc>"
        entry = f"  <url><loc>{LATEST_URL}</loc><lastmod>{LATEST_LASTMOD}</lastmod></url>\n"
        pos = text.find("\n", text.find(marker))
        if pos == -1:
            raise RuntimeError("Could not find sitemap homepage entry")
        text = text[:pos + 1] + entry + text[pos + 1:]

    import re
    text = re.sub(
        r"(<url><loc>https://blog\.sleeppathwaysguild\.com/</loc><lastmod>).*?(</lastmod></url>)",
        rf"\g<1>{LATEST_LASTMOD}\g<2>",
        text,
        count=1,
    )
    path.write_text(text, encoding="utf-8")


def fix_csa_lesson_branding() -> None:
    """Use the official Sleep Pathways Guild badge in the CSA lesson header."""
    path = Path("downloads/mini-lessons/central-sleep-apnea/index.html")
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")
    old_css = ".brandmark{width:54px;height:54px;border-radius:50%;background:var(--navy);color:#fff;border:5px solid #bfe6ea;display:grid;place-items:center;font-size:.8rem;text-align:center;line-height:1.05}"
    new_css = ".brandmark{width:68px;height:68px;object-fit:contain;display:block;flex:0 0 auto}"
    text = text.replace(old_css, new_css)

    old_mark = '<div class="brandmark">SLEEP<br>PATHWAYS</div>'
    new_mark = '<img class="brandmark" src="https://sleeppathwaysguild.com/assets/branding/spg-guild-badge.png" alt="Sleep Pathways Guild badge" width="68" height="68">'
    text = text.replace(old_mark, new_mark)

    og_anchor = '<meta property="og:type" content="article"><meta property="og:title" content="Central Sleep Apnea & TECSA — Practical Notes in Polysomnography"><meta property="og:description" content="Free case-based PSG lesson from Sleep Pathways Guild.">'
    if 'property="og:image"' not in text and og_anchor in text:
        text = text.replace(
            og_anchor,
            og_anchor + '\n<meta property="og:image" content="https://sleeppathwaysguild.com/assets/branding/spg-guild-badge.png"><meta property="og:image:alt" content="Sleep Pathways Guild badge">',
            1,
        )

    canonical = '<link rel="canonical" href="https://blog.sleeppathwaysguild.com/downloads/mini-lessons/central-sleep-apnea/">'
    if 'rel="canonical"' not in text:
        text = text.replace('</title>', '</title>\n' + canonical, 1)

    path.write_text(text, encoding="utf-8")


fix_csa_lesson_branding()
prepend_cards("index.html", home_card)
prepend_cards("archive/index.html", archive_card)
update_feed()
update_sitemap()
print("Latest Sleep Pathways Guild post added to listings, RSS feed, sitemap, and CSA lesson branding normalized.")
