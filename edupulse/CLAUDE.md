# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EduPulse** is a student dropout risk detection and intervention tool for Dutch MBO institutions. It uses a **RandomForestRegressor** from [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) to predict dropout risk and generates AI-powered explanations in Dutch via OpenAI GPT-4.1.

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

- `OPENAI_API_KEY` — used by the backend for GPT-4.1 explanations
- `ANTHROPIC_API_KEY` — used only by `main.py` (the standalone agent CLI)

## Architecture

### Data Flow
```
Streamlit frontend (frontend/app.py)
    → HTTP POST to localhost:8000
    → FastAPI backend (backend/main.py)
        → RandomForestRegressor (backend/model.joblib)
        → SHAP TreeExplainer
        → OpenAI GPT-4.1
```

### Backend (`backend/main.py`) — 5 endpoints
| Endpoint | Input | Purpose |
|----------|-------|---------|
| `POST /predict_dropout` | All model features (dict) | Continuous dropout risk score (0–1) |
| `POST /explain_risk` | Student data + probability | EduPlan: computes SHAP internally, then calls GPT-4.1 with student profile + top-5 risk factors |
| `POST /feature_importance` | Student data | SHAP values per feature (TreeExplainer on regressor) — used for the UI bar chart |
| `POST /summarize` | CSV data string or question | Management summary or Q&A via OpenAI |
| `POST /map_columns` | Uploaded + required column lists | LLM-based column name mapping for CSV uploads |

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

## Model Features

The model uses 27 features derived from `shared/data.csv` (all columns except `Dropout`, `Naam`, `Opleiding`, `Klas`, `Mentor`):

| Feature | Type | Meaning |
|---------|------|---------|
| `StudentAge` | int | Age in years |
| `StudentGender` | 0/1 | Gender (1 = man) |
| `absence_unauthorized` | float | Unauthorized absence (days) |
| `absence_authorized` | float | Authorized absence (days) |
| `Aanmel_aantal` | float | Number of enrolments for this programme |
| `max1studie` | 0/1 | 1 = this is their only ever enrolment |
| `ROCMondriaan` | 0/1 | Previously enrolled at ROC Mondriaan |
| `Richting_nan` | 0/1 | Programme direction unknown |
| `Economie` … `Anders` | 0/1 | Sector (one-hot: Economie, Landbouw, Techniek, DSV, Zorgenwelzijn, Anders) |
| `VooroplNiveau_*` | 0/1 | Prior education level (one-hot: HAVO, MBO, basis, educatie, prak, VMBO-BB/GL/KB/TL, nan, VWOplus, other) |

`Studentnummer` is present in the features list but excluded from SHAP explanations (`SHAP_EXCLUDE`).

## EduPlan Generation (`/explain_risk`)

The EduPlan prompt is structured in four sections, grounded in MBO dropout research literature (`edupulse/docs/uitval/`):

1. **🔍 Risicoprofiel** — 4–6 sentences on the student's specific risk factors, using real values and the risk level (LAAG / MATIG / HOOG)
2. **⚠️ Signalen en gespreksthema's** — 4 concrete conversation starters for the mentor's first contact
3. **🎯 Interventies op maat** — 3–5 evidence-based interventions (motivatiegesprek, verzuimaanpak, buddy-koppeling, motivatie-interventie, LEC-doorverwijzing), adapted to the student's profile
4. **📋 Actiepunten** — numbered action list sorted by urgency (this week / this month)

Risk levels: **LAAG** (< 35%), **MATIG** (35–65%), **HOOG** (≥ 65%).

The backend computes SHAP values internally and passes the top-5 risk factors (with direction and magnitude) to the prompt, so the LLM focuses on what actually drives the risk for that specific student. `_decode_student_profile()` translates raw one-hot features into readable Dutch text before sending to the LLM.

## Key Implementation Notes

- **No hard threshold** — all students are returned with their risk score; the frontend sorts high→low
- **Auto-prediction** — prediction runs automatically when the opleiding/klas filter changes; results cached in `st.session_state.risicostudenten`
- **Features determined dynamically** from `shared/data.csv` columns at startup
- The model was trained with numpy arrays (no feature names); always pass `.values` to avoid sklearn warnings
- SHAP for a regressor returns shape `(n_samples, n_features)` directly — no `[1]` class index needed
- `/explain_risk` and `/feature_importance` both compute SHAP — this is intentional: the former uses SHAP for the prompt, the latter serves the UI bar chart
- All user-facing text and AI responses are in **Dutch**
- `frontend/ui.py` exists but is currently unused
- Package manager is **UV** (preferred over pip); cache stored in `./.uv_cache/`
- Model source: [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) — `models/random_forest_regressor.joblib`
- Data source: [cedanl/Uitnodigingsregel](https://github.com/cedanl/Uitnodigingsregel) — `data/raw/synth_data_pred.csv`
- Research basis for EduPlan prompts: `edupulse/docs/uitval/uitval_en_interventies.md`
