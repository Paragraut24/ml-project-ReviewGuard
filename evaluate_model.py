import argparse
from transformers import pipeline
from collections import Counter
import numpy as np
import hashlib
import re
import pandas as pd
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay
)
import matplotlib.pyplot as plt
import os

# â”€â”€ Load model â”€â”€
print("Loading BERT model...")
classifier = pipeline(
    'text-classification',
    model='./bert_model',
    tokenizer='./bert_model'
)
print("Model loaded âœ…\n")

STOP_WORDS = {
    'i','the','a','is','it','and','to','in','for','this','was','with',
    'my','of','very','so','not','be','am','are','that','have','on','at',
    'by','an','as','do','if','or','its','we','you','he','she','they',
    'all','one','but','had'
}
VAGUE_WORDS = [
    'amazing','best','ever','perfect','love','great','awesome',
    'excellent','fantastic','wonderful','superb','outstanding','incredible'
]
NEGATIVE_WORDS = [
    'but','however','although','except','issue','problem','disappointed',
    'unfortunately','broke','returned','bad','poor','worse','lack',
    'missing','slow','cheap','difficult','confusing','failed','stopped',
    'cracked','damaged','wrong','late','never'
]

def heuristic_boost(text):
    boost = 0.0
    words = text.split()
    text_lower = text.lower()

    if text.count('!') >= 3:
        boost += 0.25

    matches = sum(1 for w in VAGUE_WORDS if w in text_lower)
    if matches >= 3:
        boost += 0.20

    word_counts = Counter(
        w.strip('.,!?').lower() for w in words
        if w.strip('.,!?').lower() not in STOP_WORDS and len(w.strip('.,!?')) > 2
    )
    if word_counts and word_counts.most_common(1)[0][1] >= 4:
        boost += 0.30

    sentences = [s.strip() for s in text.replace('!','.').split('.') if s.strip()]
    if len(sentences) > 2 and len(set(sentences)) < len(sentences):
        boost += 0.15

    caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 2) / max(len(words), 1)
    if caps_ratio > 0.3:
        boost += 0.15

    has_negative = any(w in text_lower for w in NEGATIVE_WORDS)
    if not has_negative and len(words) > 15:
        boost += 0.10

    return min(boost, 0.50)


def simulate_gnn_score(text):
    words = text.split()
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    score = 0.5

    word_count = len(words)
    if word_count < 12:
        score += 0.15
    elif word_count > 40:
        score -= 0.12

    if len(sentences) > 1:
        lengths = [len(s.split()) for s in sentences]
        variance = np.var(lengths)
        if variance < 2.0:
            score += 0.12
        elif variance > 10.0:
            score -= 0.10

    punct_count = sum(1 for c in text if c in '!?')
    punct_ratio = punct_count / max(word_count, 1)
    if punct_ratio > 0.15:
        score += 0.10

    unique_ratio = len(set(w.lower().strip('.,!?') for w in words)) / max(word_count, 1)
    if unique_ratio < 0.55:
        score += 0.13
    elif unique_ratio > 0.80:
        score -= 0.10

    hash_val = int(hashlib.md5(text.encode()).hexdigest()[:4], 16)
    noise = (hash_val / 65535 - 0.5) * 0.08
    score += noise

    return round(min(max(score, 0.05), 0.97), 4)


def predict(text):
    result = classifier(text, truncation=True, max_length=128)[0]
    bert_score = result['score'] if result['label'] == 'LABEL_1' else 1 - result['score']
    gnn_score = simulate_gnn_score(text)
    fused = 0.65 * bert_score + 0.35 * gnn_score
    boost = heuristic_boost(text)
    final = min(fused + boost, 1.0)
    return "FAKE" if final > 0.35 else "GENUINE"


# â”€â”€ Load dataset â”€â”€
print("Loading dataset...")
df = pd.read_csv('reviews.csv')
print(f"Columns found: {list(df.columns)}\n")

# Auto-detect text and label columns
text_col   = next((c for c in df.columns if 'review' in c.lower() or 'text' in c.lower()), df.columns[0])
label_col  = next((c for c in df.columns if 'label' in c.lower() or 'fake' in c.lower() or 'class' in c.lower()), df.columns[1])

print(f"Using text column  : '{text_col}'")
print(f"Using label column : '{label_col}'\n")

# Command line arguments for sample size
parser = argparse.ArgumentParser(description='Evaluate ReviewGuard Model')
parser.add_argument('--run-full', action='store_true', help='Run on the entire dataset')
parser.add_argument('--sample', type=int, default=500, help='Number of reviews to sample (default: 500)')
args = parser.parse_args()

if args.run_full:
    print(f"Running on FULL dataset ({len(df)} rows)...")
    sample = df.reset_index(drop=True)
else:
    print(f"Running on a sample of {args.sample} reviews for speed...")
    sample = df.sample(min(args.sample, len(df)), random_state=42).reset_index(drop=True)

# Normalize labels to FAKE / GENUINE
label_map = {}
unique_labels = sample[label_col].unique()
print(f"Unique labels in dataset: {unique_labels}")

for l in unique_labels:
    s = str(l).strip().upper()
    if s in ['1', 'FAKE', 'CG', 'DECEPTIVE', 'COMPUTER GENERATED']:
        label_map[l] = 'FAKE'
    elif s in ['0', 'GENUINE', 'OR', 'ORIGINAL', 'TRUTHFUL']:
        label_map[l] = 'GENUINE'
    else:
        label_map[l] = 'GENUINE'  # safe default

print(f"Label mapping: {label_map}\n")

sample['true_label'] = sample[label_col].map(label_map)
sample = sample.dropna(subset=['true_label', text_col])

# â”€â”€ Run predictions â”€â”€
print(f"Running predictions on {len(sample)} reviews...")
preds = []
for i, row in sample.iterrows():
    pred = predict(str(row[text_col]))
    preds.append(pred)
    if (len(preds)) % 50 == 0:
        print(f"  {len(preds)}/{len(sample)} done...")

sample['predicted'] = preds

# â”€â”€ Results â”€â”€
y_true = sample['true_label']
y_pred = sample['predicted']

acc = accuracy_score(y_true, y_pred)
print(f"\n{'='*45}")
print(f"  Overall Accuracy : {acc*100:.2f}%")
print(f"{'='*45}\n")
print(classification_report(y_true, y_pred, target_names=['FAKE','GENUINE']))

# â”€â”€ Save confusion matrix chart â”€â”€
os.makedirs('static', exist_ok=True)
cm = confusion_matrix(y_true, y_pred, labels=['FAKE','GENUINE'])

fig, ax = plt.subplots(figsize=(6,5))
fig.patch.set_facecolor('#0b1228')
ax.set_facecolor('#0b1228')

import seaborn as sns
sns.heatmap(
    cm, annot=True, fmt='d', cmap='RdPu',
    xticklabels=['Predicted FAKE','Predicted GENUINE'],
    yticklabels=['Actual FAKE','Actual GENUINE'],
    linewidths=1.5, linecolor='#1e2a45',
    annot_kws={"size":18, "weight":"bold", "color":"white"},
    ax=ax, cbar=False
)
ax.set_title(f'Confusion Matrix  (Accuracy: {acc*100:.1f}%)',
             color='white', fontsize=13, fontweight='bold', pad=14)
ax.tick_params(colors='#94a3b8', labelsize=10)
for spine in ax.spines.values():
    spine.set_edgecolor('#1e2a45')

plt.tight_layout()
plt.savefig('static/confusion_matrix.png', dpi=150,
            bbox_inches='tight', facecolor='#0b1228')
plt.close()
print("\nConfusion matrix saved to static/confusion_matrix.png âœ…")
print("Refresh your browser to see updated chart!")

