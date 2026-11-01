# Atlas empirical demonstration protocol

## Research question
How does a uniform hypothetical asset impairment affect capital buffers in a fixed cohort of large US banks, and how sensitive is modeled capital exhaustion to the chosen market-to-asset loss mapping? The secondary descriptive question compares reported capital ratios at December 2019 and June 2020. This is an exploratory, retrospective scenario analysis, not a preregistered study or a forecasting exercise.

## Literature basis
The existing Undermind Atlas review contains 292 results (26 September 2026). On 1 November we read full texts for Battiston et al. (2015), Macchiati et al. (2024), Niu et al. (2020), and Ferracci/Cimini. The last record has inconsistent publication-year metadata and is not used as a formal citation here. The synthesis is focused, not a comprehensive systematic review.

- Battiston et al., *Leveraging the network: A stress-test framework based on DebtRank*, https://doi.org/10.1515/strm-2015-0005 : commercial Bankscope source, reconstructed networks, assumed density; margin matching does not validate bilateral edges.
- Macchiati et al., *Interbank network reconstruction enforcing density and reciprocity*, https://doi.org/10.1016/j.chaos.2024.115279 : strengths alone do not identify topology. Binary reconstruction needs density/reciprocity information and does not alone provide exposure weights.
- Niu et al., *iConViz*, https://doi.org/10.1109/VAST50239.2020.00013 : private enterprise-guarantee networks and expert case studies. Different financial contracts from interbank loans.
- Eisenberg & Noe, *Systemic Risk in Financial Systems*, https://doi.org/10.1287/mnsc.47.2.236.9835 : clearing model reference; not the model implemented in the existing default-cascade engine.

Full decision review: https://app.undermind.ai/projects/0fc02641-fd90-41a3-bd60-b5043202955b?path=/Atlas%20data%20and%20literature%20decision%20review

## Source acquisition and field audit
FDIC BankFind financial API, https://api.fdic.gov/banks/docs . Raw data and official schema are preserved in data/raw. data/manifest.json records exact requests and SHA-256 digests. Retrieve the largest 100 records by assets separately for 20191231 and 20200630. The total reporting population is larger; this is deliberately a large-bank cohort rather than a representative sample. Historical observations are the revised vintage available on retrieval, not what was necessarily known before COVID.

Field mapping: CERT identifies the reporting bank, REPDTE the quarter end, BKCLASS the institution class, CERTCONS the consolidated parent-bank certificate. ASSET is total assets, LIAB total liabilities, EQTOT total equity capital, DEP deposits. Monetary source units are USD thousands; divide by 1000 to obtain USD millions. EQ differs from EQTOT: an initial probe found that EQ did not reconcile assets and liabilities. EQTOT reconciles to within $1,000 in these files; tolerance is $2,000 for rounding. Do not plug residuals into other categories. Preserve raw values and residuals. The requested FFSOLD field was omitted by the API, so it cannot be used as an observed margin. Broad cash/due balances and repo aggregates are not substituted for unsecured interbank exposures.

Retain classes N, NM, SM, SB, SI, SL with positive equity and assets, nonnegative liabilities and deposits, deposits no greater than liabilities, and CERTCONS=0. Report exclusions; do not fill missing equity with zero. Select top 30 eligible institutions by baseline assets, then left-join follow-up by CERT. Top-100 follow-up coverage is checked in the executed notebook; missing banks must not be replaced. Reports may cover multiple subsidiaries and common holding-company ownership; this is a reporting-bank cohort, not 30 independent bank holding companies. CERTCONS removes explicitly reported bank-parent consolidation. Sums are cohort descriptions, not estimates of system-wide risk.

The packaged S&P 500 file has its own provenance in docs/DATA_PROVENANCE.md. Missing holiday prices are dropped without interpolation. No balance-sheet interpolation is performed. Index points and currency amounts are not merged; a dimensionless drawdown supplies a scenario parameter.

## Model and outputs
Uniform impairment q gives loss L_i=q A_i and remaining equity E_i'=E_i−q A_i. Capital exhaustion is E_i'<=0; shortfall is max(0,−E_i'). q_i*=E_i/A_i is the exact break-even impairment. No legal-default label is inferred. Sweep q from 0 to 20% in 0.25 percentage-point steps. For the historical driver let q=min(1,mD), where D is maximum drawdown within the selected Feb–Apr window, and m ranges from 0 to 0.5. m=0.3 is illustrative and uncalibrated.

This deliberately simple model makes a strong uniform haircut assumption across assets with different risks. It holds liabilities fixed and omits income, recapitalization, tax, hedging, liquidity, policy responses, and contagion. Observed June ratios are descriptive context, not ground-truth outcomes of the assumed scenario. No p-value, predictive accuracy or causal effect is claimed.

A separate three-bank synthetic chain verifies the existing Furfine-style engine: B's default causes A's 60-unit loss and C's subsequent 48-unit loss. Do not combine these edges with named-bank financials. Existing notebooks 01/02 retain the more extensive synthetic-network experiments. Extending the empirical study to contagion requires compatible bank lending/borrowing margins, explicit outside-sample exposures, reconstruction ensembles and validation.

## Presentation framework
The notebook follows a reproducible scientific talk structure: question, prior work, data and audit, observed findings, model equations, experimental design, results and sensitivity, mechanism control, limitations and next work, references. Each section has slideshow metadata and execution outputs. It is an IMRaD-style presentation organization, not a claim of compliance with an external reporting standard.

## Acceptance criteria
Raw input checksums verified; cohort and joining rules reproducible; accounting audit displayed; unit conversion checked; no missing-bank substitution; zero-shock and hand-loss controls; boundary and monotonicity checks; all tests pass; fresh notebook execution; static HTML fallback generated; local Jupyter and API health checked. See LOCAL_SETUP.md and LIVE_VERIFICATION.md.
