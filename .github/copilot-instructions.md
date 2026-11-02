# Copilot instructions: NetShift-IDS

## Project
Cross-network intrusion detection. XGBoost and Random Forest with SMOTE are trained on
CIC-IDS2017 and tested on CSE-CIC-IDS2018 and our own lab data (Network C). The main
contribution is a label-budget curve (0%, 1%, 5%, 10% of target labels).

## Non-negotiable rules
- Python 3.11. Code must run the same on macOS (Apple Silicon) and Ubuntu 24.04.
- Use pathlib. No hardcoded paths, no backslashes, no OS-specific shell commands.
- Files use LF line endings. Module and file names are lowercase with underscores.
- Split before any fitting. SMOTE, undersampling and scalers are fit on training data only.
  The target network's evaluation half must never touch training.
- Seeds come from netshift.config.SEEDS. Never call random functions without a seed.
- Report macro-F1 and MCC as primary metrics. Accuracy is secondary.
- Results are written only through netshift.metrics.log_result, into results/results_log.csv.
- Label mapping only through netshift.labels. Unknown labels must raise, never be dropped silently.
- Feature selection only through netshift.features.align. Missing features must raise.
- Do not add a dependency without pinning it in requirements.txt.
- Never commit files from data/ or results_log.csv.
- Dashboard code reads results/ only. It never trains models.

## Style
- Type hints on public functions. One-line or short docstrings that explain why, not what.
- Put tests in tests/ with pytest. Every new label or rename needs a test.
- Keep scripts in scripts/ thin: they call functions in src/netshift/.

## Before you finish a change
1. Run `pytest -q`.
2. Confirm no paths are hardcoded and no file uses CRLF line endings.
