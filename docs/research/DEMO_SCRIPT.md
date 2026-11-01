# Ten-minute panel walkthrough

0:00–1:00 — Question and finance: equity is the loss buffer; explain E−qA using assets 100 and equity 10. A 5% loss leaves 5; 10% exhausts the buffer.

1:00–2:00 — Literature: explain why bank financials are public while bilateral lending is not supplied by these files. Cite reconstruction literature and distinguish implementation verification from empirical validation.

2:00–3:30 — Data: show FDIC source/manifest, eligible rows, fixed cohort and accounting residuals. Explain why EQTOT is used, USD thousands converted to millions, and why matching by CERT matters.

3:30–4:30 — Observed changes: explain December-to-June capital ratios. Avoid causal claims about COVID. These are revised historical reports.

4:30–6:00 — Model: show q*=E/A, the sensitivity curves and historical drawdown. Explain that 0.3 is an assumed mapping, not an estimated coefficient. Change the multiplier list or shock grid and rerun those cells if desired.

6:00–7:30 — Results: use the executed scenario table. Explain capital exhaustion and shortfall; do not call these actual defaults. Ask what omitted earnings, policy or heterogeneous exposures could change.

7:30–8:30 — Contagion: walk through the synthetic three-bank chain (60 then 48). The actual contagion engine works, but no observed named-bank network is claimed.

8:30–10:00 — Verification and future work: show assertions and saved outputs. Engineering contribution is the reproducible pipeline; future research compares reconstructed networks with fixed financial margins. If visual analytics returns, compare a node-link view against the same exposure matrix.

If asked why no realistic contagion on named banks: the public fields audited here do not identify their counterparties or compatible lending/borrowing margins. Adding arbitrary edges would change the question. The current empirical model is a complete limited-scope study; the network mechanism has independent controls.
