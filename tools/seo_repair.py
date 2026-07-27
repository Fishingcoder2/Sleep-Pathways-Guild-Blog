#!/usr/bin/env python3
"""Repair analytics and technical SEO across the static blog migration."""

from __future__ import annotations

import html
import json
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://blog.sleeppathwaysguild.com/"
SITE_NAME = "Sleep Pathways Guild Blog"
PUBLISHER = "Sleep Pathways Guild"
AUTHOR = "Tracy Frazier, RHIT, RPSGT, CCS-P"
GA_ID = "G-MZTRYT67VG"
AHREFS_KEY = "/s9HvK+nlfPasBLtcJ6y3A"
DEFAULT_IMAGE = "https://sleeppathwaysguild.com/assets/branding/spg-guild-badge.png"
TODAY = date.today().isoformat()
START = "<!-- SPG SEO START -->"
END = "<!-- SPG SEO END -->"

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value, flags=re.S)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def attr_escape(value: str) -> str:
    return html.escape(value, quote=True)


def get_title(text: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", text, re.I | re.S)
    return clean_text(match.group(1)) if match else SITE_NAME


def get_description(text: str, title: str) -> str:
    patterns = [
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
        r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']\s*/?>',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            value = clean_text(match.group(1))
            if value:
                return value[:300]
    post = re.search(r'<div\s+class=["\']post-content["\'][^>]*>(.*?)</div>', text, re.I | re.S)
    if post:
        value = clean_text(post.group(1))
        if value:
            return value[:300]
    return f"{title}. Sleep technology education and RPSGT study support from Sleep Pathways Guild."


def canonical_for(path: Path, text: str) -> str:
    match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']\s*/?>', text, re.I | re.S)
    if match:
        return match.group(1).strip()
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return BASE_URL
    if rel.endswith("/index.html"):
        return urljoin(BASE_URL, rel[:-10])
    return urljoin(BASE_URL, rel)


def published_date(path: Path, text: str) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    path_match = re.match(r"(\d{4})/(\d{2})/", rel)
    date_match = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})\b",
        text,
        re.I,
    )
    if date_match:
        month = MONTHS[date_match.group(1).lower()]
        try:
            return date(int(date_match.group(3)), month, int(date_match.group(2))).isoformat()
        except ValueError:
            pass
    if path_match:
        return f"{path_match.group(1)}-{path_match.group(2)}-01"
    return None


def git_lastmod(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", rel],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if result:
            return result[:10]
    except (OSError, subprocess.CalledProcessError):
        pass
    return TODAY


def page_kind(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if re.match(r"\d{4}/\d{2}/.+\.html$", rel):
        return "post"
    if rel == "index.html":
        return "home"
    if rel == "404.html":
        return "error"
    if "archive" in rel:
        return "collection"
    return "page"


def structured_data(kind: str, title: str, description: str, canonical: str, published: str | None) -> dict | list[dict]:
    organization = {
        "@type": "Organization",
        "@id": "https://sleeppathwaysguild.com/#organization",
        "name": PUBLISHER,
        "url": "https://sleeppathwaysguild.com/",
        "logo": {"@type": "ImageObject", "url": DEFAULT_IMAGE},
    }
    if kind == "home":
        return [
            {"@context": "https://schema.org", **organization},
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "@id": f"{BASE_URL}#website",
                "url": BASE_URL,
                "name": SITE_NAME,
                "description": description,
                "publisher": {"@id": organization["@id"]},
            },
        ]
    if kind == "post":
        data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "headline": title,
            "description": description,
            "url": canonical,
            "image": [DEFAULT_IMAGE],
            "author": {"@type": "Person", "name": AUTHOR},
            "publisher": organization,
        }
        if published:
            data["datePublished"] = published
            data["dateModified"] = published
        return data
    schema_type = "CollectionPage" if kind == "collection" else "WebPage"
    return {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@id": f"{BASE_URL}#website"},
        "publisher": organization,
    }


def seo_block(path: Path, text: str) -> tuple[str, dict]:
    title = get_title(text)
    description = get_description(text, title)
    canonical = canonical_for(path, text)
    kind = page_kind(path)
    published = published_date(path, text)
    robots = "noindex,nofollow" if kind == "error" else "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"
    og_type = "article" if kind == "post" else "website"
    schema = structured_data(kind, title, description, canonical, published)

    lines = [
        START,
        f'<meta name="robots" content="{robots}">',
        f'<meta name="author" content="{attr_escape(AUTHOR)}">',
        f'<link rel="canonical" href="{attr_escape(canonical)}">',
        '<link rel="alternate" type="application/rss+xml" title="Sleep Pathways Guild Blog RSS" href="https://blog.sleeppathwaysguild.com/feed.xml">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{attr_escape(title)}">',
        f'<meta property="og:description" content="{attr_escape(description)}">',
        f'<meta property="og:url" content="{attr_escape(canonical)}">',
        f'<meta property="og:image" content="{DEFAULT_IMAGE}">',
        '<meta property="og:image:alt" content="Sleep Pathways Guild badge">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{attr_escape(title)}">',
        f'<meta name="twitter:description" content="{attr_escape(description)}">',
        f'<meta name="twitter:image" content="{DEFAULT_IMAGE}">',
        '<script async src="https://www.googletagmanager.com/gtag/js?id=G-MZTRYT67VG"></script>',
        '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-MZTRYT67VG");</script>',
        f'<script src="https://analytics.ahrefs.com/analytics.js" data-key="{AHREFS_KEY}" async></script>',
        '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + '</script>',
        END,
    ]
    return "\n".join(lines) + "\n", {
        "path": path,
        "title": title,
        "description": description,
        "canonical": canonical,
        "kind": kind,
        "published": published,
    }


def remove_duplicate_head_tags(text: str) -> str:
    text = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\s*", "", text, flags=re.S)
    # The replacement block is authoritative for these tags.
    patterns = [
        r'<meta\s+name=["\']robots["\'][^>]*>\s*',
        r'<meta\s+name=["\']author["\'][^>]*>\s*',
        r'<link\s+rel=["\']canonical["\'][^>]*>\s*',
        r'<link\s+rel=["\']alternate["\'][^>]*application/(?:rss|atom)\+xml[^>]*>\s*',
        r'<meta\s+property=["\']og:[^"\']+["\'][^>]*>\s*',
        r'<meta\s+name=["\']twitter:[^"\']+["\'][^>]*>\s*',
        r'<script\s+async\s+src=["\']https://www\.googletagmanager\.com/gtag/js\?id=G-MZTRYT67VG["\']\s*></script>\s*',
        r'<script[^>]*>\s*window\.dataLayer\s*=.*?gtag\(["\']config["\']\s*,\s*["\']G-MZTRYT67VG["\']\s*\);?\s*</script>\s*',
        r'<script\s+src=["\']https://analytics\.ahrefs\.com/analytics\.js["\'][^>]*></script>\s*',
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.I | re.S)
    return text


def fix_imported_article_body(path: Path, text: str) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel != "2026/05/common-pap-failures-sleep-technologist.html":
        return text
    pattern = r'(<div\s+class=["\']post-content["\'][^>]*>)(.*?)(</div>\s*</article>)'
    match = re.search(pattern, text, re.I | re.S)
    if not match:
        return text
    inner = match.group(2)
    style_pos = re.search(r"<style\b", inner, re.I)
    if style_pos and re.search(r"<(?:html|head|title|meta)\b", inner[: style_pos.start()], re.I):
        inner = inner[style_pos.start():]
    replacement = match.group(1) + inner + match.group(3)
    return text[: match.start()] + replacement + text[match.end():]


def update_html(path: Path) -> dict:
    original = path.read_text(encoding="utf-8", errors="replace")
    text = fix_imported_article_body(path, original)
    text = remove_duplicate_head_tags(text)
    block, record = seo_block(path, text)
    head = re.search(r"<head\b[^>]*>", text, re.I)
    if not head:
        print(f"SKIP no <head>: {path.relative_to(ROOT)}")
        return record
    text = text[: head.end()] + "\n" + block + text[head.end():]
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"UPDATED {path.relative_to(ROOT)}")
    return record


def write_404() -> None:
    path = ROOT / "404.html"
    if path.exists():
        return
    path.write_text(
        """<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Page Not Found | Sleep Pathways Guild Blog</title><meta name=\"description\" content=\"The requested Sleep Pathways Guild Blog page could not be found.\"></head><body><main style=\"max-width:760px;margin:4rem auto;padding:1.5rem;font-family:system-ui,sans-serif\"><h1>That trail ends here.</h1><p>The page may have moved during the blog migration.</p><p><a href=\"/\">Return to the blog</a> · <a href=\"/archive/\">Browse all articles</a> · <a href=\"https://sleeppathwaysguild.com/\">Visit the Guild home page</a></p></main></body></html>\n""",
        encoding="utf-8",
    )


def write_sitemap(records: list[dict]) -> None:
    rows = []
    for record in sorted(records, key=lambda item: item["canonical"]):
        if record["kind"] == "error":
            continue
        lastmod = git_lastmod(record["path"])
        rows.append(
            "  <url><loc>" + xml_escape(record["canonical"]) + "</loc><lastmod>" + lastmod + "</lastmod></url>"
        )
    output = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"
    (ROOT / "sitemap.xml").write_text(output, encoding="utf-8")


def write_feed(records: list[dict]) -> None:
    posts = [record for record in records if record["kind"] == "post"]
    posts.sort(key=lambda item: item["published"] or "", reverse=True)
    updated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    items = []
    for record in posts[:20]:
        pub = record["published"] or TODAY
        items.append(
            "  <item>\n"
            f"    <title>{xml_escape(record['title'])}</title>\n"
            f"    <link>{xml_escape(record['canonical'])}</link>\n"
            f"    <guid isPermaLink=\"true\">{xml_escape(record['canonical'])}</guid>\n"
            f"    <pubDate>{pub}T12:00:00Z</pubDate>\n"
            f"    <description>{xml_escape(record['description'])}</description>\n"
            "  </item>"
        )
    output = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>\n'
        f"  <title>{SITE_NAME}</title>\n"
        f"  <link>{BASE_URL}</link>\n"
        "  <description>Sleep technology education, RPSGT exam preparation, scoring review, EKG learning, and professional growth.</description>\n"
        f"  <lastBuildDate>{updated}</lastBuildDate>\n"
        + "\n".join(items)
        + "\n</channel></rss>\n"
    )
    (ROOT / "feed.xml").write_text(output, encoding="utf-8")


def main() -> None:
    write_404()
    html_files = sorted(
        path for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and "node_modules" not in path.parts
    )
    records = [update_html(path) for path in html_files]
    write_sitemap(records)
    write_feed(records)
    robots = "User-agent: *\nAllow: /\nSitemap: https://blog.sleeppathwaysguild.com/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print(f"Processed {len(records)} HTML files.")


if __name__ == "__main__":
    main()
