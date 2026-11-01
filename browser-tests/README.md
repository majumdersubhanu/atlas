# Optional browser verification

This is JavaScript tooling, managed with npm independently of the uv-managed
Python project. It is not required to read the notebooks or run numerical tests.

From the repository root, leave `uv run --locked python scripts/start_local.py`
running in another terminal on the default ports. Then:

```bash
cd browser-tests
npm ci
npx playwright install chromium
npm run qa
npm run smoke
```

`qa` checks authenticated Jupyter, Run All, Swagger, and desktop/mobile/offline
HTML presentation behavior. It writes evidence under `reports/` and regenerates
notebook-derived outputs. `smoke` checks the Playwright MCP tool surface against
the local API. `inspect` captures Jupyter UI state for diagnosis.

The authentication URL is read from ignored `.runtime/jupyter_url.txt`. Keep logs
and authenticated screenshots local. Existing QA reports record previous runs;
a Python-only CI pass does not imply a new browser QA pass.
