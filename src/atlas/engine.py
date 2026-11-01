"""Conditional credit losses, default cascades, DebtRank, and Monte Carlo trials."""

import numpy as np
import pandas as pd

from atlas.models import Dataset, Scenario


def credit_risk(data: Dataset, recovery=0.4, pd_override=None) -> pd.DataFrame:
    """One-period assumed marginal borrower PD × LGD × EAD, without contagion."""
    if not 0 <= recovery <= 1 or (pd_override is not None and not 0 <= pd_override <= 1):
        raise ValueError("PD and recovery must be in [0,1]")
    banks = {b.id: b for b in data.banks}
    rows = [
        {
            "lender": e.lender,
            "borrower": e.borrower,
            "ead": e.amount,
            "pd": banks[e.borrower].pd if pd_override is None else pd_override,
            "lgd": 1 - recovery,
        }
        for e in data.exposures
    ]
    frame = pd.DataFrame(rows, columns=["lender", "borrower", "ead", "pd", "lgd"])
    frame["expected_loss"] = frame.ead * frame.pd * frame.lgd
    return frame


def bank_risk(data: Dataset, recovery=0.4, pd_override=None) -> pd.DataFrame:
    """Bank balance sheets, expected credit loss and lending/funding concentration."""
    credit = credit_risk(data, recovery, pd_override)
    rows = []
    for b in data.banks:
        loans = credit[credit.lender == b.id]
        hhi = float(((loans.ead / loans.ead.sum()) ** 2).sum()) if len(loans) else 0.0
        funding = [e.amount for e in data.exposures if e.borrower == b.id]
        borrowing_hhi = sum((x / sum(funding)) ** 2 for x in funding) if funding else 0.0
        rows.append(
            {
                **b.model_dump(),
                "total_assets": b.total_assets,
                "equity_ratio": b.equity / b.total_assets,
                "expected_loss": float(loans.expected_loss.sum()),
                "lending_hhi": hhi,
                "borrowing_hhi": borrowing_hhi,
            }
        )
    return pd.DataFrame(rows)


def furfine(data: Dataset, scenario: Scenario) -> dict:
    """Synchronous, fixed-recovery defaults. Each borrower transmits once.

    Lender -> borrower is the loan direction; losses travel in reverse.
    Losses are posted only to creditors still alive at the start of each round.
    Defaults occur at equity <= 0. Forced defaults do not erase book equity.
    """
    ids = {b.id for b in data.banks}
    if not set(scenario.initial_defaults) <= ids:
        raise ValueError("Unknown initial default bank")
    external = {b.id: b.external_assets * scenario.external_impairment for b in data.banks}
    equity = {b.id: b.equity - external[b.id] for b in data.banks}
    initial = set(scenario.initial_defaults) | {k for k, v in equity.items() if v <= 0}
    failed, frontier = set(initial), set(initial)
    rounds = [
        {
            "round": 0,
            "new_defaults": sorted(initial),
            "cumulative_defaults": len(initial),
            "interbank_loss": 0.0,
            "equity": equity.copy(),
        }
    ]
    events = []
    losses = dict.fromkeys(ids, 0.0)
    while frontier:
        step = dict.fromkeys(ids, 0.0)
        for e in data.exposures:
            if e.borrower in frontier and e.lender not in failed:
                loss = e.amount * (1 - scenario.recovery)
                step[e.lender] += loss
                events.append(
                    {
                        "round": len(rounds),
                        "lender": e.lender,
                        "borrower": e.borrower,
                        "ead": e.amount,
                        "loss": loss,
                    }
                )
        for bid in ids:
            equity[bid] -= step[bid]
            losses[bid] += step[bid]
        frontier = {bid for bid in ids - failed if equity[bid] <= 0}
        failed |= frontier
        rounds.append(
            {
                "round": len(rounds),
                "new_defaults": sorted(frontier),
                "cumulative_defaults": len(failed),
                "interbank_loss": sum(step.values()),
                "equity": equity.copy(),
            }
        )
    return {
        "events": sorted(events, key=lambda e: (e["round"], e["lender"], e["borrower"])),
        "scenario": scenario.model_dump(),
        "defaults": sorted(failed),
        "initial_defaults": sorted(initial),
        "secondary_defaults": sorted(failed - initial),
        "default_count": len(failed),
        "external_loss": sum(external.values()),
        "interbank_loss": sum(losses.values()),
        "equity": equity,
        "bank_external_loss": external,
        "bank_interbank_loss": losses,
        "rounds": rounds,
    }


def debt_rank(data: Dataset, impairment: float, recovery=0.4) -> dict:
    """Original one-active-step DebtRank variant; distress is not a default forecast.

    W[creditor,borrower] = min(1, LGD * loan / creditor equity).
    Nodes transmit their current distress once, then become inactive.
    """
    Scenario(external_impairment=impairment, recovery=recovery)
    ids = [b.id for b in data.banks]
    ix = {bid: i for i, bid in enumerate(ids)}
    equity = np.array([b.equity for b in data.banks])
    w = np.zeros((len(ids), len(ids)))
    for e in data.exposures:
        w[ix[e.lender], ix[e.borrower]] = min(1, (1 - recovery) * e.amount / equity[ix[e.lender]])
    h0 = np.minimum(1, np.array([b.external_assets for b in data.banks]) * impairment / equity)
    h, active, used = h0.copy(), h0 > 0, np.zeros(len(ids), dtype=bool)
    while active.any():
        next_h = np.minimum(1, h + w[:, active] @ h[active])
        used |= active
        active = (next_h > h) & ~used
        h = next_h
    values = np.array([b.total_assets for b in data.banks])
    values /= values.sum()
    return {"distress": dict(zip(ids, h.tolist())), "incremental_debtrank": float((h - h0) @ values)}


def monte_carlo(data: Dataset, scenario: Scenario, trials=200, seed=42, pd_override=None) -> pd.DataFrame:
    """Independent Bernoulli assumed defaults, conditional on a fixed external shock."""
    if not 1 <= trials <= 2000:
        raise ValueError("Trials must be between 1 and 2000")
    credit_risk(data, scenario.recovery, pd_override)
    rng = np.random.default_rng(seed)
    rows = []
    for trial in range(trials):
        sampled = [b.id for b in data.banks if rng.random() < (b.pd if pd_override is None else pd_override)]
        s = scenario.model_copy(update={"initial_defaults": sorted(set(sampled + scenario.initial_defaults))})
        result = furfine(data, s)
        rows.append(
            {
                "trial": trial,
                "defaults": result["default_count"],
                "secondary_defaults": len(result["secondary_defaults"]),
                "interbank_loss": result["interbank_loss"],
            }
        )
    return pd.DataFrame(rows)
