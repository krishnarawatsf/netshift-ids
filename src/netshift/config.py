"""Central settings. Change values here, not inside scripts."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("NETSHIFT_DATA_DIR", ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
RESULTS_DIR = ROOT / "results"
RESULTS_LOG = RESULTS_DIR / "results_log.csv"

# The six common classes (see labels.py for the mapping from raw labels)
CLASSES = ["Benign", "DoS", "DDoS", "Brute-force", "Web attack", "Bot"]
CLASS_TO_ID = {c: i for i, c in enumerate(CLASSES)}

SEEDS = [42, 43, 44]
TEST_SIZE = 0.2

# CSE-CIC-IDS2018 is large: stratified sample, keeping at least this many rows per class
CSE_SAMPLE_FRAC = 0.05
CSE_MIN_PER_CLASS = 2000

# Balancing (training data only). Big classes are undersampled, small ones are SMOTE-d.
MAJORITY_CAP = int(os.environ.get("NETSHIFT_MAJORITY_CAP", "200000"))
SMOTE_CAP = int(os.environ.get("NETSHIFT_SMOTE_CAP", "50000"))
if MAJORITY_CAP < 1 or SMOTE_CAP < 2:
    raise ValueError("NETSHIFT_MAJORITY_CAP must be >= 1 and NETSHIFT_SMOTE_CAP must be >= 2")

# SHAP and shortcut detection
SHAP_SAMPLE = 5000
KS_SAMPLE = 20000
KS_THRESHOLD = 0.3
SHORTCUT_TOP_K = 15

LABEL_BUDGETS = [0.0, 0.01, 0.05, 0.10]

# Identifier columns: removed, never used as features
ID_COLUMNS = ["Flow ID", "Source IP", "Source Port", "Destination IP", "Timestamp"]
LABEL_COL = "Label"
