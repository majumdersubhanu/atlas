# Visual comparison MVP: implementation, data and decisions

## Run locally

From the repository root, after `uv sync --locked`:

```bash
uv run --locked uvicorn atlas.api:app --host 127.0.0.1 --port 8000
```

- Dashboard: <http://127.0.0.1:8000/>
- Swagger API documentation: <http://127.0.0.1:8000/docs>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>
- Jupyter separately: `uv run --locked jupyter lab`, then open notebook 04.

The existing `scripts/start_local.py` starts Jupyter and this same API together. It opens notebook 04 by default; use `--notebook 03` for the earlier FDIC workflow. Its printed dashboard link uses the selected API port. No frontend build, API key, remote font or CDN library is required. Initial dependency installation requires internet; normal demo calculation uses local assets. Swagger's default documentation assets may require internet even though the dashboard does not; the OpenAPI JSON and exported notebook remain available locally.

## Architecture and design choices

### Dark workspace and manual builder (2 November update)

The default view is now a compact dark, graph-first workspace. Matrix and Compare
remain available; optional practice tasks are collapsed. **New network** opens a
native dialog with bank inputs, directed-loan editing, a clickable preview and
live balance-sheet checks. **Edit current network** clones any displayed fixture
or generated network into a draft. IDs stay stable while names and values can change.

Add 2–50 banks with external assets and positive equity. Connect them with a lender,
borrower and positive amount; clicking two preview nodes fills the same fields.
Edit or delete loans, or remove a bank and its connected loans. Removing a bank is
explicitly labeled as removing those connections. No graph edits affect the active
simulation until **Use this network** succeeds. Cancel and Escape preserve it.

`POST /networks/manual` accepts `ManualNetworkRequest` from `src/atlas/manual.py`.
It aggregates outgoing loans into interbank assets and incoming loans into borrowing,
then calculates deposits as `external_assets + lending − borrowing − equity`.
Negative deposits, self-loans, duplicate directed pairs, missing endpoints,
nonfinite values and invalid counts are rejected. External assets and equity are
never silently adjusted. Zero deposits and isolated banks are allowed. This is a
synthetic balance-sheet construction convention, not an empirical funding estimate.

The new network starts in the existing scenario controls; inspect the selected
initial failure, recovery and impairment before interpreting the result. Each
manual network uses the same graph/matrix evidence path and cascade engine as the
fixtures. The independent manual-chain test reproduces deposits 70/50/140 and
posted cascade loss 108.

Drafts auto-save under `atlas.manual-draft.v1` in localStorage when edited. **Resume
draft** restores the last edited draft, including one canceled before applying.
This is one local draft per browser origin, not a network library or server database;
another port/browser has separate storage. If storage is blocked, a visible message
says the draft is in memory only. Applied networks can be downloaded through the
existing evidence JSON export. The builder is disabled during practice tasks.

New frontend files are `static/builder.js` and `static/workbench.css`. The bank/loan
editor is tested in Chromium at desktop and mobile widths. Run
`node browser-tests/manual-builder.mjs` alongside the existing dashboard checks.

`Browser (HTML/CSS/JS) → FastAPI → validated Dataset + Scenario → existing engine / baseline → shared visual payload → graph + matrix + ledger`.

- `src/atlas/visualization.py`: hand-checkable fixtures and common presentation payload.
- `src/atlas/static/`: responsive frontend; native SVG graph and HTML matrix.
- `src/atlas/api.py`: serves assets and adds two documented visual-comparison endpoints.
- `src/atlas/study.py`: future participant-data validation and paired descriptive summaries.
- `notebooks/04_visualization_comparison.ipynb`: numerical/representation experiments.
- `notebooks/05_visualization_study_analysis.ipynb`: empty-data-safe analysis scaffold.

Native SVG/HTML was chosen for a small dependable local demo; it reuses FastAPI and avoids introducing a Node build pipeline or cloud dependency. This is a deliberate reduction from the original React/TypeScript/D3 proposal. A production frontend can later consume the same payload. No database or authentication layer is added to this local-only MVP.

### New routes

| Route | Input | Output / errors |
| --- | --- | --- |
| `GET /` | None | Dashboard HTML |
| `GET /static/...` | Packaged static path | CSS/JS assets |
| `GET /fixtures/{name}` | `chain` or `branch` | Validated synthetic dataset; unknown name → 404 |
| `POST /visualization` | `{dataset, scenario}` using existing schema | Dataset hash, graph positions, original exposure matrix, cascade rounds/events, direct baseline, network descriptors; invalid scenario/dataset or >80 banks → 422 |

Existing `/generate`, `/simulate`, `/baseline`, `/credit`, `/market`, `/debt-rank`, `/monte-carlo`, `/network-metrics`, `/impact-ranking` and `/experiments` remain available. `/health` still identifies the synthetic-network service. No API route treats FDIC reports as observed bilateral exposures.

Example request using the Python environment:

```python
import httpx
base = "http://127.0.0.1:8000"
dataset = httpx.get(f"{base}/fixtures/chain").json()
response = httpx.post(f"{base}/visualization", json={
    "dataset": dataset,
    "scenario": {"initial_defaults": ["B"], "recovery": 0.4, "external_impairment": 0},
})
response.raise_for_status()
evidence = response.json()
assert evidence["cascade"]["interbank_loss"] == 108
```

## Data description and assumptions

| Data | Source | Use | Boundary |
| --- | --- | --- | --- |
| 3-bank chain / 6-bank branch | Authored fixtures in `visualization.py` | Independent arithmetic; demo | Fictional, units labeled `synthetic teaching units` |
| Generated networks | Existing seeded `generate.py` | Scale/shape exploration | Nominal synthetic INR crore; not fitted to banks |
| Frozen FDIC 2019-12-31 / 2020-06-30 | Existing `data/raw`, checksums in manifest | Notebook 03 capital-stress context | Source USD thousands → model USD millions; no bilateral network |
| S&P 500 observations | Existing packaged CSV and provenance | Illustrative shock magnitude | Market-to-bank impairment multiplier assumed |
| Study CSV | Future eligible consenting participants | Visualization outcomes | Empty template now; practice/test rows excluded |

No raw financial inputs were refreshed. Teaching loans are not inferred from correlations. Every bank starts with positive equity and reconciles assets to deposits, borrowing and equity. A loan is an asset of the lender and liability of the borrower. Losses flow in the reverse direction. Fixed recovery, zero-equity threshold and survivor-only loss accounting match [MODELS.md](MODELS.md).

## Algorithms and exact visual semantics

1. **Validate:** reuse Pydantic Dataset and Scenario validators; reject inconsistent accounts, invalid endpoints and nonfinite values.
2. **Simulate:** apply external haircut once; propagate fixed-LGD losses synchronously from newly failed borrowers; stop at no new failures. Reuse the engine without modifying its economics.
3. **Control:** independently run direct-loss-only with identical starting accounts and scenario.
4. **Matrix:** `M[lender, borrower] = original exposure amount`; diagonal and absent loans are zero. Every bank, including isolates, has a row/column.
5. **Layout:** the three-bank teaching chain uses fixed horizontal C→A→B positions for legibility; other networks use NetworkX spring layout with `seed=42`, `weight=None`, 100 iterations. Coordinates depend only on input topology and node order, not recovery, impairment, or displayed round. They are not geographic locations or financial distances. Formal study stimuli need their own frozen layout specification.
6. **Render:** graph widths and matrix intensity encode original loan amounts; states come from the same default-round map. Current-round loss events highlight the corresponding **loan**, whose arrow still points lender→borrower. The ledger explicitly names the opposite loss direction. Exact values remain available; zero cells use an em dash.
7. **Replay:** slider steps through engine snapshots; play advances at 1.2-second intervals for illustration. This interval is not economic time and is not an animation performance claim.
8. **Inspect:** select a bank through the graph, matrix cell (its lender), or common selector. Display starting/current equity and account values. Selection highlights; it does not remove exposures from computation.
9. **Export:** JSON includes the shared evidence, dataset fingerprint, scenario, selected representation and displayed round. No new scientific result is created by changing view.

The graph draws both directions of reciprocal loans as separated curves. Labels are limited on larger graphs to reduce overlap; exact values remain in titles/tooltips and the matrix. This is not a tested optimal layout. The UI supports up to 50 generated banks; the comparison endpoint caps inputs at 80. Larger networks, detailed collision handling, zoom/pan and scalable rendering remain future work.

## Practice recorder

Choose one representation, select lookup or secondary-failure task, and start. Controls lock; both-view switching and shared answer tables hide. Timing uses `performance.now()` from task presentation to submission, then exports CSV with correctness, duration, confidence, dataset hash, scenario, viewport and `record_type=rehearsal`. Records stay in memory in the browser tab until downloaded; closing the tab loses them. No personal details are requested or uploaded.

This recorder has no formal counterbalancing, study allocation, authenticated storage, timeout protocol or browser-visibility handling. The client holds the answer, and its response timing is not tamper-proof. These are accepted **rehearsal** limitations; it must not be used as the final research collector without the gates in the study protocol.

## Verification and reproducibility

```bash
uv run --locked pytest -q
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
uv run --locked jupyter nbconvert --to notebook --execute notebooks/04_visualization_comparison.ipynb --inplace
uv run --locked jupyter nbconvert --to notebook --execute notebooks/05_visualization_study_analysis.ipynb --inplace
```

Notebook 04 writes fresh results under `reports/visualization/`. Notebook 05 has no human outcomes unless explicitly supplied valid study data. Static assets are inside the Python package and must be checked in the built wheel. Browser QA is `node browser-tests/dashboard.mjs` with the API running; it checks controls, views, downloads, errors, responsive layout and absence of remote requests. Consult [verification](VERIFICATION.md) for actual run evidence rather than treating these commands as completed checks.
