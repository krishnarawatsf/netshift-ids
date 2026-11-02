import csv

import numpy as np
import pytest

from netshift import metrics


def test_evaluate_excludes_absent_true_classes_from_macro_f1():
    result = metrics.evaluate(np.array([0, 0, 1, 1]), np.array([0, 1, 1, 1]))
    assert result["macro_f1"] == pytest.approx((2 / 3 + 0.8) / 2)
    assert set(result["per_class_f1"]) == {"Benign", "DoS"}


def test_log_result_records_default_caps(tmp_path, monkeypatch):
    log_path = tmp_path / "results_log.csv"
    monkeypatch.setattr(metrics, "RESULTS_LOG", log_path)
    metrics.log_result({
        "experiment": "test", "model": "rf", "seed": 42,
        "macro_f1": 0.5, "mcc": 0.25, "per_class_f1": {"Benign": 0.5},
    })

    with log_path.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file))
    assert int(row["majority_cap"]) == metrics.MAJORITY_CAP
    assert int(row["smote_cap"]) == metrics.SMOTE_CAP


def test_log_result_rejects_mismatched_existing_schema(tmp_path, monkeypatch):
    log_path = tmp_path / "results_log.csv"
    log_path.write_text("old,columns\n1,2\n", encoding="utf-8")
    monkeypatch.setattr(metrics, "RESULTS_LOG", log_path)
    with pytest.raises(ValueError, match="schema mismatch"):
        metrics.log_result({
            "experiment": "test", "model": "rf", "seed": 42,
            "macro_f1": 0.5, "mcc": 0.25, "per_class_f1": {},
        })
