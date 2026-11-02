"""Column names and feature selection. Keeps CIC-IDS2017 and CSE-CIC-IDS2018 aligned."""
import pandas as pd

from netshift.config import ID_COLUMNS, LABEL_COL

# CSE-CIC-IDS2018 uses shorter names for many CICFlowMeter columns. Identifiers are
# renamed too, so both networks remove the same fields before model training.
RENAME_CSE2018 = {
    "Src IP": "Source IP",
    "Src Port": "Source Port",
    "Dst IP": "Destination IP",
    "Dst Port": "Destination Port",
    "Tot Fwd Pkts": "Total Fwd Packets",
    "Tot Bwd Pkts": "Total Backward Packets",
    "TotLen Fwd Pkts": "Total Length of Fwd Packets",
    "TotLen Bwd Pkts": "Total Length of Bwd Packets",
    "Fwd Pkt Len Max": "Fwd Packet Length Max",
    "Fwd Pkt Len Min": "Fwd Packet Length Min",
    "Fwd Pkt Len Mean": "Fwd Packet Length Mean",
    "Fwd Pkt Len Std": "Fwd Packet Length Std",
    "Bwd Pkt Len Max": "Bwd Packet Length Max",
    "Bwd Pkt Len Min": "Bwd Packet Length Min",
    "Bwd Pkt Len Mean": "Bwd Packet Length Mean",
    "Bwd Pkt Len Std": "Bwd Packet Length Std",
    "Flow Byts/s": "Flow Bytes/s",
    "Flow Pkts/s": "Flow Packets/s",
    "Fwd IAT Tot": "Fwd IAT Total",
    "Bwd IAT Tot": "Bwd IAT Total",
    "Fwd Header Len": "Fwd Header Length",
    "Bwd Header Len": "Bwd Header Length",
    "Fwd Pkts/s": "Fwd Packets/s",
    "Bwd Pkts/s": "Bwd Packets/s",
    "Pkt Len Min": "Min Packet Length",
    "Pkt Len Max": "Max Packet Length",
    "Pkt Len Mean": "Packet Length Mean",
    "Pkt Len Std": "Packet Length Std",
    "Pkt Len Var": "Packet Length Variance",
    "Pkt Size Avg": "Average Packet Size",
    "Fwd Seg Size Avg": "Avg Fwd Segment Size",
    "Bwd Seg Size Avg": "Avg Bwd Segment Size",
    "Fwd Byts/b Avg": "Fwd Avg Bytes/Bulk",
    "Fwd Pkts/b Avg": "Fwd Avg Packets/Bulk",
    "Fwd Blk Rate Avg": "Fwd Avg Bulk Rate",
    "Bwd Byts/b Avg": "Bwd Avg Bytes/Bulk",
    "Bwd Pkts/b Avg": "Bwd Avg Packets/Bulk",
    "Bwd Blk Rate Avg": "Bwd Avg Bulk Rate",
    "Subflow Fwd Pkts": "Subflow Fwd Packets",
    "Subflow Fwd Byts": "Subflow Fwd Bytes",
    "Subflow Bwd Pkts": "Subflow Bwd Packets",
    "Subflow Bwd Byts": "Subflow Bwd Bytes",
    "Init Fwd Win Byts": "Init_Win_bytes_forward",
    "Init Bwd Win Byts": "Init_Win_bytes_backward",
    "Fwd Act Data Pkts": "act_data_pkt_fwd",
    "Fwd Seg Size Min": "min_seg_size_forward",
}

_EXCLUDE = set(ID_COLUMNS) | {LABEL_COL, "label"}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize CICFlowMeter headers without silently merging distinct columns."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns=RENAME_CSE2018)
    duplicated = df.columns[df.columns.duplicated()].unique().tolist()
    if duplicated:
        raise ValueError(f"Duplicate columns after header normalization: {duplicated}")
    return df


def feature_columns(df: pd.DataFrame) -> list:
    """Feature names: everything except identifiers, the raw label and the mapped label."""
    return [c for c in df.columns if c not in _EXCLUDE]


def align(df: pd.DataFrame, feats: list) -> pd.DataFrame:
    """Select the training features from another network. Missing features raise an error."""
    missing = [f for f in feats if f not in df.columns]
    if missing:
        raise ValueError(f"{len(missing)} features missing, e.g. {missing[:5]}. Check the rename map.")
    return df[feats]
