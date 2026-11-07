# ZYQ / MARKETS

A dark, responsive daily market overview with a historical archive. Designed for GitHub + GitHub Actions + Cloudflare Pages.

## Included
- S&P 500, NASDAQ Composite, Dow Jones, Russell 2000, VIX, gold futures, US Dollar Index and US 10-year yield.
- Rule-based daily context summary.
- Historical pages at `/markets/YYYY-MM-DD/`.
- Weekday scheduled GitHub Action; generated data is committed back to the repository and Cloudflare Pages deploys the commit.

## Data-source caveat
The starter uses Yahoo Finance's unofficial chart endpoint without an API key. It may be rate-limited or changed without notice, and this does not grant redistribution rights. Data may be delayed. Confirm provider terms and exchange display permissions before publishing publicly, especially for commercial use. For a commercial product, replace the provider with a licensed market-data API.

The script selects the latest candle dated before the current New York date to avoid using an in-progress daily candle. On holidays, the latest available session may be earlier than the current weekday. It refuses to publish if fewer than five instruments are fetched, preserving the last good data.

## Deploy
1. Create a GitHub repository (e.g. `zyq-markets`) and push the contents of this folder to its default branch.
2. In Cloudflare Dashboard: **Workers & Pages → Create → Pages → Connect to Git**. Select the repository.
3. Framework preset: **None**. Build command: leave blank. Build output directory: `/` (repository root).
4. Deploy, then add your custom domain such as `www.yourdomain.com` in Pages and follow its DNS instructions.
5. In GitHub, open **Actions → Daily market refresh → Run workflow**. On success, generated JSON and the dated archive page are committed. That push triggers a Cloudflare Pages deployment.

The workflow runs at 22:30 UTC, Monday-Friday. GitHub may delay scheduled jobs during high load. It can also be run manually.

## Local preview
Run `python -m http.server 8000` from the repository root and open `http://localhost:8000`. Run `python scripts/fetch_market.py` to fetch data locally.

## Customize
- Branding and copy: `index.html`
- Visual design: `assets/styles.css`
- Data rendering: `assets/app.js`
- Symbols and data provider: `scripts/fetch_market.py`
- Schedule: `.github/workflows/daily-market.yml`

Informational only; not investment advice. This starter does not provide real-time quotes or trading signals.
