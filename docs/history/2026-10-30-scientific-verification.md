# Verification record — Atlas 0.5.0, 30 October 2026

This record applies to the notebook/API release. Historical UI verification is retained separately under `history/`.

## Executed checks
- `uv sync --group notebook --dev`: resolved and installed the lockfile environment, removed Streamlit/Plotly dependencies.
- `uv run --locked --group notebook --dev pytest -q`: **44 passed**. One upstream Starlette TestClient deprecation warning concerning httpx remains; requests passed.
- Ruff check and format check on `src tests`: passed.
- Both notebooks executed from fresh kernels: 10 code cells each, no error outputs. HTML exports available in `reports/`.
- `uv run --locked atlas-research`: generated baseline, graph metrics, impact ranking, sensitivity grid, 30-network ensemble, 500 Monte Carlo trials, input/output manifests and a complete saved experiment.
- Saved experiment reloaded through Dataset/Scenario validators and Furfine replay matched the full saved result, including loan events. Output checksums matched.
- A real Uvicorn process on loopback served health and OpenAPI successfully; 12 API paths present. Process terminated after smoke test.
- `uv build`: source distribution and wheel built. An isolated Python import directly from the 0.5.0 wheel loaded packaged market data, reproduced cascade 45 and direct-only 21 defaults.
- Notebook plot review checked all plotted outputs and improved graph/axis readability.

## Exact presentation scenario
Seed 42, 50 synthetic banks, core/periphery generator, recovery 0.4, market multiplier 0.3. Observed selected-window drawdown magnitude 0.3392495902426059. Assumed external-asset impairment 0.10177487707278177. Initial defaults 14, final cascade defaults 45 (31 secondary). Independent direct-only control has 21 total defaults. These are synthetic model outcomes.

The hand chain produces baseline loss 60 and cascade loss 108, in synthetic INR crore. Total default counts are 2 and 3 respectively. These arithmetic results establish the effect of additional transmission rounds in this example, not predictive superiority on real banks.

## Material fixes and limits
Removed UI. Fixed derived balance-sheet overflow validation and added regression test. Added reconciled loan event traces, analytical controls and metadata. Tests verify implementation; no real-world model validation or superiority benchmark is claimed. No exhaustive proof of floating-point behavior, security audit or production load testing was performed.
