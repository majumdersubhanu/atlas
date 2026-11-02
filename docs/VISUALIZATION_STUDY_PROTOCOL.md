# Visualization study protocol — draft for faculty review

Version 0.1, 2 November 2026. **No research participants have been run.** This protocol is proposed, not preregistered. The dashboard's optional timed task is labeled `rehearsal`; it is insufficient for confirmatory collection.

## Recruitment and eligibility

Recruit openly through a Google Form. Financial analysts are especially relevant; anyone with relevant qualifications, experience or interest who can understand the task and provide valid input may volunteer. Describe the actual resulting sample. Do not imply that an open-interest sample represents professional analysts.

Proposed eligibility: adult consenting volunteers; a desktop/laptop with a supported browser; ability to read the study language; and completion of a brief banking/network tutorial plus a comprehension check before allocation. No financial credential is mandatory. Record experience before the study so professional/relevant-experience and interest-only responses can be reported separately. Final categories and inclusion rules must be frozen before main collection.

Comprehension check (training questions, not outcome questions): identify lender versus borrower; compute loss on a 100-unit loan at 40% recovery; explain why a positive-capital bank can be forced to fail. Allow a tutorial retry, record the attempt, and report training failures. Do not exclude participants because they score poorly on the experimental tasks.

Google Form is the invitation/screening and scheduling mechanism, not a precise task timer. Browser instrumentation records task times. Keep contact information separate from anonymous session IDs; do not commit participant data to GitHub. Collect only fields necessary for screening/scheduling. Final consent, retention duration and institutional review requirements must be settled with the supervisor before recruitment begins.

### Ready-to-copy Google Form draft

**Title:** Volunteer for the Atlas financial-network visualization study

**Description:** We are studying how people use graphs and matrix heatmaps to understand hypothetical losses in a financial network. You do not need a specific qualification to express interest. Financial analysts and people with relevant experience are especially welcome. A short tutorial and comprehension check precede participation. The proposed session takes approximately 30–45 minutes on a desktop/laptop. This is research about an interface, not financial advice or a test of professional competence. Participation is voluntary. We will confirm eligibility, consent details and scheduling before your session.

| Field | Suggested type | Purpose |
| --- | --- | --- |
| Preferred contact email | Short answer | Scheduling only; separate storage from task results |
| Are you 18 or older? | Yes/no | Proposed adult-only protocol |
| Describe your relevant work, qualifications or interest | Paragraph | Open eligibility and sample description |
| Experience with finance/risk analysis | None; under 1 year; 1–3; 4–7; 8+ years | Predeclared experience strata |
| Familiarity with balance sheets | 1–5 scale | Covariate, not an automatic exclusion |
| Familiarity with network graphs / heatmaps | Two 1–5 scales | Prior visualization experience |
| Access to desktop/laptop and suitable browser | Yes/no | Interface suitability |
| Preferred session availability and timezone | Paragraph | Scheduling |
| May we contact you about this study? | Required yes/no | Recruitment contact consent only |
| Accessibility or accommodation needs | Optional paragraph | Arrange support without unnecessary sensitive detail |

Replace or add supervisor contact, host institution, retention policy and withdrawal instructions before publication. The form has **not** been created or distributed by this work. A separate study-information/consent step is required; invitation contact consent is not consent to research recording.

## Conditions: what changes and what stays fixed

- **M:** directed exposure-matrix heatmap, stable bank-ID order.
- **G:** node–link graph, seeded fixed positions.
- Same dataset, loan direction, amount precision, node states, scenario, round navigation, inspection access, viewport budget, color key, tutorial duration and task prompts.
- In the isolated study, show only the assigned representation. No combined view; no automatic answer table, full loss ledger, impact ranking or reveal-before-submit. Decide which node facts/tooltips are allowed and give both conditions equivalent access.
- The graph layout and matrix order are part of the tested implementation. A stronger future study should compare credible ordering/layout alternatives rather than assume these are optimal.
- Side-by-side and shared explanatory tables remain available in **exploration/demo mode**. That experience answers a different design question from G versus M.

## Stimuli and tasks

Use synthetic directed weighted loans because complete exposures, accounting and ground-truth propagation are known. Use the three-bank chain for teaching only. It is too simple for a substantive study and repeating it would cause memory effects.

Proposed main corpus: 12- and 24-bank networks, with sparse/denser exposure settings and several balanced seeds per cell. Existing generator families also vary financial scale; do not call differences causal density effects. Create matched financial fixtures or treat size/density descriptively if independent control is not feasible. Screen for nontrivial scenarios without selecting only graph-friendly examples. Include no-propagation and surviving-branch cases. Freeze fixture hashes, all answer keys and selection criteria before main data collection.

| Task | Prompt pattern | Ground truth / score |
| --- | --- | --- |
| T1: direct lookup (comparison task) | How much did X lend to Y? | Numeric amount; predeclared rounding tolerance |
| T2: identify propagation | Which banks fail after the initially failed bank(s)? | Exact set primary; set precision/recall as secondary; no penalty-free extra guesses |
| T3: trace a specified transmission | List the borrower-to-creditor sequence by which this event reaches Z | Event-ledger-backed sequence; distinguish loan direction from loss direction; allow all prespecified equivalent valid answers |
| T4: explain a threshold crossing | Why did Z fail in round r? | Blind 0–3 rubric: correct source/event, correct loss amount, correct equity/threshold arithmetic |

When several simultaneous losses jointly cause failure, do not invent a unique causal path. Either ask for the set of contributing events or choose a fixture with an unambiguous trace. For T4, two coders should independently score a subset, reconcile rubric ambiguities, and report agreement. Confidence (1–5) is not explanation correctness.

## Assignment and procedure

1. Consent, experience questionnaire, standardized tutorial and comprehension check.
2. Equal practice with both encodings; practice stimuli are disjoint from measured stimuli.
3. Within-participant comparison. Allocate balanced G→M and M→G sequences, and rotate parallel stimulus sets A/B across conditions. Do not show the exact same labeled question twice to the same person. Across participants each fixture must appear in both representations so fixture difficulty is not confounded with view.
4. Balance task type and size/density within each condition; randomize task order subject to the frozen design. Log allocation and order.
5. Suggested 180-second task limit, confirmed in pilot. Start timing only after the complete stimulus is rendered; stop on submit or timeout. Record hidden-tab/interruption events; preregister their handling. Scenario and condition switching are locked during a measured task.
6. Collect confidence after each response and brief workload/clarity feedback after each condition. If SUS or NASA-TLX is retained from the original proposal, use the official instrument and scoring instructions; do not label a homemade single question as those scales.
7. Short qualitative interview: what was difficult, how direction was interpreted, where trust in the result came from, and when the other view would help.

Pilot suggestion: 5–8 eligible volunteers to debug instructions, ceiling effects and session length; these are not confirmatory participants. Main recruitment target should follow a justified power/precision analysis using pilot variability and a declared practically meaningful difference. A planning range of 24–36 complete sessions is logistical only, not a claim of sufficient power. If recruitment falls short, report exploratory estimates rather than manufacture certainty.

## Outcomes and analysis

- **Primary:** participant-level mean T2/T3 accuracy difference G−M, averaged over balanced task/stimulus cells. Report percentage-point difference and uncertainty. Do not treat every trial from one participant as an independent person.
- **Secondary time:** report times, timeout rate and accuracy jointly. A capped elapsed-time metric includes timeouts; correct-only time is a sensitivity analysis because conditioning on success can bias comparison. Faster wrong answers are not evidence of a better interface.
- **Secondary explanation:** mean blinded rubric score difference, and reliability of scoring.
- **Exploratory:** lookup, task-by-view, size/density, confidence, experience and professional analyst subgroup. Avoid strong subgroup conclusions from small cells.
- **Inference plan:** freeze the participant-paired approach before the main study; bootstrap participants (keeping their repeated trials together) for intervals. For a prespecified hypothesis test, use an appropriate paired/randomization procedure or a model accounting for participant and stimulus effects. Specify multiplicity handling for secondary confirmatory tests. The current analysis helper provides descriptive paired means/intervals, not the full final inferential model.
- **Validity:** exclude only predeclared consent/training failures, duplicates, corrupted sessions and technically unusable records. Log reasons without outcome-based cherry-picking. Analyze incomplete pairs separately; report how many were omitted from paired estimation. Keep incorrect and timed-out tasks.
- **Interpretation:** statistical uncertainty is not a measure of financial-model validity. A task-specific or null finding remains an honest outcome.

## Data contract and readiness gates

`data/study/README.md` and the header-only `trials_template.csv` define the analysis input. `record_type` explicitly separates `study`, `pilot`, `rehearsal` and `test`; the analysis accepts only eligible `study` rows. Participant IDs are pseudonyms. The dashboard exports **rehearsal only** and never silently promotes those rows to study observations.

Before research collection: approve consent/recruitment; implement allocation, task corpus, timeout and interruption tracking; verify equivalent information and no answer leakage; pilot; freeze versions and analysis; choose secure collection/storage; then publish the invitation. None of these pending gates is implied complete by a working timer.
