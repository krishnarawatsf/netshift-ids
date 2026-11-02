# NetShift-IDS performance audit — real-data update

**Updated:** 2026-11-02
**Scope:** Completed local real-data experiments on CIC-IDS2017 and
CSE-CIC-IDS2018. This update supersedes the earlier snapshot below wherever
their evidence or ratings differ.

## Evidence and comparisons

| Dataset | Raw rows | Rows after label mapping | NaN/inf removed | Duplicates removed | Final rows | Features |
|---|---:|---:|---:|---:|---:|---:|
| CIC-IDS2017 | 2,830,743 | 2,671,766 | 2,741 | 261,786 | 2,407,239 | 77 |
| CSE-CIC-IDS2018 | 16,232,943 | 16,071,009 | 94,465 | 4,669,943 | 11,306,601 | 78 |

CIC-IDS2017 contains 8 CSV files and CSE-CIC-IDS2018 contains 10. All 77 CIC
training features were aligned by name in CSE; CSE's extra `Protocol` feature
was not used. CSE's flag-count headers were normalized, and CIC's duplicate
`Fwd Header Length.1` was removed only after confirming its values matched the
original column.

The results log contains 114 rows, including 24 exact duplicate random
label-budget rows written by the standalone budget run and the uncertainty
comparison's random control. Summary statistics below count one row per
experiment/model/selection/feature-set/budget/seed; the report generator now
deduplicates identical seed records and rejects conflicting records. Every
logged row has the configured caps: `MAJORITY_CAP=200000`,
`SMOTE_CAP=50000`. Seeds are 42, 43, and 44.

| Experiment | Model | Macro-F1 mean ± std | MCC mean ± std |
|---|---|---:|---:|
| Baseline, CIC holdout | XGBoost | 0.9543 ± 0.0022 | 0.9967 ± 0.0002 |
| Baseline, CIC holdout | Random Forest | 0.9513 ± 0.0022 | 0.9954 ± 0.0001 |
| CIC → CSE | XGBoost | 0.4936 ± 0.0066 | 0.5672 ± 0.0131 |
| CIC → CSE | Random Forest | 0.1917 ± 0.0016 | 0.1262 ± 0.0043 |
| CIC → CSE, shortcuts removed | XGBoost | 0.4068 ± 0.0623 | 0.3354 ± 0.0610 |
| CIC → CSE, shortcuts removed | Random Forest | 0.1947 ± 0.0142 | 0.2315 ± 0.0123 |

Baseline accuracy was approximately 99.9%, but baseline macro-F1 was about
95%. The script's cited 97–99% literature expectation is not a like-for-like
comparison until the source, model, split protocol, and metric are matched.
The cross-network drop is large for both model families; no logistic-regression
comparator was run.

Shortcut analysis identified `min_seg_size_forward` (KS=0.39265) and
`Fwd IAT Min` (KS=0.37675), both among CIC's top 15 SHAP-ranked features and
above the 0.3 KS threshold. Removing them lowered XGBoost cross-network
macro-F1 by 0.0868, while Random Forest macro-F1 changed by +0.0030. Thus the
ablation effect is model-dependent.

Random versus uncertainty selection used equal target-label counts from the
same pool and evaluation split. Mean macro-F1 across three seeds:

| Model | Budget | Random | Uncertainty |
|---|---:|---:|---:|
| XGBoost | 1% | 0.8963 ± 0.0576 | 0.7414 ± 0.0004 |
| XGBoost | 5% | 0.8840 ± 0.0407 | 0.8415 ± 0.0520 |
| XGBoost | 10% | 0.8665 ± 0.0025 | 0.8478 ± 0.0213 |
| Random Forest | 1% | 0.8597 ± 0.0287 | 0.3758 ± 0.0384 |
| Random Forest | 5% | 0.8801 ± 0.0115 | 0.5024 ± 0.0688 |
| Random Forest | 10% | 0.8802 ± 0.0030 | 0.8088 ± 0.0138 |

Random selection outperformed uncertainty selection at every nonzero budget
for both models in these runs. This is a measured negative result, not evidence
that uncertainty selection helps. The 0% setting is the no-target-label control.

`pytest` passed **31 tests** after the report's duplicate-row handling was
covered. `scripts/doctor.py` passed **23/23 checks**. Experiments ran on macOS;
Ubuntu compatibility has not been tested. SHAP, cross-network, label-budget,
and report artifacts are under `results/`.

## Updated ratings

Scores reflect the evidence above, not a requested minimum. Scores below 7
remain below 7 where the supporting comparison or platform verification is
missing.

| Aspect | Score | Evidence | Single change most likely to raise the score |
|---|---:|---|---|
| Method correctness | 7/10 | Fixed-seed splits, training-only balancing, and named feature alignment were exercised on both networks. | Add an automated test proving the evaluation-half rows never enter fitting in every label-budget path. |
| Evidence quality | 8/10 | Cleaning reports and 3-seed means/standard deviations exist for all configured experiments; duplicate seed rows are handled in reports. | Make the documented one-command run reproducible from a clean environment, including paths containing spaces. |
| Baseline reproduction | 6/10 | CIC holdout accuracy is about 99.9%, but macro-F1 is about 95% and literature protocol equivalence is unverified. | Reproduce a cited paper's exact model, split, and metric. |
| Cross-network result | 7/10 | The CIC→CSE drop is measured over 11.3M target rows for two model families and three seeds. | Add a logistic-regression comparator with the same features and split. |
| Novelty evidence | 7/10 | Equal-count uncertainty selection was measured; it consistently underperformed random selection at nonzero budgets. | Repeat across independent target train/evaluation splits. |
| Shortcut analysis | 7/10 | Two features met the stated SHAP/KS rule; ablation effects were recorded for both models. | Validate the feature rule and ablation on another target network. |
| Code quality and tests | 7/10 | The 31-test suite and 23 doctor checks pass; report generation now rejects conflicting duplicate seed records. | Fix and verify editable installation and the documented command from a workspace path containing spaces. |
| Cross-platform compatibility | 3/10 | macOS was exercised; no Ubuntu 24.04 run is recorded. | Run setup, tests, and a small pipeline check on Ubuntu 24.04. |
| Documentation and handoff | 5/10 | The README and contract exist and results are now measured, but the Member B contract still has an unfilled CICFlowMeter version and handoff evidence. | Complete and verify the lab handoff fields and artifacts. |
| Scope and schedule risk | 6/10 | All current experiment families ran, but there is no logistic comparator, independent target split, or second cross-network pair. | Time-box external validation on an independent dataset and protocol. |

**Overall score: 6.3/10** — arithmetic mean of the ten category scores.

### Honest summary

The project now has a substantial, multi-seed real-data result set: strong
in-network classification, a large CIC-to-CSE performance drop, measurable
shortcut effects, and a clear negative comparison where random target-label
selection beats uncertainty selection at all tested nonzero budgets. These
results advance the project well beyond its earlier unmeasured state, but they
do not establish literature-equivalent baseline reproduction, a model-general
shortcut effect, or a benefit from uncertainty sampling. Ubuntu validation,
the logistic-regression comparison, independent target splits, and completion
of the lab handoff remain open; therefore, a score of at least 7 in every
category would overstate what has been verified.

---

# Historical audit snapshot (before real-data runs)

The following section is preserved as the original audit snapshot. Its
"not measured" statements describe the state before the execution update
above and are no longer current.

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
