# ReviewGuard

**Professional AI-Powered Review Fraud Detection System**

ReviewGuard is an enterprise-grade platform that combines advanced machine learning techniques to detect fraudulent product reviews with industry-leading accuracy. Built for e-commerce platforms that demand absolute integrity.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://your-deployment-url.com)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)](https://flask.palletsprojects.com/)

---

## 🎯 Overview

ReviewGuard employs a sophisticated three-layer hybrid AI architecture to identify synthetic and fraudulent product reviews:

- **92.35%** System Accuracy
- **99.7%** FAKE Review Recall
- **3-Layer** AI Pipeline (BERT + GNN + Heuristics)

### Key Features

✅ **Semantic Analysis** - Fine-tuned BERT model analyzes linguistic patterns and deceptive language markers  
✅ **Behavioral Detection** - Graph Neural Network maps reviewer behavior and coordinated fraud campaigns  
✅ **Heuristic Engine** - Rule-based system detects common manipulation patterns  
✅ **UNVERIFIABLE State** - Flags edge cases for human review instead of forcing incorrect verdicts  
✅ **Real-time Analysis** - Instant fraud detection with detailed confidence scores  
✅ **Bulk Processing** - Analyze multiple reviews or scrape from Amazon/Flipkart  

---

## 🚀 Live Demo

**Try it now:** [https://your-deployment-url.com](https://your-deployment-url.com)

### Quick Test

1. Visit the [Workbench](https://your-deployment-url.com/workbench)
2. Paste a product review
3. Optionally add a star rating (1-5)
4. Click "Execute Trace" to see the analysis

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **System Accuracy** | 92.35% |
| **FAKE Precision** | 86.77% |
| **FAKE Recall** | 99.7% |
| **GENUINE Precision** | 99.65% |
| **GENUINE Recall** | 85.19% |
| **F1 Score** | 0.923 |
| **Test Set Size** | 2,000 reviews |

### Model Comparison

| Model | Accuracy | F1 Score |
|-------|----------|----------|
| BERT Only | 87.5% | 0.87 |
| GNN Only | 83.2% | 0.83 |
| **Fused System** | **92.35%** | **0.923** |

---

## 🏗️ Architecture

### Three-Layer Detection Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT: Review Text                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┬─────────────────────┬─────────────────────┐
        │                     │                     │                     │
        ▼                     ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ BERT Model   │      │  GNN Model   │      │  Heuristic   │
│ (Semantic)   │      │ (Behavioral) │      │   Engine     │
│              │      │              │      │              │
│  87.5% Acc   │      │  83.2% Acc   │      │  +5% Boost   │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  Fusion Layer    │
                    │  0.65×BERT +     │
                    │  0.35×GNN +      │
                    │  Heuristic       │
                    └──────────────────┘
                              ↓
                    ┌──────────────────┐
                    │ Divergence Check │
                    │  (≥0.35 = UNVER) │
                    └──────────────────┘
                              ↓
        ┌─────────────────────┬─────────────────────┬─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│     FAKE     │      │   GENUINE    │      │ UNVERIFIABLE │
│  (>0.35)     │      │   (≤0.35)    │      │ (div ≥0.35)  │
└──────────────┘      └──────────────┘      └──────────────┘
```

### Fusion Formula

```python
final_score = (0.65 × BERT) + (0.35 × GNN) + heuristic_boost
```

Where:
- `BERT ∈ [0, 1]` - Semantic fake probability
- `GNN ∈ [0, 1]` - Behavioral fake probability  
- `heuristic_boost ∈ [0, 0.5]` - Rule-based boost (capped at +50%)

---

## 🔧 Technology Stack

### Backend
- **Python 3.11+** - Core runtime
- **Flask 3.0** - Web framework
- **PyTorch** - Deep learning framework
- **Transformers** - BERT model implementation
- **PyTorch Geometric** - Graph Neural Network
- **NumPy** - Numerical computing
- **BeautifulSoup4** - Web scraping

### Frontend
- **HTML5/CSS3** - Modern web standards
- **Vanilla JavaScript** - No framework dependencies
- **Forensic Precision Design System** - Custom UI theme

### Deployment
- **Render/Railway/Heroku** - Cloud hosting
- **Gunicorn** - WSGI HTTP server
- **Environment Variables** - Secure configuration

---

## 📡 API Reference

### Analyze Single Review

**Endpoint:** `POST /predict`

**Request:**
```json
{
  "review": "string (required)",
  "rating": 3 (optional, 1-5)
}
```

**Response:**
```json
{
  "verdict": "FAKE" | "GENUINE" | "UNVERIFIABLE",
  "confidence": 94.2,
  "bert_score": 92.5,
  "gnn_score": 87.1,
  "heuristic_score": 45.0,
  "divergence": 0.071,
  "reasons": ["Exclamation mark spam - 5 found", "..."],
  "submitted_rating": 5
}
```

### Scrape & Analyze

**Endpoint:** `POST /scrape`

**Request:**
```json
{
  "url": "https://amazon.com/product/...",
  "max_reviews": 10
}
```

**Response:**
```json
{
  "platform": "amazon",
  "total_reviews_analysed": 10,
  "fake_count": 3,
  "genuine_count": 7,
  "fake_percentage": 30.0,
  "trust_score": 70.0,
  "verdict": "MODERATE RISK",
  "reviews": [...]
}
```

### Bulk Analysis

**Endpoint:** `POST /bulk-analyze`

**Request:**
```json
{
  "reviews_text": "Review 1\n\n---\n\nReview 2\n\n---\n\nReview 3"
}
```

---

## 🚀 Deployment

### Environment Variables

Required environment variables for deployment:

```bash
# Model Configuration
HF_MODEL_ID=your-huggingface-model-id
HF_TOKEN=your-huggingface-token (optional for public models)
MODEL_BACKEND=auto  # Options: auto, local, pipeline, hf_api

# Flask Configuration
FLASK_DEBUG=0
SECRET_KEY=your-secret-key
PORT=5000

# Optional
RENDER=1  # Set if deploying to Render
```

### Deploy to Render

1. Fork this repository
2. Create a new Web Service on [Render](https://render.com)
3. Connect your GitHub repository
4. Set environment variables in Render dashboard
5. Deploy!

### Deploy to Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Set environment variables: `railway variables set KEY=value`
5. Deploy: `railway up`

### Local Development

```bash
# Clone repository
git clone https://github.com/Paragraut24/ml-project-ReviewGuard.git
cd ml-project-ReviewGuard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HF_MODEL_ID=your-model-id
export HF_TOKEN=your-token

# Run application
python app.py
```

Visit `http://localhost:5000`

---

## 📖 Documentation

### Verdict States

**FAKE** - High confidence detection of synthetic content
- `final_score > 0.35` and `divergence < 0.35`
- Models agree the review is fraudulent
- Multiple deception signals detected

**GENUINE** - Authentic content verified
- `final_score ≤ 0.35` and `divergence < 0.35`
- Low fake probability across all models
- Natural language patterns detected

**UNVERIFIABLE** - Models disagree, human review required
- `divergence ≥ 0.35` (models strongly disagree)
- System refuses to force a potentially incorrect verdict
- Flags edge cases for manual inspection

### Heuristic Signals

The system detects 6 common fraud patterns:

1. **Exclamation Abuse** - ≥3 exclamation marks
2. **Vague Superlatives** - Overuse of "amazing", "best", "perfect"
3. **Word Repetition** - Same word used ≥4 times
4. **Duplicate Sentences** - Copy-paste patterns
5. **ALL CAPS Overuse** - ≥3 fully capitalized words
6. **Missing Negatives** - No criticism in long reviews

---

## 🔒 Security & Privacy

- **No Data Storage** - Reviews are analyzed in real-time and not stored
- **HTTPS Only** - All traffic encrypted
- **Rate Limiting** - Prevents API abuse
- **No Tracking** - No user analytics or cookies
- **Open Source** - Transparent and auditable (with proprietary license)

---

## 📄 License

**© 2026 ReviewGuard. All Rights Reserved.**

This software is proprietary and confidential. Unauthorized copying, modification, distribution, or use of this software, via any medium, is strictly prohibited without explicit written permission from the copyright holder.

See [LICENSE](LICENSE) file for full terms.

---

## 🤝 Contributing

This is a proprietary project. Contributions are not accepted at this time.

For bug reports or feature requests, please open an issue on GitHub.

---

## 📧 Contact

- **GitHub:** [@Paragraut24](https://github.com/Paragraut24)
- **Repository:** [ml-project-ReviewGuard](https://github.com/Paragraut24/ml-project-ReviewGuard)
- **Live Demo:** [https://your-deployment-url.com](https://your-deployment-url.com)

---

## 🙏 Acknowledgments

- **BERT** - Transformers library by HuggingFace
- **PyTorch Geometric** - Graph Neural Network framework
- **YelpChi Dataset** - GNN training data
- **Amazon Review Dataset** - BERT fine-tuning data

---

**Built with ❤️ for e-commerce integrity**

