# Observed-data and browser verification — 1 November 2026

Historical run record before repository cleanup. See [current verification](../VERIFICATION.md) for the uv-managed checkout.

- uv 0.13.6 installed inside project; locked Python 3.12.16 environment synchronized. No conda needed.
- 47 pytest tests passed in 0.86 seconds. One existing upstream Starlette/httpx deprecation warning remains.
- Ruff on src and tests passed.
- New notebook executed with a fresh kernel: all eight code cells executed, no error outputs. Source checksums, cohort assertions, accounting and numerical controls passed.
- HTML exported with code hidden and three embedded figures. All three PNG plots visually inspected: labels and axes legible. nbconvert reports missing alt text for three figures; captions and surrounding narrative explain them.
- 100 official source records per date; maximum absolute accounting residual $1,000, within the documented $2,000 tolerance. Fixed 30-bank baseline cohort matched to follow-up.
- Illustrative 0.3 market multiplier: observed drawdown 33.924959%; assumed asset impairment 10.177488%; modeled capital exhaustion 8/30; shortfall USD 26,607.032 million. These are conditional static scenarios, not observed defaults.
- Independent synthetic chain: 3 total defaults, 108 synthetic loss units.
- Jupyter localhost:8888 authenticated contents endpoint returned HTTP 200 for the demo notebook. Authentication retained.
- Existing synthetic-model API localhost:8000 health and OpenAPI returned HTTP 200; 12 API paths.
- Browser UI opening was denied by the browser permission gate. No browser-based end-to-end interaction check was performed; notebook execution, HTTP responses and plot inspection succeeded.

Frozen input manifest: data/manifest.json. Current output/source digests: reports/real_data_artifacts.sha256.json. The archived docs/history/2026-10-30-release-manifest.sha256.json and older verification records belong to the prior release, not this update.

## Subsequent Playwright verification
The user explicitly requested Playwright testing after the earlier browser-gate denial. The local Playwright MCP installation and seven Chromium checks now pass, including Jupyter Run All, Swagger execution, desktop/mobile and offline presentation checks. All 47 Python tests and Ruff pass again. The static HTML was repaired to remove CDN dependencies and add image descriptions. See reports/PLAYWRIGHT_QA_REPORT.md.
