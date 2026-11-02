"""Author the two mid-term visualization notebooks; replay uses Run All instead.

This authoring script overwrites notebooks 04/05, not existing notebooks 01–03.
"""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def markdown(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    return nbf.v4.new_code_cell(text.strip())


def write(name, cells):
    notebook = nbf.v4.new_notebook(cells=cells)
    notebook.metadata.kernelspec = {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata.language_info = {"name": "python", "version": "3.12"}
    nbf.write(notebook, ROOT / "notebooks" / name)


def main():
    write(
        "04_visualization_comparison.ipynb",
        [
            markdown("""
# ATLAS · From contagion engine to visual analytics
## Mid-term demonstration · 2 November 2026

**Question:** Does an interactive graph help users trace financial-loss propagation
more accurately and efficiently than an exposure-matrix heatmap of the **same** network?

This notebook verifies the experimental foundation. It does **not** contain user-study results.
The proposed participant pool is open recruitment, screened for basic task understanding,
with domain experience recorded and financial analysts particularly relevant.

**Two comparisons:** graph vs matrix changes the visual encoding; direct-loss vs full cascade
changes the financial propagation model. A model difference is not a visualization improvement.
        """),
            code(r"""
from pathlib import Path
import hashlib
import json
import platform
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from IPython.display import display
from atlas.generate import generate
from atlas.models import Scenario
from atlas.visualization import teaching_fixture, visualization_payload

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'pyproject.toml').exists())
OUT = ROOT / 'reports' / 'visualization'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'figure.dpi': 130, 'font.size': 10, 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.facecolor': '#fffefa'})
data = teaching_fixture('chain')
scenario = Scenario(initial_defaults=['B'], recovery=0.4)
evidence = visualization_payload(data, scenario)
print('Data: fictional banks; amounts in', data.units)
print('Dataset fingerprint:', evidence['dataset_hash'])
        """),
            markdown("""
## 1 · A controlled example with an answer we can check

A lends 100 to B. C lends 80 to A. Starting equity is A=50, B=50, C=40.
B is forced to fail; recovery is 40%; the external haircut is zero.

- A loses 100 × 60% = **60**, leaving equity **−10**.
- C then loses 80 × 60% = **48**, leaving equity **−8**.
- The full cascade posts **108**; the direct-loss control posts **60**.

Loan arrows point **lender → borrower**; losses travel **borrower → lender**.
A forced default can retain positive book equity. All figures are synthetic teaching units.
        """),
            code(r"""
comparison = pd.DataFrame({
    'Outcome': ['Initial defaults', 'Secondary defaults', 'Total defaults', 'Interbank loss'],
    'Direct only': [len(evidence['baseline']['initial_defaults']), len(evidence['baseline']['secondary_defaults']),
                    evidence['baseline']['default_count'], evidence['baseline']['interbank_loss']],
    'Full cascade': [len(evidence['cascade']['initial_defaults']), len(evidence['cascade']['secondary_defaults']),
                     evidence['cascade']['default_count'], evidence['cascade']['interbank_loss']],
})
assert evidence['baseline']['interbank_loss'] == 60
assert evidence['cascade']['interbank_loss'] == 108
assert evidence['cascade']['equity'] == {'A': -10, 'B': 50, 'C': -8}
display(comparison)
display(pd.DataFrame(evidence['cascade']['events']))
        """),
            markdown("""
## 2 · Same loans, two encodings

These displays are built from the same payload. Neither receives extra hidden exposures.
The graph below is at round zero: B is the forced initial failure. The matrix contains
original loan amounts; it is **not** a price-correlation matrix. Both are valid views of the same data.
        """),
            code(r"""
ids = evidence['matrix']['ids']
matrix = np.array(evidence['matrix']['values'])
graph = nx.DiGraph()
graph.add_nodes_from(ids)
graph.add_weighted_edges_from((e['lender'], e['borrower'], e['amount']) for e in evidence['edges'])
positions = {n['id']: (n['x'], n['y']) for n in evidence['nodes']}
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
nx.draw_networkx(graph, positions, ax=axes[0], arrows=True, arrowsize=22,
                 node_color=['#b83b3f' if i == 'B' else '#166c60' for i in ids],
                 font_color='white', node_size=1000, edge_color='#84998d', width=2.5)
nx.draw_networkx_edge_labels(graph, positions, ax=axes[0], edge_labels=nx.get_edge_attributes(graph, 'weight'))
axes[0].set_title('Graph: lender → borrower\nRound 0: B forced to fail')
axes[0].axis('off')
image = axes[1].imshow(matrix, cmap='Greens', vmin=0, vmax=100)
axes[1].set_xticks(range(len(ids)), ids); axes[1].set_yticks(range(len(ids)), ids)
axes[1].set_xlabel('Borrower'); axes[1].set_ylabel('Lender')
axes[1].set_title('Exposure matrix: identical original loans')
for i in range(len(ids)):
    for j in range(len(ids)):
        axes[1].text(j, i, f'{matrix[i,j]:g}', ha='center', va='center',
                     color='white' if matrix[i,j] > 50 else '#183332')
fig.colorbar(image, ax=axes[1], label='Synthetic loan amount', shrink=.75)
fig.savefig(OUT / 'graph_matrix.png', bbox_inches='tight')
plt.show()
        """),
            markdown("""
## 3 · Trace the loss, round by round

Positions stay fixed. Each newly failed borrower transmits once, to creditors alive at the
start of that round. The ledger distinguishes the initial failure from secondary failures.
Rounds are computational steps, not days.
        """),
            code(r"""
rounds = evidence['cascade']['rounds']
fig, axes = plt.subplots(1, 3, figsize=(11, 3.5), constrained_layout=True)
for r, ax in zip(rounds[:3], axes):
    colors = ['#b83b3f' if n['default_round'] == r['round'] else
              '#80323c' if n['default_round'] is not None and n['default_round'] < r['round'] else
              '#166c60' for n in evidence['nodes']]
    nx.draw_networkx(graph, positions, ax=ax, arrows=True, arrowsize=20,
                     node_color=colors, font_color='white', node_size=800, edge_color='#93a398')
    ax.set_title(f"Round {r['round']} | new: {', '.join(r['new_defaults']) or 'none'}")
    ax.set_xlabel('Equity: ' + ', '.join(f'{bid}={r["equity"][bid]:g}' for bid in ids))
    ax.set_xticks([]); ax.set_yticks([])
fig.savefig(OUT / 'cascade_rounds.png', bbox_inches='tight')
plt.show()
display(pd.DataFrame([{'round': r['round'], 'new_failures': ', '.join(r['new_defaults']),
                       'cumulative_failures': r['cumulative_defaults'], 'new_loan_loss': r['interbank_loss']}
                      for r in rounds]))
        """),
            markdown("""
## 4 · Change one assumption

At 50% recovery, A and then C reach exactly zero equity and fail under our threshold.
At 51%, A remains solvent and does not propagate. At 100%, there are no interbank losses,
but forced B remains an initial failure. These are conditional arithmetic results.
        """),
            code(r"""
rows = []
for recovery in [0, .2, .4, .5, .51, .6, .8, 1]:
    result = visualization_payload(data, Scenario(initial_defaults=['B'], recovery=recovery))
    rows.append({'recovery': recovery, 'defaults': result['cascade']['default_count'],
                 'direct_loss': result['baseline']['interbank_loss'], 'cascade_loss': result['cascade']['interbank_loss']})
sensitivity = pd.DataFrame(rows)
assert sensitivity.loc[sensitivity.recovery == .5, 'defaults'].iloc[0] == 3
assert sensitivity.loc[sensitivity.recovery == .51, 'defaults'].iloc[0] == 1
assert sensitivity.iloc[-1].cascade_loss == 0
display(sensitivity)
fig, ax = plt.subplots(figsize=(8, 3.4), constrained_layout=True)
ax.plot(sensitivity.recovery * 100, sensitivity.direct_loss, 'o--', color='#8a9c91', label='Direct loss only')
ax.plot(sensitivity.recovery * 100, sensitivity.cascade_loss, 'o-', color='#166c60', label='Full cascade')
ax.set(xlabel='Recovery (%)', ylabel='Posted interbank loss (synthetic units)', title='Model sensitivity, not a visualization effect')
ax.legend(); fig.savefig(OUT / 'recovery_sensitivity.png', bbox_inches='tight'); plt.show()
sensitivity.to_csv(OUT / 'recovery_sensitivity.csv', index=False)
        """),
            markdown("""
## 5 · Branching and scale checks

The six-bank fixture includes survivors and simultaneous losses. Generated cases exercise
larger layouts. We check exact matrix-edge parity and report **local payload computation time**,
which includes layout and network metrics. This is not browser rendering latency or participant time.
Only three timing repeats are used; the timing is a smoke diagnostic, not a performance claim.
        """),
            code(r"""
branch = visualization_payload(teaching_fixture('branch'), Scenario(initial_defaults=['B']))
assert branch['cascade']['interbank_loss'] == 180
assert branch['baseline']['interbank_loss'] == 90
assert branch['cascade']['defaults'] == ['A', 'B', 'C', 'D']
cases = [('chain', data), ('branch', teaching_fixture('branch'))]
cases += [(f'generated_{n}', generate(n, 42)) for n in [12, 24, 50]]
checks = []
for name, dataset in cases:
    initial = 'B' if name in ['chain', 'branch'] else dataset.banks[0].id
    settings = Scenario(initial_defaults=[initial], recovery=.4)
    durations = []
    for _ in range(3):
        start = time.perf_counter()
        result = visualization_payload(dataset, settings)
        durations.append((time.perf_counter() - start) * 1000)
    order = result['matrix']['ids']
    rebuilt = {(order[i], order[j]): value for i, row in enumerate(result['matrix']['values'])
               for j, value in enumerate(row) if value != 0}
    expected = {(e.lender, e.borrower): e.amount for e in dataset.exposures}
    assert rebuilt == expected
    checks.append({'case': name, 'banks': len(order), 'loans': len(expected),
                   'matrix_edge_parity': rebuilt == expected,
                   'direct_loss': result['baseline']['interbank_loss'],
                   'cascade_loss': result['cascade']['interbank_loss'],
                   'median_payload_ms': float(np.median(durations))})
checks = pd.DataFrame(checks)
display(checks)
checks.to_csv(OUT / 'engineering_checks.csv', index=False)
        """),
            markdown("""
## 6 · What can we conclude today?

| Claim | Status |
| --- | --- |
| A controlled failure propagates through explicit exposures | Verified on hand-calculated examples |
| Both encodings receive identical loan evidence | Verified by assertions; browser QA checks interaction |
| The demo responds to changed assumptions | Implemented; sensitivity shown above |
| Users perform better with graphs | **Not evaluated** |
| The model predicts actual bank defaults | **Not claimed** |

The real FDIC analysis in notebook 03 remains contextual evidence about capital sensitivity.
It does not supply this synthetic loan network. The next research step is a controlled
participant comparison with preregistered tasks, matched information, counterbalancing,
experience reporting and uncertainty—not declaring a graph victory from a screenshot.

For the panel: open the dashboard, step through the chain, switch to Matrix, then set recovery
to 100%. See the research brief, literature review and study protocol in `docs/`.
        """),
            code(r"""
summary = {
    'scope': 'Synthetic visual-comparison MVP; no human-performance findings',
    'python': platform.python_version(),
    'chain_direct_loss': 60, 'chain_cascade_loss': 108, 'chain_added_loss': 48,
    'branch_cascade_loss': 180,
    'all_matrix_edge_checks_passed': bool(checks.matrix_edge_parity.all()),
    'human_study_status': 'not evaluated',
    'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted((ROOT / 'src' / 'atlas').glob('*.py'))},
}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2))
(OUT / 'chain_evidence.json').write_text(json.dumps(evidence, indent=2))
print('Saved numerical evidence and figures to', OUT.relative_to(ROOT))
        """),
        ],
    )
    write(
        "05_visualization_study_analysis.ipynb",
        [
            markdown("""
# ATLAS · Visualization study analysis scaffold

**Status: no participant data collected.** This notebook intentionally reports “not evaluated.”
It is ready to validate the agreed schema and compute per-task participant-paired descriptive
summaries when genuine eligible study data become available. It is not a completed final analysis.

Recruitment will be open through a Google Form, with relevant knowledge/interest, a tutorial,
comprehension screening, consent and experience recording. Financial analysts are especially
relevant; claims must describe the people actually recruited. Practice rows are never study evidence.
        """),
            code(r"""
from pathlib import Path
import json
import pandas as pd
from IPython.display import display
from atlas.study import eligible_trials, paired_summary

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'pyproject.toml').exists())
# For future analysis, explicitly choose an untracked, de-identified input file.
INPUT = ROOT / 'data' / 'study' / 'trials_template.csv'
trials = pd.read_csv(INPUT)
valid, audit = eligible_trials(trials)
display(pd.DataFrame([audit]))
print('NOT EVALUATED: no eligible participant records.' if valid.empty else
      'Records available: verify protocol, allocation, exclusions and sample before interpretation.')
        """),
            markdown("""
## Proposed estimands

- Primary: participant-level accuracy difference (graph − matrix) over propagation tasks,
  with equal weighting of the frozen task/stimulus cells.
- Secondary: capped elapsed-time difference alongside errors and timeouts; blind explanation
  score difference; confidence as a separate subjective measure.
- Exploratory: direct lookup, size/density, experience and professional analyst subgroup.

The helper below computes **per-task** paired summaries only. Equal trial counts do not prove
balanced stimuli. Final combined analysis, stimulus effects, exclusions, multiplicity and
power/precision planning must be frozen before main collection. Bootstrap intervals resample
participants, not independent trials. No confidence interval is produced for a single pair.
        """),
            code(r"""
summaries = [paired_summary(trials, task) for task in ['lookup', 'secondary', 'path']]
display(pd.DataFrame([{'task': s['task'], 'paired_participants': s['paired_participants'],
                       'status': s['status']} for s in summaries]))
if valid.empty:
    print('No effect sizes, p-values, task-time advantages or workload results can be reported.')
else:
    for summary in summaries:
        print(json.dumps(summary, indent=2))
        """),
            markdown("""
## Before promoting this to the main analysis

1. Agree and freeze the question, hypotheses and study protocol with the supervisor.
2. Pilot a counterbalanced runner using parallel nontrivial stimuli; do not reuse the teaching chain.
3. Publish the invitation only after consent, data handling and any institutional review are settled.
4. Record condition order, task order, fixture/version/hash, interruptions and experience strata.
5. Apply predefined exclusions, retaining incorrect responses and timeouts.
6. Report paired effects, intervals, uncertainty, sample composition and qualitative explanations.

Dashboard practice exports are rehearsal data with a different schema. Do not rename their
record type to manufacture study rows. Artificial records used in unit tests are software checks,
not observations and never enter these saved notebook outputs.

See `docs/VISUALIZATION_STUDY_PROTOCOL.md` and `data/study/README.md`.
        """),
        ],
    )


if __name__ == "__main__":
    main()
