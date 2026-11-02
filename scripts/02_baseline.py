"""Step 2 (Review I): in-network baseline on CIC-IDS2017. Reproduces base paper 2 (expect ~97-99%)."""
import pandas as pd
from sklearn.model_selection import train_test_split

from netshift.config import CLEAN_DIR, SEEDS, TEST_SIZE
from netshift.features import feature_columns
from netshift.metrics import evaluate, log_result
from netshift.models import encode, fit_predict

MODELS = ["xgboost", "rf"]


def main():
    df = pd.read_parquet(CLEAN_DIR / "clean_cicids2017.parquet")
    feats = feature_columns(df)
    X = df[feats].to_numpy("float32")
    y = encode(df["label"])

    for seed in SEEDS:
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=seed)
        for name in MODELS:
            _, pred = fit_predict(name, Xtr, ytr, Xte, seed)
            m = evaluate(yte, pred)
            log_result({
                "experiment": "baseline", "train_net": "cicids2017", "test_net": "cicids2017_holdout",
                "model": name, "selection": "none", "feature_set": "all",
                "label_budget": 0.0, "seed": seed,
                "n_train": len(ytr), "n_test": len(yte), "n_labelled_target": 0, **m,
            })
            print(f"[baseline] {name} seed={seed} macroF1={m['macro_f1']:.4f} MCC={m['mcc']:.4f}")


if __name__ == "__main__":
    main()
