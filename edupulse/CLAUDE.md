# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EduPulse** is a student dropout risk detection and intervention tool for Dutch MBO institutions. It uses a **RandomForestRegressor** from [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) to predict dropout risk and generates AI-powered explanations in Dutch via OpenAI GPT-4o-mini.

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

- `OPENAI_API_KEY` — used by the backend for GPT-4o-mini explanations
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
| `POST /predict_dropout` | All model features (dict) | Continuous dropout risk score (0–1) |
| `POST /explain_risk` | Student data + probability | Dutch-language AI explanation via GPT-4o-mini |
| `POST /feature_importance` | Student data | SHAP values per feature (TreeExplainer on regressor) |
| `POST /summarize` | CSV data string or question | Management summary or Q&A via OpenAI |

### Frontend (`frontend/app.py`) — two screens

**Start screen** (`page = "start"`)
- Search field + START button to select an opleiding
- Quick-select pills: first 4 opleidingen visible, rest behind "Meer ↓" toggle
- Checkbox to remember the chosen opleiding

**Main screen** (`page = "main"`)
- Header: CEDA logo + UITNODIGINGSREGEL / EDUPLAN nav tabs; light pink background with shadow
- White card (bordered container) containing:
  - Card header: opleiding name + KLAS selectbox + pencil edit button
  - Terracotta banner: "Toon mij X lerenden…" with slider (default top_n = **10**)
  - UITNODIGINGSREGEL tab: horizontal bar chart sorted high→low by risk score
  - EDUPLAN tab: student selector → TOON EDUPLAN → Dutch AI explanation + PRINT/DOWNLOAD (.docx)
- Footer with CC license text

### Shared (`shared/`)
- `data.csv` — **1.000** synthetic student records across 11 opleidingen; `Opleiding` column stores the program name directly
- `data_prep.py` — downloads `synth_data_pred.csv` from cedanl/Uitnodigingsregel and `model.joblib` from MondriaanBI/Uitnodigingsregel
- `synth_data_pred.csv` — raw download, tab-separated

### `main.py` — Standalone Claude agent
Independent CLI tool with file read/edit tools. Not part of the main app.

## Key Implementation Notes

- **No hard threshold** — all students are returned with their risk score; the frontend sorts high→low
- **Auto-prediction** — prediction runs automatically when the opleiding/klas filter changes; results cached in `st.session_state.risicostudenten`
- **Features are determined dynamically** from `shared/data.csv` columns, excluding `Dropout`, `Naam`, `Opleiding`, `Klas`, `Mentor`
- The model was trained with numpy arrays (no feature names); always pass `.values` to avoid sklearn warnings
- SHAP for a regressor returns shape `(n_samples, n_features)` directly — no `[1]` class index needed
- All user-facing text and AI responses are in **Dutch**
- `frontend/ui.py` exists but is currently unused
- Package manager is **UV** (preferred over pip); cache stored in `./.uv_cache/`
- Model source: [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) — `models/random_forest_regressor.joblib`
- Data source: [cedanl/Uitnodigingsregel](https://github.com/cedanl/Uitnodigingsregel) — `data/raw/synth_data_pred.csv`
