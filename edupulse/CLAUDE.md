# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EduPulse** is a student dropout risk detection and intervention tool built for educational institutions. It uses a **RandomForestRegressor** from [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) to predict dropout risk and generates AI-powered explanations in Dutch via OpenAI GPT-4o-mini.

## Running the Application

**Step 0 — Download data and model (first time only):**
```bash
python shared/data_prep.py
```

The app requires two processes running simultaneously:

```bash
# Terminal 1 — FastAPI backend (port 8000)
./1_start_fastapi.sh
# or: uv run uvicorn --host 127.0.0.1 --port 8000 backend.main:app --reload

# Terminal 2 — Streamlit frontend (port 8502)
./2_start_streamlit.sh
# or: uv run streamlit run --server.port 8502 frontend/app.py
```

**Install dependencies:**
```bash
uv sync
# or: pip install -r requirements.txt
```

**Run the standalone Claude agent CLI:**
```bash
python main.py  # requires ANTHROPIC_API_KEY
```

## Required Environment Variables

- `OPENAI_API_KEY` — used by the backend for GPT-4o-mini explanations and summaries
- `ANTHROPIC_API_KEY` — used only by `main.py` (the standalone agent CLI)

## Architecture

### Data Flow
```
Streamlit frontend (frontend/app.py)
    → HTTP POST to localhost:8000
    → FastAPI backend (backend/main.py)
        → RandomForestRegressor (backend/model.joblib)
        → SHAP TreeExplainer
        → OpenAI GPT-4o-mini
```

### Backend (`backend/main.py`) — 4 endpoints
| Endpoint | Input | Purpose |
|----------|-------|---------|
| `POST /predict_dropout` | All model features (dict) | Continuous dropout risk score (0–1), all students returned |
| `POST /explain_risk` | Student data + probability | Dutch-language AI explanation via GPT-4o-mini |
| `POST /feature_importance` | Student data | SHAP values per feature (TreeExplainer on regressor) |
| `POST /summarize` | CSV data string or question | Management summary or Q&A via OpenAI |

### Frontend (`frontend/app.py`)
- Sidebar filters: Opleiding (derived from sector columns), Klas, Mentor
- Dashboard: student table (Studentnummer, Naam, Opleiding, Klas, StudentAge, verzuim, Mentor)
- Metrics: average age, unauthorized absence, authorized absence
- Charts: age distribution histogram, absence per program boxplot
- Risk prediction: all students ranked high→low by dropout score
- Export: Markdown or Word (.docx) report per student

### Shared (`shared/`)
- `data.csv` — synthetic student records from Uitnodigingsregel + synthetic Naam/Klas/Mentor columns
- `data_prep.py` — downloads `synth_data_pred.csv` from cedanl/Uitnodigingsregel and `model.joblib` from MondriaanBI/Uitnodigingsregel; saves to `shared/data.csv` and `backend/model.joblib`
- `synth_data_pred.csv` — raw download, tab-separated

### `main.py` — Standalone Claude agent
Independent CLI tool with file read/edit tools. Not part of the main app.

## Key Implementation Notes

- **No hard threshold** — all students are returned with their risk score; the frontend sorts high→low
- **Features are determined dynamically** from `shared/data.csv` columns, excluding `Dropout`, `Naam`, `Opleiding`, `Klas`, `Mentor`
- The model was trained with numpy arrays (no feature names); always pass `.values` to avoid sklearn warnings
- SHAP for a regressor returns shape `(n_samples, n_features)` directly — no `[1]` class index needed
- All user-facing text and AI responses are in **Dutch**
- The frontend uses `st.session_state.risicostudenten` to persist risk prediction results across Streamlit reruns
- `frontend/ui.py` exists but is currently unused
- Package manager is **UV** (preferred over pip); cache stored in `./.uv_cache/`
- Model source: [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) — `models/random_forest_regressor.joblib`
- Data source: [cedanl/Uitnodigingsregel](https://github.com/cedanl/Uitnodigingsregel) — `data/raw/synth_data_pred.csv`
