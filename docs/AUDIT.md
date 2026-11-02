# NetShift-IDS performance audit

**Audit date:** 2026-11-02
**Scope:** Read-only review of the project and available workspace evidence. No
code, mappings, splits, metrics, or results were changed.

## Part 1 — Evidence gathered

### Doctor and tests

| Check | Result |
|---|---|
| `python scripts/doctor.py` | **Blocked / failed to run:** `scripts/doctor.py` does not exist (`can't open file`). No doctor pass/fail checklist is available. |
| `pytest -q` | **Failed during collection:** 2 test modules errored. The active Python 3.13 environment could not import `pandas` or the `netshift` package. |
| `.venv/bin/python -m pytest -q` | **Passed:** 11 tests passed in 1.16 seconds using the project virtual environment. |

The passing virtual-environment test run is useful code-level evidence, but it
does not replace the exact requested `pytest -q` result or a data-backed run.

### Cleaning reports and data

No `results/data_quality_*.json`, cleaned Parquet files, or raw dataset CSVs
were present. The raw and clean data folders contained only `.gitkeep` files.
Accordingly, all data-derived figures below are **not measured**; they are not
zero-row dataset results.

| Dataset | Rows raw | Rows after label mapping | NaN/inf rows removed | Duplicate rows removed | Final rows / feature count | Class counts |
|---|---:|---:|---:|---:|---:|---|
| CIC-IDS2017 | not measured | not measured | not measured | not measured | not measured | not measured |
| CSE-CIC-IDS2018 | not measured | not measured | not measured | not measured | not measured | not measured |

The cleaner is designed to write these fields in `src/netshift/data.py:31`,
`src/netshift/data.py:36`, `src/netshift/data.py:44`, and
`src/netshift/data.py:49`; no generated report was available to supply values.

### Experiment results

`results/results_log.csv` was absent. There are **0 recorded rows available for
audit**. The requested experiment categories therefore have no measured
sample sizes, seeds, means, or standard deviations.

| Experiment | Recorded rows | Seeds used | Macro-F1 mean ± std | MCC mean ± std |
|---|---:|---|---|---|
| baseline | 0 | not measured | not measured | not measured |
| cross_network | 0 | not measured | not measured | not measured |
| shortcut_removed | 0 | not measured | not measured | not measured |
| label_budget | 0 | not measured | not measured | not measured |
| label_budget_uncertainty | 0 | not measured | not measured | not measured |

There are no result rows to classify as dry-run; **dry-run rows excluded: 0**.
The cap check is also **not auditable per result row** because the log is
absent. The visible configured defaults are `MAJORITY_CAP = 200_000` and
`SMOTE_CAP = 50_000` in `src/netshift/config.py:24` and
`src/netshift/config.py:25`. The experiment row dictionaries do not include
cap fields, and `src/netshift/metrics.py:31` writes only fields supplied in
each row, so future logs cannot independently prove which caps were used.

### Shortcut artifacts

Neither `results/shortcut_features.json` nor `results/feature_shift.csv` was
present. Shortcut feature names and their KS statistics are **not measured**.
The SHAP/KS calculation and selection rule are implemented in
`scripts/04_shap.py:42`, `scripts/04_shap.py:53`, and
`scripts/04_shap.py:65`, but there is no generated evidence to list or compare.

## Part 2 — Method checks

| # | Answer | Evidence and finding |
|---|---|---|
| 1 | **Yes** | The in-network holdout split occurs before `fit_predict` in `scripts/02_baseline.py:20` and `scripts/02_baseline.py:22`; the label-budget target split occurs before fitting in `scripts/05_label_budget.py:54` and `scripts/05_label_budget.py:66`. `src/netshift/models.py:57` balances training inputs before fitting; no scaler-fitting path was found. |
| 2 | **Yes (indirectly)** | Evaluation rows are not concatenated into the training matrices, but `scripts/05_label_budget.py:53` calculates class totals from all of `tgt` before the evaluation/pool split at line 54. Those totals set the per-class training label counts in `scripts/05_label_budget.py:30`, so evaluation-half labels influence training-set construction. |
| 3 | **Partly** | Default seeds are fixed to `[42, 43, 44]` in `src/netshift/config.py:16`; the label-budget CLI permits overriding them in `scripts/05_label_budget.py:40`. Results are logged per run, while `dashboard/app.py:26` and `dashboard/app.py:37` aggregate mean and standard deviation. Actual multi-seed values are not measured because no results log exists. |
| 4 | **Yes** | Both networks pass through the same cleaner and `map_series` call in `src/netshift/data.py:33`; mapping decisions are centralized in `src/netshift/labels.py`. |
| 5 | **Yes** | `src/netshift/features.py:76` selects the named training features, and line 78 checks for absent features and raises an error. |
| 6 | **Yes** | `src/netshift/metrics.py:11` documents macro-F1 and MCC as primary; lines 18–19 calculate them. Accuracy is also returned at line 17 and is identified as secondary by `.github/copilot-instructions.md`. |
| 7 | **Yes** | `src/netshift/metrics.py:14` derives the macro-F1 labels from classes present in `y_true`, so classes absent from that test target are not included in macro-F1. |
| 8 | **No** | The label-budget path samples randomly within each class using `group.sample` in `scripts/05_label_budget.py:30`. No uncertainty-selection implementation or `label_budget_uncertainty` results were found, so equal-count random-versus-uncertainty comparison is not present. |

## Part 3 — Ratings

Scores are out of 10. Every score for an aspect lacking real-data evidence is
below 8, as required.

| Aspect | Score | Evidence | Single change that would raise the score most |
|---|---:|---|---|
| Method correctness | 5/10 | Split-before-fit and feature alignment are present, but evaluation labels indirectly influence the label-budget sample counts (`scripts/05_label_budget.py:53`). | Derive the per-class budget totals only from the training-side pool. |
| Evidence quality | 1/10 | No cleaning reports, experiment log, or shortcut artifacts are present; the requested doctor script is missing. | Produce one real-data run bundle that records seeds and balancing caps with its metrics. |
| Baseline reproduction | 0/10 | The baseline script states an expected 97–99% in its docstring (`scripts/02_baseline.py:1`), but measured macro-F1 and MCC are not measured. | Run and report the in-network baseline on CIC-IDS2017 across the configured seeds. |
| Cross-network result | 0/10 | Cross-network results are not measured, and the implemented model list contains XGBoost and Random Forest, not logistic regression (`scripts/03_cross_network.py:9`). | Run a logistic-regression comparator alongside the existing models on the same real datasets. |
| Novelty evidence | 0/10 | The stratified random label-budget path exists, but no uncertainty selector or real-data results establish a difference beyond seed variance. | Add and evaluate an equal-label-count uncertainty-selection comparison across seeds. |
| Shortcut analysis | 0/10 | SHAP/KS and shortcut removal are implemented, but the feature list, KS statistics, and metric deltas are not measured. | Run the SHAP/KS ablation on real data and report per-seed deltas. |
| Code quality and tests | 6/10 | The project has separate data, feature, model, and metric modules; 11 tests pass in `.venv`, but the plain requested command fails collection and no real-data pipeline test was possible. | Add fixture-backed integration tests for cleaning, budget construction, and result logging. |
| Cross-platform compatibility | 2/10 | The README provides macOS and Ubuntu setup steps, but both verification boxes remain unchecked and Ubuntu has not been tested (`README.md:63`, `README.md:64`). | Run and record the pinned setup and test suite on Ubuntu 24.04. |
| Documentation and handoff | 3/10 | README and contract describe the workflow, but real-data and platform checks are open; the CICFlowMeter version is blank (`docs/MEMBER_B_CONTRACT.md:7`), and `lab/` contains only its README. | Complete and verify the Member B handoff artifacts: pinned tool version, reference header, run log, and class counts. |
| Scope and schedule risk | 3/10 | The one-command pipeline includes cleaning, two model families, SHAP, and repeated label-budget runs (`run_all.sh`), while real data and the uncertainty comparison are not ready. | Time-box a representative-data end-to-end pilot before committing to full-scale runs. |

**Overall score: 2.0/10** — arithmetic mean of the ten aspect scores.

### Honest summary

NetShift-IDS has a reasonably modular experimental scaffold and its 11 unit
tests pass in the project virtual environment, but the project has no available
real-data outputs, so baseline performance, cross-network degradation,
label-budget effects, shortcut impact, and class counts are all **not
measured**. There is also an indirect evaluation-label prevalence leak in the
label-budget sampler, and uncertainty selection is not implemented, so the
main novelty comparison cannot currently be assessed. The project is not yet
ready to claim experimental validation: first remove the evaluation-label
influence, complete the missing Member B handoff, then run and preserve the
real-data experiment artifacts on both supported platforms.
