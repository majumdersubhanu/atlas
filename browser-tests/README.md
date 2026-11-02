# Optional browser verification

## Current visualization dashboard

Start `uv run --locked uvicorn atlas.api:app --host 127.0.0.1 --port 8030`.
With the existing npm dependencies installed, run from the repository root:

```bash
node browser-tests/dashboard.mjs
node browser-tests/manual-builder.mjs
```

Override `ATLAS_BASE_URL` if needed. The script writes browser QA and screenshots
under `reports/visualization/`, checks the two executed offline notebook exports,
and never treats its automated practice answers as participant observations.
The manual-builder suite checks creation, accounting validation, deletion, cancel,
canvas connections, local draft recovery and responsive dialog behavior. It uses a
fresh browser context; its saved draft does not touch your browser's draft.
Run `uv run --locked python scripts/export_visualization_report.py` after notebook
execution to regenerate those exports. The earlier workflows below are separate.

This is JavaScript tooling, managed with npm independently of the uv-managed
Python project. It is not required to read the notebooks or run numerical tests.

From the repository root, leave `uv run --locked python scripts/start_local.py --notebook 03`
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
