# Evaluation milestone — 2 November 2026

**Scope update:** this document preserves the financial-analysis walkthrough. The
current mid-term presentation now reconnects that foundation to the original
visualization question. Start with [MIDTERM_RESEARCH_BRIEF.md](MIDTERM_RESEARCH_BRIEF.md)
and notebook 04 for the implemented graph/matrix MVP. Human effectiveness remains
untested; statements below about the earlier deliverable are historical context.

## Question and deliverable

**How does an assumed asset loss affect bank capital, and how can lending
relationships transmit losses to other banks?**

Atlas currently delivers a reproducible Python research prototype with an executed
notebook presentation. Public bank financials support the empirical capital-stress
study. A separate controlled synthetic network demonstrates contagion arithmetic.

The original project proposal asks whether interactive graph views improve task
accuracy, speed, and interpretability compared with matrix views. That hypothesis
has not been tested. It remains a later milestone requiring equivalent views of
the same exposure data, task definitions, and a controlled user study.

## What to inspect

- [Notebook 03](../notebooks/03_real_data_defense.ipynb): primary presentation and saved outputs.
- [Offline HTML](../reports/03_real_data_defense.html): download and open locally.
- [observed.py](../src/atlas/observed.py): source validation, cohort selection, stress arithmetic.
- [engine.py](../src/atlas/engine.py) and [baseline.py](../src/atlas/baseline.py): cascade and independent direct-loss control.
- [Tests](../tests/): hand calculations, boundaries, accounting, and API consistency.
- [Verification](VERIFICATION.md): commands and dated evidence.

## Demonstration scope

| Segment | Time | Evidence |
| --- | --- | --- |
| Question and equity as the loss buffer | 1 minute | Assets 100, equity 10: a 5% loss leaves equity 5 |
| Official financial inputs and fixed cohort | 1½ minutes | FDIC snapshots, certificate join, eligibility, unit conversion, checksums |
| Capital stress and sensitivity | 3 minutes | E′ = E − qA; threshold q* = E/A; change one impairment assumption |
| Separate synthetic contagion chain | 2 minutes | B defaults; A loses 60; C subsequently loses 48 |
| Verification, limits, and next milestone | 1 minute | Independent arithmetic, tests, reproducible inputs; visualization evaluation remains open |

Keep API documentation, Monte Carlo, DebtRank, topology comparisons, and notebooks
01–02 as supporting material for questions. No new frontend or live data acquisition
is required for this milestone.

## Saved results

The [saved summary](../reports/real_data_summary.json) records a fixed 30-bank
cohort, baseline 2019-12-31, follow-up 2020-06-30. The observed market drawdown is
33.925%. An **assumed** multiplier of 0.3 gives a 10.177% uniform asset impairment;
under that static model, 8 of 30 banks exhaust modeled capital, with approximately
USD 26.607 billion in summed shortfall. These are conditional model outputs, not
observed defaults. The June reports provide descriptive context, not ground-truth
validation of this hypothetical shock.

The independent synthetic chain posts losses of 60 and 48, totaling 108 synthetic
units. It verifies propagation; it does not reconstruct the FDIC banks' exposures.

## Contribution and limits

The demonstrated contribution is an auditable implementation and reproducible
analysis using established methods. Neither a new contagion theory nor forecasting
accuracy is claimed. The stress model holds liabilities fixed, applies a uniform
asset haircut, and omits earnings, recapitalization, hedging, liquidity runs, and
policy responses. The market multiplier is an assumption rather than an estimate.

The public fields used here do not identify bilateral counterparties. Correlation
is not a contractual loan exposure. Any future named-bank network experiment needs
suitable lending/borrowing constraints, explicit reconstruction assumptions, and
uncertainty analysis.

## Rehearsal

Run the checks in the [README](../README.md), start Jupyter with uv, and execute
notebook 03 from a fresh kernel. Rehearse one parameter change, keeping the baseline
and the changed assumption visible. Retain the offline HTML as a presentation
fallback. Do not refresh frozen data immediately before the evaluation.
