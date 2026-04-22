import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from pathlib import Path
import numpy as np
import pickle
import threading

# ── File paths ────────────────────────────────────────────────────────────────
_BASE        = Path(__file__).parent
_MODEL_PATH  = _BASE / "gnn_model_weighted.pt"
_GRAPH_PATH  = _BASE / "graph_data.pt"
_SCALER_PATH = _BASE / "scaler.pkl"

# ── Thread-safe singleton state ───────────────────────────────────────────────
_lock        = threading.Lock()
_gnn_model   = None
_graph_data  = None
_scaler      = None
_initialized = False
_init_error  = None


# ── Model architecture — must match Colab training exactly ────────────────────
class FakeReviewGNN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(7, 64)
        self.conv2 = GCNConv(64, 32)
        self.classifier = torch.nn.Linear(32, 2)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.3, training=self.training)
        x = F.relu(self.conv2(x, edge_index))
        return F.log_softmax(self.classifier(x), dim=1)


# ── One-time loader (first request triggers this) ─────────────────────────────
def _load_all():
    global _gnn_model, _graph_data, _scaler, _initialized, _init_error
    with _lock:
        if _initialized:
            return
        try:
            if not _GRAPH_PATH.exists():
                raise FileNotFoundError(f"graph_data.pt not found at {_GRAPH_PATH}")
            if not _MODEL_PATH.exists():
                raise FileNotFoundError(f"gnn_model_weighted.pt not found at {_MODEL_PATH}")
            if not _SCALER_PATH.exists():
                raise FileNotFoundError(f"scaler.pkl not found at {_SCALER_PATH}")

            print("[GNN] Loading graph_data.pt ...", flush=True)
            _graph_data = torch.load(_GRAPH_PATH, map_location="cpu", weights_only=False)
            print(f"[GNN] Graph loaded — {_graph_data.num_nodes} nodes, "
                  f"{_graph_data.num_edges} edges", flush=True)

            with open(_SCALER_PATH, "rb") as f:
                _scaler = pickle.load(f)
            print("[GNN] Scaler loaded.", flush=True)

            _gnn_model = FakeReviewGNN()
            _gnn_model.load_state_dict(
                torch.load(_MODEL_PATH, map_location="cpu", weights_only=True)
            )
            _gnn_model.eval()
            print("[GNN] Model loaded. Ready for inference.", flush=True)
            _initialized = True

        except Exception as e:
            _init_error = str(e)
            _initialized = True   # mark done so we don't retry every request
            print(f"[GNN] Load failed: {e}", flush=True)


# ── Feature extraction — order must match training feature_cols exactly ───────
# ['rating_norm', 'text_length', 'word_count', 'avg_word_length',
#  'exclamation',  'caps_ratio',  'bert_score']
def _extract_features(text: str, rating: float, bert_score: float) -> list:
    words       = text.split()
    word_count  = max(len(words), 1)
    text_length = float(len(text))
    avg_wl      = float(np.mean([len(w) for w in words])) if words else 0.0
    excl        = float(text.count("!"))
    caps_ratio  = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    rating_norm = float(rating) / 5.0
    return [rating_norm, text_length, float(word_count),
            avg_wl, excl, caps_ratio, float(bert_score)]


# ── Public API ────────────────────────────────────────────────────────────────
def get_gnn_score(text: str, rating: float = 3.0, bert_score: float = 0.5) -> float:
    """
    Appends the review as a new node to the loaded 40K-node graph,
    connects it to 5 nearest neighbors by bert_score similarity,
    runs GCN forward pass, returns fake probability [0.0–1.0].

    Falls back to bert_score if model/graph files are unavailable.
    """
    _load_all()

    if _init_error or _gnn_model is None or _graph_data is None:
        return round(float(bert_score), 4)

    try:
        raw    = _extract_features(text, rating, bert_score)
        scaled = _scaler.transform([raw])                      # (1, 7)
        new_feat = torch.tensor(scaled, dtype=torch.float)

        # Augment: append new node to graph
        x_aug   = torch.cat([_graph_data.x, new_feat], dim=0)
        new_idx = x_aug.shape[0] - 1

        # Connect to 5 nearest neighbors by bert_score (feature index 6)
        existing_bert = _graph_data.x[:, 6].numpy()
        diffs     = np.abs(existing_bert - float(scaled[0][6]))
        neighbors = np.argsort(diffs)[:5].tolist()

        src = [new_idx] * len(neighbors) + neighbors + [new_idx]
        dst = neighbors + [new_idx] * len(neighbors) + [new_idx]
        new_edges  = torch.tensor([src, dst], dtype=torch.long)
        edge_aug   = torch.cat([_graph_data.edge_index, new_edges], dim=1)

        with torch.no_grad():
            log_probs = _gnn_model(x_aug, edge_aug)
            probs     = torch.exp(log_probs)
            fake_prob = float(probs[new_idx][0].item())

        return round(fake_prob, 4)

    except Exception as e:
        print(f"[GNN] Inference error: {e}", flush=True)
        return round(float(bert_score), 4)


def gnn_status() -> dict:
    """Returns load status — expose via /api/gnn-status for debugging."""
    return {
        "initialized":  _initialized,
        "error":        _init_error,
        "model_loaded": _gnn_model  is not None,
        "graph_loaded": _graph_data is not None,
        "nodes": int(_graph_data.num_nodes) if _graph_data else 0,
        "edges": int(_graph_data.num_edges) if _graph_data else 0,
    }
