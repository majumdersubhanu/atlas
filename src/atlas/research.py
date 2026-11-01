"""Batch reproduction of the notebook experiment design, without Jupyter or UI."""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from atlas.analysis import graph_metrics, impact_ranking, monte_carlo_summary, topology_ensemble
from atlas.baseline import direct_loss_only
from atlas.engine import bank_risk, debt_rank, furfine, monte_carlo
from atlas.generate import generate
from atlas.market import calibration
from atlas.models import Scenario
from atlas.storage import experiment, export_dataset


def run(output: Path) -> dict:
    """Save fixed, declared experiments and a manifest of their exact output bytes."""
    output.mkdir(parents=True, exist_ok=True)
    data = generate(50, 42, "core_periphery")
    export_dataset(data, output / "network")
    bank_risk(data).to_csv(output / "bank_risk.csv", index=False)
    impact_ranking(data).to_csv(output / "impact_ranking.csv", index=False)
    mapping = calibration(multiplier=0.3)
    scenario = Scenario(
        name="Illustrative historical-market mapping", external_impairment=mapping["external_impairment"]
    )
    result = furfine(data, scenario)
    mc_scenario = Scenario(name="Independent initial-default experiment", external_impairment=0.05)
    mc = monte_carlo(data, mc_scenario, trials=500, seed=42)
    mc.to_csv(output / "monte_carlo.csv", index=False)
    topology_ensemble(range(10), impairment=0.1).to_csv(output / "topology_ensemble.csv", index=False)
    sensitivity = []
    for multiplier in [0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        for recovery in [0, 0.2, 0.4, 0.6, 0.8, 1]:
            shock = calibration(multiplier=multiplier)["external_impairment"]
            r = furfine(data, Scenario(external_impairment=shock, recovery=recovery))
            sensitivity.append(
                {
                    "multiplier": multiplier,
                    "recovery": recovery,
                    "impairment": shock,
                    "initial": len(r["initial_defaults"]),
                    "total": r["default_count"],
                    "secondary": len(r["secondary_defaults"]),
                    "posted_loss": r["interbank_loss"],
                }
            )
    pd.DataFrame(sensitivity).to_csv(output / "sensitivity.csv", index=False)
    record = experiment(
        data,
        result,
        mapping,
        {
            "baseline": direct_loss_only(data, scenario),
            "debt_rank_variant": debt_rank(data, scenario.external_impairment),
            "graph_metrics": graph_metrics(data),
            "mc_parameters": {
                "scenario": mc_scenario.model_dump(),
                "trials": 500,
                "seed": 42,
                "pd_override": None,
            },
            "mc_summary": monte_carlo_summary(mc),
            "ensemble_parameters": {
                "seeds": list(range(10)),
                "banks": 50,
                "impairment": 0.1,
                "recovery": 0.4,
            },
        },
    )
    lock = Path(__file__).resolve().parents[2] / "uv.lock"
    record["uv_lock_sha256"] = hashlib.sha256(lock.read_bytes()).hexdigest() if lock.exists() else None
    (output / "experiment.json").write_text(json.dumps(record, indent=2, allow_nan=False))
    manifest = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name != "manifest.json"
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return {
        "output": str(output),
        "initial_defaults": len(result["initial_defaults"]),
        "secondary_defaults": len(result["secondary_defaults"]),
        "total_defaults": result["default_count"],
        "drawdown": mapping["drawdown_magnitude"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/final"))
    print(json.dumps(run(parser.parse_args().output), indent=2))


if __name__ == "__main__":
    main()
