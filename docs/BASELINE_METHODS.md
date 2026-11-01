# Baseline methods and the boundary of the contribution

Sources checked on 30 October 2026. This document separates established methods,
current public supervisory examples, and the deliberately simplified experimental
control implemented in this repository.

## What “current practice” can defensibly mean

There is no single industry-wide algorithm that this prototype can reproduce from
public information. Institution-specific data, calibration, portfolios, jurisdictions
and supervisory objectives differ. Public sources establish several relevant methods;
they do not establish that every institution uses the same pipeline.

Contemporary supervisory analysis already includes network amplification. The ECB's
November 2025 ISA analysis combines banks, funds and insurers, iterating counterparty
losses, liquidity redistribution and forced asset sales. It uses granular supervisory
and commercial data. Its bank default criterion includes a regulatory CET1 threshold,
which is different from Atlas's zero book-equity threshold. The article also studies
correlated counterparty defaults. Atlas does not reproduce that framework, its data,
or its reported results. [ECB, *Integrating contagion risk into the 2025 EU-wide stress
test*](https://www.ecb.europa.eu/press/financial-stability-publications/macroprudential-bulletin/html/ecb.mpbu202511_03.en.html).

Consequently, “existing practice ignores contagion” is not an acceptable claim. The
parallel baseline below is a controlled truncation of our model, intended to reveal
what additional default propagation contributes under otherwise identical assumptions.
It is not advertised as an exact implementation of a bank's current risk system.

## Methods represented or discussed

| Method | Question and output | Status in Atlas | Important distinction |
| --- | --- | --- | --- |
| Static expected credit loss | Given marginal PD, LGD and EAD, what is expected direct credit loss? | `engine.credit_risk` | Expectation under assumptions, not a realized scenario loss |
| Direct-loss-only stress | What happens after external losses and losses from the initially defaulted borrowers? | `baseline.direct_loss_only` | Experimental control; newly insolvent creditors do not transmit |
| Furfine-style cascade | Which further banks fail as counterparty losses consume capital? | `engine.furfine` | Established default-only propagation tradition, with documented Atlas conventions |
| DebtRank-style distress | How can distress transmit before a binary default? | `engine.debt_rank` | One-active-step variant; score is not a default probability |
| Eisenberg–Noe clearing | Which mutually consistent payments settle a network of obligations? | Not implemented | Limited-liability clearing problem, not fixed-recovery loss bookkeeping |

### Static expected credit loss

For lender i and borrower j, Atlas uses

`EL_ij = PD_j × (1 − recovery) × A_ij`,

where `A_ij` is the loan exposure. The Basel framework's IRB treatment uses PD and
LGD to calculate an expected-loss rate for applicable non-defaulted exposures and
converts rates to amounts using exposure. Atlas uses the elementary decomposition;
it does not implement regulatory parameter floors, provisioning treatment, portfolio
segmentation or the rest of the Basel framework. [BCBS, Basel Framework,
CRE35](https://www.bis.org/committees/bcbs/basel-framework/standard/cre?allChapters=true&chapter=50).

This is also not a full IFRS 9 accounting model: discounting, staging, forward-looking
scenario weights, maturity and lifetime expected losses are absent. In particular,
`sum(EL_ij)` is not asserted to equal the average simulated cascade loss. The latter
includes endogenous defaults and uses a survivor-only loss ledger.

### Direct-loss-only control: an explicit computational definition

Let initial equity be `E_i`, external assets be `X_i`, impairment be `s`, and recovery
be `r`. Set `E'_i = E_i − s X_i`. Let `D0` contain explicitly forced defaults and every
bank with `E'_i <= 0`. Compute exactly once:

`L_i = (1 − r) Σ_{j in D0} A_ij` for `i not in D0`, and `L_i = 0` otherwise.

Then `E''_i = E'_i − L_i`. Banks outside D0 with `E''_i <= 0` are recorded as
first-generation secondary defaults. They do **not** create additional losses. Losses
at banks already in D0 are omitted to preserve the cascade's accounting convention.
The function does not call the cascade engine; tests independently check its output.

This is a transparent ablation, not a new economic model. Its usefulness is that the
same dataset, shock, recovery, initial default set and default threshold are held fixed.
Any additional losses in the full cascade arise from later transmission rounds within
these specified models. This is a mechanistic comparison, not evidence that actual
bank losses would equal either result.

### Furfine-style default cascade

Furfine's original study used interbank exposures to simulate the consequences of
bank-failure scenarios. Atlas follows that default-contagion tradition, with fixed
recovery and synchronous waves of losses to surviving creditors. It does not recreate
the paper's dataset or empirical conclusions. [Furfine, BIS Working Paper 70
(1999)](https://www.bis.org/publications/working-paper-70-interbank-exposures-quantifying-risk-contagion).

Atlas stops when no new defaults occur. Its ledger permits negative equity, omits
losses arriving after a lender has already failed, and does not solve for the funding
of recoveries. Total reported loan loss is neither aggregate economic welfare loss nor
a complete resolution balance sheet. These conventions must accompany every result.

### DebtRank

The original DebtRank literature distinguishes distress propagation from binary
cascade models. The implementation here uses a one-active-step state convention,
with LGD-adjusted exposure weights and initial-total-assets weights for aggregation.
Those are stated Atlas choices, not an exact replication of the original empirical
application. [Battiston et al. (2012), *DebtRank: Too Central to Fail?*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3412322/).

Under uniform positive impairment of positive external assets, all nodes are initially
active. In this variant all transmit in the first wave and then become inactive, so the
demo does not display repeated amplification from those nodes. A DebtRank score cannot
be compared numerically to a default count as though they measure the same quantity.

### Clearing models

Eisenberg and Noe formulate a clearing-payment problem in which obligations are resolved
simultaneously subject to limited liability and debt priority. Their existence and
uniqueness analysis is fundamentally different from imposing a fixed recovery fraction
and subtracting losses from creditors' equity. A future implementation would require
its own liabilities representation, external assets, clearing rules and independent
verification. It cannot be added merely by relabeling the existing simulator.
[Eisenberg and Noe (2001), *Systemic Risk in Financial Systems*](https://pubsonline.informs.org/doi/10.1287/mnsc.47.2.236.9835).

## Hand-computed comparison

A lends 100 to B, C lends 80 to A, and initial equity is `(A=50, B=50, C=40)`.
B is forced to default; recovery is 40%; there is no external-asset impairment.
All quantities are synthetic monetary units.

| Quantity | Direct-loss-only control | Full default cascade |
| --- | ---: | ---: |
| Initial defaults | B | B |
| Loss on A's claim on B | 60 | 60 |
| A's remaining equity | −10 | −10 |
| Loss on C's claim on A | 0 (suppressed) | 48 |
| C's remaining equity | 40 | −8 |
| Secondary defaults, excluding initial B | A (1) | A and C (2) |
| Total defaults | 2 | 3 |
| Recorded interbank loss | 60 | 108 |

The cascade adds 48 in later-round losses and one further default. Do not say the
baseline has zero secondary defaults: A fails after the first loss update even though
its failure is not propagated. This comparison is asserted in `tests/test_baseline.py`.

## What is and is not novel

The defensible present contribution is an inspectable software and experimental
framework: consistent synthetic balance sheets, explicit loss conventions, independently
checked controls, notebook explanations, sensitivity studies and replayable results.
Neither PD–LGD–EAD, default cascades, DebtRank, graph metrics nor Monte Carlo simulation
is a new algorithm introduced by Atlas.

No experiment here establishes superior prediction accuracy, supervisory adequacy,
empirical forecasting power or improved user comprehension. A claim about improved
explanations needs a designed user study; a claim about predictive validity needs
appropriate observed targets, calibration and out-of-sample evaluation. The COVID-period
market observations supply a scenario magnitude, not historical bilateral exposures or
observed bank defaults against which predictive accuracy could be measured.
