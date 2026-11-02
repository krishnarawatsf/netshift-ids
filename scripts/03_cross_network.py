"""Step 3 (Review I): train on CIC-IDS2017, test on CSE-CIC-IDS2018 WITHOUT retraining."""
import pandas as pd

from netshift.config import CLEAN_DIR, SEEDS
from netshift.features import align, feature_columns
from netshift.metrics import evaluate, log_result
from netshift.models import encode, fit_predict

MODELS = ["xgboost", "rf"]


def main():
    src = pd.read_parquet(CLEAN_DIR / "clean_cicids2017.parquet")
    tgt = pd.read_parquet(CLEAN_DIR / "clean_cse2018.parquet")
    feats = feature_columns(src)

    Xs, ys = src[feats].to_numpy("float32"), encode(src["label"])
    Xt, yt = align(tgt, feats).to_numpy("float32"), encode(tgt["label"])

    for seed in SEEDS:
        for name in MODELS:
            _, pred = fit_predict(name, Xs, ys, Xt, seed)
            m = evaluate(yt, pred)
            log_result({
                "experiment": "cross_network", "train_net": "cicids2017", "test_net": "cse2018",
                "model": name, "feature_set": "all", "label_budget": 0.0, "seed": seed,
                "n_train": len(ys), "n_test": len(yt), "n_labelled_target": 0, **m,
            })
            print(f"[cross] {name} seed={seed} macroF1={m['macro_f1']:.4f} MCC={m['mcc']:.4f}")


if __name__ == "__main__":
    main()
