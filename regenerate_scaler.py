"""
regenerate_scaler.py
────────────────────
Rebuilds scaler.pkl using the current sklearn version to eliminate the
InconsistentVersionWarning that appears when loading a scaler saved with
sklearn 1.6.1 under sklearn 1.8.0.

The 7 features used here EXACTLY match what _extract_features() in
gnn_inference.py computes and what FakeReviewGNN (GCNConv input_dim=7)
was trained on:

    ['rating_norm', 'text_length', 'word_count', 'avg_word_length',
     'exclamation',  'caps_ratio',  'bert_score']

The CSV already contains all these columns, so we read them directly
rather than recomputing from raw text — this guarantees identical values.
"""

import pickle
import numpy as np
import pandas as pd
import sklearn
from sklearn.preprocessing import StandardScaler

CSV_PATH    = "reviews_with_features.csv"
OUTPUT_PATH = "scaler.pkl"

# ── Must match gnn_inference._extract_features() return order exactly ─────────
FEATURE_COLS = [
    "rating_norm",
    "text_length",
    "word_count",
    "avg_word_length",
    "exclamation",
    "caps_ratio",
    "bert_score",
]

# ── Load dataset ──────────────────────────────────────────────────────────────
print(f"[1/4] Loading {CSV_PATH} ...")
df = pd.read_csv(CSV_PATH)
print(f"      Rows loaded : {len(df):,}")

missing = [c for c in FEATURE_COLS if c not in df.columns]
if missing:
    raise ValueError(
        f"Missing columns in CSV: {missing}\n"
        f"Available columns: {df.columns.tolist()}"
    )

# ── Extract the 7-feature matrix ──────────────────────────────────────────────
print("[2/4] Extracting feature matrix ...")
X = df[FEATURE_COLS].values.astype(np.float32)
print(f"      Feature matrix shape : {X.shape}")
print(f"      Feature columns       : {FEATURE_COLS}")

# ── Fit scaler ────────────────────────────────────────────────────────────────
print("[3/4] Fitting StandardScaler ...")
scaler = StandardScaler()
scaler.fit(X)
print(f"      scaler.n_features_in_ : {scaler.n_features_in_}")
print(f"      mean_  : {np.round(scaler.mean_, 4).tolist()}")
print(f"      scale_ : {np.round(scaler.scale_, 4).tolist()}")

# ── Save with current sklearn ─────────────────────────────────────────────────
print(f"[4/4] Saving to {OUTPUT_PATH} (sklearn {sklearn.__version__}) ...")
with open(OUTPUT_PATH, "wb") as f:
    pickle.dump(scaler, f)

# ── Sanity check ──────────────────────────────────────────────────────────────
print("\n-- Verification ---------------------------------------------------")

with open(OUTPUT_PATH, "rb") as f:
    loaded = pickle.load(f)

sample_raw  = X[0:1]
sample_scaled = loaded.transform(sample_raw)

print(f"  Reload OK   : True")
print(f"  n_features  : {loaded.n_features_in_}")
print(f"  Feature cols: {FEATURE_COLS}")
print(f"  Raw row 0   : {sample_raw[0].tolist()}")
print(f"  Scaled row 0: {sample_scaled[0].tolist()}")
print(f"\n[OK] scaler.pkl regenerated successfully with sklearn {sklearn.__version__}.")
print("     No InconsistentVersionWarning will appear when loading this file.")
