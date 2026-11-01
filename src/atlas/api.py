"""HTTP interface to the synthetic network model; observed analysis is separate."""

from fastapi import FastAPI, HTTPException
from pydantic import Field

from atlas.engine import bank_risk, credit_risk, debt_rank, furfine, monte_carlo
from atlas.generate import generate
from atlas.market import calibration, market_data
from atlas.models import Dataset, GenerateRequest, Scenario, StrictModel
from atlas.storage import experiment, save_experiment

app = FastAPI(title="Atlas synthetic interbank risk", version="0.5.0")


class SimulationRequest(StrictModel):
    dataset: Dataset
    scenario: Scenario


@app.get("/health")
def health():
    return {"status": "ok", "synthetic_network_only": True}


@app.post("/generate")
def network(req: GenerateRequest):
    return generate(req.banks, req.seed, req.topology)


@app.post("/validate")
def validate(data: Dataset):
    return {"valid": True, "banks": len(data.banks), "exposures": len(data.exposures)}


@app.post("/credit")
def credit(data: Dataset, recovery: float = 0.4, pd: float | None = None):
    try:
        return {
            "banks": bank_risk(data, recovery, pd).to_dict("records"),
            "loans": credit_risk(data, recovery, pd).to_dict("records"),
        }
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/simulate")
def simulate(req: SimulationRequest):
    try:
        return furfine(req.dataset, req.scenario)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/experiments")
def save(req: SimulationRequest):
    try:
        record = experiment(req.dataset, furfine(req.dataset, req.scenario))
        return {"filename": save_experiment(record).name, "record": record}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/market")
def market():
    frame = market_data().drop(columns="return")
    frame["date"] = frame.date.dt.strftime("%Y-%m-%d")
    return {"observations": frame.to_dict("records"), "calibration": calibration()}


class DebtRankRequest(StrictModel):
    dataset: Dataset
    impairment: float = Field(ge=0, le=1)
    recovery: float = Field(default=0.4, ge=0, le=1)


class MonteCarloRequest(SimulationRequest):
    trials: int = Field(default=200, ge=1, le=2000)
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    pd_override: float | None = Field(default=None, ge=0, le=1)


@app.post("/debt-rank")
def debt_rank_endpoint(req: DebtRankRequest):
    return debt_rank(req.dataset, req.impairment, req.recovery)


@app.post("/monte-carlo")
def monte_carlo_endpoint(req: MonteCarloRequest):
    try:
        return {
            "trials": monte_carlo(req.dataset, req.scenario, req.trials, req.seed, req.pd_override).to_dict(
                "records"
            )
        }
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/network-metrics")
def network_metrics(data: Dataset):
    from atlas.analysis import graph_metrics

    return graph_metrics(data)


@app.post("/impact-ranking")
def impact(data: Dataset, recovery: float = 0.4):
    from atlas.analysis import impact_ranking

    try:
        return {"ranking": impact_ranking(data, recovery).to_dict("records")}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/baseline")
def baseline(req: SimulationRequest):
    from atlas.baseline import direct_loss_only

    try:
        return direct_loss_only(req.dataset, req.scenario)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
