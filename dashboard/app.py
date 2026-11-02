"""Streamlit dashboard. Reads results/ only. It never runs models.

Run: streamlit run dashboard/app.py
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

RESULTS = Path(__file__).resolve().parents[1] / "results"
st.set_page_config(page_title="NetShift-IDS", layout="wide")
st.title("NetShift-IDS results")

log = RESULTS / "results_log.csv"
if not log.exists():
    st.info("No results yet. Run the scripts in scripts/ first.")
    st.stop()

df = pd.read_csv(log)
if "selection" not in df.columns:
    df["selection"] = "none"
tab1, tab2, tab3 = st.tabs(["Cross-network results", "Label budget", "Shortcut features"])

with tab1:
    subset = df[df["experiment"].isin(["baseline", "cross_network", "shortcut_removed"])]
    summary = (subset.groupby(["experiment", "model", "feature_set", "test_net"])
               [["macro_f1", "mcc", "accuracy"]].agg(["mean", "std"]).round(4))
    st.dataframe(summary)

with tab2:
    lb = df[df["experiment"].isin(["label_budget", "label_budget_uncertainty"])]
    if lb.empty:
        st.info("No random or uncertainty label-budget results yet.")
    else:
        metric = st.selectbox("Metric", ["macro_f1", "mcc"])
        st.line_chart(
            lb.groupby(["label_budget", "model", "selection"])[metric]
            .mean().unstack(["model", "selection"])
        )
        st.dataframe(lb.groupby(["model", "selection", "feature_set", "label_budget"])
                     [["macro_f1", "mcc"]].agg(["mean", "std"]).round(4))

with tab3:
    shift = RESULTS / "feature_shift.csv"
    if shift.exists():
        st.dataframe(pd.read_csv(shift).head(30))
    sc = RESULTS / "shortcut_features.json"
    if sc.exists():
        st.json(json.loads(sc.read_text()))
    else:
        st.info("Run scripts/04_shap.py first.")
