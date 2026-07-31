from pathlib import Path

EDITORIAL_PATH = "/2026/07/shift-report-growing-sleep-tech-newsroom.html"

HOME_CARD = (
    '<article class="card" data-spg-post="shift-report-editorial">'
    '<div class="meta">July 30, 2026</div>'
    '<h2>The Shift Report Is Growing: A Sleep-Tech Newsroom Takes Shape</h2>'
    '<p class="summary">A founder editorial on how The Shift Report is becoming a practical newsroom for sleep technologists, expanding free CEC coverage, strengthening editorial standards, and preparing to move closer to Sleep Pathways Guild.</p>'
    f'<a class="read" href="{EDITORIAL_PATH}">Read article</a>'
    '</article>'
)

ARCHIVE_CARD = (
    '<article class="card" data-spg-post="shift-report-editorial">'
    '<div class="meta">July 30, 2026</div>'
    f'<h2><a href="{EDITORIAL_PATH}">The Shift Report Is Growing: A Sleep-Tech Newsroom Takes Shape</a></h2>'
    '</article>'
)


def prepend_card(path: str, card: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")

    if EDITORIAL_PATH in text:
        return

    marker = '<section class="wrap grid">'
    if marker not in text:
        raise RuntimeError(f"Could not find article-grid marker in {path}")

    text = text.replace(marker, marker + card, 1)
    file_path.write_text(text, encoding="utf-8")


prepend_card("index.html", HOME_CARD)
prepend_card("archive/index.html", ARCHIVE_CARD)
print("Shift Report editorial added to homepage and archive listings.")
