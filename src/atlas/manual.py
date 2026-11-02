"""Build validated synthetic accounts from manually specified banks and loans."""

import math

from pydantic import Field

from atlas.models import Bank, Dataset, Exposure, StrictModel


class ManualBank(StrictModel):
    id: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=80)
    external_assets: float = Field(ge=0)
    equity: float = Field(gt=0)
    pd: float = Field(default=0.02, ge=0, le=1)


class ManualNetworkRequest(StrictModel):
    banks: list[ManualBank] = Field(min_length=2, max_length=50)
    exposures: list[Exposure] = Field(default_factory=list, max_length=2450)
    units: str = Field(default="synthetic teaching units", min_length=1, max_length=100)


def build_manual_network(req: ManualNetworkRequest) -> Dataset:
    """Derive loan assets/borrowing, then residual deposits; never repair invalid inputs.

    Deposits = external assets + lending - borrowing - equity.
    Negative residuals are rejected rather than inventing additional funding.
    """
    ids = {bank.id for bank in req.banks}
    if len(ids) != len(req.banks):
        raise ValueError("Each bank needs a unique ID")
    outgoing, incoming, pairs = dict.fromkeys(ids, 0.0), dict.fromkeys(ids, 0.0), set()
    for loan in req.exposures:
        if loan.lender not in ids or loan.borrower not in ids:
            raise ValueError("Every loan must connect two banks in this network")
        if loan.lender == loan.borrower:
            raise ValueError("A bank cannot lend to itself")
        pair = (loan.lender, loan.borrower)
        if pair in pairs:
            raise ValueError("One loan per directed pair; edit its amount instead of adding a duplicate")
        pairs.add(pair)
        outgoing[loan.lender] += loan.amount
        incoming[loan.borrower] += loan.amount
    banks = []
    for bank in req.banks:
        deposits = bank.external_assets + outgoing[bank.id] - incoming[bank.id] - bank.equity
        if not math.isfinite(deposits):
            raise ValueError(f"{bank.id}: account totals must be finite")
        if deposits < 0:
            raise ValueError(
                f"{bank.id}: deposits would be {deposits:g}. Increase external assets or lending, "
                "or reduce borrowing or equity, to balance this bank."
            )
        banks.append(
            Bank(
                **bank.model_dump(),
                interbank_assets=outgoing[bank.id],
                interbank_liabilities=incoming[bank.id],
                deposits=deposits,
            )
        )
    return Dataset(topology="manual", units=req.units, banks=banks, exposures=req.exposures)
