from flask import Flask, request, jsonify, render_template
from collections import Counter
from pathlib import Path
import hashlib
import os
import re

import numpy as np
import requests

app = Flask(__name__)

LOCAL_MODEL_DIR = Path("./bert_model")
MODEL_WEIGHT_FILES = ("model.safetensors", "pytorch_model.bin")
_classifier = None
_remote_classifier = None


STOP_WORDS = {
    "i", "the", "a", "is", "it", "and", "to", "in", "for", "this",
    "was", "with", "my", "of", "very", "so", "not", "be", "am", "are",
    "that", "have", "on", "at", "by", "an", "as", "do", "if", "or",
    "its", "we", "you", "he", "she", "they", "all", "one", "but", "had"
}

VAGUE_WORDS = [
    "amazing", "best", "ever", "perfect", "love", "great", "awesome",
    "excellent", "fantastic", "wonderful", "superb", "outstanding", "incredible"
]

NEGATIVE_WORDS = [
    "but", "however", "although", "except", "issue", "problem",
    "disappointed", "unfortunately", "broke", "returned", "bad", "poor",
    "worse", "lack", "missing", "slow", "cheap", "difficult", "confusing",
    "failed", "stopped", "cracked", "damaged", "wrong", "late", "never"
]


def get_hf_credentials():
    model_id = (os.environ.get("HF_MODEL_ID") or "").strip()
    token = (os.environ.get("HF_TOKEN") or "").strip()
    return model_id, token


def is_running_on_render():
    return bool(os.environ.get("RENDER")) or bool(os.environ.get("RENDER_SERVICE_ID"))


def has_local_model_weights():
    return LOCAL_MODEL_DIR.exists() and any((LOCAL_MODEL_DIR / wf).exists() for wf in MODEL_WEIGHT_FILES)


def get_model_backend():
    configured = (os.environ.get("MODEL_BACKEND") or "auto").strip().lower()
    if configured in {"local", "pipeline", "hf_api"}:
        return configured

    if is_running_on_render():
        return "hf_api"

    if has_local_model_weights():
        return "local"

    return "pipeline"


def load_local_classifier():
    global _classifier
    if _classifier is not None:
        return _classifier

    if not has_local_model_weights():
        raise RuntimeError("Local model weights are missing from ./bert_model")

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
    except Exception as exc:
        raise RuntimeError("Local backend requires transformers and torch installed.") from exc

    model_ref = str(LOCAL_MODEL_DIR)
    _, token = get_hf_credentials()
    token = token or None

    model = AutoModelForSequenceClassification.from_pretrained(model_ref, token=token)
    tokenizer = AutoTokenizer.from_pretrained(model_ref, token=token)
    _classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)
    return _classifier


def load_remote_pipeline_classifier():
    global _remote_classifier
    if _remote_classifier is not None:
        return _remote_classifier

    model_id, token = get_hf_credentials()
    if not model_id:
        raise RuntimeError("HF_MODEL_ID is missing in environment variables.")
    if not token:
        raise RuntimeError("HF_TOKEN is missing in environment variables for pipeline mode.")

    try:
        from transformers import pipeline
    except Exception as exc:
        raise RuntimeError(
            "Pipeline mode requires transformers + torch. Install requirements.local-ml.txt."
        ) from exc

    _remote_classifier = pipeline(
        "text-classification",
        model=model_id,
        tokenizer=model_id,
        token=token,
    )
    return _remote_classifier


def parse_hf_prediction(payload):
    if isinstance(payload, list) and payload:
        first = payload[0]
        if isinstance(first, list) and first:
            best = max(first, key=lambda row: row.get("score", 0.0))
            return str(best.get("label", "")), float(best.get("score", 0.0))
        if isinstance(first, dict):
            return str(first.get("label", "")), float(first.get("score", 0.0))

    if isinstance(payload, dict) and "label" in payload:
        return str(payload.get("label", "")), float(payload.get("score", 0.0))

    raise RuntimeError("Unexpected response format from Hugging Face inference API.")


def infer_with_hf_api(text):
    model_id, token = get_hf_credentials()
    if not model_id:
        raise RuntimeError("HF_MODEL_ID is missing in environment variables.")

    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{model_id}",
        headers=headers,
        json={
            "inputs": text,
            "options": {"wait_for_model": True}
        },
        timeout=90,
    )

    if response.status_code >= 400:
        if response.status_code in {401, 403}:
            raise RuntimeError(
                "Hugging Face auth failed for private model access. "
                "Verify HF_TOKEN has read access to HF_MODEL_ID."
            )
        if response.status_code == 404:
            raise RuntimeError(
                "Hugging Face model not found or inaccessible. "
                "Check HF_MODEL_ID format (owner/repo) and repo visibility/token permissions."
            )
        raise RuntimeError(f"Hugging Face API error ({response.status_code}).")

    payload = response.json()
    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(f"Hugging Face API error: {payload['error']}")

    return parse_hf_prediction(payload)


def infer_with_local_pipeline(text):
    classifier = load_local_classifier()
    result = classifier(text, truncation=True, max_length=128)[0]
    return str(result["label"]), float(result["score"])


def infer_with_pipeline(text):
    classifier = load_remote_pipeline_classifier()
    result = classifier(text, truncation=True, max_length=128)[0]
    return str(result["label"]), float(result["score"])


def get_bert_fake_score(text):
    backend = get_model_backend()

    if backend == "local":
        label, score = infer_with_local_pipeline(text)
    elif backend == "pipeline":
        label, score = infer_with_pipeline(text)
    elif backend == "hf_api":
        label, score = infer_with_hf_api(text)
    else:
        raise RuntimeError(f"Unsupported MODEL_BACKEND '{backend}'.")

    normalized = label.strip().upper()
    fake_labels = {"LABEL_1", "FAKE", "CG", "DECEPTIVE"}
    bert_fake_score = score if normalized in fake_labels else 1.0 - score
    return bert_fake_score, backend


def heuristic_boost(text):
    boost = 0.0
    words = text.split()
    text_lower = text.lower()

    if text.count("!") >= 3:
        boost += 0.25

    matches = sum(1 for w in VAGUE_WORDS if w in text_lower)
    if matches >= 3:
        boost += 0.20

    word_counts = Counter(
        w.strip(".,!?").lower() for w in words
        if w.strip(".,!?").lower() not in STOP_WORDS and len(w.strip(".,!?")) > 2
    )
    if word_counts and word_counts.most_common(1)[0][1] >= 4:
        boost += 0.30

    sentences = [s.strip() for s in text.replace("!", ".").split(".") if s.strip()]
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

    exclamations = text.count("!")
    if exclamations >= 3:
        reasons.append(f"Exclamation mark spam - {exclamations} found (strong fake signal)")

    vague_matches = [w for w in VAGUE_WORDS if w in text_lower]
    if len(vague_matches) >= 3:
        reasons.append(f"Vague superlative overload - words like '{', '.join(vague_matches[:3])}' detected")

    word_counts = Counter(
        w.strip(".,!?").lower() for w in words
        if w.strip(".,!?").lower() not in STOP_WORDS and len(w.strip(".,!?")) > 2
    )
    if word_counts:
        top_word, top_count = word_counts.most_common(1)[0]
        if top_count >= 4:
            reasons.append(f"Repetitive language - '{top_word}' used {top_count} times")

    sentences = [s.strip() for s in text.replace("!", ".").split(".") if s.strip()]
    if len(sentences) > 2 and len(set(sentences)) < len(sentences):
        reasons.append("Duplicate sentences detected - copy-paste pattern found")

    caps_words = [w for w in words if w.isupper() and len(w) > 2]
    if len(caps_words) >= 3:
        reasons.append(f"ALL CAPS overuse - {len(caps_words)} words fully capitalised")

    has_negative = any(w in text_lower for w in NEGATIVE_WORDS)
    if not has_negative and len(words) > 15:
        reasons.append("No criticism found - genuine reviews often mention at least one flaw")

    specific_patterns = re.findall(r"\d+\s*(inch|cm|mm|hour|day|week|month|year|gb|kg|ft|star|%)", text_lower)
    if specific_patterns:
        reasons.append("Contains specific measurements or data - strong authenticity signal")

    if has_negative and len(words) > 20:
        reasons.append("Balanced review - mentions both positives and negatives")

    unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
    if unique_ratio > 0.75 and len(words) > 20:
        reasons.append("High vocabulary diversity - natural writing pattern detected")

    if len(words) > 30 and verdict == "GENUINE":
        reasons.append("Detailed and descriptive - provides useful context for buyers")

    if not reasons:
        if verdict == "FAKE":
            reasons.append("Model detected unnatural sentiment patterns in the text")
        else:
            reasons.append("No fake signals detected - review appears authentic")

    return reasons


def simulate_gnn_score(text):
    words = text.split()
    sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]

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

    punct_count = sum(1 for c in text if c in "!?")
    punct_ratio = punct_count / max(word_count, 1)
    if punct_ratio > 0.15:
        score += 0.10

    unique_ratio = len(set(w.lower().strip(".,!?") for w in words)) / max(word_count, 1)
    if unique_ratio < 0.55:
        score += 0.13
    elif unique_ratio > 0.80:
        score -= 0.10

    hash_val = int(hashlib.md5(text.encode()).hexdigest()[:4], 16)
    noise = (hash_val / 65535 - 0.5) * 0.08
    score += noise

    return round(min(max(score, 0.05), 0.97), 4)


def predict_review(review_text):
    bert_warning = None
    try:
        bert_fake_score, backend = get_bert_fake_score(review_text)
    except Exception as exc:
        # Keep the app functional in production even when remote model auth/config breaks.
        bert_fake_score = 0.50
        backend = "fallback_bert_unavailable"
        bert_warning = str(exc)

    gnn_score = simulate_gnn_score(review_text)
    fused_score = 0.65 * bert_fake_score + 0.35 * gnn_score
    boost = heuristic_boost(review_text)
    final_score = min(fused_score + boost, 1.0)

    verdict = "FAKE" if final_score > 0.35 else "GENUINE"
    reasons = get_reasons(review_text, verdict)
    if bert_warning:
        reasons.insert(0, f"BERT temporarily unavailable. Using fallback scoring. Details: {bert_warning}")

    return {
        "verdict": verdict,
        "confidence": round(final_score * 100, 1),
        "bert_score": round(bert_fake_score * 100, 1),
        "gnn_score": round(gnn_score * 100, 1),
        "heuristic_score": round(min(boost, 0.50) * 100, 1),
        "reasons": reasons,
        "model_backend": backend,
        "bert_warning": bert_warning,
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model_backend": get_model_backend(),
            "has_local_weights": has_local_model_weights(),
            "hf_model_id_configured": bool((os.environ.get("HF_MODEL_ID") or "").strip()),
            "hf_token_configured": bool((os.environ.get("HF_TOKEN") or "").strip()),
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    review = str(data.get("review", "")).strip()

    if not review:
        return jsonify({"error": "No review text provided"}), 400

    try:
        result = predict_review(review)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    selected = get_model_backend()
    print(f"Starting ReviewGuard with backend: {selected}")

    port = int((os.environ.get("PORT") or "5000").strip())
    debug = (os.environ.get("FLASK_DEBUG") or "1").strip() == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
