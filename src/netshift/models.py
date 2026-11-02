"""Model construction. Balancing is applied to training data only, never to test data."""
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from netshift.config import CLASS_TO_ID, MAJORITY_CAP, SMOTE_CAP


def encode(labels):
    """Map class names to fixed integer IDs, so every network uses the same mapping."""
    ids = labels.map(CLASS_TO_ID)
    if ids.isna().any():
        bad = sorted(labels[ids.isna()].unique())
        raise ValueError(f"Labels not in CLASSES: {bad}")
    return ids.to_numpy(dtype="int64")


def balance(X, y, seed):
    """Undersample classes above MAJORITY_CAP, then SMOTE classes below SMOTE_CAP."""
    rng = np.random.default_rng(seed)
    keep = []
    for c in np.unique(y):
        ids = np.flatnonzero(y == c)
        if len(ids) > MAJORITY_CAP:
            ids = rng.choice(ids, MAJORITY_CAP, replace=False)
        keep.append(ids)
    keep = np.concatenate(keep)
    X, y = X[keep], y[keep]

    counts = {int(c): int((y == c).sum()) for c in np.unique(y)}
    targets = {c: n for c, n in counts.items() if 1 < n < SMOTE_CAP}
    if targets:
        k = min(5, min(targets.values()) - 1)
        smote = SMOTE(sampling_strategy={c: SMOTE_CAP for c in targets},
                      k_neighbors=k, random_state=seed)
        X, y = smote.fit_resample(X, y)
    return X, y


def build_model(name: str, seed: int):
    if name == "xgboost":
        return XGBClassifier(
            n_estimators=300, max_depth=8, learning_rate=0.1,
            tree_method="hist", objective="multi:softprob",
            num_class=len(CLASS_TO_ID), eval_metric="mlogloss",
            random_state=seed, n_jobs=-1,
        )
    if name == "rf":
        return RandomForestClassifier(
            n_estimators=200, class_weight="balanced_subsample",
            n_jobs=-1, random_state=seed,
        )
    raise ValueError(f"Unknown model {name!r}")


def train_model(name, X_train, y_train, seed):
    X_bal, y_bal = balance(X_train, y_train, seed)
    model = build_model(name, seed)
    model.fit(X_bal, y_bal)
    return model


def fit_predict(name, X_train, y_train, X_test, seed):
    model = train_model(name, X_train, y_train, seed)
    return model, model.predict(X_test)
