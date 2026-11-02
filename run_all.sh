#!/usr/bin/env bash
# Runs the full pipeline in order. Works on macOS and Ubuntu.
# Usage: bash run_all.sh   (activate the virtualenv first)
set -euo pipefail
cd "$(dirname "$0")"

python scripts/doctor.py
python scripts/01_clean.py cicids2017
python scripts/01_clean.py cse2018
python scripts/02_baseline.py
python scripts/03_cross_network.py
python scripts/04_shap.py
python scripts/05_label_budget.py
python scripts/05_label_budget.py --feature-set shortcut_removed
python scripts/07_active_labels.py
python scripts/06_report.py
echo "Done. Results are in results/. Open the dashboard with: streamlit run dashboard/app.py"
