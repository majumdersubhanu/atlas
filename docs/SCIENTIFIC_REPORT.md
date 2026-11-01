# Atlas: a reproducible interbank credit-contagion research prototype

## Research question and contribution
How do assumed borrower defaults and external-asset impairments propagate through a specified interbank exposure network under fixed recovery, and which seed institutions cause the largest conditional cascades?

The contribution at this milestone is an inspectable computational workflow: validated synthetic data, documented propagation conventions, matched inputs across baseline comparisons, bank-level explanations, repeatable experiments and notebook presentation. The contagion algorithm is established. This release does not demonstrate a novel estimator, predictive accuracy, a historical bank network, or improved human decision-making. The planned graph-versus-matrix usability study requires participants and a controlled protocol and has not been performed.

## Data and estimands
Bank balance sheets and bilateral loans are synthetic. A loan A[i,j] is an asset of lender i and liability of borrower j. Interbank assets are row sums, liabilities column sums. External assets plus interbank assets equal deposits plus interbank liabilities plus equity. Deposits represent all external funding in this simplified schema. Units are synthetic nominal INR crore, unrelated to the index's points.

The historical S&P 500 fixture supplies a dimensionless drawdown. It is not bank balance-sheet evidence. Let M=max_t(1-P_t/max_{s<=t} P_s). The scenario sets q=min(1,m M), where m is a deliberately chosen sensitivity parameter. No regression or empirical calibration estimates m. Applying a US equity index shock to nominal synthetic INR balance sheets is a teaching scenario, not an India-specific economic estimate.

## Model specification
Initial stressed equity is E_i(0)=E_i-q X_i, with X_i external assets. Round-zero defaults include nonpositive equity and explicitly forced credit events. Forced events may retain positive book equity; they represent an exogenous default assumption, not a computed insolvency.

For each subsequent synchronous round, surviving creditors lose (1-r) times their loans to the previous round's newly defaulted borrowers. After aggregating all simultaneous losses, nonpositive equity triggers new defaults. Each borrower transmits once. The algorithm stops when no new defaults occur. The current implementation scans all exposures and banks per round, O(T(E+V)), and records capital snapshots plus loan-level loss events. Finite-size default propagation terminates in at most V nonempty default waves.

Posted interbank loss sums only the loan-loss events recognized at creditors still alive at the start of a round. It excludes later claims of already failed banks. It is not system-wide resolution loss, welfare loss or GDP loss. Larger exogenous shocks can reduce this posted-loss statistic by killing creditors earlier. External and interbank losses must therefore remain separately labeled.

Expected credit loss sums PD_j (1-r) A[i,j], with assumed one-period borrower marginal PD. It is distinct from the cascade's realized scenario loss and from the Monte Carlo mean cascade loss. The equity/assets ratio is a book-capital proxy, not a regulatory risk-weighted ratio.

## Experimental design
1. Hand-calculated three-bank chain checks orientation, loss accounting and second-round propagation.
2. Seed-42 50-bank core/periphery network supplies the presentation example. The no-shock and full-recovery cases are negative controls.
3. Recovery and shock sweeps restart from identical initial balance sheets, isolating those parameter changes within the specified model.
4. Each single-bank impact experiment forces one institution to default with zero common shock. Ranking is conditional impact, not default likelihood or additive systemic-risk attribution.
5. Ten seeds per network family describe generated ensembles. The presets differ in edge density, total lending, funding and capital, so comparisons cannot isolate a causal effect of topology. The `scale_free` label denotes an oriented finite Barabási–Albert sample, not verified power-law behavior.
6. Monte Carlo independently samples initial defaults conditional on assumed PDs and a fixed shock. MCSE=s/sqrt(n) quantifies simulation error of a mean. Empirical quantiles describe simulated outcomes, not confidence intervals or validated risk forecasts. Parameter and structural uncertainty remain outside this calculation.

## DebtRank variant
The implementation uses LGD-adjusted impact weights min(1,(1-r)A[i,j]/E_i), and initial-total-assets economic weights. These are explicitly Atlas conventions. The original active/inactive rule permits each institution to transmit its current distress once. With a positive common impairment and positive external assets, all nodes start active, so this particular experiment has one network transmission wave. It must not be interpreted as repeated mark-to-market feedback or an exact replication of the original empirical DebtRank study.

## Verification versus empirical validation
Tests check accounting, invalid inputs, a hand calculation, limiting cases, replay, event reconciliation and agreement between HTTP and Python interfaces. An independent direct-only baseline shows which losses require secondary propagation. Such checks establish implementation consistency. They do not establish that these assumptions reproduce actual banking systems. A fresh-kernel notebook run verifies executable analysis, not scientific truth of its assumptions.

## Threats to validity
Synthetic networks need not resemble observed exposures. Uniform recovery ignores collateral, seniority and resolution. Default timing is algorithmic, not calendar time. No endogenous recovery, liquidity runs, fire sales, depositor flight, clearing equilibrium or correlated default mechanism is present. Calibration to real banks, out-of-sample evaluation, controlled topology interventions and human-subject evidence remain future research.

## Primary literature and implementation references
- Furfine (1999 working paper, later published 2003), *Interbank Exposures: Quantifying the Risk of Contagion*: https://www.bis.org/publ/work70.pdf
- Battiston et al. (2012), *DebtRank: Too Central to Fail?*: https://pmc.ncbi.nlm.nih.gov/articles/PMC3412322/
- Market provenance and exact fixture checksum: DATA_PROVENANCE.md.
- NetworkX graph conventions checked through Context7: https://networkx.org/documentation/stable/reference/classes/digraph.html and https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html . Exposure amounts are not distances; Atlas uses unweighted shortest-path betweenness.
