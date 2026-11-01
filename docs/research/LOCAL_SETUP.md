# Local setup and reproduction

Run commands from the repository root. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
first. uv selects Python 3.12 from `.python-version`, creates `.venv`, and installs
`uv.lock` exactly. The tested uv version is 0.13.6; the project requires at least
that version.

```bash
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
uv run --locked python scripts/start_local.py
```

The default dependency groups are `dev` and `notebook`. All Python tools run through
uv; no shell activation, conda, global Jupyter installation, or credentials are
needed. Initial dependency installation needs internet access. Frozen data permit
offline replay after setup (`uv run --offline --locked ...`).

## Run the presentation

The launcher owns Jupyter and the synthetic API, prints their URLs, and waits in
the terminal. Ctrl-C stops both child services. It binds to `127.0.0.1` and keeps
Jupyter token authentication. Logs and the local authenticated URL live under
ignored `.runtime/`; do not share that folder. Occupied ports produce an error
instead of attaching to an unrelated server. Choose alternatives if needed:

```bash
uv run --locked python scripts/start_local.py --jupyter-port 8890 --api-port 8001
```

For separate terminals:

```bash
uv run --locked jupyter lab --no-browser --ip=127.0.0.1 --port=8888
uv run --locked uvicorn atlas.api:app --host 127.0.0.1 --port 8000
```

Open `notebooks/03_real_data_defense.ipynb` and Run All. Notebooks 01 and 02 are
earlier synthetic studies. The API serves synthetic models; the observed-data
study is available through Python and notebook 03.

## Execute and export

```bash
uv run --locked jupyter nbconvert --to notebook --execute --inplace notebooks/03_real_data_defense.ipynb
uv run --locked jupyter nbconvert --to html --no-input notebooks/03_real_data_defense.ipynb --output-dir reports
uv run --locked python scripts/finalize_presentation.py
```

Notebook execution updates `data/processed/` and `reports/real_data_summary.json`.
Export replaces the HTML report. The finalizer removes remote scripts and adds
figure descriptions for the current three-figure presentation. Download the HTML
and open it locally; GitHub's source view does not render it as a website.

## Synthetic batch reproduction

```bash
uv run --locked atlas-demo --output experiments/quick_demo
uv run --locked atlas-research --output experiments/reproduced
```

Both output directories are ignored, leaving reference runs intact. Saved records
include runtime versions and source/data hashes; timestamps and run identifiers
are not expected to match older run records byte for byte.

## Data refresh and notebook authoring

The frozen input manifest is `data/manifest.json`. An explicit online refresh must
use a new directory:

```bash
uv run --locked python scripts/fetch_observed.py --output data-refresh
```

Audit field definitions, units, eligibility, joins, and provider terms before
adopting refreshed data. A refresh changes the data vintage; do not commit it as
though it were the original frozen input.

`uv run --locked python scripts/build_evaluation.py` is an **authoring command**:
it overwrites notebook 03 and rebuilds its input manifest. It is not needed for
ordinary setup, replay, or rehearsal. Preserve any notebook edits before using it.

## Optional browser QA

Python dependencies are uv-managed. Playwright and the MCP smoke client are
JavaScript tooling and use the separate `browser-tests/package-lock.json`:

```bash
cd browser-tests
npm ci
npx playwright install chromium
npm run qa
```

Start the local launcher in another terminal first, using the default ports.
The QA suite executes notebook cells and writes screenshots/results. It reads the
ignored authentication URL locally. See [browser tooling](../../browser-tests/README.md).

## Troubleshooting

- `uv: command not found`: finish the uv installation and open a new terminal.
- Lockfile mismatch: use the committed `pyproject.toml` and `uv.lock` together;
  `uv lock` intentionally changes the lockfile and belongs in dependency updates.
- Missing notebook or test tools after a minimal install: run `uv sync --locked`.
- Ports occupied: stop the previous launcher in its terminal or choose new ports.
- A kernel from another environment: launch Jupyter using the uv command above.
