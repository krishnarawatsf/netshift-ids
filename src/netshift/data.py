"""Load raw CSVs and clean them. Cleaning happens before any split."""
from pathlib import Path

import numpy as np
import pandas as pd

from netshift.config import LABEL_COL
from netshift.features import feature_columns, normalize_columns
from netshift.labels import DROP, map_series


def load_folder(folder) -> pd.DataFrame:
    files = sorted(Path(folder).glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {folder}")
    frames = []
    for f in files:
        df = pd.read_csv(f, low_memory=False, encoding="utf-8", encoding_errors="replace")
        df = normalize_columns(df)
        if LABEL_COL not in df.columns:
            raise ValueError(f"{f.name}: no '{LABEL_COL}' column")
        # CSE-CIC-IDS2018 files contain repeated header rows in the middle of the data
        df = df[df[LABEL_COL].astype(str).str.strip() != LABEL_COL]
        frames.append(df)
        print(f"loaded {f.name}: {len(df):,} rows")
    return pd.concat(frames, ignore_index=True)


def clean(df: pd.DataFrame):
    """Map labels, coerce numeric, remove inf/NaN and duplicates. Returns (clean_df, report)."""
    report = {"rows_raw": int(len(df))}
    df = df.copy()
    df["label"] = map_series(df[LABEL_COL])
    df = df.dropna(subset=["label"])
    df = df[df["label"] != DROP]
    report["rows_after_label_mapping"] = int(len(df))

    feats = feature_columns(df)
    for c in feats:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df[feats] = df[feats].replace([np.inf, -np.inf], np.nan)
    before = len(df)
    df = df.dropna(subset=feats)
    report["rows_dropped_nan_or_inf"] = int(before - len(df))

    df = df[feats + ["label"]].astype({c: "float32" for c in feats})
    before = len(df)
    df = df.drop_duplicates()
    report["rows_dropped_duplicates"] = int(before - len(df))
    report["n_features"] = len(feats)
    return df.reset_index(drop=True), report


def stratified_sample(df: pd.DataFrame, frac: float, min_per_class: int, seed: int) -> pd.DataFrame:
    """Sample each class separately so rare attacks survive the sampling."""
    parts = []
    for _, group in df.groupby("label"):
        n = min(len(group), max(min_per_class, int(len(group) * frac)))
        parts.append(group.sample(n=n, random_state=seed))
    return pd.concat(parts).sample(frac=1, random_state=seed).reset_index(drop=True)
