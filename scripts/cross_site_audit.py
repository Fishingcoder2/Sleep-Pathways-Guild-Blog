#!/usr/bin/env python3
"""Audit the public connection between the Sleep Pathways Guild main site and blog.

The audit treats sleeppathwaysguild.com and blog.sleeppathwaysguild.com as one
visitor journey. It verifies every sitemap URL on both hosts and checks that key
landing pages expose sensible paths between study apps, downloads, the bookstore,
topic hubs, and core Guild pages.
"""
from __future__ import annotations

import html
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

MAIN = "https://sleeppathwaysguild.com"
BLOG = "https://blog.sleeppathwaysguild.com"
SITEMAPS = (f"{MAIN}/sitemap.xml", f"{BLOG}/sitemap.xml")
OWNED_HOSTS = {"sleeppathwaysguild.com", "blog.sleeppathwaysguild.com"}
USER_AGENT = "Mozilla/5.0 (compatible; SleepPathwaysGuild-CrossSiteAudit/1.0; +https://sleeppathwaysguild.com/)"

CRITICAL_ROUTES = {
    "Guild home": f"{MAIN}/",
    "CPSGT webapp": f"{MAIN}/cpsgt-study-app.html",
    "RPSGT webapp": f"{MAIN}/RPSGTv2.2026.html",
    "EKG lab": f"{MAIN}/ekg.2026.html",
    "Flashcards": f"{MAIN}/flashcards.2026.html",
    "About": f"{MAIN}/about/",
    "Contact": f"{MAIN}/contact/",
    "Blog home": f"{BLOG}/",
    "Blog archive": f"{BLOG}/archive/",
    "Downloads": f"{BLOG}/downloads/",
    "Book store": f"{BLOG}/p/rpsgt-exam-prep-book-store.html",
    "RPSGT topic hub": f"{BLOG}/topics/rpsgt-exam-prep/",
    "CPSGT topic hub": f"{BLOG}/topics/cpsgt-exam-prep/",
    "Scoring topic hub": f"{BLOG}/topics/sleep-scoring-practice/",
    "PSG artifact topic hub": f"{BLOG}/topics/psg-artifact-recognition/",
    "PAP topic hub": f"{BLOG}/topics/pap-titration-troubleshooting/",
}

# These are visitor-experience expectations, not hard deployment requirements.
# Missing items are warnings so an existing navigation gap does not break deploys.
NAV_EXPECTATIONS = {
    f"{MAIN}/": {
        "blog": f"{BLOG}/",
        "downloads": f"{BLOG}/downloads/",
        "CPSGT": f"{MAIN}/cpsgt-study-app.html",
        "RPSGT": f"{MAIN}/RPSGTv2.2026.html",
        "EKG": f"{MAIN}/ekg.2026.html",
        "about": f"{MAIN}/about/",
        "contact": f"{MAIN}/contact/",
    },
    f"{BLOG}/": {
        "main site": f"{MAIN}/",
        "CPSGT": f"{MAIN}/cpsgt-study-app.html",
        "RPSGT": f"{MAIN}/RPSGTv2.2026.html",
        "archive": f"{BLOG}/archive/",
        "downloads": f"{BLOG}/downloads/",
        "book store": f"{BLOG}/p/rpsgt-exam-prep-book-store.html",
    },
    f"{BLOG}/downloads/": {
        "blog home": f"{BLOG}/",
    },
    f"{BLOG}/p/rpsgt-exam-prep-book-store.html": {
        "blog home": f"{BLOG}/",
        "main site": f"{MAIN}/",
    },
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        values = {str(k).lower(): (v or "") for k, v in attrs}
        href = values.get("href", "").strip()
        if href:
            self.hrefs.append(href)


def request(url: str, *, want_body: bool = False, timeout: float = 18.0) -> tuple[int | None, str, str, bytes]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf,*/*;q=0.8",
    }
    methods = ("GET",) if want_body else ("HEAD", "GET")
    for method in methods:
        try:
            req = urllib.request.Request(url, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read(4_000_000) if want_body or method == "GET" else b""
                return response.status, response.geturl(), response.headers.get("Content-Type", ""), body
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {400, 403, 405, 406, 501}:
                continue
            return exc.code, exc.geturl() or url, str(exc.reason or "HTTP error"), b""
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            if method == "HEAD":
                continue
            return None, url, str(getattr(exc, "reason", exc)), b""
    return None, url, "request failed", b""


def fetch_sitemap(url: str) -> tuple[list[str], str | None]:
    status, final_url, meta, body = request(url, want_body=True)
    if status is None or status >= 400:
        return [], f"{url}: could not fetch sitemap ({status or 'ERR'} {meta})"
    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        return [], f"{url}: invalid XML ({exc})"
    urls = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "loc" and node.text and node.text.strip():
            urls.append(node.text.strip())
    return urls, None


def normalized(url: str) -> str:
    parsed = urllib.parse.urlsplit(html.unescape(url.strip()))
    path = parsed.path or "/"
    return urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, ""))


def links_from(page_url: str, body: bytes) -> set[str]:
    parser = LinkParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    result: set[str] = set()
    for href in parser.hrefs:
        raw = html.unescape(href.strip())
        if not raw or raw.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        absolute = urllib.parse.urljoin(page_url, raw)
        parsed = urllib.parse.urlparse(absolute)
        if parsed.scheme in {"http", "https"}:
            result.add(normalized(absolute))
    return result


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    sitemap_urls: dict[str, list[str]] = {}

    for sitemap in SITEMAPS:
        urls, problem = fetch_sitemap(sitemap)
        sitemap_urls[sitemap] = urls
        if problem:
            errors.append(problem)

    all_urls = list(dict.fromkeys(url for urls in sitemap_urls.values() for url in urls))
    status_rows: list[str] = []
    for url in all_urls:
        code, final_url, reason, _ = request(url)
        host = urllib.parse.urlparse(final_url).netloc.lower()
        if code is None:
            warnings.append(f"UNVERIFIED {url}: {reason}")
            status_rows.append(f"[CHECK] ERR | {url}")
        elif code >= 400:
            errors.append(f"HTTP {code}: {url} -> {final_url}")
            status_rows.append(f"[FAIL] {code} | {url}")
        elif host not in OWNED_HOSTS:
            warnings.append(f"OWNED URL redirected off-site: {url} -> {final_url}")
            status_rows.append(f"[CHECK] {code} | {url} -> {final_url}")
        else:
            status_rows.append(f"[OK] {code} | {url}")

    critical_rows: list[str] = []
    for label, url in CRITICAL_ROUTES.items():
        code, final_url, reason, _ = request(url)
        if code is None:
            warnings.append(f"Critical route unverified: {label} | {url} ({reason})")
            critical_rows.append(f"[CHECK] {label} | {url}")
        elif code >= 400:
            errors.append(f"Critical route HTTP {code}: {label} | {url}")
            critical_rows.append(f"[FAIL] {label} | {url}")
        else:
            critical_rows.append(f"[OK] {label} | {url}")

    nav_rows: list[str] = []
    for page, expected in NAV_EXPECTATIONS.items():
        code, final_url, meta, body = request(page, want_body=True)
        if code is None or code >= 400:
            warnings.append(f"Could not inspect navigation on {page} ({code or 'ERR'} {meta})")
            nav_rows.append(f"[CHECK] {page}: navigation not inspected")
            continue
        links = links_from(final_url, body)
        for label, destination in expected.items():
            dest = normalized(destination)
            if dest in links:
                nav_rows.append(f"[OK] {page} -> {label}: {destination}")
            else:
                warnings.append(f"Navigation gap: {page} has no direct link to {label} ({destination})")
                nav_rows.append(f"[GAP] {page} -> {label}: {destination}")

    # Confirm that both properties are represented in the combined sitemap set.
    main_count = sum(1 for u in all_urls if urllib.parse.urlparse(u).netloc.lower() == "sleeppathwaysguild.com")
    blog_count = sum(1 for u in all_urls if urllib.parse.urlparse(u).netloc.lower() == "blog.sleeppathwaysguild.com")
    if main_count == 0 or blog_count == 0:
        errors.append("Combined sitemap audit did not include URLs from both Guild hosts.")
    else:
        notes.append(f"Main-site sitemap URLs: {main_count}")
        notes.append(f"Blog sitemap URLs: {blog_count}")
        notes.append(f"Combined owned URLs checked: {len(all_urls)}")

    report_lines = [
        "Sleep Pathways Guild cross-site audit",
        f"Main site: {MAIN}",
        f"Blog: {BLOG}",
        *notes,
        f"Errors: {len(errors)}",
        f"Warnings / navigation gaps: {len(warnings)}",
        "",
        "CRITICAL ROUTES",
        *critical_rows,
        "",
        "NAVIGATION MATRIX",
        *nav_rows,
        "",
        "SITEMAP URL STATUS",
        *status_rows,
        "",
        "ERRORS",
        *(f"- {item}" for item in errors),
        "",
        "WARNINGS / MANUAL REVIEW",
        *(f"- {item}" for item in warnings),
        "",
    ]
    report = "\n".join(report_lines)
    Path("cross-site-audit-report.txt").write_text(report, encoding="utf-8")
    print(report)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
