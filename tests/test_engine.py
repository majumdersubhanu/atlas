import json

import numpy as np
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from atlas.api import app
from atlas.engine import bank_risk, credit_risk, debt_rank, furfine, monte_carlo
from atlas.generate import generate
from atlas.market import calibration, market_data
from atlas.models import Bank, Dataset, Exposure, Scenario
from atlas.storage import dataset_hash, experiment, export_dataset, read_dataset, save_experiment


@pytest.fixture
def chain():
    # B fails exogenously; A loses 60 > equity 50, then C loses 48 > equity 40.
    return Dataset(
        topology="manual_chain",
        banks=[
            Bank(
                id="A",
                name="A",
                external_assets=100,
                interbank_assets=100,
                interbank_liabilities=80,
                deposits=70,
                equity=50,
            ),
            Bank(
                id="B",
                name="B",
                external_assets=200,
                interbank_assets=0,
                interbank_liabilities=100,
                deposits=50,
                equity=50,
            ),
            Bank(
                id="C",
                name="C",
                external_assets=100,
                interbank_assets=80,
                interbank_liabilities=0,
                deposits=140,
                equity=40,
            ),
        ],
        exposures=[
            Exposure(lender="A", borrower="B", amount=100),
            Exposure(lender="C", borrower="A", amount=80),
        ],
    )


@pytest.mark.parametrize("family", ["core_periphery", "random", "scale_free"])
@pytest.mark.parametrize("n", [2, 10, 50, 100])
def test_generator_accounting(family, n):
    data = generate(n, 42, family)
    assert data == generate(n, 42, family)
    assert len(data.banks) == n
    assert Dataset.model_validate_json(data.model_dump_json()) == data
    assert sum(b.interbank_assets for b in data.banks) == pytest.approx(
        sum(b.interbank_liabilities for b in data.banks)
    )
    assert all(b.deposits >= 0 for b in data.banks)


def test_seed_changes_network():
    assert generate(seed=42) != generate(seed=43)


@pytest.mark.parametrize(
    "mutation", ["accounting", "unknown", "duplicate", "self", "nan", "negative", "bank_id"]
)
def test_validation_rejects_bad_data(chain, mutation):
    raw = chain.model_dump()
    if mutation == "accounting":
        raw["banks"][0]["deposits"] += 1
    elif mutation == "unknown":
        raw["exposures"][0]["borrower"] = "missing"
    elif mutation == "duplicate":
        raw["exposures"].append(raw["exposures"][0])
    elif mutation == "self":
        raw["exposures"][0]["borrower"] = "A"
    elif mutation == "nan":
        raw["banks"][0]["equity"] = float("nan")
    elif mutation == "negative":
        raw["exposures"][0]["amount"] = -2
    else:
        raw["banks"][0]["id"] = "B"
    with pytest.raises(ValidationError):
        Dataset.model_validate(raw)


def test_credit_hand_calculation(chain):
    frame = credit_risk(chain, 0.4)
    assert frame.expected_loss.sum() == pytest.approx(2.16)
    assert frame.ead.sum() == 180
    assert credit_risk(chain, 0.4, 0).expected_loss.sum() == 0
    risk = bank_risk(chain)
    assert risk.set_index("id").loc["A", "lending_hhi"] == 1
    assert risk.set_index("id").loc["B", "lending_hhi"] == 0


def test_furfine_chain_and_no_mutation(chain):
    before = chain.model_dump_json()
    result = furfine(chain, Scenario(initial_defaults=["B"]))
    assert result["defaults"] == ["A", "B", "C"]
    assert result["secondary_defaults"] == ["A", "C"]
    assert result["interbank_loss"] == pytest.approx(108)
    assert result["equity"]["A"] == -10
    assert result["equity"]["C"] == -8
    assert [r["new_defaults"] for r in result["rounds"]] == [["B"], ["A"], ["C"], []]
    assert before == chain.model_dump_json()


def test_extreme_recovery_and_no_shock(chain):
    assert furfine(chain, Scenario())["default_count"] == 0
    assert furfine(chain, Scenario(initial_defaults=["B"], recovery=1))["defaults"] == ["B"]
    assert furfine(chain, Scenario(external_impairment=1))["default_count"] == 3


def test_exact_zero_capital_defaults(chain):
    result = furfine(chain, Scenario(initial_defaults=["B"], recovery=0.5))
    assert result["defaults"] == ["A", "B", "C"]
    assert result["equity"]["A"] == 0
    assert result["equity"]["C"] == 0


def test_multiple_defaults_and_order_independence(chain):
    s = Scenario(initial_defaults=["A", "B", "B"])
    a = furfine(chain, s)
    raw = chain.model_dump()
    raw["banks"].reverse()
    raw["exposures"].reverse()
    assert a == furfine(Dataset.model_validate(raw), s)
    # Already defaulted A is not charged for B; C is charged exactly once.
    assert a["interbank_loss"] == 48


def test_invalid_scenarios(chain):
    with pytest.raises(ValueError):
        furfine(chain, Scenario(initial_defaults=["X"]))
    with pytest.raises(ValidationError):
        Scenario(recovery=1.1)
    with pytest.raises(ValueError):
        credit_risk(chain, pd_override=-0.01)


def test_market_authentic_dates_and_calibration():
    frame = market_data().set_index("date")
    assert len(frame) == 62
    assert frame.loc["2020-02-19", "close"] == 3386.15
    assert frame.loc["2020-03-23", "close"] == 2237.40
    assert frame.loc["2020-04-30", "close"] == 2912.43
    assert "2020-02-17" not in frame.index
    c = calibration()
    assert c["peak_date"] == "2020-02-19"
    assert c["trough_date"] == "2020-03-23"
    assert c["drawdown_magnitude"] == pytest.approx(1 - 2237.4 / 3386.15)
    assert c["external_impairment"] == pytest.approx(c["drawdown_magnitude"] * 0.3)
    assert calibration(multiplier=10)["external_impairment"] == 1
    assert np.isnan(frame["return"].iloc[0])
    with pytest.raises(ValueError):
        calibration("2020-02-17", "2020-02-17")


def test_debtrank_and_monte_carlo(chain):
    assert debt_rank(chain, 0)["incremental_debtrank"] == 0
    dr = debt_rank(chain, 0.1)
    assert all(0 <= h <= 1 for h in dr["distress"].values())
    assert 0 <= dr["incremental_debtrank"] <= 1
    a = monte_carlo(chain, Scenario(), 50, 10, 0.2)
    assert a.equals(monte_carlo(chain, Scenario(), 50, 10, 0.2))
    assert monte_carlo(chain, Scenario(), 5, pd_override=0).defaults.sum() == 0
    assert (monte_carlo(chain, Scenario(), 5, pd_override=1).defaults == 3).all()


def test_debtrank_one_active_step_hand_calculation(chain):
    # h0 = [.2, .4, .25]; W[A,B]=1, W[C,A]=1. h_final=[.6,.4,.45].
    dr = debt_rank(chain, 0.1, recovery=0.4)
    assert dr["distress"] == pytest.approx({"A": 0.6, "B": 0.4, "C": 0.45})
    assert dr["incremental_debtrank"] == pytest.approx((0.4 * 200 + 0.2 * 180) / 580)


def test_storage_roundtrip(chain, tmp_path):
    export_dataset(chain, tmp_path)
    assert read_dataset(tmp_path / "network.json") == chain
    record = experiment(chain, furfine(chain, Scenario()))
    path = save_experiment(record, tmp_path)
    loaded = json.loads(path.read_text())
    assert loaded["dataset_sha256"] == dataset_hash(chain)
    assert (
        furfine(
            Dataset.model_validate(loaded["dataset"]), Scenario.model_validate(loaded["result"]["scenario"])
        )
        == loaded["result"]
    )


def test_api(chain, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.post("/generate", json={"banks": 50}).status_code == 200
    assert client.post("/generate", json={"banks": 1}).status_code == 422
    assert client.post("/validate", json=chain.model_dump()).json()["valid"]
    assert client.post("/credit?pd=0.02", json=chain.model_dump()).status_code == 200
    assert client.post("/credit?recovery=2", json=chain.model_dump()).status_code == 422
    req = {"dataset": chain.model_dump(), "scenario": {"initial_defaults": ["B"]}}
    assert client.post("/simulate", json=req).json()["default_count"] == 3
    assert client.post("/experiments", json=req).status_code == 200
    assert list(tmp_path.glob("experiments/*.json"))
    req["scenario"]["initial_defaults"] = ["X"]
    assert client.post("/simulate", json=req).status_code == 422
    assert len(client.get("/market").json()["observations"]) == 62
