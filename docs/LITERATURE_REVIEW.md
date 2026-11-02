# Focused literature review: financial contagion and visual comparison

Prepared 2 November 2026. Primary publisher/author sources were opened for this review. This is a targeted reading set, not a systematic search; no claim of novelty follows merely from these eight papers. Summaries are deliberately limited to inspected evidence. Atlas implications below are our proposed design decisions.

## Closest financial visual-analytics precedents

### L1. Niu, Li, Wu, Cheng & Zhang (2020), iConViz

*iConViz: Interactive Visual Exploration of the Default Contagion Risk of Networked-Guarantee Loans.* IEEE VAST 2020 paper, author manuscript [arXiv record](https://arxiv.org/abs/2006.09542), [full text](https://arxiv.org/html/2006.09542v3).

- **Question/system:** explore default contagion in enterprise loan-guarantee networks using coordinated network, chain, node and contagion-effect views.
- **Evidence inspected:** system design, case studies and expert interviews; the review describes two risk-control managers and five specialists from one bank.
- **Boundary:** guarantee networks differ from our direct interbank lending exposures. This is not a controlled graph-versus-identical-matrix accuracy result.
- **Atlas inference:** expose the chain and the financial quantities behind a highlighted path. Integrate exact evidence with an overview, but independently evaluate our own representation comparison.
- **Panel use:** establishes that financial contagion visual analytics already exists; our novelty cannot simply be “finance + graph.”

### L2. Niu et al. (2021), Regshock

*Regshock: Interactive Visual Analytics of Systemic Risk in Financial Networks.* [Author preprint](https://arxiv.org/abs/2104.11863), [full text](https://arxiv.org/html/2104.11863v1). Treat this inspected version as a preprint; this review does not verify a later publication venue.

- **Question/system:** support exploration of financial risk and intervention strategies using a risk-island representation, details and intervention assessment views.
- **Evidence inspected:** case studies and a review with eight financial experts after a tutorial.
- **Boundary:** positive expert feedback is not proof that Atlas's graph beats a matched exposure matrix. Its risk model, visual design and intervention scope differ from ours.
- **Atlas inference:** enable changing one assumption and seeing the consequences immediately; retain provenance for the scenario and label model scope. Claim a reproducible teaching/research MVP rather than a new supervisory intervention system.

## Direct representation-comparison evidence

### L3. Ghoniem, Fekete & Castagliola (2005)

*On the Readability of Graphs Using Node-Link and Matrix-Based Representations: A Controlled Experiment and Statistical Analysis.* Information Visualization 4(2), 114–135. DOI [10.1057/palgrave.ivs.9500092](https://doi.org/10.1057/palgrave.ivs.9500092). Inspected [author manuscript at INRIA](https://www-sop.inria.fr/orion/COGC/teams/INSITUghoniem-fivj05-final.pdf).

- **Evidence:** a controlled comparison over seven graph tasks. In the tested conditions, matrices generally performed better on many tasks for graphs larger than twenty vertices, while path finding favored node–link views.
- **Boundary:** these are results for the tested graphs, tasks, layouts and interaction settings, not a universal twenty-node cutoff. The paper's pictured networks are undirected, unlike Atlas's lending networks.
- **Atlas inference:** keep a credible matrix baseline; test paths separately from direct lookup and vary size/density. A matrix win is plausible and must remain publishable.

### L4. Ren et al. (2019)

*Understanding node-link and matrix visualizations of networks: A large-scale online experiment.* Network Science. Inspected [publisher abstract and bibliographic record](https://www.cambridge.org/core/journals/network-science/article/abs/understanding-nodelink-and-matrix-visualizations-of-networks-a-largescale-online-experiment/C293136C4761F09D4C2C328E2BC19287).

- **Evidence available:** the abstract reports N=600, 20-/50-node social networks, node–link versus two matrix sorting variants, and task-time/accuracy measures. It reports a node–link advantage and matrix learning over the experiment.
- **Boundary:** this review inspected the publisher abstract, not the full statistical methods; do not quote effect sizes or detailed significance from it. Social-network comprehension does not directly establish finance-task performance.
- **Atlas inference:** interaction, matrix order, training and learning are part of the experimental condition. Equal tutorials and counterbalanced ordering are needed; the earlier literature does not justify assuming one inevitable winner.

## Task design and temporal navigation

### L5. Brehmer & Munzner (2013)

*A Multi-Level Typology of Abstract Visualization Tasks.* IEEE TVCG 19(12), 2376–2385. [Author project page](https://www.cs.ubc.ca/labs/imager/tr/2013/MultiLevelTaskTypology/), [author paper](https://www.cs.ubc.ca/labs/imager/tr/2013/MultiLevelTaskTypology/brehmer_infovis13.pdf).

- **Contribution:** distinguishes why an analysis is performed, what inputs/outputs it uses, and how the interaction is carried out.
- **Boundary:** a task framework is not empirical proof that our design is effective.
- **Atlas inference:** replace “understand systemic risk” with scored actions: read a directed loan, identify secondary failures, reconstruct a loss-transmission sequence, and explain why a bank crosses zero equity. Specify the answer before a participant sees the stimulus.

### L6. Bach, Pietriga & Fekete (2014), GraphDiaries

*GraphDiaries: Animated Transitions and Temporal Navigation for Dynamic Networks.* IEEE TVCG 20(5), 740–754. DOI [10.1109/TVCG.2013.254](https://doi.org/10.1109/TVCG.2013.254). [Author project and paper](https://aviz.fr/~bbach/graphdiaries/), [publisher abstract](https://ieeexplore.ieee.org/document/6658746/).

- **Evidence:** presents temporal navigation and staged transitions for dynamic networks; reports improvements on several tasks in its study.
- **Boundary:** Atlas's current replay changes failure states on fixed exposures; it is not a reproduction of GraphDiaries or a test of animation itself.
- **Atlas inference:** preserve coordinates across cascade rounds and provide explicit stepping/playback. Both comparison conditions get equivalent temporal controls. A separate animation ablation would be needed to isolate animation benefits.

## Financial mechanism foundations (supporting, not HCI evidence)

### L7. Furfine (1999 working paper; later published 2003)

*Interbank Exposures: Quantifying the Risk of Contagion.* BIS Working Paper 70. [BIS source](https://www.bis.org/publications/working-paper-70-interbank-exposures-quantifying-risk-contagion).

- **Role:** an established default-contagion foundation for studying losses through interbank exposures.
- **Atlas inference:** use explicit loan amounts, loss given default, and a clear failure threshold. Verify propagation independently on a hand-computable chain.
- **Boundary:** Atlas uses synthetic accounts and documented synchronous, fixed-recovery conventions; it does not recreate Furfine's empirical data or claim a new contagion algorithm. This paper supplies model context, not evidence about visual comprehension.

### L8. Battiston, Puliga, Kaushik, Tasca & Caldarelli (2012)

*DebtRank: Too Central to Fail? Financial Networks, the FED and Systemic Risk.* Scientific Reports 2, 541. [Publisher full text](https://www.nature.com/articles/srep00541), DOI [10.1038/srep00541](https://doi.org/10.1038/srep00541).

- **Role:** network distress can be analyzed beyond a simple binary default count.
- **Atlas inference:** distinguish structural centrality, conditional forced-default impact, and distress scores. Do not label all three as the same “systemic risk score.”
- **Boundary:** Atlas's one-active-step implementation includes explicit LGD and asset-weight choices. DebtRank is supporting exploration, not the primary user-study stimulus or a calibrated failure probability.

## Synthesis for the proposed RQ

1. Financial contagion visual systems are established (L1–L2); a dashboard alone is insufficient novelty.
2. Encoding advantages are conditional (L3–L4); use identical data and specific tasks rather than compare different financial relationships.
3. Comprehension requires operational measures (L5); use ground-truth answers and blind explanation scoring.
4. Temporal behavior is an interaction factor (L6); keep it equivalent across the two encodings in the main study.
5. The engine is an experimental foundation (L7–L8), not the visualization outcome.

**Proposed contribution:** a reproducible, evidence-linked comparison of interactive graph and exposure-matrix encodings for directed synthetic financial-loss propagation. Whether it improves participant outcomes is the question to test. These papers motivate that local question; they do not establish that no prior work has asked an overlapping question.

Before final submission, expand the search with forward/backward citations, additional directed weighted-network comparisons, contemporary financial visual analytics, and justified matrix-ordering alternatives. Record databases, query strings, inclusion/exclusion decisions and full-text access. The present set is appropriate to ground a mid-term scope, not a completed systematic survey.
