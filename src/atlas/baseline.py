"""Transparent direct-loss-only control for Atlas cascade experiments.

This deliberately truncated model is an experimental baseline, not a claim about
what all banks or supervisors currently implement. It shares the same input data,
external shock, default threshold and recovery as the cascade, but suppresses
transmission by banks that fail after the first loss update. It does not call the
cascade implementation, so the comparison can detect accidental propagation.
"""

from math import fsum

from atlas.models import Dataset, Scenario


def direct_loss_only(data: Dataset, scenario: Scenario) -> dict:
    """Apply external losses and exactly one generation of counterparty losses.

    All banks insolvent after the external shock, plus explicitly forced defaults,
    form D0. Only loans to D0 create losses. A creditor outside D0 can subsequently
    fail, but that failure never generates another loan loss in this baseline.
    ``secondary_defaults`` therefore includes first-generation failures; it does
    not mean that an additional propagation round was computed.

    Returns monetary amounts in the input dataset's units. Losses to banks already
    in D0 are excluded, matching Atlas's survivor-only accounting convention.
    Forced default is an imposed credit event and need not consume book equity.
    """
    bank_ids = {bank.id for bank in data.banks}
    forced = set(scenario.initial_defaults)
    if not forced <= bank_ids:
        raise ValueError("Unknown initial default bank")
    external = {bank.id: bank.external_assets * scenario.external_impairment for bank in data.banks}
    equity_after_external = {bank.id: bank.equity - external[bank.id] for bank in data.banks}
    initial = forced | {bid for bid, value in equity_after_external.items() if value <= 0}
    contributions = {bid: [] for bid in bank_ids}
    for loan in data.exposures:
        if loan.borrower in initial and loan.lender not in initial:
            contributions[loan.lender].append((1 - scenario.recovery) * loan.amount)
    losses = {bid: fsum(contributions[bid]) for bid in sorted(bank_ids)}
    equity = {bid: equity_after_external[bid] - losses[bid] for bid in sorted(bank_ids)}
    secondary = {bid for bid in bank_ids - initial if equity[bid] <= 0}
    defaults = initial | secondary
    return {
        "method": "direct_loss_only",
        "scenario": scenario.model_dump(),
        "initial_defaults": sorted(initial),
        "secondary_defaults": sorted(secondary),
        "defaults": sorted(defaults),
        "default_count": len(defaults),
        "external_loss": fsum(external.values()),
        "interbank_loss": fsum(losses.values()),
        "bank_external_loss": external,
        "bank_interbank_loss": losses,
        "equity": equity,
        "propagation_generations": 1 if initial else 0,
        "interpretation": "Direct-loss-only experimental control; subsequent failures do not transmit.",
    }
