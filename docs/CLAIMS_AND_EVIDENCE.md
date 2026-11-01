# Claims that this MVP can defend

| Claim | Evidence in this release | Boundary |
|---|---|---|
| Generated balance sheets reconcile with loans | Dataset validator; generator and accounting tests | Synthetic accounting consistency, not realism |
| Loan direction and loss direction differ | Three-bank hand fixture, exposure matrix and orientation test | Specific contractual credit channel |
| Repeated propagation adds losses in the chain | Independent direct-only 60 versus cascade108; baseline tests | Mechanism test, not statistical superiority |
| Selected historical prices imply 33.925% maximum drawdown | Packaged FRED data, checksum, peak/trough arithmetic | Selected Feb–Apr 2020 price-index window |
| Seed42 scenario yields 14 initial and 31 secondary defaults | Final experiment JSON, replay, executed notebook | Conditional synthetic outcome, not historical bank failure |
| Results depend on scenario parameters | Same-data recovery/impairment grid | Sensitivity under fixed model assumptions |
| Single-bank impact differs from default probability | Forced-default ranking with zero common shock | No calibration of probability or causal attribution |
| Different generator ensembles have different outcomes | 30 replicate rows with density/assets/equity/exposure totals | Confounded descriptive comparison, not isolated topology effect |
| Monte Carlo sampling error can be quantified | 500 independent draws, explicit seed/PD, mean MCSE and empirical quantiles | No parameter/model uncertainty or correlated macro defaults |
| Notebook, Python and API agree | Executed notebooks, HTTP integration tests, live server smoke test | Software verification rather than empirical validity |
| UI is unnecessary for computation | UI source/dependencies removed; headless batch and notebooks run | Visual-usability research remains unperformed |

## Claims deliberately not made
Atlas does not forecast the next crisis, reconstruct real bilateral lending from an equity index, estimate real bank PDs, reproduce all financial-resolution flows, identify a causal topology ranking, outperform current supervisory models, invent Furfine/DebtRank, or demonstrate improved human decision-making.

## Original requirements trace
The original chats requested bank/exposure schemas, three generator families, ECL, default cascade, rankings, network/matrix exploration, recovery comparison, advanced models, saved experiments, tests and a demonstration. Source modules implement the computations, notebooks provide the inspection surface, and the local API offers programmatic access. The latest instruction explicitly removes UI. Reconstruction, liquidity/clearing extensions and a visual-analysis user study remain final-project research milestones.
