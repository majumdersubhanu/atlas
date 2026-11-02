"""Descriptive participant-paired analysis; never promote practice to study data."""

import numpy as np
import pandas as pd

TRIAL_COLUMNS = [
    "record_type",
    "participant_id",
    "trial_id",
    "stimulus_id",
    "task",
    "representation",
    "correct",
    "duration_seconds",
    "timeout",
    "eligible",
    "experience_group",
    "dataset_hash",
]


def eligible_trials(frame: pd.DataFrame, timeout_seconds: float = 180) -> tuple[pd.DataFrame, dict]:
    """Validate measured records, retaining errors/timeouts and reporting exclusions.

    Eligibility must be assigned using the frozen protocol, not experimental accuracy.
    CSVs remain local; this function performs no collection or participant identification.
    """
    missing = set(TRIAL_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing study columns: {sorted(missing)}")
    if not np.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("Timeout must be positive and finite")
    if not frame.record_type.isin(["study", "pilot", "rehearsal", "test"]).all():
        raise ValueError("Unknown record_type")
    measured = frame[frame.record_type == "study"].copy()
    for column in ["eligible", "correct", "timeout"]:
        measured[column] = pd.to_numeric(measured[column], errors="raise")
        if not measured[column].isin([0, 1]).all():
            raise ValueError(f"{column} must be 0 or 1")
    measured["duration_seconds"] = pd.to_numeric(measured.duration_seconds, errors="raise")
    if (
        not np.isfinite(measured.duration_seconds).all()
        or not measured.duration_seconds.between(0, timeout_seconds).all()
    ):
        raise ValueError("Duration must be finite and within the declared timeout")
    if not measured.representation.isin(["graph", "matrix"]).all():
        raise ValueError("Study representation must be graph or matrix")
    for column in ["participant_id", "trial_id", "stimulus_id", "task", "dataset_hash"]:
        if measured[column].isna().any() or measured[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Missing identifier: {column}")
    if measured.duplicated(["participant_id", "trial_id"]).any():
        raise ValueError("Duplicate participant/trial record")
    if (
        (measured.timeout == 1) & ((measured.correct != 0) | (measured.duration_seconds != timeout_seconds))
    ).any():
        raise ValueError("Timeout must have correct=0 and duration equal to the declared cap")
    kept = measured[measured.eligible == 1].copy()
    return kept, {
        "input_rows": len(frame),
        "excluded_nonstudy_rows": int((frame.record_type != "study").sum()),
        "excluded_ineligible_rows": int((measured.eligible == 0).sum()),
        "eligible_study_rows": len(kept),
        "interpretation": "Descriptive study records only; eligibility is supplied, not inferred from performance",
    }


def paired_summary(frame: pd.DataFrame, task: str, seed: int = 42) -> dict:
    """Equal-weight participants, complete balanced pairs, bootstrap participant differences.

    This is a per-task descriptive helper, not the preregistered combined primary
    estimand, a power analysis, a significance test, or a crossed-stimulus model.
    """
    valid, audit = eligible_trials(frame)
    subset = valid[valid.task == task]
    participants = sorted(subset.participant_id.unique())
    differences, omitted = [], []
    for pid in participants:
        records = subset[subset.participant_id == pid]
        graph = records[records.representation == "graph"]
        matrix = records[records.representation == "matrix"]
        if len(graph) == 0 or len(graph) != len(matrix):
            omitted.append(pid)
            continue
        differences.append(
            {
                "participant_id": pid,
                "accuracy_difference_pp": float(100 * (graph.correct.mean() - matrix.correct.mean())),
                "time_difference_seconds": float(
                    graph.duration_seconds.mean() - matrix.duration_seconds.mean()
                ),
            }
        )
    result = {
        "task": task,
        "audit": audit,
        "paired_participants": len(differences),
        "omitted_incomplete_or_unbalanced_participants": len(omitted),
        "status": "not evaluated" if not differences else "descriptive estimates; verify frozen protocol",
    }
    if not differences:
        return result
    rng = np.random.default_rng(seed)
    for metric in ["accuracy_difference_pp", "time_difference_seconds"]:
        values = np.array([row[metric] for row in differences])
        interval = None
        if len(values) >= 2:
            means = rng.choice(values, size=(2000, len(values)), replace=True).mean(axis=1)
            interval = np.quantile(means, [0.025, 0.975]).tolist()
        result[metric] = {
            "mean": float(values.mean()),
            "participant_bootstrap_95_percentile_interval": interval,
        }
    result["interpretation"] = (
        "Graph minus matrix. Positive accuracy favors graph; negative capped time is faster. "
        "Interpret time jointly with errors/timeouts; small samples give unstable intervals. "
        "No participant-level identifiers are returned."
    )
    return result
