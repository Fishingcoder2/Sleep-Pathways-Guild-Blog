#!/usr/bin/env python3
"""Add verified official, scholarly, and disclosed affiliate links to blog references."""

from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
POST_GLOB = "20[0-9][0-9]/*/*.html"
AFFILIATE_TAG = "spg_rpsgt-20"
START = "<!-- SPG LINKED REFERENCES START -->"
END = "<!-- SPG LINKED REFERENCES END -->"


def amazon_search(title: str) -> str:
    return f"https://www.amazon.com/s?k={quote_plus(title)}&tag={AFFILIATE_TAG}"


BOOKS = (
    (r"\bFundamentals of Sleep Technology\b", "Fundamentals of Sleep Technology", "Fundamentals of Sleep Technology"),
    (r"\bPolysomnography for the Sleep Technologist\b", "Polysomnography for the Sleep Technologist", "Polysomnography for the Sleep Technologist"),
    (r"\bSleep Medicine Pearls\b", "Sleep Medicine Pearls", "Sleep Medicine Pearls"),
    (r"\bPediatric Sleep Medicine Pearls\b", "Pediatric Sleep Medicine Pearls", "Pediatric Sleep Medicine Pearls"),
    (r"\bA Clinical Guide to Pediatric Sleep\b", "A Clinical Guide to Pediatric Sleep", "A Clinical Guide to Pediatric Sleep"),
    (r"\bFundamentals for Sleep Professionals\b", "Fundamentals for Sleep Professionals", "Fundamentals for Sleep Professionals"),
    (r"\bFundamentals of Sleep Medicine\b", "Fundamentals of Sleep Medicine", "Fundamentals of Sleep Medicine"),
    (r"\bPrinciples and Practice of Sleep Medicine\b", "Principles and Practice of Sleep Medicine", "Principles and Practice of Sleep Medicine"),
    (r"\bRPSGT Scoring Mastery\b", "RPSGT Scoring Mastery", "RPSGT Scoring Mastery"),
)

OFFICIAL = (
    (
        r"AASM (?:Manual for the Scoring|Scoring Manual)|The AASM manual for the scoring|current AASM scoring manual",
        "AASM Scoring Manual — official page",
        "https://aasm.org/clinical-resources/scoring-manual/",
        "Use the current version followed by your facility.",
    ),
    (
        r"International Classification of Sleep Disorders|\bICSD-3(?:-TR)?\b",
        "International Classification of Sleep Disorders — official AASM page",
        "https://aasm.org/clinical-resources/international-classification-sleep-disorders/",
        "Official source for current edition information.",
    ),
    (
        r"RPSGT Candidate Handbook|RPSGT Handbook",
        "BRPT RPSGT Candidate Handbook",
        "https://brpt.org/rpsgt/rpsgt-handbook/",
        "Official candidate requirements and exam information.",
    ),
    (
        r"RPSGT Exam Blueprint|BRPT blueprint|current exam blueprint",
        "BRPT RPSGT Exam Blueprint",
        "https://brpt.org/rpsgt/exam-blueprint/",
        "Official exam-domain outline.",
    ),
    (
        r"RPSGT Exam References|BRPT (?:primary )?references",
        "BRPT RPSGT Exam References",
        "https://brpt.org/rpsgt/exam-prep/references/",
        "Official BRPT reference list.",
    ),
    (
        r"AAST:? Technical Guidelines|AAST technical guidelines|PAP Titration Technical Guideline",
        "AAST Technical Guidelines",
        "https://aastweb.org/clinical-resources/technical-guidelines/",
        "Official technical-guideline collection.",
    ),
    (
        r"AASM:? Clinical Practice Guidelines|AASM practice guidelines",
        "AASM Clinical Practice Guidelines",
        "https://aasm.org/clinical-resources/practice-standards/practice-guidelines/",
        "Official guideline collection.",
    ),
    (
        r"AAST.*Scope of Practice|Scope of Practice for Sleep Technologists",
        "AAST Sleep Technologist Scope of Practice",
        "https://aastweb.org/career/scope-of-practice/",
        "Official professional scope resource.",
    ),
)

# References whose original citations are incomplete or are not reliably identifiable are
# linked to a PubMed search rather than silently assigning the wrong article.
POST_SPECIFIC = {
    "2026/05/common-pap-failures-sleep-technologist.html": [
        ("Aloia, Arnedt, Stanchina & Millman — PAP adherence citation", "https://pubmed.ncbi.nlm.nih.gov/?term=Aloia+Arnedt+Stanchina+Millman+PAP+adherence", "PubMed author/topic search for the citation as written."),
        ("Bachour & Maasilta (2004) — Mouth breathing and nasal CPAP adherence", "https://pubmed.ncbi.nlm.nih.gov/15486389/", "PubMed record."),
        ("Budhiraja et al. (2007) — Early CPAP use and subsequent adherence", "https://pubmed.ncbi.nlm.nih.gov/17425228/", "PubMed record."),
        ("Javaheri, Smith & Chung — Prevalence and natural history of complex sleep apnea", "https://pubmed.ncbi.nlm.nih.gov/?term=The+prevalence+and+natural+history+of+complex+sleep+apnea", "PubMed title search."),
        ("Morgenthaler et al. — Complex sleep apnea syndrome", "https://pubmed.ncbi.nlm.nih.gov/?term=Complex+sleep+apnea+syndrome+is+it+a+unique+clinical+syndrome", "PubMed title search."),
        ("Rotenberg, Murariu & Pang (2016) — Trends in CPAP adherence", "https://doi.org/10.1186/s40463-016-0156-0", "Publisher DOI link."),
        ("Sawyer et al. (2011) — Systematic review of CPAP adherence", "https://pubmed.ncbi.nlm.nih.gov/?term=A+systematic+review+of+CPAP+adherence+across+age+groups", "PubMed title search."),
        ("Weaver & Grunstein (2008) — CPAP adherence challenge", "https://pubmed.ncbi.nlm.nih.gov/18250209/", "PubMed record."),
    ],
    "2026/05/when-sleep-tech-cant-stay-awake.html": [
        ("AASM circadian rhythm and shift-work education package", "https://learn.aasm.org/Listing/AASM-Circadian-Rhythm-Sleep-Wake-Disorders-Lecture-Package-On-Demand-4018", "Includes the cited Circadian Adaptation to Shift Work provider fact sheet."),
    ],
    "2026/05/where-path-leads-sleep-pathways-guild.html": [
        ("BRPT — About the RPSGT Credential and certification statistics", "https://brpt.org/rpsgt/about-the-rpsgt-credential/", "Official credential statistics."),
        ("AAST — Sleep Technologist Scope of Practice", "https://aastweb.org/career/scope-of-practice/", "Official professional source."),
        ("U.S. Bureau of Labor Statistics — Employment Projections 2024–2034", "https://www.bls.gov/news.release/ecopro.nr0.htm", "Official federal projections."),
        ("U.S. Bureau of Labor Statistics — Healthcare Occupations", "https://www.bls.gov/ooh/healthcare/home.htm", "Official Occupational Outlook Handbook overview."),
        ("Zippia — Sleep Technologist careers and jobs", "https://www.zippia.com/sleep-technologist-jobs/", "Career-site source named in the article."),
        ("LinkedIn — Sleep Technologist jobs", "https://www.linkedin.com/jobs/sleep-technologist-jobs/", "Job-posting source named in the article."),
    ],
}


def visible_text(source: str) -> str:
    body = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->", " ", source, flags=re.I | re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", html.unescape(body))


def remove_block(source: str) -> str:
    return re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\s*", "", source, flags=re.S)


def add_entry(entries: list[tuple[str, str, str, str]], seen: set[str], label: str, url: str, note: str, kind: str) -> None:
    if url in seen:
        return
    seen.add(url)
    entries.append((label, url, note, kind))


def build_block(entries: list[tuple[str, str, str, str]]) -> str:
    has_affiliate = any(kind == "affiliate" for _, _, _, kind in entries)
    lines = [
        START,
        '<section class="spg-linked-references" id="linked-references" aria-labelledby="linked-references-heading" style="margin:2rem 0;padding:1.15rem 1.25rem;border:1px solid #c9dedb;border-radius:16px;background:#f4fbfa;color:#102f32;">',
        '<h2 id="linked-references-heading" style="margin:.1rem 0 .65rem;">Linked references &amp; resources</h2>',
        '<p style="margin:.25rem 0 1rem;">Official sources are prioritized. Book links open Amazon search results so readers can compare available editions.</p>',
    ]
    if has_affiliate:
        lines.append('<p class="spg-affiliate-disclosure" style="margin:.5rem 0 1rem;padding:.75rem;border-left:4px solid #b47b12;background:#fff8e7;"><strong>Affiliate disclosure:</strong> As an Amazon Associate I earn from qualifying purchases. Book links marked “paid link” may generate a commission at no additional cost to you.</p>')
    lines.append('<ul style="margin:.5rem 0;padding-left:1.3rem;">')
    for label, url, note, kind in entries:
        if kind == "affiliate":
            rel = "nofollow sponsored noopener"
            suffix = ' <strong>(paid link)</strong>'
        else:
            rel = "noopener"
            suffix = ""
        lines.append(f'<li style="margin:.55rem 0;"><a href="{html.escape(url, quote=True)}" target="_blank" rel="{rel}">{html.escape(label)}</a>{suffix}<br><small>{html.escape(note)}</small></li>')
    lines.extend(["</ul>", "</section>", END])
    return "\n".join(lines) + "\n"


def insert_block(source: str, block: str, path: Path) -> str:
    marker = "</div></article>"
    pos = source.rfind(marker)
    if pos < 0:
        raise SystemExit(f"Could not locate article-content closing marker: {path}")
    return source[:pos] + "\n" + block + source[pos:]


def process(path: Path) -> bool:
    original = path.read_text(encoding="utf-8", errors="replace")
    source = remove_block(original)
    text = visible_text(source)
    existing_urls = set(re.findall(r'href=["\']([^"\']+)["\']', source, flags=re.I))
    entries: list[tuple[str, str, str, str]] = []
    seen = set(existing_urls)

    for pattern, label, search_title in BOOKS:
        if re.search(pattern, text, re.I):
            add_entry(entries, seen, f"{label} — view available editions on Amazon", amazon_search(search_title), "Verify the title, author, and edition before purchasing.", "affiliate")

    for pattern, label, url, note in OFFICIAL:
        if re.search(pattern, text, re.I):
            add_entry(entries, seen, label, url, note, "official")

    rel = path.relative_to(ROOT).as_posix()
    for label, url, note in POST_SPECIFIC.get(rel, []):
        add_entry(entries, seen, label, url, note, "scholarly")

    if entries:
        source = insert_block(source, build_block(entries), path)

    if source != original:
        path.write_text(source, encoding="utf-8")
        print(f"UPDATED {rel}: {len(entries)} links")
        return True
    return False


def update_store_disclosure() -> bool:
    path = ROOT / "p/rpsgt-exam-prep-book-store.html"
    original = path.read_text(encoding="utf-8", errors="replace")
    source = re.sub(
        r'<div class="notice"><strong>Affiliate disclosure:</strong>.*?</div>',
        '<div class="notice"><strong>Affiliate disclosure:</strong> As an Amazon Associate I earn from qualifying purchases. Links marked as Amazon links are paid affiliate links and may generate a commission at no additional cost to you.</div>',
        original,
        count=1,
        flags=re.I | re.S,
    )
    if source != original:
        path.write_text(source, encoding="utf-8")
        print("UPDATED bookstore affiliate disclosure")
        return True
    return False


def main() -> None:
    changed = sum(process(path) for path in sorted(ROOT.glob(POST_GLOB)))
    changed += int(update_store_disclosure())
    print(f"Reference-link update completed; changed {changed} files.")


if __name__ == "__main__":
    main()
