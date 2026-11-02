import pandas as pd
import pytest

from netshift.features import align, feature_columns, normalize_columns


def test_strip_and_rename():
    df = normalize_columns(pd.DataFrame({" Dst Port": [80], "Label": ["BENIGN"]}))
    assert "Destination Port" in df.columns


def test_normalize_cse_headers_and_identifiers():
    df = normalize_columns(pd.DataFrame({
        "Src IP": ["10.0.0.1"],
        "Src Port": [1234],
        "Dst IP": ["10.0.0.2"],
        "Tot Fwd Pkts": [3],
        "Flow Byts/s": [42.0],
        "Pkt Len Mean": [14.0],
    }))
    assert list(df.columns) == [
        "Source IP", "Source Port", "Destination IP", "Total Fwd Packets",
        "Flow Bytes/s", "Packet Length Mean",
    ]
    assert feature_columns(df) == ["Total Fwd Packets", "Flow Bytes/s", "Packet Length Mean"]


def test_normalize_duplicate_alias_raises():
    df = pd.DataFrame({"Dst Port": [80], "Destination Port": [443]})
    with pytest.raises(ValueError, match="Duplicate columns"):
        normalize_columns(df)


def test_feature_columns_exclude_ids_and_labels():
    df = pd.DataFrame({"Flow ID": [1], "Source IP": [1], "Destination Port": [80], "label": ["Benign"]})
    assert feature_columns(df) == ["Destination Port"]


def test_align_missing_raises():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        align(df, ["a", "b"])
