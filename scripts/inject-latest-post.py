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
    {
        "id": "rpsgt-domain1-before-lights-out-2026",
        "path": "/2026/09/rpsgt-domain-1-before-the-lights-go-out.html",
        "date": "September 18, 2026",
        "title": "Before the Lights Go Out: RPSGT Domain 1 Interactive Study Lesson",
        "summary": "A full interactive RPSGT Domain 1 lesson on clinical assessment, patient education, ESS, STOP-BANG, PAP support, 25 practice questions, flashcards, glossary terms, clinical scenarios, and blueprint-based weak-area tracking.",
    },
    {
        "id": "rpsgt-domain2-can-you-trust-the-signal-2026",
        "path": "/2026/09/rpsgt-domain-2-can-you-trust-the-signal.html",
        "date": "September 23, 2026",
        "title": "Can You Trust the Signal? RPSGT Domain 2 Interactive Study Lesson",
        "summary": "An interactive RPSGT Domain 2 lesson on instrumentation, signal quality, artifact recognition, HSAT, MSLT, MWT, troubleshooting, 25 original practice questions, flashcards, scenarios, and blueprint-based repair.",
    },
    {
        "id": "rpsgt-recert-delay-2027",
        "path": "/2026/10/rpsgt-recertification-processing-delay-january-2027.html",
        "date": "October 19, 2026",
        "title": "RPSGT Recertification Alert: BRPT Reports Processing Delays",
        "summary": "BRPT reports significant processing delays for the January 1, 2027 RPSGT recertification cycle. More than 3,000 credential holders are due to renew; here is what to do now.",
    },
]

LATEST = POSTS[-1]
LATEST_URL = "https://blog.sleeppathwaysguild.com" + LATEST["path"]
LATEST_BUILD = "2026-10-19T12:19:00Z"
LATEST_LASTMOD = "2026-10-19"


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

    # Rebuild all script-managed cards every deployment so partial prior
    # updates cannot leave the newest post below an older injected card.
    import re
    managed_ids = {post["id"] for post in POSTS}
    pattern = re.compile(
        r'<article class="card" data-spg-post="([^"]+)">.*?</article>',
        re.DOTALL,
    )
    text = pattern.sub(
        lambda m: "" if m.group(1) in managed_ids else m.group(0),
        text,
    )

    cards = "".join(card_factory(post) for post in reversed(POSTS))
    text = text.replace(marker, marker + cards, 1)
    file_path.write_text(text, encoding="utf-8")


def update_feed() -> None:
    """Add the approved latest editorial and normalize RSS 2.0 dates.

    POSTS is the curated editorial list. Never auto-publish arbitrary HTML files.
    """
    from datetime import datetime, timezone
    from email.utils import format_datetime, parsedate_to_datetime
    import xml.etree.ElementTree as ET

    path = Path("feed.xml")
    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag != "rss" or root.attrib.get("version") != "2.0":
        raise RuntimeError("Expected RSS 2.0 feed")
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("RSS channel missing")

    # Preserve existing feed entries, including editorial content outside POSTS.
    items = channel.findall("item")
    seen = set()
    for item in items:
        guid = (item.findtext("guid") or item.findtext("link") or "").strip()
        if not guid or guid in seen:
            raise RuntimeError(f"Missing or duplicate RSS GUID: {guid}")
        seen.add(guid)
        date_node = item.find("pubDate")
        if date_node is not None and date_node.text:
            raw = date_node.text.strip()
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                parsed = parsedate_to_datetime(raw)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            date_node.text = format_datetime(parsed.astimezone(timezone.utc), usegmt=True)

    published = datetime.fromisoformat(LATEST_BUILD.replace("Z", "+00:00"))
    if LATEST_URL not in seen:
        item = ET.Element("item")
        ET.SubElement(item, "title").text = LATEST["title"] + " | Sleep Pathways Guild"
        ET.SubElement(item, "link").text = LATEST_URL
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = LATEST_URL
        ET.SubElement(item, "pubDate").text = format_datetime(published, usegmt=True)
        ET.SubElement(item, "description").text = LATEST["summary"]
        first = list(channel).index(items[0]) if items else len(channel)
        channel.insert(first, item)

    build = channel.find("lastBuildDate")
    if build is None:
        build = ET.SubElement(channel, "lastBuildDate")
    # Build date reflects the newest *published* entry, not the deploy time.
    all_dates = [parsedate_to_datetime(n.text) for n in channel.findall("item/pubDate") if n.text]
    build.text = format_datetime(max(all_dates).astimezone(timezone.utc), usegmt=True)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)

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
