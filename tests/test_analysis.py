import numpy as np
import pandas as pd
import pytest

from atlas.analysis import (
    exposure_matrix,
    graph_metrics,
    impact_ranking,
    monte_carlo_summary,
    topology_ensemble,
)
from atlas.generate import generate
from atlas.models import Bank, Dataset, Exposure


def chain():
    # A lends 100 to B, C lends 80 to A. B default causes A then C.
    return Dataset(
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


def test_graph_orientation_and_matrix():
    data = chain()
    matrix = exposure_matrix(data)
    assert matrix.loc["A", "B"] == 100
    assert matrix.loc["B", "A"] == 0
    assert matrix.sum(axis=1).to_dict() == {"A": 100, "B": 0, "C": 80}
    assert matrix.sum(axis=0).to_dict() == {"A": 80, "B": 100, "C": 0}
    metrics = graph_metrics(data)
    assert metrics["directed_density"] == pytest.approx(1 / 3)
    bank = {b["id"]: b for b in metrics["bank_metrics"]}
    assert bank["A"]["unweighted_betweenness"] == 0.5
    assert bank["B"]["creditor_count"] == 1
    assert bank["B"]["borrower_count"] == 0


def test_impact_hand_calculation():
    data = chain()
    before = data.model_dump_json()
    ranking = impact_ranking(data)
    assert ranking.bank_id.tolist() == ["B", "A", "C"]
    assert ranking.secondary_defaults.tolist() == [2, 1, 0]
    assert ranking.posted_interbank_loss.tolist() == [108, 48, 0]
    assert data.model_dump_json() == before
    assert impact_ranking(data, recovery=1).secondary_defaults.sum() == 0


def test_mc_summary_hand_calculation():
    frame = pd.DataFrame({"defaults": [0, 2], "secondary_defaults": [0, 0], "interbank_loss": [0, 100]})
    summary = monte_carlo_summary(frame)["conditional_summary"]
    assert summary["defaults"]["mean"] == 1
    assert summary["defaults"]["mcse_mean"] == pytest.approx(1)
    assert summary["interbank_loss"]["empirical_q95"] == 100
    assert monte_carlo_summary(frame.head(1))["conditional_summary"]["defaults"]["mcse_mean"] is None
    with pytest.raises(ValueError):
        monte_carlo_summary(frame.head(0))
    frame.loc[0, "defaults"] = np.nan
    with pytest.raises(ValueError):
        monte_carlo_summary(frame)


def test_ensemble_reproducible_and_no_shock():
    a = topology_ensemble([1, 2], n=8, impairment=0)
    pd.testing.assert_frame_equal(a, topology_ensemble([1, 2], n=8, impairment=0))
    assert len(a) == 6
    assert a.total_defaults.sum() == 0
    assert a.total_exposure.ge(0).all()
    with pytest.raises(ValueError):
        topology_ensemble([1, 1])


def test_matrix_empty_edges():
    data = generate(2, seed=42, topology="random")
    assert not data.exposures
    assert exposure_matrix(data).to_numpy().sum() == 0
    assert graph_metrics(data)["weak_components"] == 2
