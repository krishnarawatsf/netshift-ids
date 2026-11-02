"""Report runtime and dataset prerequisites before starting experiments."""
import importlib
import sys
from pathlib import Path

from netshift.config import RAW_DIR

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_MODULES = (
    "numpy", "pandas", "scipy", "sklearn", "imblearn", "xgboost",
    "shap", "pyarrow", "matplotlib", "streamlit", "pytest", "kagglehub",
)
REQUIRED_SCRIPTS = (
    "01_clean.py", "02_baseline.py", "03_cross_network.py", "04_shap.py",
    "05_label_budget.py", "06_report.py", "07_active_labels.py",
)


def check(name: str, ok: bool, detail: str) -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return ok


def main() -> int:
    outcomes = [
        check(
            "Python",
            sys.version_info[:2] == (3, 11),
            f"found {sys.version.split()[0]}, expected 3.11",
        )
    ]
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except ImportError as exc:
            outcomes.append(check("Package " + module_name, False, str(exc)))
        else:
            outcomes.append(check("Package " + module_name, True, "importable"))

    for script_name in REQUIRED_SCRIPTS:
        path = ROOT / "scripts" / script_name
        outcomes.append(check("Script " + script_name, path.is_file(), str(path)))

    for dataset in ("cicids2017", "cse2018"):
        folder = RAW_DIR / dataset
        csv_files = sorted(folder.glob("*.csv")) if folder.is_dir() else []
        outcomes.append(check(
            "Dataset " + dataset,
            bool(csv_files),
            f"{len(csv_files)} CSV file(s) in {folder}",
        ))

    synthetic = sorted(RAW_DIR.rglob("synthetic_part1.csv")) if RAW_DIR.exists() else []
    outcomes.append(check(
        "Synthetic input exclusion",
        not synthetic,
        "none found" if not synthetic else ", ".join(str(path) for path in synthetic),
    ))
    passed = sum(outcomes)
    failed = len(outcomes) - passed
    print(f"\nDoctor summary: {passed} passed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
