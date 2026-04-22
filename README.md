# ReviewGuard — Fake Review Detector

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)

A dual-layer AI system using fine-tuned BERT and Graph Neural Networks to detect fake product reviews in real time, with a three-state output: **FAKE / GENUINE / UNVERIFIABLE**.

---

## Architecture Overview

ReviewGuard runs every review through three independent layers before producing a verdict.

```
Review Text
    │
    ├──► [Layer 1] Fine-tuned BERT        → bert_fake_score  (0–1)
    │
    ├──► [Layer 2] GNN (YelpChi graph)    → gnn_score        (0–1)
    │              polarity-corrected     → 1.0 − gnn_score
    │
    └──► [Layer 3] Heuristic rule engine  → boost            (0–0.5)

Fusion:
    final_score = 0.65 × bert_fake_score
                + 0.35 × (1.0 − gnn_score)
                + heuristic_boost

Verdict:
    final_score > 0.35  AND  divergence < 0.55  →  FAKE
    final_score ≤ 0.35  AND  divergence < 0.55  →  GENUINE
    |bert_fake_score − (1 − gnn_score)| ≥ 0.55  →  UNVERIFIABLE
```

### Layer Details

| Layer | Model | Role |
|---|---|---|
| **1 — BERT** | `bert-base-uncased` fine-tuned on Yelp/Amazon fake review corpus | Semantic & linguistic fake signal |
| **2 — GNN** | 2-layer GCN trained on YelpChi graph (40,432 nodes · 521,140 edges) | Behavioral & relational fake signal |
| **3 — Heuristics** | Rule engine: exclamation spam, vague superlatives, repetition, ALL CAPS | Bounded boost (+0 to +50%) |

---

## Performance

> Evaluated on a 2,000-sample stratified subset of `reviews_with_features.csv` using `predict_review()` — the exact same function the live app calls.

| Model | Accuracy | F1 |
|---|---|---|
| BERT Only | 87.5% | 0.87 |
| GNN Only | 83.2% | 0.83 |
| **Dual-Layer Fusion** | **92.35%** | **0.923** |

### Confusion Matrix (n = 2,000)

```
                  Pred FAKE   Pred GENUINE
  Actual FAKE        984            3
  Actual GENUINE     150          863
```

| Metric | FAKE class | GENUINE class |
|---|---|---|
| Precision | 86.77% | 99.65% |
| Recall    | **99.70%** | 85.19% |
| F1        | 92.79% | 91.86% |

> **FAKE Recall: 99.7%** — the fused model misses only 3 fake reviews out of 987. The system is tuned to minimise false negatives (missed fakes) at the cost of some genuine reviews being over-flagged.

---

## Key Technical Innovations

### 1 · Polarity-Aware Fusion

The GNN was trained independently on the YelpChi graph with the label convention **1 = genuine, 0 = fake**, while BERT uses the opposite convention. A naive fusion would cause the two models to cancel each other out on the most unambiguous reviews.

ReviewGuard automatically inverts the GNN output before fusion:

```python
gnn_corrected = 1.0 - gnn_score   # align polarity to: higher = more fake
fused_score   = 0.65 * bert_fake_score + 0.35 * gnn_corrected
```

This single line converts a near-random fusion into a 92.35% accurate system — without retraining either model.

### 2 · UNVERIFIABLE Third State

Most review detectors force a binary verdict even when the evidence is contradictory. ReviewGuard introduces a third output:

```python
divergence = abs(bert_fake_score - gnn_corrected)
if divergence >= 0.55:
    verdict = "UNVERIFIABLE"  # human inspection recommended
```

When BERT and GNN strongly disagree (divergence ≥ 0.55), the system surfaces the conflict rather than hiding it behind a false-confidence binary label.

---

## Installation & Setup

```bash
git clone https://github.com/Paragraut24/ml-project-ReviewGuard
cd ml-project-ReviewGuard

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.local-ml.txt
```

> **Note:** `bert_model/model.safetensors` (417 MB) is **not included** in this repo due to GitHub file-size limits. Download the fine-tuned weights from your HuggingFace Hub model repo and place them in `bert_model/`. Set `HF_MODEL_ID` and `HF_TOKEN` environment variables to use the remote inference API instead.

```bash
python app.py
# Open http://127.0.0.1:5000
```

---

## File Structure

```
ml-project-ReviewGuard/
│
├── app.py                  # Flask app — predict_review(), heuristics, scraping routes
├── gnn_inference.py        # GNN singleton loader + _extract_features() + get_gnn_score()
├── evaluate_model.py       # Full-dataset evaluation script
├── regenerate_scaler.py    # Rebuilds scaler.pkl for the current sklearn version
│
├── bert_model/             # Fine-tuned BERT weights (not in repo — download separately)
│   ├── config.json
│   └── model.safetensors   # 417 MB — excluded from git
│
├── static/
│   ├── confusion_matrix.png
│   └── accuracy_chart.png
│
├── templates/
│   └── index.html          # Single-page UI (glassmorphism dark theme)
│
├── requirements.txt            # Production / Render dependencies
├── requirements.local-ml.txt   # Local ML stack (torch, transformers, torch-geometric)
├── generate_charts.py          # Regenerates static chart PNGs
└── gnn_stats.json              # GNN model metadata
```

**Not tracked by git** (see `.gitignore`):

| File | Reason |
|---|---|
| `bert_model/model.safetensors` | 417 MB — GitHub limit |
| `graph_data.pt` | 9.4 MB graph binary |
| `gnn_model_weighted.pt` | Trained model weights |
| `scaler.pkl` | sklearn-version-specific binary |
| `reviews_with_features.csv` | 17 MB training dataset |
| `mlproject/`, `venv/` | Virtual environments |

---

## Evaluation

```bash
# Full dataset (40,432 rows — takes ~90 min on CPU)
python evaluate_model.py

# Fast stratified sample (recommended for verification)
python evaluate_model.py --sample 2000
```

Output includes accuracy, per-class precision / recall / F1, confusion matrix, and saves `static/confusion_matrix.png`.

To rebuild the scaler after upgrading scikit-learn:

```bash
python regenerate_scaler.py
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · Flask |
| NLP | HuggingFace Transformers · `bert-base-uncased` |
| Graph ML | PyTorch · PyTorch Geometric · GCNConv |
| Classical ML | scikit-learn · StandardScaler |
| Frontend | Vanilla JS · CSS (glassmorphism dark theme) |
| Deployment | Render (via `Procfile` + `render.yaml`) |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Semester 4 Machine Learning Project · 2026*
