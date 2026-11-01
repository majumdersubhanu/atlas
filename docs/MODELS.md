# Model conventions

## Data and balance sheets

An exposure `(lender, borrower, amount)` is a lender asset and a borrower liability.
The generators sample positive loan weights, aggregate each side, then assign external
assets, equity ratios (6–14%), and residual deposits. External assets include sufficient
funding capacity for borrowing; deposits stay nonnegative. For every bank:

`external_assets + interbank_assets = deposits + interbank_liabilities + equity`.

The validator independently reconciles each bank's loan assets and liabilities against
the exposure list. Validation tolerance is 1e-7 relative to magnitude. Initial equity is
strictly positive. Monetary values are floating-point synthetic INR crore. Banks are
fictional; neither topology nor balance sheets are empirically fitted.

## Credit risk

`ECL_ij = PD_j * (1 - recovery) * exposure_ij`.

PD is the borrower's assumed one-period marginal PD (default 2%). The Python/API caller can override
all PDs uniformly; otherwise bank-specific PDs in imported datasets are used. No maturity,
discounting, staging or credit migration is modeled. HHI is the sum of squared fractions
of a lender's total loan assets; it is zero for a bank with no lending. Equity/assets is
an accounting proxy, not a regulatory risk-weighted capital ratio.

## Furfine-style credit cascade

1. Apply `external_assets * impairment` once to each bank's equity. This is an exogenous
   write-down, unrelated to whether a bank's borrowers default.
2. Round zero defaults are banks with equity <= 0 plus user-forced defaults. Forced default
   is a credit event; it does not arbitrarily erase the bank's remaining book equity.
3. For each newly defaulted borrower, surviving creditors lose `(1 - recovery) * loan`.
   Aggregate all losses synchronously before testing equity <= 0 for the next round.
4. Each defaulted borrower transmits exactly once. Stop after no new defaults.

The input dataset stays unchanged. Stress results are equity/loss ledgers, not newly
validated full post-resolution balance sheets. No interbank liability write-offs,
creditor waterfall, depositor resolution, liquidity runs, fire sales, endogenous recovery,
netting, collateral, recapitalization or clearing-vector equilibrium is modeled.

The reported **interbank loss** is loss posted to banks alive at the start of a round;
losses on claims held by already failed banks are not posted. It is not a gross all-claims
resolution loss or an aggregate welfare loss. External and interbank losses must be
interpreted separately. Defaulted equity can be negative (no clipping); a forced default
can retain positive book equity. Recovery is a fixed assumption, with no funding source
modeled. Cascade rounds are computational steps, not actual days.

## Market mapping

For a selected observed window, compute `close / running_peak(close) - 1` and take the
magnitude of its minimum. Impairment = `min(1, multiplier * maximum_drawdown)`.
The window peak must precede the drawdown trough. Recompute from the original bank
balance sheet for every scenario; do not cumulate daily drawdowns. Daily returns are
shown as observations but are not used to estimate PD or to claim historical contagion.

## Advanced exploratory scope

DebtRank uses `W[creditor,borrower] = min(1, LGD * loan / creditor_equity)` and initial
distress `h0 = min(1, external_loss/equity)`. Each active node transmits its distress once,
then becomes inactive, following the original active/inactive convention. Distress stays
in [0,1]. The score is incremental final distress above h0 weighted by initial total
assets. This variant is explicitly distinct from iterative mark-to-market DebtRank and
does not convert directly into default probabilities or Furfine counts. Forced initial
defaults are a Furfine control and do not enter this external-shock DebtRank calculation.

Monte Carlo samples independent Bernoulli initial borrower defaults using assumed PDs,
adds any user-forced defaults, then runs Furfine with the fixed external shock. Seed and
trial count are explicit. Outputs are conditional scenario distributions, not validated
forecasts; there is no correlated macro/default model or parameter estimation.

Conceptual references: Furfine, “Interbank Exposures: Quantifying the Risk of
Contagion” ([BIS working paper, 1999](https://www.bis.org/publ/work70.pdf), later
published 2003); Battiston et al. (2012),
[“DebtRank: Too Central to Fail?”](https://www.nature.com/articles/srep00541).
This MVP uses the specific conventions above, not a claim of reproducing all results
in those papers.

## Scope corrections from independent audit

The scale_free preset is an oriented Barabási–Albert sample, not empirical proof of a power-law distribution. Generator comparisons change density and financial scale as well as topology. Under the positive uniform external shock every bank begins active in the one-active-step DebtRank variant, yielding one network transmission wave. LGD adjustment and total-assets weights are explicit variant choices. See SCIENTIFIC_REPORT.md for experimental interpretation and BASELINE_METHODS.md for comparison with current literature.

## Exact generator parameters

For n banks, the core size is max(2, floor(n/5)). The core/periphery generator samples each possible directed edge independently with probability 0.65 for core/core pairs, 0.18 for mixed pairs and 0.015 for periphery/periphery pairs. The random generator uses 0.08 for every directed pair. Self-loans are excluded. These values are scenario construction choices, not estimates from banking data.

The preferential-attachment preset uses NetworkX's Barabási–Albert graph with m=min(3,n−1) and independently orients each resulting edge with probability 0.5 in either direction. The input seed controls NetworkX and NumPy generation. Each existing loan receives an independent uniform amount in [5,40). For each bank, external assets equal a uniform draw in [150,700) plus its interbank borrowing. Equity is a uniform fraction in [0.06,0.14) of total assets. Deposits are the residual external funding needed to satisfy the identity. The Dataset validator rejects negative deposits or inconsistent accounts. A seed gives reproducibility under the locked implementation and versions, not an economic meaning or matched random inputs across generator families.

Default borrower PD is 0.02 for one unspecified period. Recovery defaults to 0.4. Neither has an empirical estimate in this MVP. Lending HHI sums squared shares of lending over borrower counterparties. Borrowing HHI analogously sums squared funding shares over creditor counterparties. HHI is defined as zero for a bank with no corresponding exposures.
