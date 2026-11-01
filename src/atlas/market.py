"""Offline market observations and explicitly assumed stress mappings."""

from importlib.resources import files

import numpy as np
import pandas as pd


def market_data() -> pd.DataFrame:
    """Read packaged observations; omit missing holiday closes, never interpolate."""
    with files("atlas").joinpath("data/sp500_2020.csv").open("rb") as source:
        frame = pd.read_csv(source, parse_dates=["observation_date"])
    frame = frame.rename(columns={"observation_date": "date", "SP500": "close"}).dropna()
    if not frame.date.is_monotonic_increasing or frame.date.duplicated().any():
        raise ValueError("Market dates must be unique and ordered")
    if not (np.isfinite(frame.close) & (frame.close > 0)).all():
        raise ValueError("Market closes must be finite and positive")
    frame["return"] = frame.close.pct_change(fill_method=None)
    frame["drawdown"] = frame.close / frame.close.cummax() - 1
    return frame.reset_index(drop=True)


def calibration(start=None, end=None, multiplier=0.3) -> dict:
    if not np.isfinite(multiplier) or multiplier < 0:
        raise ValueError("Multiplier must be finite and nonnegative")
    frame = market_data()
    if start is not None:
        frame = frame[frame.date >= pd.Timestamp(start)]
    if end is not None:
        frame = frame[frame.date <= pd.Timestamp(end)]
    if len(frame) < 2:
        raise ValueError("Select at least two observed trading dates")
    dd = frame.close / frame.close.cummax() - 1
    trough_i = dd.idxmin()
    peak_i = frame.loc[:trough_i, "close"].idxmax()
    magnitude = float(-dd.loc[trough_i])
    return {
        "series": "SP500",
        "source": "https://fred.stlouisfed.org/series/SP500",
        "window_start": str(frame.date.iloc[0].date()),
        "window_end": str(frame.date.iloc[-1].date()),
        "peak_date": str(frame.loc[peak_i, "date"].date()),
        "trough_date": str(frame.loc[trough_i, "date"].date()),
        "drawdown_magnitude": magnitude,
        "multiplier": multiplier,
        "external_impairment": min(1.0, magnitude * multiplier),
        "mapping": "min(1, selected-window maximum drawdown magnitude * multiplier)",
    }
