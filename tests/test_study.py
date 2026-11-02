"""Artificial test records verify analysis logic; these are not research outcomes."""

import pandas as pd
import pytest

from atlas.study import TRIAL_COLUMNS, eligible_trials, paired_summary


def record(pid, view, correct, duration, kind="study", **extra):
    return {
        "record_type": kind,
        "participant_id": pid,
        "trial_id": view,
        "stimulus_id": "test-fixture",
        "task": "path",
        "representation": view,
        "correct": correct,
        "duration_seconds": duration,
        "timeout": 0,
        "eligible": 1,
        "experience_group": "test",
        "dataset_hash": "test-hash",
        **extra,
    }


def test_empty_is_not_evaluated():
    result = paired_summary(pd.DataFrame(columns=TRIAL_COLUMNS), "path")
    assert result["status"] == "not evaluated"
    assert result["paired_participants"] == 0


def test_excludes_practice_and_uses_paired_people():
    frame = pd.DataFrame(
        [
            record("P1", "graph", 1, 20),
            record("P1", "matrix", 0, 40),
            record("P2", "graph", 0, 40),
            record("P2", "matrix", 0, 40),
            record("P3", "graph", 1, 10),
            record("practice", "graph", 1, 1, "rehearsal"),
        ]
    )
    result = paired_summary(frame, "path")
    assert result["audit"]["excluded_nonstudy_rows"] == 1
    assert result["paired_participants"] == 2
    assert result["omitted_incomplete_or_unbalanced_participants"] == 1
    assert result["accuracy_difference_pp"]["mean"] == 50
    assert result["time_difference_seconds"]["mean"] == -10


def test_rejects_invalid_and_duplicate_trials_retains_timeout():
    frame = pd.DataFrame([record("P1", "graph", 0, 180, timeout=1)])
    assert len(eligible_trials(frame)[0]) == 1
    with pytest.raises(ValueError, match="Duplicate"):
        eligible_trials(pd.concat([frame, frame]))
    with pytest.raises(ValueError, match="Duration"):
        eligible_trials(pd.DataFrame([record("P1", "graph", 1, -1)]))
    with pytest.raises(ValueError, match="Timeout"):
        eligible_trials(pd.DataFrame([record("P1", "graph", 1, 180, timeout=1)]))
