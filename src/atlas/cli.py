"""Reproduce the introductory synthetic experiments from the command line."""

import argparse
import json
from pathlib import Path

from atlas.engine import furfine, monte_carlo
from atlas.generate import generate
from atlas.market import calibration
from atlas.models import Scenario
from atlas.storage import experiment, export_dataset, save_experiment


def main():
    parser = argparse.ArgumentParser(description="Generate and run the reproducible offline Atlas demo")
    parser.add_argument("--banks", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--topology", choices=["core_periphery", "random", "scale_free"], default="core_periphery"
    )
    parser.add_argument("--output", type=Path, default=Path("experiments"))
    args = parser.parse_args()
    data = generate(args.banks, args.seed, args.topology)
    export_dataset(data, args.output / "network")
    c = calibration()
    summaries = []
    for multiplier in [0.0, 0.2, 0.3, 0.4, 0.6]:
        c = calibration(multiplier=multiplier)
        scenario = Scenario(name=f"COVID mapping {multiplier}", external_impairment=c["external_impairment"])
        result = furfine(data, scenario)
        path = save_experiment(experiment(data, result, c), args.output)
        summaries.append(
            {
                "multiplier": multiplier,
                "impairment": c["external_impairment"],
                "initial": len(result["initial_defaults"]),
                "defaults": result["default_count"],
                "secondary": len(result["secondary_defaults"]),
                "saved": str(path),
            }
        )
    mc = monte_carlo(data, Scenario(), trials=200, seed=args.seed)
    mc.to_csv(args.output / "monte_carlo.csv", index=False)
    print(
        json.dumps(
            {
                "banks": len(data.banks),
                "exposures": len(data.exposures),
                "comparisons": summaries,
                "monte_carlo_mean_defaults": mc.defaults.mean(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
