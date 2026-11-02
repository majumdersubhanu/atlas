"""Independent accounting controls for the manual network editor API."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from atlas.api import app
from atlas.engine import furfine
from atlas.manual import ManualNetworkRequest, build_manual_network
from atlas.models import Scenario


def chain_request():
    return {
        "banks": [
            {"id": "A", "name": "Alpha", "external_assets": 100, "equity": 50},
            {"id": "B", "name": "Beta", "external_assets": 200, "equity": 50},
            {"id": "C", "name": "Gamma", "external_assets": 100, "equity": 40},
        ],
        "exposures": [
            {"lender": "A", "borrower": "B", "amount": 100},
            {"lender": "C", "borrower": "A", "amount": 80},
        ],
    }


def test_manual_chain_has_independent_accounts_and_cascade():
    req = ManualNetworkRequest(**chain_request())
    data = build_manual_network(req)
    assert [b.deposits for b in data.banks] == [70, 50, 140]
    assert [b.interbank_assets for b in data.banks] == [100, 0, 80]
    assert [b.interbank_liabilities for b in data.banks] == [80, 100, 0]
    assert furfine(data, Scenario(initial_defaults=["B"]))["interbank_loss"] == 108
    assert req.banks[0].external_assets == 100


@pytest.mark.parametrize(
    "loan,match",
    [
        ({"lender": "A", "borrower": "A", "amount": 1}, "itself"),
        ({"lender": "X", "borrower": "B", "amount": 1}, "connect"),
        ({"lender": "A", "borrower": "B", "amount": 1}, "duplicate"),
    ],
)
def test_invalid_manual_connections(loan, match):
    payload = chain_request()
    payload["exposures"].append(loan)
    with pytest.raises(ValueError, match=match):
        build_manual_network(ManualNetworkRequest(**payload))


def test_negative_deposits_rejected_and_isolates_allowed():
    payload = chain_request()
    payload["banks"][1]["external_assets"] = 100
    with pytest.raises(ValueError, match="B: deposits would be -50"):
        build_manual_network(ManualNetworkRequest(**payload))
    payload["exposures"] = []
    data = build_manual_network(ManualNetworkRequest(**payload))
    assert data.banks[1].deposits == 50
    payload["banks"][1]["id"] = "A"
    with pytest.raises(ValueError, match="unique"):
        build_manual_network(ManualNetworkRequest(**payload))


def test_manual_api_validates_and_accepts_zero_deposits():
    client = TestClient(app)
    payload = chain_request()
    payload["banks"][1]["external_assets"] = 150
    response = client.post("/networks/manual", json=payload)
    assert response.status_code == 200
    assert response.json()["banks"][1]["deposits"] == 0
    payload["banks"][1]["external_assets"] = 149
    assert client.post("/networks/manual", json=payload).status_code == 422
    with pytest.raises(ValidationError):
        ManualNetworkRequest(banks=payload["banks"][:1])
    payload["banks"][0]["equity"] = float("nan")
    with pytest.raises(ValidationError):
        ManualNetworkRequest(**payload)
