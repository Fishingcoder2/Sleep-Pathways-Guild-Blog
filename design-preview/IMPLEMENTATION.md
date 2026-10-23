# RSS and homepage refresh: review checklist

This branch is a **non-production concept**. The current root index.html, existing articles, feed.xml, sitemap.xml, deployment workflow, and public redirects remain unchanged.

## Findings
- The repository already includes feed.xml and the homepage already advertises it with a rel=alternate link.
- The committed feed's lastBuildDate is 2026-10-11, so it may be missing newer published articles.
- GitHub Actions deploy-pages.yml deploys the repository root from main using GitHub Pages. Do not assume Cloudflare Pages deploys the blog.
- The current deploy pipeline runs scripts/inject-latest-post.py, which may mutate listings during deployment. Inspect it before integrating a generator.

## Proposed production implementation (not yet implemented)
1. Determine the canonical approved/published article inventory and source metadata; do not infer approval merely from the presence of an HTML file.
2. Generate RSS 2.0 and homepage cards from that inventory, with stable GUIDs, canonical URLs, escaped XML, RFC 2822 pubDate, valid lastBuildDate, and no drafts.
3. Add a feed validation check that fails if the feed is invalid, stale relative to the approved published inventory, contains duplicate GUIDs, or links to missing posts.
4. Integrate generation before GitHub Pages artifact upload; avoid deployment-only changes that diverge from the committed feed without a clear ownership model.
5. Verify navigation, mobile accessibility, focus states, contrast, article links, structured metadata, and existing search indexing.
6. Test Facebook Page integration with a single approved new article only after feed verification; deduplicate by GUID and require editorial approval before publication.
7. Preserve all existing post URLs and redirect behavior. No migration to Astro/Jekyll is proposed for this initial pass.

## Acceptance criteria
- Existing public URLs remain unchanged.
- RSS is valid and includes all and only approved published articles.
- New articles update RSS without manual editing.
- No accidental re-sharing of old posts.
- No changes to the live site until the PR is reviewed and merged.
