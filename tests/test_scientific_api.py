from fastapi.testclient import TestClient

from atlas.api import app
from atlas.engine import debt_rank, monte_carlo
from atlas.generate import generate
from atlas.models import Scenario


def test_exploratory_endpoints_match_engine_and_validate():
    client = TestClient(app)
    data = generate(8, 42)
    scenario = Scenario(external_impairment=0.05)
    payload = data.model_dump(mode="json")
    response = client.post("/debt-rank", json={"dataset": payload, "impairment": 0.05})
    assert response.status_code == 200
    assert response.json() == debt_rank(data, 0.05)
    request = {"dataset": payload, "scenario": scenario.model_dump(), "trials": 5, "seed": 42}
    response = client.post("/monte-carlo", json=request)
    assert response.status_code == 200
    assert response.json()["trials"] == monte_carlo(data, scenario, 5, 42).to_dict("records")
    assert client.post("/monte-carlo", json={**request, "trials": 0}).status_code == 422


def test_analysis_and_baseline_api():
    client = TestClient(app)
    data = generate(8, 42).model_dump(mode="json")
    assert client.post("/network-metrics", json=data).json()["banks"] == 8
    assert len(client.post("/impact-ranking", json=data).json()["ranking"]) == 8
    assert client.post("/impact-ranking?recovery=2", json=data).status_code == 422
    request = {"dataset": data, "scenario": {"initial_defaults": ["B001"]}}
    assert client.post("/baseline", json=request).json()["method"] == "direct_loss_only"
    request["scenario"]["initial_defaults"] = ["missing"]
    assert client.post("/baseline", json=request).status_code == 422
