"""Observed FDIC financials and conditional static capital stress.

No bilateral exposure estimates or default probabilities are inferred here.
All modeled monetary outputs are USD millions; source amounts are USD thousands.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_snapshot(path: str | Path) -> pd.DataFrame:
    payload = json.loads(Path(path).read_text())
    frame = pd.DataFrame([r["data"] for r in payload["data"]])
    required = ["CERT", "CERTCONS", "BKCLASS", "NAME", "REPDTE", "ASSET", "EQTOT", "LIAB", "DEP"]
    if not set(required) <= set(frame):
        raise ValueError("Required FDIC fields absent")
    if frame.duplicated(["CERT", "REPDTE"]).any():
        raise ValueError("Duplicate bank/date")
    for field in ["ASSET", "EQTOT", "LIAB", "DEP"]:
        frame[field] = pd.to_numeric(frame[field], errors="raise")
        if np.isinf(frame[field]).any():
            raise ValueError("Infinite observation")
    frame["accounting_residual_usd_thousand"] = frame.ASSET - frame.LIAB - frame.EQTOT
    # Each reported line is rounded to USD thousands; never silently repair it.
    frame["eligible"] = (
        frame.BKCLASS.isin(["N", "NM", "SM", "SB", "SI", "SL"])
        & frame.CERTCONS.astype(str).eq("0")
        & frame.ASSET.gt(0)
        & frame.EQTOT.gt(0)
        & frame.LIAB.ge(0)
        & frame.DEP.ge(0)
        & frame.DEP.le(frame.LIAB)
        & frame.accounting_residual_usd_thousand.abs().le(2)
    )
    frame["bank_id"] = frame.CERT.astype(int).astype(str)
    frame["date"] = pd.to_datetime(frame.REPDTE, format="%Y%m%d")
    for source, target in [
        ("ASSET", "assets"),
        ("EQTOT", "equity"),
        ("LIAB", "liabilities"),
        ("DEP", "deposits"),
    ]:
        frame[target] = frame[source] / 1000
    frame["equity_ratio"] = frame.equity / frame.assets
    return frame


def cohort(before: pd.DataFrame, after: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    if not 2 <= n <= len(before[before.eligible]):
        raise ValueError("Insufficient eligible banks")
    base = before[before.eligible].sort_values(["assets", "bank_id"], ascending=[False, True]).head(n)
    later = after[["bank_id", "assets", "equity", "equity_ratio", "eligible"]]
    return base.merge(later, on="bank_id", how="left", validate="one_to_one", suffixes=("", "_later"))


def stress(banks: pd.DataFrame, impairment: float) -> pd.DataFrame:
    """E'=E-qA. Static loss scenario; capital exhaustion is not legal default."""
    if not np.isfinite(impairment) or not 0 <= impairment <= 1:
        raise ValueError("Impairment must be in [0,1]")
    if not np.isfinite(banks[["assets", "equity"]]).all().all():
        raise ValueError("Nonfinite balance sheet")
    if (banks.assets <= 0).any() or (banks.equity <= 0).any() or (banks.equity > banks.assets).any():
        raise ValueError("Invalid balance sheet")
    out = banks[["bank_id", "NAME", "assets", "equity", "equity_ratio"]].copy()
    out["impairment"] = impairment
    out["loss"] = impairment * out.assets
    out["remaining_equity"] = out.equity - out.loss
    out["capital_exhausted"] = out.remaining_equity <= 0
    out["capital_shortfall"] = (-out.remaining_equity).clip(lower=0)
    return out


def checksum(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
