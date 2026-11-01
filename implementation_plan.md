# Implementation plan — scientific MVP, 30 October 2026

## Recovered scope
Read `Atlas Evaluation Plan` (6ae3e72d-d650-83ee-941b-0f1319a09519), `ATLAS MVP Plan` (6adc94a8-7db4-83ee-af85-2291b6faf03b), and the prior `Complete Atlas MVP demo`. Older chat claims and inaccessible attachment results are context, not evidence for this release. The supplied 0.4.0 artifact is the starting source. Current user instruction supersedes all UI requirements.

## Acceptance criteria
- Validated bank balance sheets and directed weighted interbank exposures; seeded random, preferential-attachment and core/periphery generators.
- Bank inspection, lending/borrowing concentration, assumed PD/LGD/EAD credit risk.
- Reproducible Furfine-style synchronous cascade with per-round capital and loan-loss events; hand-computed validation.
- Matrix/network diagnostics and single-bank counterfactual impact ranking.
- Recovery/shock sensitivity; descriptive topology ensembles; exploratory DebtRank and independent-default Monte Carlo with simulation-error reporting.
- Historical market fixture with provenance; explicit exogenous mapping rather than historical default inference.
- APIs, executed notebooks, persisted/replayed experiments, test evidence, scientific methodology, data dictionary and professor demo script.
- Remove dashboard code and dependencies.

## Scientific scope boundary
The MVP is a computational research instrument. No empirical claim about real bank defaults, causal topology effects, algorithmic novelty, prediction accuracy or visualization usability follows from these simulations. Exposure reconstruction, empirical parameter fitting, clearing/resolution, liquidity/fire sales and a graph-versus-matrix user study are final-project research, not completed MVP features.

## Implementation sequence
1. Recover requirements and independently audit implementation.
2. Remove UI; implement missing analytical functionality and loss audit trail.
3. Integrate API and research notebook, persist reproducibility evidence.
4. Execute tests/notebooks, export presentation fallback and document observed results.

## 1 November implemented scope adjustment
The public-data field audit supports observed bank capital stress, but not a validated bilateral exposure network. Notebook 03 now presents the complete research workflow using official FDIC data for a fixed 30-bank cohort and a clearly assumed loss mapping. Existing synthetic contagion notebooks remain available. Empirical network reconstruction is deferred pending compatible margins and outside-sample accounting; see docs/research/PROTOCOL.md. Local environment, fresh execution, tests, presentation exports and HTTP service checks are complete.
