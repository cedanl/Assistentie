# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EduPulse** is a student dropout risk detection and intervention tool for Dutch MBO institutions. It uses a **RandomForestRegressor** from [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) to predict dropout risk and generates AI-powered explanations in Dutch via OpenAI GPT-4.1.

## Running the Application

**Step 0 — Download data and model (first time only, run from `edupulse/`):**
```bash
uv run python shared/data_prep.py
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
# Dev dependencies (pytest, httpx, ruff):
uv sync --extra dev
```

**Lint and format:**
```bash
uv run ruff check backend/ frontend/ tests/
uv run ruff format backend/ frontend/ tests/
```

**Run tests (from the `edupulse/` directory):**
```bash
uv run pytest tests/
# Single test:
uv run pytest tests/test_backend.py::test_factor_label_binary_value_1
```

The test suite uses `fastapi.testclient.TestClient` (no running server needed) and `monkeypatch` to mock the OpenAI client. Tests must be run from inside `edupulse/` so relative paths to `shared/data.csv` and `backend/model.joblib` resolve correctly. Shared fixtures (client, demo_student, mock_openai) live in `tests/conftest.py`. `test_trainer.py` tests `backend/trainer.py` in isolation using a temporary joblib path.

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

### Backend (`backend/main.py`) — 8 endpoints
| Endpoint | Input | Purpose |
|----------|-------|---------|
| `POST /predict_dropout` | All model features (dict) + `use_default_model` | Continuous dropout risk score (0–1) |
| `POST /explain_risk` | Student data + probability + `imputed_columns` + `use_default_model` | EduPlan: sectie 1 deterministisch HTML; secties 2–4 via GPT-4.1 met alleen SHAP-factoren (geen studentprofiel) |
| `POST /feature_importance` | Student data + `use_default_model` | SHAP values per feature (TreeExplainer on regressor) — used for the UI bar chart |
| `POST /summarize` | CSV data string or question | Management summary or Q&A via OpenAI |
| `POST /map_columns` | Uploaded + required column lists | LLM-based column name mapping for CSV uploads |
| `POST /train_model` | `data` (list of dicts) + `dropout_column` + optional `rf_parameters` | Train a custom RandomForest on institution data; runs in background thread; saves to `backend/model_custom.joblib` |
| `GET /train_status` | — | Returns current training state: `idle \| training \| done \| failed` with message |
| `DELETE /reset_model` | — | Deletes `model_custom.joblib` and resets active model to default |

### Backend (`backend/trainer.py`)
Standalone training module. `train_model()` runs GridSearchCV over `DEFAULT_PARAM_GRID` on the provided DataFrame, requires ≥ 30 training rows, and saves the best estimator to disk. Called by `/train_model` in a background thread via `threading.Thread`.

**Dual-model architecture:** At startup, `clf_default`/`explainer_default` are always loaded from `backend/model.joblib`. If `backend/model_custom.joblib` exists, `clf`/`explainer` (the active model) point to it; otherwise they alias the default. `use_default_model: bool` on each request selects which pair to use via `_get_model()`.

### Frontend (`frontend/app.py`, `frontend/styles.py`) — two screens

`styles.py` is the only other frontend module. It exports CSS strings (`START_CSS`, `MAIN_CSS`) and color constants (`TERRACOTTA`, `ROZE_BG`, `ROZE_LICHT`) imported by `app.py`. All visual styling lives there.

`frontend/static/` contains SVG branding assets (e.g. `npuls-logo.svg`) served directly by Streamlit.

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

The EduPlan is split into two parts to prevent hallucination:

**Sectie 1 — deterministisch (geen LLM)**
`_build_risicoprofiel_html()` renders Section 1 as HTML directly from actual student data. Imputed columns are shown as `<i style='color:#999;'>niet beschikbaar</i>`. The top-5 SHAP factors are listed with direction and magnitude. If data quality is insufficient (`data_onvoldoende = True`), a warning is shown instead of calling the LLM.

**Secties 2–4 — LLM (GPT-4.1, temperature=0.2)**
The LLM receives **only** the risk level and SHAP factors — no student profile. This eliminates hallucination of absent values like age, gender, and absence days.

1. **🔍 Risicoprofiel** — deterministisch HTML (geen LLM)
2. **⚠️ Signalen en gespreksthema's** — 4 gespreksstarters afgeleid van SHAP-factoren
3. **🎯 Interventies op maat** — 3–5 evidence-based interventions, only for available factors
4. **📋 Actiepunten** — numbered action list sorted by urgency (this week / this month)

Risk levels: **LAAG** (< 35%), **MATIG** (35–65%), **HOOG** (≥ 65%).

### Key implementation details

- `BINARY_LABELS: dict[str, tuple[str, str]]` — single source of truth for 22 binary features; maps each feature to `(label_bij_1, label_bij_0)`. Used by `_factor_label(key, value)` so the LLM never sees ambiguous values like `VooroplNiveau_HAVO: 0.0`.
- `imputed_columns: list[str]` — passed from frontend via `ExplainRequest`; features in this set are excluded from SHAP analysis and shown as "niet beschikbaar" in the profile.
- `data_onvoldoende = max(abs(shap_val)) < 0.01` — detects when all imputed-at-median data leaves no variance; LLM call is skipped, warning returned.
- `SHAP_EXCLUDE = {"Studentnummer"}` — excluded from SHAP display regardless.
- `_SECTOR_COLS` and `_VOOROPL_MAP` — module-level dicts for decoding one-hot sector/education columns in the deterministic profile.
- `_markdown_to_html()` — converts LLM markdown output to HTML. Calls `html.escape()` first to prevent XSS via raw HTML in LLM responses, then applies bold/italic/list regex substitutions.

## OpenAI Client

The backend uses the **Responses API** (not Chat Completions):

```python
response = client.responses.create(model="gpt-4.1", ...)
text = response.output_text  # NOT .choices[0].message.content
```

The `mock_openai` fixture in `tests/conftest.py` mocks `mock_client.responses.create` and sets `mock_response.output_text`. When writing new tests that touch LLM calls, mock this path — not `chat.completions.create`.

## Key Implementation Notes

- **No hard threshold** — all students are returned with their risk score; the frontend sorts high→low
- **Auto-prediction** — prediction runs automatically when the opleiding/klas filter changes; results cached in `st.session_state.risicostudenten`
- **Features determined dynamically** from `shared/data.csv` columns at startup
- The model was trained with numpy arrays (no feature names); always pass `.values` to avoid sklearn warnings
- SHAP for a regressor returns shape `(n_samples, n_features)` directly — no `[1]` class index needed
- `/explain_risk` and `/feature_importance` both compute SHAP — this is intentional: the former uses SHAP for the deterministic profile + LLM prompt, the latter serves the UI bar chart
- CSV uploads use `sep=None, engine="python"` to auto-detect comma, tab, semicolon, etc.
- `vul_log` (list of imputed column names) is stored in `st.session_state` after upload and passed to `/explain_risk` as `imputed_columns`
- Training UI state lives in `st.session_state`: `training_status` (`idle|training|done|failed`), `training_message`, and `model_is_custom` (bool). The frontend polls `/train_status` and updates these.
- `gebruik_demo_data` (bool) and `heeft_dropout_kolom` (bool) track whether the uploaded CSV has a `Dropout` column (required to offer custom model training)
- All user-facing text and AI responses are in **Dutch**
- `frontend/ui.py` exists but is currently unused
- Package manager is **UV** (preferred over pip); cache stored in `./.uv_cache/`
- Model source: [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) — `models/random_forest_regressor.joblib`
- Data source: [cedanl/Uitnodigingsregel](https://github.com/cedanl/Uitnodigingsregel) — `data/raw/synth_data_pred.csv`
- Research basis for EduPlan prompts: `edupulse/docs/uitval/uitval_en_interventies.md`
