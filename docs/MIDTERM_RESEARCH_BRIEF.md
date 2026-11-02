# Atlas: visualization of systemic risk contagion

**Panel edition — 2 November 2026, after 16:00 IST.** This is a working mid-term MVP, not a completed effectiveness study. Start here for the research argument; use [the demo script](MIDTERM_DEMO_AND_QA.md) during the presentation.

## 1. The original topic and the work completed

The original [Notion proposal](https://app.notion.com/p/3a4dfad78e42805e9660fe3e14f2dcdd) is titled *A Graph-Based Visual Analytics Framework for Exploring Systemic Risk Propagation in Financial Networks*. The fetched proposal was last edited 31 July 2026. It asks whether graph-based visual analytics improves accuracy, efficiency and interpretability relative to heatmaps. It proposes a platform **and** a comparative user study. The original architecture illustration was an attachment; this reconciliation uses the page's textual requirements.

Terminology: **systemic risk** concerns disruption spreading through a system. **Systematic risk** normally refers to common market-wide risk. Our subject is systemic contagion; a common asset shock is one possible starting event.

| Original proposal | Existing work before this MVP | Mid-term bridge / remaining boundary |
| --- | --- | --- |
| Financial data acquisition | Frozen FDIC reports and packaged S&P 500 series | Retain as observed capital-stress context; do not infer bilateral loans from these fields |
| Weighted financial networks | Validated synthetic loans; directed matrices and network measures | Both visible encodings now use the exact same exposure dataset |
| Contagion simulation | Furfine-style engine, direct-loss control, event ledger | Replay rounds interactively with fixed positions and inspect individual loss entries |
| Interactive visual exploration | Executed notebooks and reports; no paired dashboard | Local dashboard with graph, matrix, side-by-side exploration, bank inspection and live scenario controls |
| Baseline heatmap/matrix | Numerical direct-loss baseline only | Add a **visual baseline**, a directed exposure-matrix heatmap; retain the model baseline separately |
| Accuracy, time, interpretability evaluation | No participant study | Operationalized tasks and recruitment/protocol; practice recorder; effectiveness remains untested |
| Broad production platform | Python package and FastAPI | Same-origin static frontend served by FastAPI; deliberately small, offline-capable research MVP |
| Open-source / publication | Public review repository, no chosen code license | License and publication decisions remain outstanding |

The earlier work supplies a credible **stimulus generator and ground-truth calculator**. It did not answer the original visualization RQ. This MVP connects that calculator to a controlled visual comparison rather than treating a financial stress result as HCI evidence.

## 2. Literature → inferences → decisions

The [literature review](LITERATURE_REVIEW.md) contains eight close papers, primary-source links, evidence boundaries and design implications. It is a focused narrative review, not a systematic review or a claim to exhaust the literature.

| Evidence strand | Inference for Atlas (our reasoning, not the source's claim about Atlas) | Decision |
| --- | --- | --- |
| Ghoniem et al. (2005) and Ren et al. (2019) find different task/context-dependent graph–matrix performance patterns | A universal “graphs are better” hypothesis is too broad | Separate path/propagation tasks from direct lookup; control size, density, interaction and learning |
| iConViz and Regshock already combine financial networks with interactive analysis | A financial graph dashboard by itself is not a defensible novelty claim | Present an auditable exposure-to-loss trace and a fair, reproducible representation comparison |
| Brehmer & Munzner distinguish why/how/what in tasks | “Understand risk” needs observable questions and scoring | Define exact prompts, answer keys, accuracy, time and explanation rubric |
| GraphDiaries examines temporal navigation | Propagation is a sequence that benefits from explicit navigation, but animation benefits must be tested | Stable coordinates, round slider, play/pause; same round access in both conditions |
| Furfine and DebtRank provide established propagation foundations | Economic modeling and visualization evaluation are distinct contributions | Use a small verified default cascade for the main display; retain DebtRank as optional context |

## 3. Proposed final research question

> **For qualified or interested users who demonstrate basic task understanding, how does an interactive node–link view, compared with an interaction-matched exposure-matrix heatmap of the same synthetic interbank network and cascade, affect accuracy, completion time and explanation quality when tracing loss propagation and identifying secondary failures? How do task type, network size/density and relevant experience moderate the result?**

Financial analysts are a particularly relevant audience, but recruitment is open through a Google Form. Screen and record domain experience; do not describe every participant as an analyst. Report the sample actually recruited, and distinguish any analyst subgroup from the full sample.

This narrows the original question to directed loan exposures and default contagion. Correlation, ownership and supply-chain edges have different semantics and are deferred. A stock-price correlation is not a contractual loan: comparing a correlation heatmap with an exposure graph would confound representation with information content.

## 4. Hypotheses and falsifiability

**H1 (primary):** mean within-participant accuracy on propagation/path tasks is higher in the graph condition than in the matrix condition. The planned estimand is graph accuracy minus matrix accuracy, measured in percentage points. The null is no positive difference. A zero or negative result does not support H1.

**H2 (secondary):** graph-condition task completion is faster on these tasks. Report completion time alongside errors/timeouts; do not claim speed improvement by silently discarding difficult failures.

**H3 (secondary):** graph-condition causal explanations score higher on a predefined, representation-blind rubric. Self-reported confidence is separate from correctness.

**Exploratory:** exact exposure lookup, density, size and experience may change or reverse the difference. No blanket graph advantage is hypothesized for lookup. The full graph+matrix workspace is a useful exploration design, but is **not** one of the two isolated comparison conditions.

The initial prototype does not implement a complete confirmatory trial runner. Its practice recorder tests timing/export only. See [study protocol](VISUALIZATION_STUDY_PROTOCOL.md) for recruitment, counterbalancing, scoring, analysis and gates before collecting research data.

## 5. What counts as the baseline?

### Visual baseline: exposure matrix

Rows are lenders, columns are borrowers, and cell values are original loan amounts. Cell intensity shows amount; labels make direction explicit. The graph displays those same exposures as directed arrows, with width encoding amount. The common bank selector and identical round slider support both views. Failure states and exact loan values are available in both. Stable bank-ID matrix order and seeded graph positions are documented layout choices, not optimized competitors.

This is a conventional representation implemented for this experiment. We have not surveyed proprietary analyst workstations, and do not claim this exact interface is “the current industry solution.” Existing visual analytics systems are discussed in the literature review.

### Model control: direct losses only

The independent baseline applies external losses and one generation of losses from initial failures. Newly failed creditors are counted but do not transmit. Full Furfine propagation continues until no new failures occur. This isolates later-round losses within the model; it says nothing by itself about human visualization performance.

## 6. Small-scale solution and experiments

**E1 — numerical control:** A lends 100 to B; C lends 80 to A. Starting equity is A=50, B=50, C=40. Force B to fail; recovery=40%; external impairment=0. A loses 60 and fails at −10; C then loses 48 and fails at −8. Forced B can retain positive book equity because its credit event is imposed.

| Outcome | Direct-loss control | Full cascade |
| --- | ---: | ---: |
| Initial failures | 1 | 1 |
| Secondary failures | 1 | 2 |
| Total failures | 2 | 3 |
| Posted interbank loss | 60 | 108 |

Later propagation adds **48 synthetic units and one failure**. This is a model result, not a visualization improvement percentage.

**E2 — visual evidence parity:** Verify that every graph edge equals the corresponding matrix cell, both views share the dataset hash and loss ledger, and shock changes do not move nodes. Browser QA exercises both displays. This establishes data consistency, not perceptual equivalence or usability.

**E3 — sensitivity:** Change recovery from 40% to 100%; the forced initial failure remains, but all loan losses are zero. At 50% recovery A reaches exactly zero and fails; C subsequently reaches exactly zero and fails. At 51%, A retains positive equity and the chain stops. This demonstrates why threshold assumptions matter.

**E4 — branching example:** Six banks illustrate multiple lenders and survivors. At 40% recovery with B initially failed, posted losses are 60+30+48+24+18=180. A, B, C and D fail; E and F survive with equity 6 and 12. Direct-loss control posts 90.

**E5 — small generated networks:** Seeded 12-, 24- and 50-bank fixtures test nontrivial input sizes and parity. Runtime measurements are local engineering diagnostics. Different generator families do not isolate pure topology effects.

**E6 — human evaluation:** Not conducted. The second new notebook validates the empty study schema and supplies participant-level paired summaries for future eligible records. It does not invent participants, task times, ratings, significance or effect sizes.

Reproduce E1–E5 in [notebook 04](../notebooks/04_visualization_comparison.ipynb); inspect the human-analysis scaffold in [notebook 05](../notebooks/05_visualization_study_analysis.ipynb). [Technical documentation](VISUALIZATION_IMPLEMENTATION.md) describes data and algorithms.

## 7. Qualitative comparison, with claims kept separate

| Aspect | Exposure matrix | Node–link graph | Current evidence |
| --- | --- | --- | --- |
| Exact loan lookup | Explicit row/column intersection and value | Arrow endpoints and exact label/tooltip | Implemented; no measured human advantage |
| Multi-step loss trace | Follow borrower column back to lender rows across rounds | Follow losses opposite loan arrows across rounds | Implemented; H1 pending |
| Dense networks | Cells avoid edge crossings; require scrolling at larger sizes | Crossings and occlusion can increase | Design trade-off; not measured superiority |
| Round-by-round state | Colored headers and failure marks | Colored nodes and textual state details | Same ledger, common controls |
| Explanation evidence | Shared loss ledger / bank details during exploration | Same shared evidence | Hidden equally in practice tasks; formal conditions to be frozen |
| Quantitative output | Same simulator results | Same simulator results | Numerical equality is intended, not a win for either view |

## 8. Conclusion for the panel

Atlas now demonstrates the end-to-end research mechanism: a validated synthetic lending network, a transparent cascade, and two interactive encodings of identical evidence. Existing observed-data work motivates capital vulnerability but remains separate from fictional exposures. The defensible mid-term contribution is an inspectable MVP and an evaluation design. The central empirical claim—whether the graph helps people—is **open**. A null or task-specific result is a useful research outcome.

## 9. Work left and proposed completion schedule

The only confirmed deadline is today's mid-term panel. The following **six-week estimate** assumes access to willing participants and faculty approval of the study protocol; it is not a promised final-submission date.

| Dates (IST) | Work | Exit evidence |
| --- | --- | --- |
| 2 Nov 2026, before panel | MVP, executed notebooks, literature argument, live + offline demo | Reproducible example, tests, browser check, saved notebook outputs |
| 3–8 Nov | Faculty feedback; refine RQ and eligibility; prepare Google Form invitation and consent; review matrix ordering/layout alternatives | Agreed scope, task definitions, documented recruitment plan |
| 9–15 Nov | Implement counterbalanced runner; freeze parallel stimulus sets; add timeout/visibility logging, blind scoring workflow and deployment/export controls | Versioned task corpus, parity tests, no condition switching or answer leakage in formal mode |
| 16–22 Nov | Small usability pilot (suggested 5–8 eligible volunteers); revise tasks; estimate variance and feasibility | Pilot report, task difficulty/ceiling checks, preregistered main analysis and recruitment target |
| 23–29 Nov | Open recruitment and main study, subject to required institutional review | De-identified complete/partial sessions and predeclared exclusion log |
| 30 Nov–6 Dec | Analyze paired outcomes; experience strata; explanation coding and uncertainty | Reproducible analysis notebook; effect estimates, intervals and limitations |
| 7–13 Dec | Write results/discussion; strengthen UI based on evidence; independent replay; final demonstration | Final report, versioned release, documentation and demo |

Recruitment and study review are critical-path uncertainties. If sample size is inadequate, report an exploratory pilot with wide uncertainty and do not upgrade the claim to validated analyst effectiveness. Production hardening, real exposure acquisition, sophisticated layout comparisons, a license decision and publication are separate follow-on work.
