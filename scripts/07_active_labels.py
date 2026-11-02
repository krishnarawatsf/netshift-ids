"""Compare random and uncertainty-based target label selection."""
import argparse

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from netshift.active_labels import random_selection, uncertainty_selection
from netshift.config import CLEAN_DIR, LABEL_BUDGETS, SEEDS
from netshift.features import align, feature_columns
from netshift.metrics import evaluate, log_result
from netshift.models import encode, fit_predict, train_model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["xgboost", "rf"])
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    args = parser.parse_args()

    source = pd.read_parquet(CLEAN_DIR / "clean_cicids2017.parquet")
    target = pd.read_parquet(CLEAN_DIR / "clean_cse2018.parquet")
    features = feature_columns(source)
    eval_df, pool = train_test_split(
        target, test_size=0.5, stratify=target["label"], random_state=SEEDS[0]
    )
    X_eval = align(eval_df, features).to_numpy("float32")
    y_eval = encode(eval_df["label"])
    X_pool = align(pool, features).to_numpy("float32")
    X_source = source[features].to_numpy("float32")
    y_source = encode(source["label"])

    for seed in args.seeds:
        for model_name in args.models:
            selector = train_model(model_name, X_source, y_source, seed)
            probabilities = selector.predict_proba(X_pool)
            for budget in LABEL_BUDGETS:
                selections = {
                    "random": random_selection(len(pool), budget, seed),
                    "uncertainty": uncertainty_selection(probabilities, budget),
                }
                if len(selections["random"]) != len(selections["uncertainty"]):
                    raise RuntimeError("Random and uncertainty selections must use equal label counts.")
                for strategy, indices in selections.items():
                    labelled = pool.iloc[indices]
                    X_train = np.vstack([
                        X_source, align(labelled, features).to_numpy("float32")
                    ])
                    y_train = np.concatenate([y_source, encode(labelled["label"])])
                    _, predictions = fit_predict(
                        model_name, X_train, y_train, X_eval, seed
                    )
                    metrics = evaluate(y_eval, predictions)
                    experiment = (
                        "label_budget_uncertainty"
                        if strategy == "uncertainty"
                        else "label_budget"
                    )
                    log_result({
                        "experiment": experiment,
                        "train_net": "cicids2017",
                        "test_net": "cse2018_eval_half",
                        "model": model_name,
                        "selection": strategy,
                        "feature_set": "all",
                        "label_budget": budget,
                        "seed": seed,
                        "n_train": len(y_train),
                        "n_test": len(y_eval),
                        "n_labelled_target": len(labelled),
                        **metrics,
                    })
                    print(
                        f"[{strategy} budget={budget:.2f}] {model_name} "
                        f"seed={seed} labels={len(labelled)} "
                        f"macroF1={metrics['macro_f1']:.4f} MCC={metrics['mcc']:.4f}"
                    )


if __name__ == "__main__":
    main()
