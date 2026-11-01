# Atlas

Reproducible bank capital stress and synthetic interbank contagion experiments.

**Current milestone: academic evaluation, 2 November 2026.** Atlas combines a
conditional capital-stress study of public FDIC financial reports with a separately
verified synthetic contagion engine. The original graph-versus-matrix user study
is future work; this repository does not establish visualization superiority or
predict historical bank failures.

## For the professor / reviewer

1. Read the [evaluation brief](docs/EVALUATION.md) for the question, scope, results,
   and a ten-minute walkthrough.
2. Open [notebook 03](notebooks/03_real_data_defense.ipynb) to inspect the analysis
   and saved outputs directly on GitHub.
3. Download [the executed HTML presentation](reports/03_real_data_defense.html)
   and open it locally for an offline, code-hidden version with embedded figures.
4. Follow the [codebase index](docs/CODEBASE_INDEX.md) to inspect implementation
   and tests, or [verification record](docs/VERIFICATION.md) for recorded checks.

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

The launcher prints the authenticated Jupyter notebook URL and the API documentation
URL. Keep its terminal open; **Ctrl-C stops both services**. If ports are occupied,
stop the existing services or select alternatives:

```bash
uv run --locked python scripts/start_local.py --jupyter-port 8890 --api-port 8001
```

Prefer just Jupyter? Run `uv run --locked jupyter lab` and open notebook 03. See
[local setup](docs/research/LOCAL_SETUP.md) for notebook execution, export, and
separate API commands.

## What is implemented

| Workflow | Inputs | Outputs / interpretation |
| --- | --- | --- |
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
src/atlas/       Python models, calculations, analysis, API, CLI, and provenance
notebooks/      Current observed-data presentation (03), earlier synthetic studies (01–02)
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
