"""Step 1: load raw CSVs, map labels, clean, and save Parquet.

Usage:
  python scripts/01_clean.py cicids2017
  python scripts/01_clean.py cse2018 --sample
"""
import argparse
import json

from netshift.config import CLEAN_DIR, CSE_MIN_PER_CLASS, CSE_SAMPLE_FRAC, RAW_DIR, RESULTS_DIR, SEEDS
from netshift.data import clean, load_folder, stratified_sample

DATASETS = {"cicids2017": RAW_DIR / "cicids2017", "cse2018": RAW_DIR / "cse2018"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dataset", choices=sorted(DATASETS))
    p.add_argument("--sample", action="store_true", help="stratified sample (use for cse2018)")
    args = p.parse_args()

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    raw = load_folder(DATASETS[args.dataset])
    clean_df, report = clean(raw)
    del raw  # free memory before sampling/saving

    if args.sample:
        before = len(clean_df)
        clean_df = stratified_sample(clean_df, CSE_SAMPLE_FRAC, CSE_MIN_PER_CLASS, SEEDS[0])
        report["rows_before_sampling"] = before
        report["sample_frac_target"] = CSE_SAMPLE_FRAC
        report["min_per_class"] = CSE_MIN_PER_CLASS

    out = CLEAN_DIR / f"clean_{args.dataset}.parquet"
    clean_df.to_parquet(out, index=False)
    report["rows_final"] = int(len(clean_df))
    report["class_counts"] = {k: int(v) for k, v in clean_df["label"].value_counts().items()}
    (RESULTS_DIR / f"data_quality_{args.dataset}.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
