# ReviewGuard - Fake Review Detector

ReviewGuard is a Flask + ML web app that detects whether a product review is likely fake or genuine.

## Current Model Stack
- BERT text classifier (fine-tuned)
- Simulated GNN behavioral score (rule-based approximation)
- Heuristic booster + explainability reasons

## Local Run
1. Activate environment:
   - Windows PowerShell: `mlproject\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. (Optional for private HF pipeline mode) Install local ML runtime:
   - `pip install -r requirements.local-ml.txt`
4. Choose backend:
   - `$env:MODEL_BACKEND="local"` (use local `./bert_model`)
   - `$env:MODEL_BACKEND="pipeline"` (download private model using `HF_MODEL_ID` + `HF_TOKEN`)
   - `$env:MODEL_BACKEND="hf_api"` (lightweight inference API mode)
5. Start app:
   - `python app.py`
6. Open:
   - `http://127.0.0.1:5000`

## Deployment (Render Free Tier)
This repo is prepared for Render using:
- `render.yaml`
- `Procfile`
- `runtime.txt`

### Important model note
Large model weight files are not tracked in this repo. In production, the app will:
- use local `./bert_model` if weights exist, otherwise
- load from Hugging Face via `HF_MODEL_ID` (required if local weights are missing).

Set these Render environment variables:
- `HF_MODEL_ID` = your hosted model id (example: `your-username/reviewguard-bert`)
- `HF_TOKEN` = optional, only if your model repo is private

### Render steps
1. Push this code to GitHub.
2. In Render, create a new **Web Service** from your repo.
3. Render will detect `render.yaml` automatically.
4. Add `HF_MODEL_ID` (and `HF_TOKEN` if needed).
5. Deploy.

## API
- `GET /` -> Web UI
- `POST /predict` -> JSON input: `{ "review": "text" }`

Response keys:
- `verdict`
- `confidence`
- `bert_score`
- `gnn_score`
- `heuristic_score`
- `reasons`
