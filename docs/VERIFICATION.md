# Verification

## Dark workspace and manual networks — 2 November 2026

- **62 Python tests passed**, including independent manual-network accounting,
  invalid exposures, finite values and zero/negative deposit boundaries. One existing
  Starlette/httpx deprecation warning remains.
- **21 Chromium checks passed**: 13 dashboard regressions plus 8 manual-builder
  checks. See [builder evidence](../reports/visualization/manual-builder-qa.json)
  and [dashboard evidence](../reports/visualization/browser-qa.json).
- Manual construction of the teaching chain reproduces deposits **70, 50, 140**
  and cascade loss **108**. UI tests also cover self/duplicate loans, invalid account
  balances, bank removal with incident loans, cancellation, clicked connections,
  browser-local draft recovery and rejected API responses.
- Dark workspace and native builder dialog inspected at desktop and 390px mobile
  widths. [Desktop builder](../reports/visualization/manual-builder-desktop.png)
  and [mobile builder](../reports/visualization/manual-builder-mobile.png).
- Ruff lint/format pass for **31 Python files**; JavaScript syntax and diff checks pass.

The saved notebook numerical outputs below remain the preceding experiment snapshot;
their original source hashes are retained. New UI/API modules do not retroactively
change that provenance. Updated browser screenshots reflect the dark interface.
No participant study has been conducted.

## Earlier visual comparison MVP snapshot — 2 November 2026

Current local evidence for the mid-term work. These checks are software verification,
not participant observations or proof of visualization effectiveness.

| Check | Result |
| --- | --- |
| `uv run --locked pytest -q` | **56 passed**, one existing Starlette/httpx deprecation warning |
| Ruff lint and format checks | Passed; 29 Python files formatted |
| `git diff --check` | Passed |
| Fresh-kernel notebook 04 execution | Passed; hand-computed losses, recovery boundaries, branching and five matrix-edge parity cases |
| Fresh-kernel notebook 05 execution | Passed; zero participant records, explicitly “not evaluated” |
| Code-hidden HTML export | Both notebooks exported with embedded figures and no remote scripts |
| Chromium dashboard QA | **13 checks passed**; [machine-readable evidence](../reports/visualization/browser-qa.json) |
| Desktop/mobile rendering | Inspected; 1440px / 390px layouts, no page-level horizontal overflow |
| Graph/matrix controls | Isolation, same results, round trace, bank inspection, scenario controls and boundaries passed |
| Error/retry behavior | Injected API failure visible; invalid generator inputs cannot silently reuse older results |
| Downloads / practice mode | Evidence JSON valid; conditions lock and answer tables hide; automated practice exported only as rehearsal |
| API documentation | OpenAPI includes new routes; Swagger renders `/visualization` |
| Offline presentation | Both HTML reports opened offline with figures loaded |
| Dashboard dependencies | No remote HTTP requests or page JavaScript errors in the dashboard checks |
| Package build | Source archive and wheel built; all three static assets present in current 0.5.0 wheel and byte-identical to source |
| Provenance | Notebook summary's Python-source hashes match the final `src/atlas` files |
| Documentation links | New panel documentation's local links resolve |

New numerical controls independently verify the chain (direct 60, cascade 108),
branch (direct 90, cascade 180), fixed-coordinate parity and API validation. Study
analysis tests use artificial **unit-test records only**; notebook 05 contains no
fabricated people or outcomes. Automated browser answers are discarded after QA,
not added to `data/study/`.

Reports: [numerical summary](../reports/visualization/summary.json),
[engineering smoke measurements](../reports/visualization/engineering_checks.csv),
[desktop screenshot](../reports/visualization/dashboard-desktop.png),
[mobile screenshot](../reports/visualization/dashboard-mobile.png), and
[artifact manifest](../reports/visualization/artifact_manifest.json).

The payload timing values are three-repeat local engineering diagnostics including
layout and graph metrics. They are not browser-rendering or human task times and
do not compare visualization effectiveness. The teaching chain has a fixed horizontal
layout; other layouts use the documented seeded spring algorithm.

The full older notebook/browser suite was not rerun; notebooks 01–03 and frozen FDIC
inputs were preserved. CI was extended for notebooks 04/05 but was not executed on
GitHub in this work. The launcher now prints the dashboard URL and selects notebook
04 by default (`--notebook 03` retains the earlier workflow); its existing preflight
test passes, while the new API itself was exercised through HTTP and Chromium.

The formal participant runner, recruitment form publication, counterbalancing,
consent/storage workflow and human study remain future work. The practice recorder
does not satisfy those requirements. Changes are local and have not been committed,
pushed or deployed publicly.

## Earlier verification — uv-managed review checkout, 1 November 2026

## Current checks

Validation used a fresh temporary copy of the Git-visible files, with no existing
`.venv`, `.runtime`, downloaded tools, or cache directories copied into it. uv
0.13.6 created a separate Python 3.12.16 environment from the committed lockfile.
The dependency download cache was reused; this was not a network-isolated install.

| Check | Result |
| --- | --- |
| `uv sync --locked` | Resolved 119 packages; installed the project and 116 environment packages |
| `uv run --locked pytest -q` | 49 tests passed |
| `uv run --locked ruff check src tests scripts` | Passed |
| `uv run --locked ruff format --check src tests scripts` | All 23 Python files formatted |
| Fresh-kernel execution of notebooks 01, 02, and 03 | Passed; source notebooks retained, executed copies written to temporary runtime directory |
| `atlas-demo --banks 10` into a fresh output directory | Passed; scenario records and Monte Carlo CSV written |
| `atlas-research` into a fresh output directory | Passed; reproduced 14 initial / 45 total synthetic defaults in its declared main scenario |
| `uv build --no-sources` | Source distribution and wheel built successfully |
| Local launcher with alternate ports | API health and authenticated Jupyter notebook-content endpoint passed |
| Local launcher shutdown through uv | Ctrl-C stopped both services, released both ports, and removed the local authentication URL |
| Upload candidate inspection | Runtime, environments, assistant scratch folders, authenticated screenshots, builds, and archived release copies excluded; no matches in the checked credential patterns |

The launcher initially exposed a repeated-interrupt cleanup issue in integration
validation. Cleanup now ignores additional SIGINT signals while stopping its owned
children. The updated launcher passed the same startup/shutdown check.

The two added tests cover offline HTML finalization (including idempotency,
embedded-image preservation, and unexpected figure counts) and occupied-port
launcher preflight. The remaining 47 tests cover the established numerical/data/API
behavior. An existing upstream Starlette/httpx deprecation warning remains; tests
pass. This warning has not been hidden or treated as a scientific result.

## Evidence boundaries

GitHub Actions is configured in `.github/workflows/ci.yml` but has not been run on
GitHub yet. The equivalent Python checks were run locally. Browser checks from the
previous session are recorded in [the browser report](../reports/PLAYWRIGHT_QA_REPORT.md)
and [observed-data verification](research/LIVE_VERIFICATION.md); the full browser
suite was not rerun as part of this cleanup. Current launcher integration checks
use HTTP requests, not browser interaction.

Input checksums remain in `data/manifest.json`. The current saved observed-data
artifact hashes are in `reports/real_data_artifacts.sha256.json`. Earlier experiments
retain their original source hashes, timestamps, and results; module documentation
changes do not rewrite historical experiment provenance.

These checks establish implementation/reproduction behavior on the tested Linux
host. They do not validate real-world failure predictions, the assumed shock
mapping, or graph-versus-matrix superiority. Current scope is documented in
[EVALUATION.md](EVALUATION.md).

Earlier release evidence is retained under [history/](history/README.md).
