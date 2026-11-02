# NetShift-IDS

Label-efficient cross-network intrusion detection. Validated on CIC-IDS2017 (train),
CSE-CIC-IDS2018 (unseen-network test), and our own lab traffic (Network C).

## Team
- **Member A (Mac M3):** data, models, analysis. Owns `src/`, `scripts/`, `dashboard/`.
- **Member B (Ubuntu):** lab, capture, Wazuh. Owns `lab/`. Output contract: `docs/MEMBER_B_CONTRACT.md`.

## Setup (macOS Apple Silicon and Ubuntu 24.04 use the same steps)

macOS:
```bash
brew install libomp          # only if xgboost reports a missing libomp
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
```

Ubuntu:
```bash
sudo apt install python3.11 python3.11-venv
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
```

## Data
Download the datasets (free) and place the CSVs here:
- `data/raw/cicids2017/*.csv`  (CIC-IDS2017, from unb.ca/cic/datasets/ids-2017)
- `data/raw/cse2018/*.csv`     (CSE-CIC-IDS2018, from unb.ca/cic/datasets/ids-2018, a sample is fine)

Do not commit the data. The data folders are in .gitignore.

## Run
```bash
bash run_all.sh
streamlit run dashboard/app.py
```
Heavy steps (full CIC-IDS2017, repeated label-budget sweeps) can be run on Colab or Kaggle
with the same code and the same `requirements.txt`.

## Pipeline
| Script | Step | Output |
|---|---|---|
| 01_clean.py | Clean, map labels, sample CSE-2018 | data/clean/*.parquet, results/data_quality_*.json |
| 02_baseline.py | In-network baseline (Review I) | results_log.csv |
| 03_cross_network.py | Train CIC, test CSE, no retrain (Review I) | results_log.csv |
| 04_shap.py | Shortcut features, retrain without them (Review II) | feature_shift.csv, shortcut_features.json |
| 05_label_budget.py | Label-budget curve (Review II, main novelty) | results_log.csv |

## Compatibility checklist (Mac to Linux)
- Python 3.11 on both machines, with pinned versions in requirements.txt.
- All paths use pathlib. No backslashes, no hardcoded home directories.
- LF line endings enforced by .gitattributes.
- No macOS-only or Linux-only packages in requirements.txt.
- results_log.csv is written with `newline=""`, so it is identical on both systems.
- Commit `requirements.lock` after the first successful install on both machines.

## Status
- [ ] Verified on macOS (Member A)
- [ ] Verified on Ubuntu (Member B)
- [ ] Real data run (CIC-IDS2017, CSE-CIC-IDS2018): not yet run
- [ ] Label mapping checked against downloaded files
- [ ] RENAME_CSE2018 checked against downloaded files
- [ ] Lab schema agreed (docs/MEMBER_B_CONTRACT.md)
