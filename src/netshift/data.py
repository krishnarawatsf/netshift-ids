"""Load raw CSVs and clean them. Cleaning happens before any split."""
from pathlib import Path
import os
import tempfile

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


def clean_folder_to_parquet(folder, output, chunksize: int = 200_000) -> dict:
    """Clean large CSV collections in bounded chunks and write Parquet incrementally."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    folder = Path(folder)
    output = Path(output)
    files = sorted(folder.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {folder}")
    if chunksize < 1:
        raise ValueError("chunksize must be positive")

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{output.stem}.", suffix=".parquet", dir=output.parent
    )
    os.close(fd)
    temporary = Path(temporary_name)
    writer = None
    seen_hashes = set()
    feature_names = None
    class_counts = {}
    report = {
        "rows_raw": 0,
        "rows_after_label_mapping": 0,
        "rows_dropped_nan_or_inf": 0,
        "rows_dropped_duplicates": 0,
    }

    try:
        for csv_path in files:
            for frame in pd.read_csv(
                csv_path,
                chunksize=chunksize,
                low_memory=False,
                encoding="utf-8",
                encoding_errors="replace",
            ):
                frame = normalize_columns(frame)
                if LABEL_COL not in frame.columns:
                    raise ValueError(f"{csv_path.name}: no '{LABEL_COL}' column")
                frame = frame[frame[LABEL_COL].astype(str).str.strip() != LABEL_COL]
                clean_frame, chunk_report = clean(frame)
                if feature_names is None:
                    feature_names = [c for c in clean_frame.columns if c != "label"]
                    if not feature_names:
                        raise ValueError(f"{csv_path.name}: no numeric feature columns")
                elif [c for c in clean_frame.columns if c != "label"] != feature_names:
                    raise ValueError(f"{csv_path.name}: feature schema differs after normalization")

                for key in report:
                    report[key] += chunk_report[key]
                if clean_frame.empty:
                    continue

                hashes = pd.util.hash_pandas_object(clean_frame, index=False).to_numpy()
                keep = np.zeros(len(clean_frame), dtype=bool)
                for index, value in enumerate(hashes):
                    key = int(value)
                    if key not in seen_hashes:
                        seen_hashes.add(key)
                        keep[index] = True
                report["rows_dropped_duplicates"] += int((~keep).sum())
                clean_frame = clean_frame.loc[keep]
                if clean_frame.empty:
                    continue

                table = pa.Table.from_pandas(clean_frame, preserve_index=False)
                if writer is None:
                    writer = pq.ParquetWriter(temporary, table.schema, compression="snappy")
                writer.write_table(table)
                for label, count in clean_frame["label"].value_counts().items():
                    class_counts[label] = class_counts.get(label, 0) + int(count)
        if writer is None:
            raise ValueError(f"No valid rows remained after cleaning CSV files in {folder}")
        writer.close()
        writer = None
        temporary.replace(output)
    except Exception:
        if writer is not None:
            writer.close()
        temporary.unlink(missing_ok=True)
        raise

    report["n_features"] = len(feature_names)
    report["rows_final"] = sum(class_counts.values())
    report["class_counts"] = class_counts
    return report


def stratified_sample(df: pd.DataFrame, frac: float, min_per_class: int, seed: int) -> pd.DataFrame:
    """Sample each class separately so rare attacks survive the sampling."""
    parts = []
    for _, group in df.groupby("label"):
        n = min(len(group), max(min_per_class, int(len(group) * frac)))
        parts.append(group.sample(n=n, random_state=seed))
    return pd.concat(parts).sample(frac=1, random_state=seed).reset_index(drop=True)
