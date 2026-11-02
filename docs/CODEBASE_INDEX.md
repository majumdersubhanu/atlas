# Atlas codebase index

## Visual comparison additions — 2 November 2026

The current panel entry point is [MIDTERM_RESEARCH_BRIEF.md](MIDTERM_RESEARCH_BRIEF.md).
The existing observed-data and synthetic modules below remain the numerical foundation.

| Addition | Role |
| --- | --- |
| `src/atlas/manual.py`, `POST /networks/manual` | Validated manual bank/loan builder with residual deposits and explicit accounting errors |
| `static/builder.js`, `static/workbench.css` | Dark graph-first workspace, draft editor, connection preview and local draft recovery |
| `src/atlas/visualization.py` | Three-/six-bank fixtures, stable graph coordinates, shared matrix/cascade/control payload |
| `src/atlas/static/` | Local dashboard: graph, matrix, round replay, inspection, live scenario controls, evidence export and practice recorder |
| `src/atlas/study.py` | Eligible-study validation and per-task paired descriptive summaries; no participants yet |
| `GET /`, `GET /fixtures/{name}`, `POST /visualization` | Dashboard and documented comparison API |
| `notebooks/04_visualization_comparison.ipynb` | Executed numerical and visual-evidence comparisons |
| `notebooks/05_visualization_study_analysis.ipynb` | Empty-data-safe study analysis scaffold |
| `scripts/build_visualization_notebooks.py` | Authors notebooks 04/05; overwrites those notebooks, not needed for replay |
| `scripts/export_visualization_report.py` | Code-hidden offline HTML with embedded plots |
| `tests/test_visualization.py`, `tests/test_study.py` | New parity/arithmetic/API and analysis controls |
| `browser-tests/dashboard.mjs` | Browser interactions, responsive views, downloads and offline report checks |
| `data/study/`, `reports/visualization/` | Empty schema; saved MVP numerical/browser evidence |

See [implementation](VISUALIZATION_IMPLEMENTATION.md) and [study protocol](VISUALIZATION_STUDY_PROTOCOL.md).
The launcher now opens notebook 04 and prints the dashboard URL. The following is
the earlier source index, retained for navigation of the financial foundation.

Updated 1 November 2026 from the current workspace. This is a navigation map of the active source tree; archived releases, environments, caches, and generated artifacts are not separate implementations.

## Start here

- [Current evaluation scope](EVALUATION.md), [development and GitHub handoff](../CONTRIBUTING.md), and [third-party notices](../THIRD_PARTY_NOTICES.md).

- [README](../README.md): project overview and reproduction commands.
- [Notebook 03](../notebooks/03_real_data_defense.ipynb): current observed-data research presentation, using a fixed FDIC bank cohort and conditional capital stress.
- [Notebook 01](../notebooks/01_atlas_pipeline.ipynb): introductory synthetic network pipeline.
- [Notebook 02](../notebooks/02_research_experiments.ipynb): extended synthetic experiments.
- [Local setup](research/LOCAL_SETUP.md), [research protocol](research/PROTOCOL.md), and [current verification](research/LIVE_VERIFICATION.md).

## Runtime and entry points

Python package `atlas` lives in `src/atlas`; project `atlas-risk` is version 0.5.0 and requires Python 3.12. [pyproject.toml](../pyproject.toml) declares dependencies and entry points; `uv.lock` pins the environment. Main libraries are Pydantic, NumPy, pandas, NetworkX, and FastAPI.

| Entry point | Implementation | Purpose |
| --- | --- | --- |
| `atlas-demo` | [cli.py](../src/atlas/cli.py), `main` | Generate a network, compare market-shock mappings, save experiments and Monte Carlo trials |
| `atlas-research` | [research.py](../src/atlas/research.py), `main` → `run` | Batch synthetic research, rankings, baseline, sensitivity, ensembles, provenance manifest |
| `uvicorn atlas.api:app` | [api.py](../src/atlas/api.py) | Synthetic-model HTTP service; Swagger at `/docs` |
| `uv run --locked python scripts/start_local.py` | [start_local.py](../scripts/start_local.py) | Foreground Jupyter/API launcher; Ctrl-C stops both services |

## Source modules and symbols

| Module | Responsibility and primary symbols |
| --- | --- |
| [models.py](../src/atlas/models.py) | `StrictModel`, `Bank`, `Exposure`, `Dataset`, `Scenario`, `GenerateRequest`. Rejects extra fields/nonfinite values; validates exposure endpoints, uniqueness, and balance-sheet reconciliation. |
| [generate.py](../src/atlas/generate.py) | `generate`: seeded core-periphery, random, or scale-free networks; constructs loans before reconciling balance sheets. |
| [engine.py](../src/atlas/engine.py) | `credit_risk`: loan PD × LGD × EAD; `bank_risk`: balance sheets, losses, concentration; `furfine`: synchronous default cascade and event ledger; `debt_rank`: one-active-step distress propagation; `monte_carlo`: independent sampled initial defaults. |
| [baseline.py](../src/atlas/baseline.py) | `direct_loss_only`: comparison without repeated default propagation. |
| [analysis.py](../src/atlas/analysis.py) | `exposure_matrix`, `graph_metrics`, `impact_ranking`, `monte_carlo_summary`, `topology_ensemble`: descriptive network measurements and conditional scenario comparisons. |
| [market.py](../src/atlas/market.py) | `market_data`: packaged S&P 500 observations; `calibration`: selected-window drawdown mapped to assumed impairment. |
| [observed.py](../src/atlas/observed.py) | `load_snapshot`: FDIC fields, eligibility and units; `cohort`: fixed baseline cohort with left-joined follow-up; `stress`: static equity loss; `checksum`: input SHA-256. |
| [storage.py](../src/atlas/storage.py) | `dataset_hash`, `experiment`, `save_experiment`, `read_dataset`, `export_dataset`: JSON/CSV persistence with source hashes and runtime metadata. |
| [api.py](../src/atlas/api.py) | FastAPI application; `SimulationRequest`, `DebtRankRequest`, `MonteCarloRequest`; HTTP wrappers over the synthetic engine and analysis. |
| [cli.py](../src/atlas/cli.py), [research.py](../src/atlas/research.py) | Command-line orchestration of the modules above. |
| [__init__.py](../src/atlas/__init__.py) | Package description and `__version__`. |

## Data flow and conventions

Synthetic workflow: `generate` → validated `Dataset` + `Scenario` → engine/baseline → analysis → storage/CSV/JSON. CLI, research runner, notebooks, and API orchestrate these modules. `market.calibration` supplies an illustrative shock assumption from real market observations.

Observed workflow: frozen FDIC JSON → `observed.load_snapshot` → `observed.cohort` → `observed.stress` → notebook 03 tables, figures, and reports. The observed workflow is exposed through Python/notebook 03, not the synthetic API.

- Loans point **lender → borrower**; credit losses propagate in reverse. Exposure matrices use lender rows and borrower columns.
- Synthetic amounts use nominal INR crore. FDIC source amounts are USD thousands; modeled observed monetary outputs are USD millions.
- Furfine defaults occur at equity ≤ 0. Each defaulted borrower transmits once; losses are posted only to creditors alive at the start of the round.
- Observed capital exhaustion uses `E' = E − impairment × assets`; it does not establish legal default. Observed bilateral exposures and historical default probabilities are not inferred.
- DebtRank measures conditional distress; generator-family comparisons do not isolate causal topology effects.

## HTTP routes

All routes below are implemented in [api.py](../src/atlas/api.py).

| Method | Routes | Functionality |
| --- | --- | --- |
| GET | `/health`, `/market` | Service status; packaged market observations and calibration |
| POST | `/generate`, `/validate` | Synthetic dataset generation and validation |
| POST | `/credit`, `/simulate`, `/baseline` | Expected credit losses, cascade, direct-loss comparison |
| POST | `/debt-rank`, `/monte-carlo` | Distress propagation and conditional sampling |
| POST | `/network-metrics`, `/impact-ranking` | Graph descriptors and forced-default ranking |
| POST | `/experiments` | Simulate and save an experiment under `experiments/` |

## Scripts and supporting folders

| Path | Contents / purpose |
| --- | --- |
| [scripts/fetch_observed.py](../scripts/fetch_observed.py) | Explicit online FDIC refresh; requires `--output`. Keep frozen inputs stable for replay. |
| [scripts/build_evaluation.py](../scripts/build_evaluation.py) | Authors notebook 03 and the input manifest. **Overwrites authored notebook edits**; use Run All for normal replay. |
| [scripts/finalize_presentation.py](../scripts/finalize_presentation.py) | Post-processes exported presentation HTML, removing remote script dependencies and adding figure descriptions. |
| `src/atlas/data/` | Packaged market CSV, metadata, and demo network fixtures. |
| `data/raw/`, `data/manifest.json` | Frozen 2019-12-31 and 2020-06-30 FDIC snapshots, field definitions, and source checksums. |
| `data/processed/` | Cohort, scenario results, sensitivity, and market mapping tables. |
| `experiments/` | Saved synthetic runs; `research/` and `final/` hold experiment tables/manifests. |
| `reports/` | Executed HTML notebooks, figures, summary JSON, and browser QA evidence. |
| `presentation/` | JavaScript deck builders, evidence JSON, and PowerPoint artifact. |
| `browser-tests/` | Playwright QA (`qa.mjs`), inspection (`inspect.mjs`), and MCP smoke checks (`mcp-smoke.mjs`). |
| `dist/`, `releases/` | Built distributions and historical release copies. |
| `.runtime/`, `.venv/` | Local runtime state and installed environment; not application source. |

## Tests and verification commands

| Test file | Coverage area |
| --- | --- |
| [test_engine.py](../tests/test_engine.py) | Generation/accounting, validation, hand-calculated credit/cascades, recovery boundaries, market calibration, DebtRank, Monte Carlo, persistence, API |
| [test_audit.py](../tests/test_audit.py) | Derived-value overflow rejection and loss-event reconciliation |
| [test_baseline.py](../tests/test_baseline.py) | Direct loss versus cascade, initial failures, shock and boundary handling |
| [test_analysis.py](../tests/test_analysis.py) | Graph direction/matrix, impact ranking, Monte Carlo summary, ensemble reproducibility |
| [test_observed.py](../tests/test_observed.py) | Stress arithmetic/boundary, snapshot units/missing/duplicate data, fixed-cohort follow-up |
| [test_tooling.py](../tests/test_tooling.py) | Offline export idempotency, figure preservation, and occupied-port launcher preflight |
| [test_scientific_api.py](../tests/test_scientific_api.py) | Exploratory/analysis/baseline endpoint behavior and validation |

Run from the repository root after installing the locked environment:

```bash
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check src tests scripts
```

Notebook execution and browser QA regenerate artifacts; follow [local setup](research/LOCAL_SETUP.md) for those workflows and required servers.

## Methods and evidence references

- [MODELS.md](MODELS.md): exact model conventions.
- [SCIENTIFIC_REPORT.md](SCIENTIFIC_REPORT.md): synthetic methods, design, evidence, limitations.
- [BASELINE_METHODS.md](BASELINE_METHODS.md): established methods and baseline.
- [DATA_DICTIONARY.md](DATA_DICTIONARY.md), [DATA_PROVENANCE.md](DATA_PROVENANCE.md): fields and historical market provenance.
- [CLAIMS_AND_EVIDENCE.md](CLAIMS_AND_EVIDENCE.md): scope of supported claims.
- [implementation_plan.md](../implementation_plan.md), [todo.md](../todo.md): recorded plan and progress.

For changes, start with the relevant module and its matching test file above. Refresh this map when entry points, modules, routes, or data workflows change.
