import numpy as np
import pandas as pd

from netshift.data import clean, clean_folder_to_parquet


def test_clean_reports_mapping_invalid_numeric_and_duplicates():
    raw = pd.DataFrame({
        "Destination Port": [80, 80, 443, 22, np.inf],
        "Label": ["BENIGN", "BENIGN", "BENIGN", "PortScan", "BENIGN"],
    })
    cleaned, report = clean(raw)

    assert report["rows_raw"] == 5
    assert report["rows_after_label_mapping"] == 4
    assert report["rows_dropped_nan_or_inf"] == 1
    assert report["rows_dropped_duplicates"] == 1
    assert report["n_features"] == 1
    assert len(cleaned) == 2
    assert set(cleaned["label"]) == {"Benign"}


def test_clean_folder_to_parquet_deduplicates_across_chunks(tmp_path):
    source = tmp_path / "csv"
    source.mkdir()
    pd.DataFrame({
        "Destination Port": [80, 443, 80, 22],
        "Label": ["BENIGN", "DDoS", "BENIGN", "DoS Hulk"],
    }).to_csv(source / "part.csv", index=False)
    output = tmp_path / "clean.parquet"

    report = clean_folder_to_parquet(source, output, chunksize=2)
    result = pd.read_parquet(output)

    assert report["rows_raw"] == 4
    assert report["rows_dropped_duplicates"] == 1
    assert report["rows_final"] == 3
    assert report["class_counts"] == {"Benign": 1, "DDoS": 1, "DoS": 1}
    assert len(result) == 3
