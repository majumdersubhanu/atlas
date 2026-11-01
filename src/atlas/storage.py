"""Dataset serialization and experiment provenance; no database service required."""

import hashlib
import json
import platform
import uuid
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from atlas import __version__
from atlas.models import Dataset


def dataset_hash(data: Dataset) -> str:
    return hashlib.sha256(data.model_dump_json().encode()).hexdigest()


def experiment(data: Dataset, result: dict, calibration=None, extra=None) -> dict:
    return {
        "atlas_version": __version__,
        "runtime": {
            "python": platform.python_version(),
            "packages": {name: version(name) for name in ["numpy", "pandas", "networkx", "pydantic"]},
        },
        "source_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.glob("*.py"))
        },
        "created_utc": datetime.now(UTC).isoformat(),
        "dataset_sha256": dataset_hash(data),
        "dataset": data.model_dump(),
        "calibration": calibration,
        "result": result,
        "advanced": extra,
        "interpretation": "Synthetic model output; no historical bank defaults or bilateral network inferred.",
    }


def save_experiment(record: dict, directory="experiments") -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"experiment_{uuid.uuid4().hex}.json"
    path.write_text(json.dumps(record, indent=2, allow_nan=False))
    return path


def read_dataset(path) -> Dataset:
    return Dataset.model_validate_json(Path(path).read_text())


def export_dataset(data: Dataset, directory) -> None:
    import pandas as pd

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "network.json").write_text(data.model_dump_json(indent=2))
    pd.DataFrame([b.model_dump() for b in data.banks]).to_csv(directory / "banks.csv", index=False)
    pd.DataFrame([e.model_dump() for e in data.exposures], columns=["lender", "borrower", "amount"]).to_csv(
        directory / "exposures.csv", index=False
    )
