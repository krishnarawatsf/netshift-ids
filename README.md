<div align="center">

# `NETSHIFT // IDS`

### CROSS-NETWORK INTRUSION DETECTION

**Train on one network. Test the shift. Measure the label budget.**

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/krishnarawatsf/netshift-ids/blob/main/notebooks/netshift_colab.ipynb)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Research project](https://img.shields.io/badge/Focus-defensive%20security-00A389)](#mission)
[![Data stays out of Git](https://img.shields.io/badge/Data-never%20committed-222222)](#defensive-data-handling)

</div>

---

## Mission

NetShift-IDS is a research scaffold for **label-efficient intrusion detection
under network shift**. It is designed to train on CIC-IDS2017 and evaluate on
CSE-CIC-IDS2018, with a separate lab-network handoff described in
[`docs/MEMBER_B_CONTRACT.md`](docs/MEMBER_B_CONTRACT.md).

The workflow compares in-network and cross-network evaluation, investigates
feature distribution shifts, and measures performance across target-label
budgets. This repository does **not** claim validated real-data performance:
run the experiments and inspect the saved evidence before drawing conclusions.

## Research workflow

```text
  CIC-IDS2017 ── clean & map ──┬── stratified holdout ── baseline
                               │
                               └── train ────────────────┐
                                                        ├── CSE-CIC-IDS2018
  CSE-CIC-IDS2018 ── clean & align ─────────────────────┤   cross-network test
                                                        ├── label-budget study
                                                        └── SHAP / KS analysis
```

| Stage | Entry point | Evidence written |
|---|---|---|
| Clean and map dataset | `scripts/01_clean.py` | `data/clean/*.parquet`, `results/data_quality_*.json` |
| In-network baseline | `scripts/02_baseline.py` | `results/results_log.csv` |
| Cross-network evaluation | `scripts/03_cross_network.py` | `results/results_log.csv` |
| Shortcut feature analysis | `scripts/04_shap.py` | `results/feature_shift.csv`, `results/shortcut_features.json`, results log |
| Target label-budget curve | `scripts/05_label_budget.py` | `results/results_log.csv` |

Primary reported metrics are **macro-F1** and **MCC**; accuracy is secondary.
The Streamlit dashboard reads saved results and does not train models.

## Run locally

Python 3.11 is recommended on macOS and Ubuntu.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
pytest -q
```

Place the dataset CSVs in these folders:

```text
data/raw/
├── cicids2017/*.csv
└── cse2018/*.csv
```

Run the implemented pipeline:

```bash
bash run_all.sh
streamlit run dashboard/app.py
```

On Apple Silicon, install `libomp` with Homebrew only if XGBoost reports that
the library is missing. Large jobs can be run in Colab with the
[launcher notebook](notebooks/netshift_colab.ipynb).

### Colab setup

1. Add a GitHub access token with repository read access to Colab Secrets as
   `GITHUB_TOKEN`; the notebook reads it at runtime and does not store it in
   the Git remote URL.
2. Put CIC-IDS2017 CSVs in `MyDrive/netshift-data/cicids2017/`.
3. Add a Kaggle API token to Colab Secrets as `KAGGLE_API_TOKEN`. The notebook
   downloads CSE-CIC-IDS2018 from Kaggle dataset
   [`solarmainframe/ids-intrusion-csv`](https://www.kaggle.com/datasets/solarmainframe/ids-intrusion-csv)
   and stages its CSV files in `data/raw/cse2018/`.
4. Open the Colab badge above, select a runtime, and run the notebook cells in
   order. Environment snapshots and run results are saved under
   `MyDrive/netshift-results/`.

The launcher is orchestration only. The current repository does not yet
contain `scripts/doctor.py`, `scripts/07_active_labels.py`, or
`scripts/06_report.py`; the corresponding Colab steps stop with an explicit
missing-script error until those project scripts are added.

## Defensive data handling

- Use only authorized datasets and lab systems.
- Keep raw CSVs, cleaned datasets, and experiment outputs out of Git.
- For Network C, follow the private-VM scope in the
  [Member B contract](docs/MEMBER_B_CONTRACT.md); do not direct test traffic at
  systems you do not own or have permission to assess.

## Project map

```text
src/netshift/       Shared cleaning, feature, model, label, and metric code
scripts/            Thin experiment entry points
tests/              Pytest coverage
dashboard/          Read-only results dashboard
data/               Local datasets and cleaned data (not committed)
results/            Local experiment evidence (not committed)
lab/                Network C handoff area
notebooks/          Google Colab launcher
```

## Current validation status

The real-data run and macOS/Ubuntu parity checks are not yet recorded. Consult
[`docs/AUDIT.md`](docs/AUDIT.md) for the available test evidence, unmeasured
results, and outstanding methodology and handoff items.
