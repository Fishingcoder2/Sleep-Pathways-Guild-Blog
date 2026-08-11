#!/usr/bin/env python3
"""Audit Sleep Pathways Guild Blog links and assets.

The local pass scans every HTML file in the repository for internal href/src
references, missing files, and fragment targets. The live pass checks sitemap
pages plus every web URL referenced by the HTML. Broken Guild-owned URLs fail
CI; third-party access blocks and failures are reported for manual review so a
vendor outage does not stop a deployment.
"""
from __future__ import annotations

import argparse
import html
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

SKIP_SCHEMES = ("mailto:", "tel:", "sms:", "javascript:", "data:", "blob:")
USER_AGENT = (
    "Mozilla/5.0 (compatible; SleepPathwaysGuild-BlogLinkAudit/1.0; "
    "+https://blog.sleeppathwaysguild.com/)"
)
GUILD_HOSTS = {"blog.sleeppathwaysguild.com", "sleeppathwaysguild.com", "www.sleeppathwaysguild.com"}


@dataclass
class ParsedHTML:
    refs: list[tuple[str, str]] = field(default_factory=list)
    ids: set[str] = field(default_factory=set)


class RefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.data = ParsedHTML()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {str(k).lower(): (v or "") for k, v in attrs}
        ident = attr.get("id", "").strip()
        if ident:
            self.data.ids.add(ident)
        name = attr.get("name", "").strip()
        if tag.lower() == "a" and name:
            self.data.ids.add(name)

        tag = tag.lower()
        if tag in {"a", "link"} and attr.get("href", "").strip():
            self.data.refs.append(("href", attr["href"].strip()))
        if tag in {"img", "script", "iframe", "source", "video", "audio", "track", "embed", "input"}:
            if attr.get("src", "").strip():
                self.data.refs.append(("src", attr["src"].strip()))
        if tag in {"img", "source"} and attr.get("srcset", "").strip():
            for item in attr["srcset"].split(","):
                candidate = item.strip().split(" ", 1)[0]
                if candidate:
                    self.data.refs.append(("srcset", candidate))


def read_html(path: Path) -> ParsedHTML:
    parser = RefParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser.data


def load_sitemap(root: Path) -> list[str]:
    path = root / "sitemap.xml"
    if not path.exists():
        return []
    tree = ET.parse(path)
    return [
        node.text.strip()
        for node in tree.getroot().iter()
        if node.tag.rsplit("}", 1)[-1] == "loc" and node.text and node.text.strip()
    ]


def site_path_to_file(root: Path, path: str) -> Path | None:
    path = urllib.parse.unquote(path or "/").split("?", 1)[0]
    rel = path.lstrip("/")
    candidates: list[Path] = []
    if not rel:
        candidates.append(root / "index.html")
    else:
        direct = root / rel
        candidates.append(direct)
        if path.endswith("/"):
            candidates.append(direct / "index.html")
        elif not Path(rel).suffix:
            candidates.extend([root / f"{rel}.html", direct / "index.html"])
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    return None


def normalize_local_target(
    root: Path, source: Path, ref: str, site_host: str
) -> tuple[Path | None, str]:
    raw = html.unescape(ref.strip())
    if not raw or raw.startswith(SKIP_SCHEMES):
        return None, ""
    parsed = urllib.parse.urlparse(raw)
    fragment = urllib.parse.unquote(parsed.fragment)
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc.lower() != site_host:
            return None, fragment
        return site_path_to_file(root, parsed.path), fragment
    if parsed.scheme or raw.startswith("//"):
        return None, fragment
    if not parsed.path:
        return source.resolve(), fragment
    if parsed.path.startswith("/"):
        return site_path_to_file(root, parsed.path), fragment

    candidate = (source.parent / urllib.parse.unquote(parsed.path)).resolve()
    if candidate.exists() and candidate.is_file():
        return candidate, fragment
    if candidate.exists() and candidate.is_dir() and (candidate / "index.html").exists():
        return (candidate / "index.html").resolve(), fragment
    if not candidate.suffix:
        html_candidate = candidate.with_suffix(".html")
        if html_candidate.exists():
            return html_candidate.resolve(), fragment
        index_candidate = candidate / "index.html"
        if index_candidate.exists():
            return index_candidate.resolve(), fragment
    return None, fragment


def local_audit(root: Path, site_url: str) -> tuple[list[str], list[str], set[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    web_urls: set[str] = set()
    host = urllib.parse.urlparse(site_url).netloc.lower()
    html_files = [p for p in root.rglob("*.html") if ".git" not in p.parts]
    parsed_cache: dict[Path, ParsedHTML] = {}

    for source in html_files:
        try:
            page = parsed_cache.setdefault(source.resolve(), read_html(source))
        except OSError as exc:
            errors.append(f"{source.relative_to(root)}: could not read HTML ({exc})")
            continue
        for kind, ref in page.refs:
            raw = html.unescape(ref.strip())
            if not raw or raw.startswith(SKIP_SCHEMES):
                continue
            parsed = urllib.parse.urlparse(raw)
            if parsed.scheme in {"http", "https"} and parsed.netloc.lower() != host:
                web_urls.add(urllib.parse.urldefrag(raw)[0])
                continue
            if raw.startswith("//"):
                web_urls.add(urllib.parse.urldefrag("https:" + raw)[0])
                continue
            target, fragment = normalize_local_target(root, source, raw, host)
            if target is None:
                if parsed.scheme:
                    continue
                errors.append(f"{source.relative_to(root)}: missing internal {kind} target -> {raw}")
                continue
            if fragment and target.suffix.lower() in {".html", ".htm"}:
                try:
                    target_page = parsed_cache.setdefault(target, read_html(target))
                except OSError:
                    continue
                if fragment not in target_page.ids:
                    warnings.append(
                        f"{source.relative_to(root)}: fragment #{fragment} not found in "
                        f"{target.relative_to(root)}"
                    )

    sitemap_urls = load_sitemap(root)
    for url in sitemap_urls:
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc.lower() == host and site_path_to_file(root, parsed.path) is None:
            errors.append(f"sitemap.xml: URL has no matching local page -> {url}")

    return errors, warnings, web_urls, len(html_files)


def auth_redirect(source: str, destination: str) -> bool:
    src = urllib.parse.urlparse(source)
    dest = urllib.parse.urlparse(destination)
    if src.netloc.lower() == dest.netloc.lower():
        return False
    host = dest.netloc.lower()
    path = dest.path.lower()
    if host in {"accounts.google.com", "login.microsoftonline.com"}:
        return True
    return any(token in path for token in ("/signin", "/login", "/auth/"))


def http_probe(url: str, timeout: float = 15.0) -> tuple[int | None, str, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/pdf,image/*,*/*;q=0.8",
    }
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status, response.geturl(), ""
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {400, 403, 405, 406, 501}:
                continue
            return exc.code, exc.geturl() or url, str(exc.reason or "HTTP error")
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            if method == "HEAD":
                continue
            return None, url, str(getattr(exc, "reason", exc))
    return None, url, "request failed"


def live_audit(site_url: str, sitemap_urls: list[str], web_urls: set[str]) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    check_urls = set(sitemap_urls)
    check_urls.update(web_urls)
    # Always verify the three highest-value blog entry points.
    check_urls.update(
        {
            site_url.rstrip("/") + "/",
            site_url.rstrip("/") + "/downloads/",
            site_url.rstrip("/") + "/p/rpsgt-exam-prep-book-store.html",
        }
    )

    for idx, url in enumerate(sorted(check_urls), start=1):
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc.lower()
        if parsed.scheme not in {"http", "https"}:
            continue
        status, final_url, reason = http_probe(url)
        owned = host in GUILD_HOSTS
        redirected_to_auth = status is not None and status < 400 and auth_redirect(url, final_url)

        if redirected_to_auth:
            warnings.append(f"AUTH REDIRECT: {url} -> {final_url}")
        elif status is None:
            warnings.append(f"UNVERIFIED: {url} ({reason})")
        elif status in {401, 403, 429}:
            warnings.append(f"ACCESS {status}: {url} -> {final_url}")
        elif status >= 400:
            if owned:
                errors.append(f"OWNED {status}: {url} -> {final_url}")
            else:
                warnings.append(f"EXTERNAL {status}: {url} -> {final_url}")

        if idx % 20 == 0:
            time.sleep(0.2)

    return errors, warnings, len(check_urls)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--site-url", default="https://blog.sleeppathwaysguild.com")
    ap.add_argument("--report", default="link-audit-report.txt")
    ap.add_argument("--live", action="store_true", help="Also check sitemap and all referenced web URLs")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    site_url = args.site_url.rstrip("/")
    local_errors, local_warnings, web_urls, html_count = local_audit(root, site_url)
    sitemap_urls = load_sitemap(root)

    live_errors: list[str] = []
    live_warnings: list[str] = []
    live_count = 0
    if args.live:
        live_errors, live_warnings, live_count = live_audit(site_url, sitemap_urls, web_urls)

    errors = [*local_errors, *live_errors]
    warnings = [*local_warnings, *live_warnings]
    lines = [
        "Sleep Pathways Guild Blog link audit",
        f"Site: {site_url}",
        f"Local HTML files checked: {html_count}",
        f"Sitemap URLs: {len(sitemap_urls)}",
        f"Referenced external/other-site URLs found: {len(web_urls)}",
        f"Live URLs checked: {live_count}",
        f"Errors: {len(errors)}",
        f"Warnings / manual verification: {len(warnings)}",
        "",
        "ERRORS",
        *(f"- {item}" for item in errors),
        "",
        "WARNINGS / MANUAL VERIFICATION",
        *(f"- {item}" for item in warnings),
        "",
    ]
    report = "\n".join(lines)
    Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
