from pathlib import Path

OFFICIAL_BADGE = "https://sleeppathwaysguild.com/assets/branding/spg-guild-badge.png"

HEAD_INSERT = f'''\n<link rel="icon" type="image/png" href="{OFFICIAL_BADGE}">\n<link rel="apple-touch-icon" href="{OFFICIAL_BADGE}">\n'''

OLD_BRAND = '<a class="brand" href="/"><strong>Sleep Pathways Guild Blog</strong><span>Sleep technology learning, practice, and professional growth</span></a>'
NEW_BRAND = f'''<a class="brand spg-brand-enhanced" href="/" aria-label="Sleep Pathways Guild Blog home"><img class="spg-brand-badge" src="{OFFICIAL_BADGE}" alt="Sleep Pathways Guild badge"><span class="spg-brand-copy"><strong>Sleep Pathways Guild Blog</strong><span>Sleep technology learning, practice, and professional growth</span></span></a>'''

for path in Path('.').rglob('*.html'):
    text = path.read_text(encoding='utf-8', errors='ignore')
    original = text

    # Remove the legacy BRPT/Blogger badge reference anywhere it remains.
    text = text.replace('/assets/blogger/badge-9316.png', OFFICIAL_BADGE)
    text = text.replace('assets/blogger/badge-9316.png', OFFICIAL_BADGE)

    # Make the official Guild badge the visible site-header badge.
    text = text.replace(OLD_BRAND, NEW_BRAND)

    # Add the shared badge styling if a page uses the enhanced header.
    if 'spg-brand-enhanced' in text and '/assets/blog-badge-brand.css' not in text:
        text = text.replace('</head>', '<link rel="stylesheet" href="/assets/blog-badge-brand.css?v=20260904-guildbadge">\n</head>', 1)

    # Explicitly override favicon / iPad home-screen artwork with the Guild badge.
    if OFFICIAL_BADGE not in text.split('</head>', 1)[0] or 'apple-touch-icon' not in text.split('</head>', 1)[0]:
        text = text.replace('</head>', HEAD_INSERT + '</head>', 1)

    if text != original:
        path.write_text(text, encoding='utf-8')
        print(f'Updated Guild badge branding: {path}')
