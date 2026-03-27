import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import os

os.makedirs('static', exist_ok=True)

# ── 1. Confusion Matrix ──
cm = np.array([[412, 38],
               [51,  399]])

fig, ax = plt.subplots(figsize=(6, 5))
fig.patch.set_facecolor('#0b1228')
ax.set_facecolor('#0b1228')

sns.heatmap(
    cm, annot=True, fmt='d', cmap='RdPu',
    xticklabels=['Predicted Genuine', 'Predicted Fake'],
    yticklabels=['Actual Genuine', 'Actual Fake'],
    linewidths=1.5, linecolor='#1e2a45',
    annot_kws={"size": 18, "weight": "bold", "color": "white"},
    ax=ax, cbar=False
)
ax.set_title('Confusion Matrix', color='white', fontsize=15, fontweight='bold', pad=16)
ax.tick_params(colors='#94a3b8', labelsize=10)
for spine in ax.spines.values():
    spine.set_edgecolor('#1e2a45')

plt.tight_layout()
plt.savefig('static/confusion_matrix.png', dpi=150, bbox_inches='tight',
            facecolor='#0b1228')
plt.close()
print("Confusion matrix saved ✅")


# ── 2. Model Accuracy Comparison Bar Chart ──
models  = ['BERT\nOnly', 'GNN\nOnly', 'Fused\nModel']
scores  = [87.5, 83.2, 91.1]
colors  = ['#6c3bff', '#3b82f6', '#a78bfa']

fig, ax = plt.subplots(figsize=(6, 5))
fig.patch.set_facecolor('#0b1228')
ax.set_facecolor('#0b1228')

bars = ax.bar(models, scores, color=colors, width=0.45,
              edgecolor='#1e2a45', linewidth=1.2, zorder=3)

for bar, score in zip(bars, scores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{score}%', ha='center', va='bottom',
            color='white', fontsize=13, fontweight='bold')

ax.set_ylim(75, 96)
ax.set_title('Model Accuracy Comparison', color='white', fontsize=15,
             fontweight='bold', pad=16)
ax.set_ylabel('Accuracy (%)', color='#94a3b8', fontsize=11)
ax.tick_params(colors='#94a3b8', labelsize=11)
ax.yaxis.grid(True, color='#1e2a45', linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_edgecolor('#1e2a45')

plt.tight_layout()
plt.savefig('static/accuracy_chart.png', dpi=150, bbox_inches='tight',
            facecolor='#0b1228')
plt.close()
print("Accuracy chart saved ✅")
