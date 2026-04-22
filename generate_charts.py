"""
generate_charts.py
──────────────────
Regenerates two static chart PNGs from real evaluation results:

  Evaluation run : 2,000-row stratified sample of reviews_with_features.csv
  Script         : evaluate_model.py --sample 2000
  Pipeline       : BERT (local) + GNN (real graph, 40,432 nodes) + Heuristics

  Results:
    Overall Accuracy : 92.35%
    FAKE    P=86.77%  R=99.70%  F1=92.79%
    GENUINE P=99.65%  R=85.19%  F1=91.86%
    CM : TN=984  FP=3  FN=150  TP=863

Outputs:
  static/confusion_matrix.png
  static/accuracy_chart.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

os.makedirs("static", exist_ok=True)

# ── Real evaluation numbers ───────────────────────────────────────────────────
ACCURACY = 92.35   # full-pipeline fused accuracy (n=2,000)

# Confusion matrix:  rows = Actual, cols = Predicted
#                    FAKE   GENUINE
CM = np.array([
    [984,   3],    # Actual FAKE
    [150, 863],    # Actual GENUINE
])

# ── 1. Confusion Matrix Heatmap ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 5))
fig.patch.set_facecolor("#0b1228")
ax.set_facecolor("#0b1228")

sns.heatmap(
    CM, annot=True, fmt="d", cmap="RdPu",
    xticklabels=["Predicted FAKE", "Predicted GENUINE"],
    yticklabels=["Actual FAKE", "Actual GENUINE"],
    linewidths=1.5, linecolor="#1e2a45",
    annot_kws={"size": 18, "weight": "bold", "color": "white"},
    ax=ax, cbar=False,
)
ax.set_title(
    f"Confusion Matrix  (Accuracy: {ACCURACY:.1f}%)",
    color="white", fontsize=13, fontweight="bold", pad=14,
)
ax.tick_params(colors="#94a3b8", labelsize=10)
for spine in ax.spines.values():
    spine.set_edgecolor("#1e2a45")

plt.tight_layout()
plt.savefig("static/confusion_matrix.png", dpi=150, bbox_inches="tight",
            facecolor="#0b1228")
plt.close()
print("[OK] static/confusion_matrix.png saved")


# ── 2. Model Accuracy Comparison Bar Chart ────────────────────────────────────
# BERT-only and GNN-only are training/validation figures from Colab.
# Fused Model is the real end-to-end number from evaluate_model.py.
models = ["BERT\nOnly", "GNN\nOnly", "Fused\nModel"]
scores = [87.5, 83.2, ACCURACY]
colors = ["#6c3bff", "#3b82f6", "#a78bfa"]

fig, ax = plt.subplots(figsize=(6, 5))
fig.patch.set_facecolor("#0b1228")
ax.set_facecolor("#0b1228")

bars = ax.bar(models, scores, color=colors, width=0.45,
              edgecolor="#1e2a45", linewidth=1.2, zorder=3)

for bar, score in zip(bars, scores):
    ax.text(
        bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
        f"{score}%", ha="center", va="bottom",
        color="white", fontsize=13, fontweight="bold",
    )

ax.set_ylim(75, 97)
ax.set_title("Model Accuracy Comparison", color="white", fontsize=15,
             fontweight="bold", pad=16)
ax.set_ylabel("Accuracy (%)", color="#94a3b8", fontsize=11)
ax.tick_params(colors="#94a3b8", labelsize=11)
ax.yaxis.grid(True, color="#1e2a45", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_edgecolor("#1e2a45")

plt.tight_layout()
plt.savefig("static/accuracy_chart.png", dpi=150, bbox_inches="tight",
            facecolor="#0b1228")
plt.close()
print("[OK] static/accuracy_chart.png saved")

print()
print("Both charts updated with real evaluation numbers.")
print(f"  Accuracy : {ACCURACY}%  (BERT 87.5% | GNN 83.2% | Fused {ACCURACY}%)")
print(f"  CM       : TN={CM[0,0]}  FP={CM[0,1]}  FN={CM[1,0]}  TP={CM[1,1]}")
