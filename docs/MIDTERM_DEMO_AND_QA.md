# Panel walkthrough and Q&A

**2 November 2026, after 16:00 IST.** Aim for a 10–12-minute explanation followed by questions. The MVP is enough for this milestone; the participant study is future work.

## Before entering the room

1. Start `uv run --locked uvicorn atlas.api:app --host 127.0.0.1 --port 8030` from the repository root. If it is already running, reuse it. Stop it with Ctrl-C after the demonstration.
2. Open <http://127.0.0.1:8030/> and <http://127.0.0.1:8030/docs>. The normal documented default is port 8000; 8030 avoids an existing service in the current workspace.
3. Keep notebook 04 and `reports/visualization/04_visualization_comparison.html` open as offline fallbacks. The exported HTML embeds figures and needs no running API or internet.
4. Reset to the three-bank example: B forced failed, recovery 40%, external loss 0%. Confirm final loss 108 and added loss 48.
5. Keep [research brief](MIDTERM_RESEARCH_BRIEF.md), [literature review](LITERATURE_REVIEW.md) and [study protocol](VISUALIZATION_STUDY_PROTOCOL.md) available. Do not refresh source data or install new dependencies immediately before the panel.

## Suggested narrative

| Time | Show | Say |
| --- | --- | --- |
| 0:00–1:00 | RQ and original proposal link | “Our original topic is whether visualization helps people understand systemic contagion. The engine is the foundation needed to test that.” |
| 1:00–3:00 | Literature review L1–L6 | “Financial visual analytics already exists. Graph–matrix results depend on tasks and design. We therefore test a narrow, falsifiable comparison.” |
| 3:00–4:00 | Final RQ / hypotheses | “Our primary hypothesis is higher accuracy on tracing propagation; speed and explanation quality are secondary. Lookup may favor the matrix.” |
| 4:00–6:30 | Dashboard chain and rounds | “A lends to B; C lends to A. B fails. A loses 60, then C loses 48. The ledger explains each number.” |
| 6:30–7:30 | Matrix tab, then Compare | “This is the same directed exposure data, not a different correlation dataset. We have isolated representation rather than changed information.” |
| 7:30–8:30 | Recovery control at 100%, then reset | “The assumed recovery changes the model outcome. Changing only the view does not.” |
| 8:30–9:30 | Direct-only vs cascade table | “This numerical baseline tests later propagation. It is separate from our visual baseline.” |
| 9:30–10:30 | Notebook 04 checks; notebook 05 empty study status | “The arithmetic and data parity are verified. Human-performance improvement has not yet been measured.” |
| 10:30–12:00 | Recruitment and timeline | “Open invitation, screening, pilot, controlled study, paired analysis. We will report the experience distribution and uncertainty.” |

## Exact click sequence

1. **Reset guided example.** Top cards show final outcomes; the slider starts at round zero.
2. **Graph:** point out C→A→B loan arrows. Explain that loss flows the other way.
3. Advance **Round** to 1: A fails; ledger entry borrower B → lender A, loss 60.
4. Advance to 2: C fails; borrower A → lender C, loss 48.
5. Select **Matrix**: A/B cell is 100; C/A cell is 80. Failure marks and round slider describe the same calculation.
6. Select **Compare** for discussion, not a controlled-study trial.
7. Move **Recovery** to 100% and release: final failures 1, posted interbank loss 0. Reset to restore the reference scenario.
8. Optional: choose the six-bank branch and show E/F surviving; or generate 12 banks to demonstrate scalability beyond the teaching chain.
9. Optional: **Download evidence JSON**, then show `/docs` → `/visualization` schema. No need to edit raw API requests live.
10. Optional recorder demonstration: select Graph or Matrix, start a practice lookup, answer 100 for A→B. Clearly call it practice; do not present its time as a study result.

## Questions the panel may ask

**1. What is the research question in one sentence?**

Whether a graph, compared with a matched exposure matrix, helps eligible users trace synthetic financial-loss propagation more accurately, efficiently and explainably, and how that depends on task and experience.

**2. What changed from the original proposal?**

We narrowed multiple financial relationship types to directed credit exposures, established a reproducible ground-truth engine, and now connect it to matched visual views. The original human-comparison objective is preserved; production breadth is deferred.

**3. What is new if similar dashboards already exist?**

The current engineering contribution is transparent, reproducible loss provenance and matched visual conditions. The intended empirical contribution is a task-specific comparison in this setting. We do not claim a new graph algorithm, new contagion theory or global first without a fuller novelty review.

**4. Why not use correlation heatmaps, as originally proposed?**

Correlation measures co-movement, not an amount owed. Comparing a correlation matrix with a loan graph changes semantics. The fair main comparison uses the same exposure matrix and graph; a correlation study would require its own question and model.

**5. What is the current solution/baseline?**

The visual baseline is a conventional directed exposure-matrix heatmap with matching controls. Existing financial visual systems are literature precedents, not rerun competitors. The numerical baseline is a separate direct-loss-only control.

**6. Are you comparing a weak static matrix against a rich interactive graph?**

No. Both have round navigation, exact loan values, state information and bank inspection. A formal study must freeze the permitted interactions, equal training and fair viewport budget. The current MVP is not proof that either implementation is optimal.

**7. Why synthetic data?**

Known exposures and accounts let us check the answer independently and vary scenarios. Public FDIC fields used here do not identify bilateral counterparties. Synthetic data limit external validity; they are appropriate for a controlled mechanism and comprehension experiment, not historical reconstruction.

**8. Then what is the role of the real-data notebook?**

It demonstrates how an assumed asset loss consumes capital in real reported balance sheets. It provides context and a separate empirical-data workflow. It neither identifies a real contagion network nor validates fictional failures.

**9. Does Atlas predict actual failures?**

No. Outcomes are conditional on haircut, exposures, recovery and zero-equity rules. Legal default, liquidity, policy response and resolution details are outside this simplified model.

**10. Why does B retain positive equity after being marked failed?**

We imposed B's credit event to test propagation. Forced failure does not arbitrarily erase its book equity. Endogenous failures occur when modeled equity is at or below zero.

**11. Why do arrows and losses move in opposite directions?**

An arrow records the loan from lender to borrower. When the borrower does not repay, the lender loses an asset, so the loss travels backward along that relationship.

**12. How do you know the code is correct?**

Independent arithmetic fixtures establish 60 and 48 losses; validators reconcile accounts; tests cover boundaries, invalid inputs and shared evidence. Notebook replay and browser checks establish tested implementation behavior, not economic predictive validity.

**13. What does “48 additional loss” prove?**

Only that later transmission rounds add 48 synthetic units relative to the specified one-generation control. It does not measure a graph's advantage over a matrix.

**14. Are graphs better according to your literature?**

Not universally. The inspected studies differ in tasks, data, interactions and learning. This motivates testing path tasks and lookup separately and reporting null or reversed findings honestly.

**15. What exactly is interpretability?**

Operationally: a participant can identify the relevant loss event, state its amount, and explain why the equity threshold is crossed. Score with a predefined blind rubric. Confidence and preference are separate subjective outcomes.

**16. Who will participate?**

An open Google Form will invite qualified or interested volunteers. Financial analysts are especially relevant. Eligibility uses consent, basic tutorial understanding and technical requirements; experience is recorded and results describe the actual recruited sample.

**17. How will you prevent unfair or invalid comparisons?**

Matched evidence and controls, equal training, balanced condition order, parallel stimuli, frozen answer keys, task timers, predefined exclusions and participant-level analysis. Do not exclude people for disliking the graph or giving incorrect answers.

**18. Is the sample size enough?**

No main sample is collected yet. Pilot variability and a practical effect/precision target will inform recruitment. A provisional logistical target is not a power calculation. Too few valid sessions means exploratory findings with limitations.

**19. What if there is no graph advantage?**

Report it. A matrix advantage for lookup or a null path result identifies where each representation is useful. The research is a comparison, not a commitment to a predetermined winner.

**20. Is “real-time” live market data?**

No. It means the local interface recomputes a scenario interactively and replays its rounds. The inputs are frozen or synthetic; no live financial feed is required.

**21. Why not a full React application and database now?**

The MVP uses local SVG/HTML and FastAPI to make today's comparison reliable and reproducible. The API separates calculations from presentation so a larger frontend can be added later. Storage/hosting and the formal collector are later implementation tasks.

**22. What is your conclusion so far?**

We have a verified mechanism, a working visual comparison, a grounded research question and an explicit evaluation plan. We have not yet established human-performance benefits, historical failure prediction or production readiness.

**23. What do you need from the panel?**

Feedback on the narrowed RQ, baseline fairness, participant eligibility, task selection and intended contribution; agreement on the remaining study and final-submission scope.
