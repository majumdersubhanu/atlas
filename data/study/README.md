# Study input (no participants yet)

`trials_template.csv` is intentionally header-only. Do not fill it with invented observations. Store genuine de-identified data in an untracked location such as `.runtime/study/trials.csv` and pass that path explicitly in notebook 05. Do not put recruitment contact details in the analysis file or commit human responses.

| Column | Meaning |
| --- | --- |
| record_type | `study`, `pilot`, `rehearsal`, or `test`; only `study` enters the helper |
| participant_id | Pseudonym; never a name/email |
| trial_id | Unique within participant |
| stimulus_id | Versioned fixture/question identifier |
| task | `lookup`, `secondary`, `path`, or another frozen task identifier |
| representation | `graph` or `matrix` |
| correct | 0 or 1 from a prespecified scoring key |
| duration_seconds | Elapsed duration, 0–180 for the provisional cap |
| timeout | 1 requires correct=0 and duration_seconds=180; otherwise 0 |
| eligible | 0 or 1 under frozen consent/training/technical rules, not outcome quality |
| experience_group | Predeclared domain-experience group; report actual sample |
| dataset_hash | Fingerprint of the displayed dataset |

The final collector also needs condition order, task order, stimulus assignment, scenario, UI version, viewport, interruptions, explanation scores and consent linkage through a separate protected register. These can be additional columns; they are not supplied by the minimal template. The current helper does not verify counterbalancing or compute the full primary multi-task estimand. It reports per-task paired descriptive differences and participant-bootstrap intervals only.

Dashboard practice CSV is a different, smaller rehearsal schema. It is intentionally **not** a ready-to-submit study dataset. Preserve its `record_type=rehearsal`; do not relabel it as study. The protocol describes the implementation still needed before recruitment.
