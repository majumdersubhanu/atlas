# Executed verification — 2026-10-30

Executed in this environment using **CPython 3.12.16**, uv 0.13.6 and the committed
`uv.lock` dependency resolution. This is execution evidence for this release, not a
repetition of the prior chat's test claims.

| Check | Actual result |
|---|---|
| `uv sync --dev` | Resolved 54 packages, installed 53 dependencies/project packages successfully |
| `python -m pytest -q` (final run) | **32 passed**, 1 dependency deprecation warning, 2.13 seconds |
| `ruff check .` | All checks passed |
| `ruff format .` | Applied before final passing suite |
| `python -m atlas.cli --output experiments` | Exported 50 banks, 222 loans, five scenario records, 200 Monte Carlo trials |
| `uv run --offline --no-sync atlas-demo --output /tmp/atlas-offline-demo` | Reproduced all five scenarios without network/data downloads |
| `uv build` | Built wheel and source distribution |
| `uv build --offline` | Final package rebuilt from the setup cache; isolated wheel import reproduced 62 closes, the baseline hash, and 45 modeled defaults |
| Uvicorn bound to localhost | `/health` HTTP 200, `/openapi.json` HTTP 200; server then stopped |
| Streamlit bound to localhost | `/_stcore/health` HTTP 200, `/` HTTP 200; server then stopped |

Tests cover all three topology families at 2/10/50/100 banks, determinism, balance-sheet
and loan reconciliation, malformed datasets, ECL arithmetic, the hand-calculated cascade,
zero shock, full recovery, complete external impairment, exact zero equity, simultaneous
defaults, input immutability, market endpoints and measured drawdown, DebtRank arithmetic,
Monte Carlo determinism and PD extremes, JSON export/replay, API success/error/save routes,
and actual Streamlit reruns with topology, manual impairment, save and Monte Carlo controls.

The Streamlit test uses AppTest; HTTP checks confirm startup, not a manual visual review
of every browser viewport. No claim of cross-platform browser acceptance testing is made.

## Failures found and handled

- The first restricted `uv sync` could not write the global uv cache; the dependency
  setup succeeded with the required access.
- The first dashboard integration test found that importing a module as the app entry
  point rendered once but skipped subsequent Streamlit reruns due to Python's module
  cache. The entry point now executes the dashboard on every rerun; the integration
  test passed afterward.
- Initial Ruff checks found three style issues, subsequently fixed and reformatted.
- An isolated compressed-wheel import found that Pandas could not directly consume a
  zipped resource path. The loader now opens the resource as a binary stream; the wheel
  replay and the complete test suite both passed after the fix.
- API TestClient stalled in the restricted environment's event loop. A diagnostic
  traceback located the wait in the test transport. The complete suite was rerun with
  local networking access and passed; the separate real Uvicorn HTTP check also passed.
- The remaining warning comes from Starlette's test client deprecating its httpx
  integration. It does not represent a failing application test.
- An offline rebuild pointed at a fresh empty temporary cache could not locate Hatchling.
  Rebuilding offline against the original populated setup cache succeeded. Offline runtime
  requires installed dependencies; the bundle is not an all-platform dependency installer.

## Reproducible benchmark

Network: seed 42, core_periphery, 50 banks, 222 directed loans. Recovery 0.40.
Full observed Feb–Apr window; maximum drawdown magnitude = 0.3392495902426059.

| Multiplier | External impairment | Direct defaults | Secondary defaults | Total |
|---:|---:|---:|---:|---:|
| 0.00 | 0.000000% | 0 | 0 | 0 |
| 0.20 | 6.784992% | 2 | 0 | 2 |
| 0.30 | 10.177488% | 14 | 31 | 45 |
| 0.40 | 13.569984% | 29 | 21 | 50 |
| 0.60 | 20.354975% | 49 | 1 | 50 |

Zero external shock, independent 2% PD, 200 trials, seed 42: mean modeled default
count 0.935. The three-bank manual fixture gives 3 total defaults and ₹108 crore
posted interbank loss at 40% recovery. All are synthetic model results.

Saved full inputs/results are included as `experiments/demo_mapping_*.json` and the
packaged baseline JSON/CSVs under `src/atlas/data/demo_network/`. The UUID files created
by later CLI runs are intentionally separate, so new experiments do not overwrite old ones.
