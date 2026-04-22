"""
evaluate_model.py
─────────────────
Full-dataset evaluation of the ReviewGuard 3-layer pipeline:
  BERT  ──┐
  GNN   ──┼──► fused score ──► verdict
  Rules ──┘

Runs on reviews_with_features.csv (all 40,432 rows by default).
Uses predict_review() from app.py — the exact same function the live
app calls — so numbers represent real production behaviour.

Usage:
    python evaluate_model.py              # full dataset
    python evaluate_model.py --sample 500 # quick smoke-test
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# ── Allow importing from app.py in the same directory ────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

# Import only the pure-Python predict function; Flask is NOT started.
from app import predict_review   # noqa: E402  (after sys.path tweak)

# ── Dataset ───────────────────────────────────────────────────────────────────
CSV_PATH  = "reviews_with_features.csv"
TEXT_COL  = "text"
LABEL_COL = "label"   # original string label column (CG / OR)

# CG = Computer Generated = FAKE,  OR = Original = GENUINE
LABEL_MAP = {
    "CG": "FAKE",  "1": "FAKE",  "FAKE": "FAKE",
    "DECEPTIVE": "FAKE",  "COMPUTER GENERATED": "FAKE",
    "OR": "GENUINE", "0": "GENUINE", "GENUINE": "GENUINE",
    "ORIGINAL": "GENUINE", "TRUTHFUL": "GENUINE",
}

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Evaluate ReviewGuard on full dataset")
parser.add_argument(
    "--sample", type=int, default=None,
    help="Rows to evaluate (omit for full dataset)"
)
args = parser.parse_args()

# ── Load data ─────────────────────────────────────────────────────────────────
print(f"Loading {CSV_PATH} ...")
df = pd.read_csv(CSV_PATH)
print(f"  Rows total : {len(df):,}")
print(f"  Columns    : {list(df.columns)}\n")

# Resolve text / label columns (flexible detection)
if TEXT_COL not in df.columns:
    TEXT_COL = next(
        (c for c in df.columns if "review" in c.lower() or "text" in c.lower()),
        df.columns[0],
    )
if LABEL_COL not in df.columns:
    LABEL_COL = next(
        (c for c in df.columns if "label" in c.lower() or "fake" in c.lower()),
        df.columns[1],
    )

print(f"  Text column  : '{TEXT_COL}'")
print(f"  Label column : '{LABEL_COL}'")

# Normalise labels
unique_raw = df[LABEL_COL].dropna().unique()
label_map  = {}
for raw in unique_raw:
    key = str(raw).strip().upper()
    label_map[raw] = LABEL_MAP.get(key, "GENUINE")
print(f"  Label mapping: {label_map}\n")

df["true_label"] = df[LABEL_COL].map(label_map)
df = df.dropna(subset=["true_label", TEXT_COL]).reset_index(drop=True)

# ── Optionally subsample ──────────────────────────────────────────────────────
if args.sample and args.sample < len(df):
    print(f"Sampling {args.sample:,} rows (--sample flag) ...")
    df = df.sample(args.sample, random_state=42).reset_index(drop=True)
    print(f"  Running on {len(df):,} rows\n")
else:
    print(f"Running on FULL dataset — {len(df):,} rows\n")

# ── Predict ───────────────────────────────────────────────────────────────────
print("Running predict_review() on each row (uses real BERT + GNN + heuristics)...")
preds = []
for i, row in df.iterrows():
    result = predict_review(str(row[TEXT_COL]), rating=float(row.get("rating", 3.0)))
    preds.append(result["verdict"])
    done = len(preds)
    if done % 500 == 0 or done == len(df):
        print(f"  {done:,}/{len(df):,} done...")

df["predicted"] = preds

# ── Metrics ───────────────────────────────────────────────────────────────────
y_true = df["true_label"]
y_pred = df["predicted"]

acc   = accuracy_score(y_true, y_pred)
cm    = confusion_matrix(y_true, y_pred, labels=["FAKE", "GENUINE"])

sep = "=" * 52
print(f"\n{sep}")
print(f"  Overall Accuracy : {acc * 100:.2f}%")
print(sep)
print()
print(classification_report(y_true, y_pred, target_names=["FAKE", "GENUINE"], digits=4))

print("Confusion Matrix  (rows = Actual, cols = Predicted):")
print(f"                 Pred FAKE   Pred GENUINE")
print(f"  Actual FAKE    {cm[0,0]:>8d}   {cm[0,1]:>12d}")
print(f"  Actual GENUINE {cm[1,0]:>8d}   {cm[1,1]:>12d}")
print()
print(f"  TN={cm[0,0]}  FP={cm[0,1]}  FN={cm[1,0]}  TP={cm[1,1]}")

# ── Save confusion matrix PNG (same style as generate_charts.py) ──────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    os.makedirs("static", exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor("#0b1228")
    ax.set_facecolor("#0b1228")
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="RdPu",
        xticklabels=["Predicted FAKE", "Predicted GENUINE"],
        yticklabels=["Actual FAKE", "Actual GENUINE"],
        linewidths=1.5, linecolor="#1e2a45",
        annot_kws={"size": 18, "weight": "bold", "color": "white"},
        ax=ax, cbar=False,
    )
    ax.set_title(
        f"Confusion Matrix  (Accuracy: {acc * 100:.1f}%)",
        color="white", fontsize=13, fontweight="bold", pad=14,
    )
    ax.tick_params(colors="#94a3b8", labelsize=10)
    for spine in ax.spines.values():
        spine.set_edgecolor("#1e2a45")
    plt.tight_layout()
    plt.savefig("static/confusion_matrix.png", dpi=150,
                bbox_inches="tight", facecolor="#0b1228")
    plt.close()
    print("[OK] static/confusion_matrix.png saved")
except Exception as e:
    print(f"[WARN] Could not save PNG: {e}")

# ── Print a machine-readable summary for use in generate_charts.py ────────────
report = classification_report(
    y_true, y_pred, target_names=["FAKE", "GENUINE"],
    output_dict=True, digits=4,
)
print()
print("-- Numbers for generate_charts.py --")
print(f"  Accuracy     : {acc * 100:.2f}")
print(f"  FAKE    P={report['FAKE']['precision']*100:.2f}  R={report['FAKE']['recall']*100:.2f}  F1={report['FAKE']['f1-score']*100:.2f}")
print(f"  GENUINE P={report['GENUINE']['precision']*100:.2f}  R={report['GENUINE']['recall']*100:.2f}  F1={report['GENUINE']['f1-score']*100:.2f}")
print(f"  CM: TN={cm[0,0]} FP={cm[0,1]} FN={cm[1,0]} TP={cm[1,1]}")
