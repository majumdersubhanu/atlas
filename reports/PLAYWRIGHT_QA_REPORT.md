# Atlas Playwright and local QA report — 1 November 2026

## Outcome
PASS for the current demonstration scope. Seven browser checks, MCP smoke navigation and all 47 Python tests passed. Ruff passed. Jupyter and the API remain running on loopback.

## Installation
Plugin Management search returned no Playwright catalog entry. Microsoft @playwright/mcp 0.0.84 was installed locally in browser-tests with exact package versions and package-lock.json. Codex global MCP entry `playwright` is enabled, using /usr/bin/node and the local CLI in headless isolated mode. Chromium 157.0.8103.15 was downloaded. The OS is not officially supported by Playwright; the Ubuntu 24.04 fallback binary ran successfully. The MCP SDK client initialized the server, discovered 25 tools, and navigated through browser_navigate to the live API health endpoint. This verifies the server independently of whether an already-open Codex chat has refreshed its tool list; a new chat/restart may be needed for direct tool discovery.

Official references: https://playwright.dev/docs/getting-started-mcp and https://developers.openai.com/learn/docs-mcp . Installation followed the user request after Plugin Management discovery.

## Browser results
- PASS: Jupyter authenticated notebook loads — Authenticated notebook and rendered ATLAS content visible
- PASS: Jupyter Run All interaction — Run All triggered the final summary export; kernel returned Idle, no rendered traceback
- PASS: Jupyter browser JavaScript errors — []
- PASS: Swagger documentation and live health execution — Health endpoint executed through Swagger UI and returned ok
- PASS: Presentation desktop — Heading and 3 figures load; no page-level horizontal overflow
- PASS: Presentation mobile — Heading and 3 figures load; no page-level horizontal overflow
- PASS: Presentation offline with equations and figures — All three images embedded; equations visible without JavaScript or network

## Fixes and investigation
The initial browser harness used the pre-notebook menu label Run All; loaded Jupyter uses Run All Cells. Corrected the locator and waited for kernel readiness; the rerun reached the final summary-writing cell and returned Idle. This was a test harness issue, not a notebook calculation failure.

The HTML export relied on remote RequireJS/MathJax scripts. scripts/finalize_presentation.py now removes script dependencies from this static presentation, renders the model equation in Unicode, adds descriptive alt text for all three figures, and constrains content width. Offline Chromium verified the equation and embedded figures. Desktop 1440×1000 and mobile 390×844 have no page-level horizontal overflow. The mobile screenshot was visually reviewed.

## Remaining issues and boundaries
- API /favicon.ico returns 404; it does not affect API requests or notebook execution.
- One upstream Starlette/httpx deprecation warning remains; all tests passed.
- Browser checks cover Chromium only. No Firefox/WebKit, load, security or full accessibility audit was performed.
- This validates the software demonstration, not empirical bank-default prediction. Named-bank results are conditional capital-loss scenarios; bilateral contagion remains a separate synthetic mechanism demonstration.

## Evidence and reproduction
Workspace: repository root

Evidence: reports/browser-qa.json; reports/playwright-mcp-smoke.json; reports/playwright-mcp-tools.json; reports/jupyter-loaded.png; reports/jupyter-run-all.png; reports/swagger-health.png; reports/presentation-desktop.png; reports/presentation-mobile.png.

Commands from browser-tests: npm ci; node mcp-smoke.mjs; node qa.mjs. Start local services first with uv run --project .. --locked python ../scripts/start_local.py. The test reads the local Jupyter token file; it is not included in this report or email.

After re-exporting HTML, run uv run --locked python scripts/finalize_presentation.py from the workspace root to retain the offline fixes. Notebook 03 remains the main walkthrough. The report's static presentation is reports/03_real_data_defense.html.
