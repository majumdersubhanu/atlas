# Five-minute scientific demonstration

Run from the repository root:

```bash
uv sync --locked --group notebook --dev
uv run --locked --group notebook --dev jupyter lab
```

Open `notebooks/02_research_experiments.ipynb`. The executed notebook includes saved outputs; restart the kernel and run all cells to reproduce them. Open `01_atlas_pipeline.ipynb` for the historical market plot and API example. For a no-kernel presentation fallback, open `reports/01_atlas_pipeline.html` and `reports/02_research_experiments.html` in a browser; these exports embed the executed outputs.

## 0:00–0:45 — State the question and boundaries

“Atlas is a reproducible computational laboratory for direct counterparty credit contagion. Given a specified bank network, balance sheets, shocks and recovery assumptions, it calculates conditional capital losses and default cascades. It does not predict actual bank failures.”

Explain that a loan arrow goes from lender to borrower, while losses travel from a defaulted borrower back to its creditors. Show the matrix with the same convention.

## 0:45–1:45 — Derive the three-bank result

Show notebook section 1. B is assumed to default. A loses 100 × 60% = 60 against equity 50, ending at −10. C then loses 80 × 60% = 48 against equity 40, ending at −8. Total posted interbank loss is 108. Show the computed round table, individual loan-loss events and reconciliation assertions. Compare the independently implemented direct-loss-only control: it stops at two defaults and loss 60; the cascade adds C and loss 48. This control is a deliberate truncation baseline, not a claim about current banking practice or the state of the art.

A forced credit event does not erase B's book equity. The ledger is not a complete resolution or clearing model.

## 1:45–2:30 — Explain the bank network and impact ranking

Show a selected bank's balance sheet, loan table, and the counterfactual ranking. “Each ranking entry forces one bank to default in an otherwise unchanged system. This measures conditional impact, not likelihood of default.” Degree or betweenness alone cannot capture capital buffers and exposure magnitudes.

## 2:30–3:30 — Show assumption sensitivity

Show the recovery-by-shock heatmap. Every cell is a new run from the original balance sheet. Then show the observed market chart in notebook 1: the S&P 500 peak and trough are historical data, while `drawdown × multiplier` is an illustrative external-asset impairment. Never describe the resulting synthetic defaults as historical COVID bank failures.

## 3:30–4:15 — Explain the research experiment

Show the generator-family ensemble and Monte Carlo summary. Family comparisons are descriptive: their densities, exposures and balance sheets differ. Monte Carlo standard error describes numerical precision of a simulated mean under assumed independent trials; it is not evidence that the assumptions match reality.

## 4:15–5:00 — Demonstrate reproducibility and limits

Show the saved experiment and successful replay assertion. State what tests establish: arithmetic, accounting invariants, boundary behavior and software reproducibility. State what they do not establish: predictive accuracy, empirical calibration, legal resolution outcomes, or a visualization benefit.

## Likely questions

- **What is new?** The integrated, inspectable experimental workflow is the demonstrated engineering contribution. No new contagion algorithm is claimed. A research novelty claim needs a controlled study and comparison against baselines.
- **Why synthetic data?** Complete bilateral exposures are not supplied. Synthetic data makes assumptions explicit and permits controlled checks; it limits external validity.
- **Is 40% recovery correct?** It is a chosen scenario parameter. The sensitivity surface shows dependence on it; no empirical calibration is claimed.
- **Does more connectivity cause greater contagion?** These generator comparisons cannot establish that because financial margins and density change too.
- **Is expected loss the cascade loss?** No. ECL uses assumed PD × LGD × exposure. Cascade loss is conditional on realized modeled defaults, with contagion and survivor-only posting.
- **Is the loss total welfare loss?** No. It is the sum of loan losses posted to banks alive at each round's start. Claims held by already failed banks are excluded.
- **Why no ML?** This is a specified propagation mechanism; no supervised prediction target or empirical training dataset is supplied.
