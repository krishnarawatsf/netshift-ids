"""Step 4 (Review II): SHAP and distribution shift -> shortcut features -> retrain without them.

Shortcut rule (document any change in the report):
  a feature is a shortcut if it is in the top SHORTCUT_TOP_K by SHAP on CIC-IDS2017
  AND its distribution differs strongly between the networks (KS statistic >= KS_THRESHOLD).
"""
import json

import numpy as np
import pandas as pd
import shap
from scipy.stats import ks_2samp

from netshift.config import (CLEAN_DIR, KS_SAMPLE, KS_THRESHOLD, RESULTS_DIR,
                             SEEDS, SHAP_SAMPLE, SHORTCUT_TOP_K)
from netshift.features import align, feature_columns
from netshift.metrics import evaluate, log_result
from netshift.models import encode, fit_predict, train_model


def mean_abs_shap(model, X):
    """Mean |SHAP| per feature, averaged over samples and classes. Handles the shapes shap can return."""
    sv = shap.TreeExplainer(model).shap_values(X)
    if isinstance(sv, list):                      # one (samples, features) array per class
        return np.abs(np.stack(sv)).mean(axis=(0, 1))
    arr = np.asarray(sv)
    if arr.ndim == 3:                             # (samples, features, classes)
        return np.abs(arr).mean(axis=(0, 2))
    return np.abs(arr).mean(axis=0)


def main():
    src = pd.read_parquet(CLEAN_DIR / "clean_cicids2017.parquet")
    tgt = pd.read_parquet(CLEAN_DIR / "clean_cse2018.parquet")
    feats = feature_columns(src)
    Xs = src[feats].to_numpy("float32")
    ys = encode(src["label"])
    Xt = align(tgt, feats).to_numpy("float32")
    yt = encode(tgt["label"])

    rng = np.random.default_rng(SEEDS[0])
    model = train_model("xgboost", Xs, ys, SEEDS[0])

    s_idx = rng.choice(len(Xs), min(SHAP_SAMPLE, len(Xs)), replace=False)
    t_idx = rng.choice(len(Xt), min(SHAP_SAMPLE, len(Xt)), replace=False)
    imp_s = mean_abs_shap(model, Xs[s_idx])
    imp_t = mean_abs_shap(model, Xt[t_idx])
    if len(imp_s) != len(feats):
        raise ValueError("SHAP output does not match the feature count. Check the shap version.")

    ks_s = rng.choice(len(Xs), min(KS_SAMPLE, len(Xs)), replace=False)
    ks_t = rng.choice(len(Xt), min(KS_SAMPLE, len(Xt)), replace=False)
    ks = [ks_2samp(Xs[ks_s, j], Xt[ks_t, j]).statistic for j in range(len(feats))]
    rank_s = pd.Series(imp_s).rank(ascending=False, method="min").to_numpy()

    shift = pd.DataFrame({
        "feature": feats,
        "mean_abs_shap_cicids2017": imp_s,
        "mean_abs_shap_cse2018": imp_t,
        "rank_cicids2017": rank_s,
        "ks_stat": ks,
    }).sort_values("ks_stat", ascending=False)
    shift.to_csv(RESULTS_DIR / "feature_shift.csv", index=False)

    shortcuts = shift.loc[
        (shift["rank_cicids2017"] <= SHORTCUT_TOP_K) & (shift["ks_stat"] >= KS_THRESHOLD), "feature"
    ].tolist()
    (RESULTS_DIR / "shortcut_features.json").write_text(json.dumps(
        {"top_k": SHORTCUT_TOP_K, "ks_threshold": KS_THRESHOLD, "features": shortcuts}, indent=2))
    print("shortcut features:", shortcuts or "none (report this as a finding)")

    keep = [j for j, f in enumerate(feats) if f not in shortcuts]
    Xs_k, Xt_k = Xs[:, keep], Xt[:, keep]
    for seed in SEEDS:
        for name in ["xgboost", "rf"]:
            _, pred = fit_predict(name, Xs_k, ys, Xt_k, seed)
            m = evaluate(yt, pred)
            log_result({
                "experiment": "shortcut_removed", "train_net": "cicids2017", "test_net": "cse2018",
                "model": name, "feature_set": "shortcut_removed", "label_budget": 0.0, "seed": seed,
                "n_train": len(ys), "n_test": len(yt), "n_labelled_target": 0, **m,
            })
            print(f"[shortcut-removed] {name} seed={seed} macroF1={m['macro_f1']:.4f} MCC={m['mcc']:.4f}")


if __name__ == "__main__":
    main()
