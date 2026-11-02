# Atlas

Visual analytics for systemic financial contagion, with reproducible bank-capital
stress and synthetic interbank experiments.

**Current milestone: mid-term MVP, 2 November 2026.** The original research question
compares graph and matrix visualizations of systemic contagion. Atlas now includes
a local interactive dashboard displaying identical exposures and cascade rounds in
both views, backed by the verified synthetic engine. The FDIC capital-stress study
remains separate supporting context. The human visualization study is **not yet
conducted**: this repository does not establish visualization superiority or predict
historical bank failures.

## For the professor / reviewer

1. Read the [mid-term research brief](docs/MIDTERM_RESEARCH_BRIEF.md): original
   proposal versus current work, RQ, hypotheses, baselines, results and timeline.
2. Consult the [eight-paper literature review](docs/LITERATURE_REVIEW.md) and
   [demo script + Q&A](docs/MIDTERM_DEMO_AND_QA.md).
3. Run the dashboard below; inspect [notebook 04](notebooks/04_visualization_comparison.ipynb)
   or its [offline HTML](reports/visualization/04_visualization_comparison.html).
4. See the [study protocol and invitation draft](docs/VISUALIZATION_STUDY_PROTOCOL.md)
   and [notebook 05](notebooks/05_visualization_study_analysis.ipynb). No participant
   outcomes are fabricated; its empty-data result is “not evaluated.”
5. Use [notebook 03](notebooks/03_real_data_defense.ipynb) for the separate FDIC
   analysis, and [verification](docs/VERIFICATION.md) for checks and limitations.

No API keys, cloud accounts, database, or live data service are required for replay.

## Quick start with uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these
commands from your cloned repository:

```bash
uv sync --locked
uv run --locked python scripts/start_local.py
```

uv manages Python 3.12, the `.venv` environment, and the locked Python dependencies.
The default groups include development and notebook tools. No environment
activation or separate pip installation is needed. Initial installation requires
internet access; the analysis uses frozen local inputs.

The launcher prints the dashboard, authenticated Jupyter notebook URL and API documentation
URL. Keep its terminal open; **Ctrl-C stops both services**. If ports are occupied,
stop the existing services or select alternatives:

```bash
uv run --locked python scripts/start_local.py --jupyter-port 8890 --api-port 8001
```

Prefer just the dashboard? Run `uv run --locked uvicorn atlas.api:app --host 127.0.0.1 --port 8030`,
then open <http://127.0.0.1:8030/>; API docs are at <http://127.0.0.1:8030/docs>.
No frontend build or remote dashboard assets are needed.

The dark workspace opens with a graph-first view. Choose **New network** to add
banks and directed loans manually, or **Edit current network** to modify a copy
of an example. The builder previews connections, checks balance sheets and saves
your latest draft in this browser. **Use this network** validates and applies it;
canceling leaves the current simulation unchanged.

Prefer just Jupyter? Run `uv run --locked jupyter lab` and open notebook 04. See
[local setup](docs/research/LOCAL_SETUP.md) for notebook execution, export, and
separate API commands.

## What is implemented

| Workflow | Inputs | Outputs / interpretation |
| --- | --- | --- |
| Visual comparison MVP | Same synthetic dataset and loss ledger | Graph / exposure-matrix / compare modes, round replay, bank inspection, live controls, JSON export and practice-only task recorder |
| Observed bank analysis | Frozen FDIC financials, December 2019 and June 2020; fixed 30-bank baseline cohort | Reported capital-ratio changes and conditional static stress, in USD millions |
| Synthetic contagion | Seeded directed loan networks and reconciled balance sheets | Furfine-style fixed-recovery cascades, event ledger, direct-loss baseline, impact rankings, DebtRank, Monte Carlo |
| Market context | Packaged historical S&P 500 observations | Drawdown and an explicitly assumed market-to-asset impairment mapping |

Observed financial reports do **not** identify the banks' bilateral loan network.
Capital exhaustion in a hypothetical haircut is not an observed or legal default.
Loan arrows point lender to borrower; credit losses move in reverse. Synthetic
amounts use nominal INR crore unless a fixture specifies its own units.

## Reproduce and check

```bash
uv run --locked pytest -q
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
uv run --locked atlas-demo --output experiments/quick_demo
uv run --locked atlas-research --output experiments/reproduced
uv build --no-sources
```

Synthetic batch commands write fresh outputs into ignored directories. Notebook
replay writes the documented `data/processed/` tables and summary report. A minimal
runtime-only environment is available with `uv sync --locked --no-default-groups`;
include the default groups again before running tests or notebooks.

## Repository map

```text
src/atlas/       Python models, calculations, API, CLI, study analysis, and static dashboard
notebooks/      Visual comparison (04), study scaffold (05), observed data (03), synthetic studies (01–02)
tests/          Numerical controls, validation, persistence, and HTTP tests
scripts/        Local launcher, notebook authoring, export cleanup, data refresh
data/          Frozen FDIC snapshots, manifest, and processed tables
docs/          Evaluation scope, methods, setup, index, and verification
reports/        Executed presentations and saved verification evidence
experiments/    Reference synthetic experiments
browser-tests/  Optional JavaScript/Playwright QA (npm-managed)
presentation/   Earlier synthetic PowerPoint and historical authoring sources
```

Local tools, runtime tokens/logs, caches, release copies, and build outputs are
excluded by `.gitignore`. Historical evidence is labelled by date; saved source
hashes in old experiments describe the source that produced those experiments.

## Documentation

- [Mid-term research brief](docs/MIDTERM_RESEARCH_BRIEF.md), [literature review](docs/LITERATURE_REVIEW.md),
  [demo + Q&A](docs/MIDTERM_DEMO_AND_QA.md), [study protocol](docs/VISUALIZATION_STUDY_PROTOCOL.md),
  and [dashboard implementation/API](docs/VISUALIZATION_IMPLEMENTATION.md)
- [Evaluation scope and results](docs/EVALUATION.md)
- [Codebase index](docs/CODEBASE_INDEX.md) and [contributing / GitHub handoff](CONTRIBUTING.md)
- [Research and data protocol](docs/research/PROTOCOL.md)
- [Model conventions](docs/MODELS.md), [baseline methods](docs/BASELINE_METHODS.md),
  and [scientific report](docs/SCIENTIFIC_REPORT.md)
- [Data dictionary](docs/DATA_DICTIONARY.md), [market provenance](docs/DATA_PROVENANCE.md),
  and [frozen input manifest](data/manifest.json)
- [Third-party data and tooling notices](THIRD_PARTY_NOTICES.md)

The repository is prepared for academic review. No open-source code license has
been selected; public visibility alone does not grant a software license. Data
provider rights remain separate from any future code license.
