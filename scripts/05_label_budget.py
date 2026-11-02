"""Step 5 (Review II, main novelty): label-budget curve on CSE-CIC-IDS2018.

The target network is split 50/50 once (fixed seed). The evaluation half is never used
for training. Random labels are sampled uniformly from the pool without reading its
labels; each budget selects the same fraction of the pool for comparison.

Usage:
  python scripts/05_label_budget.py
  python scripts/05_label_budget.py --feature-set shortcut_removed
"""
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from netshift.active_labels import random_selection
from netshift.config import CLEAN_DIR, LABEL_BUDGETS, RESULTS_DIR, SEEDS
from netshift.features import align, feature_columns
from netshift.metrics import evaluate, log_result
from netshift.models import encode, fit_predict


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

    eval_df, pool = train_test_split(tgt, test_size=0.5, stratify=tgt["label"], random_state=SEEDS[0])
    Xe = align(eval_df, feats).to_numpy("float32")
    ye = encode(eval_df["label"])
    Xs = src[feats].to_numpy("float32")
    ys = encode(src["label"])

    for seed in args.seeds:
        for budget in LABEL_BUDGETS:
            selected = random_selection(len(pool), budget, seed)
            lab = pool.iloc[selected]
            X = np.vstack([Xs, align(lab, feats).to_numpy("float32")])
            y = np.concatenate([ys, encode(lab["label"])])
            for name in args.models:
                _, pred = fit_predict(name, X, y, Xe, seed)
                m = evaluate(ye, pred)
                log_result({
                    "experiment": "label_budget", "train_net": "cicids2017", "test_net": "cse2018_eval_half",
                    "model": name, "selection": "random", "feature_set": args.feature_set,
                    "label_budget": budget, "seed": seed,
                    "n_train": len(y), "n_test": len(ye), "n_labelled_target": len(lab), **m,
                })
                print(f"[budget {budget:.2f}] {name} {args.feature_set} seed={seed} "
                      f"labels={len(lab)} macroF1={m['macro_f1']:.4f} MCC={m['mcc']:.4f}")


if __name__ == "__main__":
    main()
