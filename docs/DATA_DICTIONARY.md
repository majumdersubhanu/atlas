# Data dictionary and code map

| Object | Fields and interpretation | Implementation |
|---|---|---|
| Bank | id/name (fictional), tier (generator label), external_assets, interbank_assets, deposits (all outside liabilities), interbank_liabilities, equity; PD in [0,1] | models.py |
| Exposure | lender, borrower, amount>0; no duplicate directed pair or self-loan | models.py |
| Dataset | synthetic=true, units, seed, topology, banks, exposures; accounting checked | models.py, generate.py |
| Scenario | name, recovery in [0,1], external_impairment in [0,1], initial_defaults | models.py |
| Credit | EAD=amount, LGD=1-recovery, PD=borrower's assumed marginal PD, expected_loss | engine.py |
| Furfine output | initial/secondary/default sets, per-bank external/interbank losses, equity and round snapshots, loan events | engine.py |
| Loan event | round, lender, borrower, EAD, loss; same claim transmits at most once | engine.py |
| Graph metrics | lending/borrowing strength, degree, unweighted betweenness, density/components | analysis.py |
| Impact ranking | forced single-bank default, no common shock, secondary count and posted losses | analysis.py |
| Monte Carlo | trial, defaults, secondary_defaults, interbank_loss; seeds/parameters supplied by caller | engine.py |
| MC summary | sample mean, simulation standard error, inverse empirical CDF quantiles | analysis.py |
| Market | date, close in index points, fractional close-to-close return, fractional drawdown | market.py |
| Saved experiment | input dataset and hash, scenario/result, optional market mapping/advanced settings, UTC creation time, version/runtime/source hashes | storage.py |

All monetary quantities are floating-point synthetic nominal INR crore. No regulatory risk weights, maturity structure or FX conversion is represented. NaN/infinity inputs and nonfinite derived accounting totals are rejected. Equality uses a documented relative tolerance, not exact monetary decimal accounting.

## Execution architecture
Validated data enters pure model functions. API and CLI call these same functions; notebooks orchestrate and explain them. Storage serializes inputs and outputs; experiment replay reconstructs a validated Dataset and Scenario. Scientific module docstrings describe definitions and caveats. There is no UI layer. API is a local research service without authentication, job scheduling or deployment hardening.
