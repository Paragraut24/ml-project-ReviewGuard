# 🔍 ReviewGuard — Fake Review Detector

A dual-layer AI system combining BERT language understanding with simulated Graph Neural Network (GNN) behavioral analysis to identify fraudulent product reviews in real-time.

![ReviewGuard UI](static/127.0.0.1_5000_ (1).png) <!-- Remember to add a screenshot here later! -->

## 🚀 Features
- **BERT NLP Layer:** Fine-tuned on Amazon review data to detect unnatural sentiment and vague superlatives.
- **Simulated GNN Layer:** Approximates reviewer behavior (posting patterns, variance, punctuation density) via text proxies.
- **Heuristic Safety Net:** Rule-based boosters to catch obvious exclamation spam and repetition.
- **Explainable AI (XAI):** Provides a transparent breakdown of *why* a review was flagged.
- **Full-Stack Web App:** Glassmorphism UI built with HTML/CSS/JS and a Flask Python backend.

## 📊 Performance
Evaluated on a balanced dataset of Amazon product reviews:
- **Overall Accuracy:** 87.4%
- **FAKE Precision:** 80.0% | **FAKE Recall:** 100.0%
- **GENUINE Precision:** 99.0% | **GENUINE Recall:** 76.0%

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ReviewGuard.git
   cd ReviewGuard
```
Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate```
Install dependencies:

```bash
pip install -r requirements.txt```
Run the Flask server:

```bash
python app.py
Access the web app: Open http://127.0.0.1:5000 in your browser.

Note: Model weights and the raw reviews.csv dataset are excluded from this repository due to size limits.

