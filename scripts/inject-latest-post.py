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
]

LATEST = POSTS[-1]
LATEST_URL = "https://blog.sleeppathwaysguild.com" + LATEST["path"]
LATEST_BUILD = "2026-08-10T15:23:00Z"
LATEST_LASTMOD = "2026-08-10"


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


prepend_cards("index.html", home_card)
prepend_cards("archive/index.html", archive_card)
update_feed()
update_sitemap()
print("Latest Sleep Pathways Guild post added to listings, RSS feed, and sitemap.")
