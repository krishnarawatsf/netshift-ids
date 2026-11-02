"""Build a markdown summary table from the experiment log."""
import pandas as pd

from netshift.config import RESULTS_DIR, RESULTS_LOG


def render_report(results: pd.DataFrame) -> str:
    required = {
        "experiment", "model", "seed", "macro_f1", "mcc",
        "n_train", "n_test", "n_labelled_target",
        "majority_cap", "smote_cap",
    }
    missing = sorted(required - set(results.columns))
    if missing:
        raise ValueError(f"Results log is missing required columns: {missing}")
    if results.empty:
        raise ValueError("Experiment log contains no rows.")

    dimensions = [
        column for column in
        ("experiment", "model", "selection", "feature_set", "label_budget")
        if column in results.columns
    ]
    seed_key = [*dimensions, "seed"]
    repeated = results[results.duplicated(seed_key, keep=False)]
    if not repeated.empty:
        for key, group in repeated.groupby(seed_key, dropna=False):
            if group.nunique(dropna=False).gt(1).any():
                raise ValueError(f"Conflicting result rows for experiment seed {key!r}.")
        results = results.drop_duplicates(subset=seed_key)

    summary = (
        results.groupby(dimensions, dropna=False)
        .agg(
            rows=("seed", "size"),
            seeds=("seed", "nunique"),
            n_train=("n_train", "mean"),
            n_test=("n_test", "mean"),
            n_labelled_target=("n_labelled_target", "mean"),
            macro_f1_mean=("macro_f1", "mean"),
            macro_f1_std=("macro_f1", "std"),
            mcc_mean=("mcc", "mean"),
            mcc_std=("mcc", "std"),
            majority_caps=("majority_cap", lambda values: ", ".join(map(str, sorted(values.unique())))),
            smote_caps=("smote_cap", lambda values: ", ".join(map(str, sorted(values.unique())))),
        )
        .reset_index()
    )
    numeric = summary.select_dtypes(include="number").columns
    summary[numeric] = summary[numeric].round(4)
    headers = list(summary.columns)
    rows = summary.astype(object).where(pd.notna(summary), "not measured").values.tolist()
    table = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    table.extend("| " + " | ".join(map(str, row)) + " |" for row in rows)
    return "\n".join([
        "# NetShift-IDS experiment tables",
        "",
        "Generated from `results/results_log.csv`; no metrics are recomputed here.",
        "",
        *table,
        "",
    ])


def main():
    if not RESULTS_LOG.is_file():
        raise FileNotFoundError(f"No experiment log found at {RESULTS_LOG}")
    results = pd.read_csv(RESULTS_LOG)
    report = render_report(results)
    output = RESULTS_DIR / "tables.md"
    output.write_text(report, encoding="utf-8")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
