# Verification — uv-managed review checkout, 1 November 2026

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
