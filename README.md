# Sleep Pathways Guild Blog

Static GitHub Pages site for `blog.sleeppathwaysguild.com`.

- Preserves established article and page URL paths where available
- Uses the repository-root `index.html` as the homepage
- Keeps the custom domain in `CNAME`
- Uses `.nojekyll` so the static files are published without a Jekyll build
- Normalizes Amazon Associates tracking to `spg_rpsgt-20`

## Deployment

The workflow at `.github/workflows/deploy-pages.yml` publishes the repository root to GitHub Pages after every push to `main` and can also be run manually from the Actions tab.

In repository **Settings → Pages**, the publishing source must be set to **GitHub Actions**. The custom domain should remain `blog.sleeppathwaysguild.com` with HTTPS enforcement enabled after DNS validation.

After a deployment, verify the homepage, topic hubs, downloads, bookstore, `robots.txt`, and `sitemap.xml` on the public domain.
