#!/usr/bin/env python3
"""Fail deployment if the generated RSS feed is invalid or missing the approved latest post."""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import xml.etree.ElementTree as ET

SITE = "https://blog.sleeppathwaysguild.com"
root = ET.parse("feed.xml").getroot()
assert root.tag == "rss" and root.attrib.get("version") == "2.0", "RSS 2.0 root required"
channel = root.find("channel")
assert channel is not None, "RSS channel required"
assert channel.findtext("title") and channel.findtext("link"), "Missing channel metadata"
items = channel.findall("item")
assert items, "Empty RSS feed"
seen = set()
dates = []
for item in items:
    url = (item.findtext("link") or "").strip()
    guid = (item.findtext("guid") or "").strip()
    assert url.startswith(SITE + "/"), f"Unexpected RSS URL: {url}"
    assert guid == url and guid not in seen, f"Missing or duplicate stable GUID: {guid}"
    seen.add(guid)
    local = url[len(SITE) + 1:]
    assert ".." not in Path(local).parts, f"Invalid article path: {local}"
    target = Path(local)
    assert target.is_file() or (target / "index.html").is_file(), f"Missing published page: {local}"
    assert (item.findtext("title") or "").strip(), f"Missing title: {url}"
    assert (item.findtext("description") or "").strip(), f"Missing description: {url}"
    date = parsedate_to_datetime(item.findtext("pubDate") or "")
    assert date.tzinfo is not None, f"Missing timezone: {url}"
    dates.append(date.astimezone(timezone.utc))
build = parsedate_to_datetime(channel.findtext("lastBuildDate") or "")
assert build.tzinfo is not None and build.astimezone(timezone.utc) == max(dates), "Stale build date"
from importlib.util import spec_from_file_location, module_from_spec
# Inspect the curated script as text to avoid executing its top-level deployment mutations.
script = Path("scripts/inject-latest-post.py").read_text(encoding="utf-8")
import ast
tree = ast.parse(script)
posts = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "POSTS" for t in node.targets))
latest_url = SITE + posts[-1]["path"]
assert latest_url in seen, f"Latest approved post missing from RSS: {latest_url}"
print(f"Validated {len(items)} RSS items; latest approved post included.")
