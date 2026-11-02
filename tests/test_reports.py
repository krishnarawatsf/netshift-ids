import importlib.util
from pathlib import Path

import pandas as pd
import pytest


def load_report_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "06_report.py"
    spec = importlib.util.spec_from_file_location("netshift_report", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_report_includes_metrics_caps_and_selection():
    report = load_report_module().render_report(pd.DataFrame([
        {
            "experiment": "label_budget", "model": "rf", "selection": "random",
            "feature_set": "all", "label_budget": 0.1, "seed": 42,
            "macro_f1": 0.4, "mcc": 0.3, "n_train": 120, "n_test": 50,
            "n_labelled_target": 5, "majority_cap": 200000, "smote_cap": 50000,
        },
        {
            "experiment": "label_budget_uncertainty", "model": "rf",
            "selection": "uncertainty", "feature_set": "all", "label_budget": 0.1,
            "seed": 42, "macro_f1": 0.5, "mcc": 0.4, "n_train": 120,
            "n_test": 50, "n_labelled_target": 5,
            "majority_cap": 200000, "smote_cap": 50000,
        },
    ]))

    assert "label_budget_uncertainty" in report
    assert "uncertainty" in report
    assert "majority_caps" in report
    assert "smote_caps" in report
    assert "0.5" in report


def test_report_requires_cap_columns():
    report = load_report_module()
    with pytest.raises(ValueError, match="majority_cap"):
        report.render_report(pd.DataFrame([{"experiment": "baseline"}]))


def test_report_counts_duplicate_seed_rows_once():
    row = {
        "experiment": "label_budget", "model": "rf", "selection": "random",
        "feature_set": "all", "label_budget": 0.1, "seed": 42,
        "macro_f1": 0.4, "mcc": 0.3, "n_train": 120, "n_test": 50,
        "n_labelled_target": 5, "majority_cap": 200000, "smote_cap": 50000,
    }

    report = load_report_module().render_report(pd.DataFrame([row, row]))

    assert "| label_budget | rf | random | all | 0.1 | 1 | 1 |" in report


def test_report_rejects_conflicting_rows_for_same_seed():
    row = {
        "experiment": "label_budget", "model": "rf", "selection": "random",
        "feature_set": "all", "label_budget": 0.1, "seed": 42,
        "macro_f1": 0.4, "mcc": 0.3, "n_train": 120, "n_test": 50,
        "n_labelled_target": 5, "majority_cap": 200000, "smote_cap": 50000,
    }
    conflicting = {**row, "macro_f1": 0.5}

    with pytest.raises(ValueError, match="Conflicting result rows"):
        load_report_module().render_report(pd.DataFrame([row, conflicting]))
