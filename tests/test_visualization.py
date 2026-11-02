"""Shared visual evidence must retain loan direction, accounting and cascade truth."""

import pytest
from fastapi.testclient import TestClient

from atlas.api import app
from atlas.generate import generate
from atlas.models import Scenario
from atlas.visualization import teaching_fixture, visualization_payload


def test_shared_chain_evidence_and_rounds():
    data = teaching_fixture()
    before = data.model_dump_json()
    result = visualization_payload(data, Scenario(initial_defaults=["B"]))
    assert result["matrix"] == {"ids": ["A", "B", "C"], "values": [[0, 100, 0], [0, 0, 0], [80, 0, 0]]}
    assert result["cascade"]["interbank_loss"] == 108
    assert result["baseline"]["interbank_loss"] == 60
    assert result["comparison"]["additional_defaults"] == 1
    assert result["comparison"]["additional_interbank_loss"] == 48
    assert {n["id"]: n["default_round"] for n in result["nodes"]} == {"A": 1, "B": 0, "C": 2}
    assert result["cascade"]["rounds"][1]["equity"]["A"] == -10
    assert result["cascade"]["rounds"][2]["equity"]["C"] == -8
    assert data.model_dump_json() == before


def test_branch_hand_arithmetic():
    result = visualization_payload(teaching_fixture("branch"), Scenario(initial_defaults=["B"]))
    # Round 1: A loses 60, D loses 30. Round 2: C loses 48, E loses 24.
    # Round 3: F loses 18. E and F survive on equity 6 and 12.
    assert result["cascade"]["defaults"] == ["A", "B", "C", "D"]
    assert result["cascade"]["interbank_loss"] == 180
    assert result["baseline"]["interbank_loss"] == 90
    assert result["cascade"]["equity"]["E"] == 6
    assert result["cascade"]["equity"]["F"] == 12


def test_layout_and_matrix_are_independent_of_shock():
    data = generate(12, 42)
    a = visualization_payload(data, Scenario())
    b = visualization_payload(data, Scenario(external_impairment=0.2))
    assert a["matrix"] == b["matrix"]
    assert a["dataset_hash"] == b["dataset_hash"]
    assert [(n["x"], n["y"]) for n in a["nodes"]] == [(n["x"], n["y"]) for n in b["nodes"]]
    ids = a["matrix"]["ids"]
    for edge in a["edges"]:
        assert a["matrix"]["values"][ids.index(edge["lender"])][ids.index(edge["borrower"])] == edge["amount"]


def test_dashboard_api_and_error_contract():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert "/static/workspace/assets/" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/fixtures/unknown").status_code == 404
    data = client.get("/fixtures/chain").json()
    response = client.post("/visualization", json={"dataset": data, "scenario": {"initial_defaults": ["B"]}})
    assert response.status_code == 200
    assert response.json()["cascade"]["interbank_loss"] == 108
    invalid = client.post("/visualization", json={"dataset": data, "scenario": {"initial_defaults": ["X"]}})
    assert invalid.status_code == 422
    assert (
        client.post("/visualization", json={"dataset": data, "scenario": {"recovery": 1.1}}).status_code
        == 422
    )
    assert "/visualization" in client.get("/openapi.json").json()["paths"]
    with pytest.raises(ValueError, match="80"):
        visualization_payload(generate(81), Scenario())
