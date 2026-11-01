import json

import pandas as pd
import pytest

from atlas.observed import cohort, load_snapshot, stress


def test_hand_loss_and_boundary():
    banks = pd.DataFrame(
        [{"bank_id": "a", "NAME": "A", "assets": 100.0, "equity": 10.0, "equity_ratio": 0.1}]
    )
    assert stress(banks, 0).remaining_equity.iloc[0] == 10
    assert stress(banks, 0.1).capital_exhausted.iloc[0]
    assert stress(banks, 0.2).capital_shortfall.iloc[0] == 10
    for bad in [-1, 2, float("nan")]:
        with pytest.raises(ValueError):
            stress(banks, bad)


def test_snapshot_units_missing_and_duplicate(tmp_path):
    row = {
        "CERT": 1,
        "CERTCONS": "0",
        "BKCLASS": "N",
        "NAME": "A",
        "REPDTE": "20191231",
        "ASSET": 100000,
        "EQTOT": 10000,
        "LIAB": 90000,
        "DEP": 80000,
    }
    p = tmp_path / "raw.json"
    p.write_text(json.dumps({"data": [{"data": row}]}))
    f = load_snapshot(p)
    assert f.assets.iloc[0] == 100
    assert f.eligible.iloc[0]
    row["EQTOT"] = None
    p.write_text(json.dumps({"data": [{"data": row}]}))
    assert not load_snapshot(p).eligible.iloc[0]
    p.write_text(json.dumps({"data": [{"data": row}, {"data": row}]}))
    with pytest.raises(ValueError, match="Duplicate"):
        load_snapshot(p)


def test_fixed_cohort_keeps_missing_followup():
    before = pd.DataFrame({"bank_id": ["a", "b", "c"], "assets": [100, 90, 80], "eligible": [True] * 3})
    after = pd.DataFrame(
        {
            "bank_id": ["a", "c"],
            "assets": [110, 200],
            "equity": [10, 20],
            "equity_ratio": [0.1, 0.1],
            "eligible": [True, True],
        }
    )
    result = cohort(before, after, 2)
    assert list(result.bank_id) == ["a", "b"]
    assert pd.isna(result.assets_later.iloc[1])
