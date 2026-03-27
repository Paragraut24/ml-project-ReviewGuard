from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from collections import Counter
import re
import numpy as np
import hashlib

app = Flask(__name__)

print("Loading models...")
classifier = pipeline(
    'text-classification',
    model='./bert_model',
    tokenizer='./bert_model'
)
print("Models loaded ✅")


STOP_WORDS = {
    'i', 'the', 'a', 'is', 'it', 'and', 'to', 'in', 'for', 'this',
    'was', 'with', 'my', 'of', 'very', 'so', 'not', 'be', 'am', 'are',
    'that', 'have', 'on', 'at', 'by', 'an', 'as', 'do', 'if', 'or',
    'its', 'we', 'you', 'he', 'she', 'they', 'all', 'one', 'but', 'had'
}

VAGUE_WORDS = [
    'amazing', 'best', 'ever', 'perfect', 'love', 'great', 'awesome',
    'excellent', 'fantastic', 'wonderful', 'superb', 'outstanding', 'incredible'
]

NEGATIVE_WORDS = [
    'but', 'however', 'although', 'except', 'issue', 'problem',
    'disappointed', 'unfortunately', 'broke', 'returned', 'bad', 'poor',
    'worse', 'lack', 'missing', 'slow', 'cheap', 'difficult', 'confusing',
    'failed', 'stopped', 'cracked', 'damaged', 'wrong', 'late', 'never'
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

    sentences = [s.strip() for s in text.replace('!', '.').split('.') if s.strip()]
    if len(sentences) > 2 and len(set(sentences)) < len(sentences):
        boost += 0.15

    caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 2) / max(len(words), 1)
    if caps_ratio > 0.3:
        boost += 0.15

    has_negative = any(w in text_lower for w in NEGATIVE_WORDS)
    if not has_negative and len(words) > 15:
        boost += 0.10

    return min(boost, 0.50)


def get_reasons(text, verdict):
    reasons = []
    words = text.split()
    text_lower = text.lower()

    # --- FAKE signals ---
    exclamations = text.count('!')
    if exclamations >= 3:
        reasons.append(f"Exclamation mark spam — {exclamations} found (strong fake signal)")

    vague_matches = [w for w in VAGUE_WORDS if w in text_lower]
    if len(vague_matches) >= 3:
        reasons.append(f"Vague superlative overload — words like '{', '.join(vague_matches[:3])}' detected")

    word_counts = Counter(
        w.strip('.,!?').lower() for w in words
        if w.strip('.,!?').lower() not in STOP_WORDS and len(w.strip('.,!?')) > 2
    )
    if word_counts:
        top_word, top_count = word_counts.most_common(1)[0]
        if top_count >= 4:
            reasons.append(f"Repetitive language — '{top_word}' used {top_count} times")

    sentences = [s.strip() for s in text.replace('!', '.').split('.') if s.strip()]
    if len(sentences) > 2 and len(set(sentences)) < len(sentences):
        reasons.append("Duplicate sentences detected — copy-paste pattern found")

    caps_words = [w for w in words if w.isupper() and len(w) > 2]
    if len(caps_words) >= 3:
        reasons.append(f"ALL CAPS overuse — {len(caps_words)} words fully capitalised")

    has_negative = any(w in text_lower for w in NEGATIVE_WORDS)
    if not has_negative and len(words) > 15:
        reasons.append("No criticism found — genuine reviews almost always mention a flaw")

    # --- GENUINE signals (when no fake flags triggered) ---
    specific_patterns = re.findall(r'\d+\s*(inch|cm|mm|hour|day|week|month|year|gb|kg|ft|star|%)', text_lower)
    if specific_patterns:
        reasons.append(f"Contains specific measurements or data — strong authenticity signal")

    if has_negative and len(words) > 20:
        reasons.append("Balanced review — mentions both positives and negatives")

    unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
    if unique_ratio > 0.75 and len(words) > 20:
        reasons.append("High vocabulary diversity — natural writing pattern detected")

    if len(words) > 30 and verdict == "GENUINE":
        reasons.append("Detailed and descriptive — provides useful context for other buyers")

    # Fallback
    if not reasons:
        if verdict == "FAKE":
            reasons.append("BERT model detected unnatural sentiment patterns in the text")
        else:
            reasons.append("No fake signals detected — review appears authentic")

    return reasons

def simulate_gnn_score(text):
    words = text.split()
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    
    score = 0.5  # neutral baseline

    # Signal 1: Review length (very short = suspicious)
    word_count = len(words)
    if word_count < 12:
        score += 0.15
    elif word_count > 40:
        score -= 0.12

    # Signal 2: Sentence length variance (low variance = bot-like)
    if len(sentences) > 1:
        lengths = [len(s.split()) for s in sentences]
        variance = np.var(lengths)
        if variance < 2.0:
            score += 0.12  # all sentences same length = suspicious
        elif variance > 10.0:
            score -= 0.10  # natural varied writing

    # Signal 3: Punctuation density
    punct_count = sum(1 for c in text if c in '!?')
    punct_ratio = punct_count / max(word_count, 1)
    if punct_ratio > 0.15:
        score += 0.10

    # Signal 4: Unique word ratio (low = repetitive = fake)
    unique_ratio = len(set(w.lower().strip('.,!?') for w in words)) / max(word_count, 1)
    if unique_ratio < 0.55:
        score += 0.13
    elif unique_ratio > 0.80:
        score -= 0.10

    # Signal 5: Deterministic noise per review (simulates reviewer history)
    hash_val = int(hashlib.md5(text.encode()).hexdigest()[:4], 16)
    noise = (hash_val / 65535 - 0.5) * 0.08  # ±4% max noise
    score += noise

    return round(min(max(score, 0.05), 0.97), 4)


def predict_review(review_text):
    result = classifier(review_text, truncation=True, max_length=128)[0]
    bert_fake_score = result['score'] if result['label'] == 'LABEL_1' else 1 - result['score']

    gnn_score = simulate_gnn_score(review_text)
    fused_score = 0.65 * bert_fake_score + 0.35 * gnn_score
    boost = heuristic_boost(review_text)
    final_score = min(fused_score + boost, 1.0)

    verdict = "FAKE" if final_score > 0.35 else "GENUINE"
    reasons = get_reasons(review_text, verdict)

    # Show heuristic contribution when BERT is low
    display_bert = round(bert_fake_score * 100, 1)
    heuristic_pct = round(min(boost, 0.50) * 100, 1)

    return {
        "verdict": verdict,
        "confidence": round(final_score * 100, 1),
        "bert_score": display_bert,
        "gnn_score": round(gnn_score * 100, 1),
        "heuristic_score": heuristic_pct,
        "reasons": reasons
    }

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    review = data.get('review', '').strip()
    if not review:
        return jsonify({"error": "No review text provided"}), 400
    result = predict_review(review)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
