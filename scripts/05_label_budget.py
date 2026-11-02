"""Step 5 (Review II, main novelty): label-budget curve on CSE-CIC-IDS2018.

The target network is split 50/50 once (fixed seed). The evaluation half is never used
for training. Labels are drawn from the other half (the pool), stratified by class:
budget x (class size in the target network), at least 1 row per class when budget > 0.

Usage:
  python scripts/05_label_budget.py
  python scripts/05_label_budget.py --feature-set shortcut_removed
"""
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from netshift.config import CLEAN_DIR, LABEL_BUDGETS, RESULTS_DIR, SEEDS
from netshift.features import align, feature_columns
from netshift.metrics import evaluate, log_result
from netshift.models import encode, fit_predict


def sample_labels(pool, class_totals, budget, seed):
    if budget == 0:
        return pool.iloc[0:0]
    parts = []
    for c, total in class_totals.items():
        group = pool[pool["label"] == c]
        n = min(len(group), max(1, int(round(budget * int(total)))))
        if n:
            parts.append(group.sample(n=n, random_state=seed))
    return pd.concat(parts) if parts else pool.iloc[0:0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["xgboost", "rf"])
    ap.add_argument("--feature-set", choices=["all", "shortcut_removed"], default="all")
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    args = ap.parse_args()

    src = pd.read_parquet(CLEAN_DIR / "clean_cicids2017.parquet")
    tgt = pd.read_parquet(CLEAN_DIR / "clean_cse2018.parquet")
    feats = feature_columns(src)
    if args.feature_set == "shortcut_removed":
        path = RESULTS_DIR / "shortcut_features.json"
        if not path.exists():
            raise FileNotFoundError("Run scripts/04_shap.py first.")
        drop = set(json.loads(path.read_text())["features"])
        feats = [f for f in feats if f not in drop]

    class_totals = tgt["label"].value_counts().to_dict()
    eval_df, pool = train_test_split(tgt, test_size=0.5, stratify=tgt["label"], random_state=SEEDS[0])
    Xe = align(eval_df, feats).to_numpy("float32")
    ye = encode(eval_df["label"])
    Xs = src[feats].to_numpy("float32")
    ys = encode(src["label"])

    for seed in args.seeds:
        for budget in LABEL_BUDGETS:
            lab = sample_labels(pool, class_totals, budget, seed)
            X = np.vstack([Xs, align(lab, feats).to_numpy("float32")])
            y = np.concatenate([ys, encode(lab["label"])])
            for name in args.models:
                _, pred = fit_predict(name, X, y, Xe, seed)
                m = evaluate(ye, pred)
                log_result({
                    "experiment": "label_budget", "train_net": "cicids2017", "test_net": "cse2018_eval_half",
                    "model": name, "feature_set": args.feature_set, "label_budget": budget, "seed": seed,
                    "n_train": len(y), "n_test": len(ye), "n_labelled_target": len(lab), **m,
                })
                print(f"[budget {budget:.2f}] {name} {args.feature_set} seed={seed} "
                      f"labels={len(lab)} macroF1={m['macro_f1']:.4f} MCC={m['mcc']:.4f}")


if __name__ == "__main__":
    main()
