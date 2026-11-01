"""Validated synthetic balance sheets, directed loans, and scenario contracts."""

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Bank(StrictModel):
    id: str = Field(min_length=1)
    name: str
    tier: Literal["core", "periphery", "other"] = "other"
    external_assets: float = Field(ge=0)
    interbank_assets: float = Field(ge=0)
    deposits: float = Field(ge=0)
    interbank_liabilities: float = Field(ge=0)
    equity: float = Field(gt=0)
    pd: float = Field(default=0.02, ge=0, le=1)

    @property
    def total_assets(self) -> float:
        return self.external_assets + self.interbank_assets


class Exposure(StrictModel):
    lender: str
    borrower: str
    amount: float = Field(gt=0)


class Dataset(StrictModel):
    schema_version: str = "1.0"
    synthetic: Literal[True] = True
    units: str = "INR crore (synthetic nominal amounts)"
    seed: int = 42
    topology: str = "core_periphery"
    banks: list[Bank] = Field(min_length=2)
    exposures: list[Exposure]

    @model_validator(mode="after")
    def accounting(self):
        ids = {b.id for b in self.banks}
        if len(ids) != len(self.banks):
            raise ValueError("Duplicate bank IDs")
        outgoing, incoming, pairs = dict.fromkeys(ids, 0.0), dict.fromkeys(ids, 0.0), set()
        for e in self.exposures:
            if e.lender not in ids or e.borrower not in ids:
                raise ValueError("Unknown exposure endpoint")
            pair = (e.lender, e.borrower)
            if e.lender == e.borrower or pair in pairs:
                raise ValueError("Self loan or duplicate directed exposure")
            pairs.add(pair)
            outgoing[e.lender] += e.amount
            incoming[e.borrower] += e.amount
        for b in self.banks:
            checks = [
                (b.interbank_assets, outgoing[b.id]),
                (b.interbank_liabilities, incoming[b.id]),
                (b.total_assets, b.deposits + b.interbank_liabilities + b.equity),
            ]
            if any(not math.isfinite(x) for pair in checks for x in pair):
                raise ValueError(f"Nonfinite derived balance sheet: {b.id}")
            if any(abs(a - c) > 1e-7 * max(1, abs(a), abs(c)) for a, c in checks):
                raise ValueError(f"Balance sheet or exposure reconciliation failed: {b.id}")
        return self


class Scenario(StrictModel):
    name: str = "Custom scenario"
    recovery: float = Field(default=0.4, ge=0, le=1)
    external_impairment: float = Field(default=0, ge=0, le=1)
    initial_defaults: list[str] = Field(default_factory=list)


class GenerateRequest(StrictModel):
    banks: int = Field(default=50, ge=2, le=200)
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    topology: Literal["core_periphery", "random", "scale_free"] = "core_periphery"
