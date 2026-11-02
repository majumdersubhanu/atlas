"""HTTP interface to the synthetic network model; observed analysis is separate."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from atlas.engine import bank_risk, credit_risk, debt_rank, furfine, monte_carlo
from atlas.generate import generate
from atlas.manual import ManualNetworkRequest, build_manual_network
from atlas.market import calibration, market_data
from atlas.models import Dataset, GenerateRequest, Scenario, StrictModel
from atlas.storage import experiment, save_experiment

app = FastAPI(
    title="Atlas — systemic risk visual analytics",
    version="0.5.0",
    description=(
        "Research MVP: graph and exposure-matrix views share one synthetic dataset and loss ledger. "
        "Loans point lender to borrower; losses travel in reverse. "
        "Visualization effectiveness is not yet evaluated. Observed FDIC analysis remains separate."
    ),
)
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC / "workspace" / "index.html")


@app.get("/fixtures/{name}", tags=["Visual comparison"], summary="Load a hand-checkable teaching network")
def fixture(name: str):
    """Choose `chain` (3 banks) or `branch` (6 banks). Amounts are synthetic teaching units."""
    from atlas.visualization import teaching_fixture

    try:
        return teaching_fixture(name)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.post("/networks/manual", tags=["Visual comparison"], summary="Build a network from banks and loans")
def manual_network(req: ManualNetworkRequest) -> Dataset:
    """Accept 2–50 fictional banks with external assets/equity and directed loans.

    Loan assets and borrowing are summed from exposures. Deposits balance each
    account. Negative deposits, duplicate/self loans and unknown banks are rejected.
    No external assets or equity are changed automatically. Amounts use the supplied units.
    """
    try:
        return build_manual_network(req)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


class SimulationRequest(StrictModel):
    dataset: Dataset
    scenario: Scenario


@app.post(
    "/visualization", tags=["Visual comparison"], summary="Compare views and models on identical inputs"
)
def visual_comparison(req: SimulationRequest):
    """Return graph coordinates, original exposure matrix, round ledger and direct-loss control.

    Supports at most 80 banks. Positions depend on topology, not the shock; rounds share stable positions.
    Both views must use this same response. No participant-performance result is implied.
    """
    from atlas.visualization import visualization_payload

    try:
        return visualization_payload(req.dataset, req.scenario)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


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
