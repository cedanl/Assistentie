# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EduPulse** is a student dropout risk detection and intervention tool built for educational institutions. It uses a RandomForest ML model to predict dropout risk and generates AI-powered explanations in Dutch via OpenAI GPT-4o-mini.

## Running the Application

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

**Regenerate mock data and retrain model:**
```bash
python shared/data_prep.py
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
        → RandomForest model (backend/model.pkl)
        → SHAP TreeExplainer
        → OpenAI GPT-4o-mini
```

### Backend (`backend/main.py`) — 4 endpoints
| Endpoint | Input | Purpose |
|----------|-------|---------|
| `POST /predict_dropout` | StudentData (Cijfer, Aanwezigheid, Waarschuwingen, EC) | Binary dropout prediction (threshold: 0.35) |
| `POST /explain_risk` | Student data + prediction + probability | Dutch-language AI explanation |
| `POST /feature_importance` | Student data | SHAP values per feature |
| `POST /summarize` | CSV data string | Management summary via OpenAI |

### Frontend (`frontend/app.py`)
- Sidebar filters: Opleiding (program), Klas (class), Mentor
- Dashboard: student table, metrics, grade/attendance charts
- Risk prediction: bulk prediction → high-risk student selector → SHAP analysis
- Export: Markdown or Word (.docx) report per student

### Shared (`shared/`)
- `data.csv` — 200 synthetic student records (features: Cijfer, Aanwezigheid, EC, Waarschuwingen, Uitgevallen, etc.)
- `data_prep.py` — generates `data.csv` and trains/saves `backend/model.pkl`

### `main.py` — Standalone Claude agent
Independent CLI tool with file read/edit tools. Not part of the main app.

## Key Implementation Notes

- The ML model threshold is **0.35** (not 0.5) — students above 35% predicted probability are flagged as at-risk
- All user-facing text and AI responses are in **Dutch**
- The frontend uses `st.session_state.risicostudenten` to persist risk prediction results across Streamlit reruns
- `frontend/ui.py` exists but is currently unused
- Package manager is **UV** (preferred over pip); cache stored in `./.uv_cache/`
