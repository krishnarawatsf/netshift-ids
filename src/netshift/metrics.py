"""Metrics and the single results log. All tables and plots are built from results_log.csv."""
import csv
import json

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef

from netshift.config import CLASSES, MAJORITY_CAP, RESULTS_LOG, SMOTE_CAP


def evaluate(y_true, y_pred) -> dict:
    """Macro-F1 and MCC are primary. Only classes present in y_true are scored,
    so a class missing from the target network is not counted as zero."""
    present = sorted(set(np.unique(y_true).tolist()))
    per = f1_score(y_true, y_pred, labels=present, average=None, zero_division=0)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, labels=present, average="macro", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "per_class_f1": {CLASSES[i]: round(float(v), 4) for i, v in zip(present, per)},
    }


def log_result(row: dict) -> None:
    """Append a schema-consistent, cap-auditable row to the experiment log."""
    RESULTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = dict(row)
    row.setdefault("majority_cap", MAJORITY_CAP)
    row.setdefault("smote_cap", SMOTE_CAP)
    row["per_class_f1"] = json.dumps(row["per_class_f1"])
    is_new = not RESULTS_LOG.exists()
    fieldnames = list(row.keys())
    if not is_new:
        with RESULTS_LOG.open("r", newline="", encoding="utf-8") as existing:
            existing_fieldnames = next(csv.reader(existing), None)
        if existing_fieldnames != fieldnames:
            raise ValueError(
                f"Results log schema mismatch in {RESULTS_LOG}. "
                "Archive or remove the old log before writing rows with the new schema."
            )
    with RESULTS_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            writer.writeheader()
        writer.writerow(row)
