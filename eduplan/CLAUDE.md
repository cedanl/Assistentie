# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.


## Project Overview

**EduPlan** is a student dropout risk detection and intervention tool for Dutch MBO institutions. It uses a **RandomForestRegressor** from [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) to predict dropout risk and generates AI-powered explanations in Dutch via an OpenAI model (the `MODEL` constant in `backend/main.py`).

## Running the Application

**Step 0 — Download data and model (first time only, run from `eduplan/`):**
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

**Run tests (from the `eduplan/` directory):**
```bash
uv run pytest tests/
# Single test:
uv run pytest tests/test_backend.py::test_factor_label_binary_value_1
```

The test suite uses `fastapi.testclient.TestClient` (no running server needed) and `monkeypatch` to mock the OpenAI client. Tests must be run from inside `eduplan/` so relative paths to `shared/data.csv` and `backend/model.joblib` resolve correctly. Shared fixtures (client, demo_student, mock_openai) live in `tests/conftest.py`. `test_trainer.py` uses an `autouse` fixture `mock_student_signal` that mocks `trainer.prepare` and `trainer.train_random_forest` — keeping trainer tests fast and independent of the student-signal library.

There is also a project-root `eduplan/conftest.py` that patches `openai.OpenAI` *before* `backend.main` is imported. This is required because `ALL_PROXY` in the dev environment sets a SOCKS proxy that httpx cannot use without the optional `socksio` package — without this patch, OpenAI client construction at import time would fail. Don't remove it.

**Run the standalone Claude agent CLI:**
```bash
python main.py  # requires ANTHROPIC_API_KEY
```

## Required Environment Variables

- `OPENAI_API_KEY` — used by the backend for LLM explanations (model set via the `MODEL` constant in `backend/main.py`)
- `ANTHROPIC_API_KEY` — used only by `main.py` (the standalone agent CLI)

## Architecture

### Data Flow
```
Streamlit frontend (frontend/app.py)
    → HTTP POST to localhost:8000
    → FastAPI backend (backend/main.py)
        → RandomForestRegressor (backend/model.joblib)
        → SHAP TreeExplainer
        → OpenAI Responses API
```

### Backend (`backend/main.py`) — 9 endpoints
| Endpoint | Input | Purpose |
|----------|-------|---------|
| `POST /predict_dropout` | All model features (dict) + `use_default_model` | Continuous dropout risk score (0–1) |
| `POST /rank_students` | `students` (list of dicts) + `use_default_model` | Bulk-ranking: scoort alle studenten in één call, gesorteerd hoog→laag; vervangt N losse `/predict_dropout` calls |
| `POST /explain_risk` | Student data + probability + `imputed_columns` + `use_default_model` | EduPlan: sectie 1 deterministisch HTML; secties 2–4 via LLM met alleen SHAP-factoren (geen studentprofiel) |
| `POST /feature_importance` | Student data + `use_default_model` | SHAP values per feature (TreeExplainer on regressor) — used for the UI bar chart |
| `POST /summarize` | CSV data string or question | Management summary or Q&A via OpenAI |
| `POST /map_columns` | Uploaded + required column lists | LLM-based column name mapping for CSV uploads |
| `POST /train_model` | `data` (list of dicts) + `dropout_column` + optional `rf_parameters` | Train a custom RandomForest via student-signal; runs in background thread; saves `model_custom.joblib` + `model_custom_features.json` |
| `GET /train_status` | — | Returns current training state: `idle \| training \| done \| failed` with message |
| `DELETE /reset_model` | — | Deletes `model_custom.joblib` + `model_custom_features.json` and resets active model to default |

### Backend (`backend/trainer.py`)
Standalone training module. `train_model(df, dropout_col, model_path, features_path)` uses **[student-signal](https://github.com/cedanl/student-signal)** voor data-voorbereiding (KNN-imputation via `prepare()`) en modeltraining (`train_random_forest()`). Requires ≥ 30 rows. Saves model to `model_path` and the resulting feature list to `features_path` as JSON. Returns `tuple[RandomForestRegressor, list[str]]`. Called by `/train_model` in a background thread.

**Dual-model architecture:** At startup, `clf_default`/`explainer_default`/`features_default` are always loaded from `backend/model.joblib` + `backend/model_features.json`. If `model_custom.joblib` exists, `clf`/`explainer`/`features` (the active set) point to the custom model; otherwise they alias the defaults. `_get_model(use_default)` returns the `(clf, explainer)` pair; `_get_features(use_default)` returns the matching feature list. `_reload_model(path)` updates all three globals atomically. Features path is resolved via `_FEATURES_PATH: dict[str, str]`.

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
Independent CLI tool with file read/edit tools. Not part of the main app. The `agents/` directory is a placeholder for future agent code — currently it only contains a README pointing back to `main.py`.

### Legacy artefacts (ignore)
- `backend/main.py.bak`, `frontend/app.py.bak`, `shared/data_prep.py.bak` — pre-refactor copies kept around for reference, not loaded by anything
- `backend/model.pkl` — older pickle next to the active `backend/model.joblib`; only `.joblib` is loaded

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

**Secties 2–4 — LLM (temperature=0.2)**
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
- `_markdown_to_html()` — converts LLM markdown output to HTML. Calls `html.escape()` first to prevent XSS via raw HTML in LLM responses, then applies bold/italic/list/heading (`#`–`####` → `<h2>`–`<h4>`) regex substitutions.

## OpenAI Client

The backend uses the **Responses API** (not Chat Completions):

```python
response = client.responses.create(model=MODEL, ...)
text = response.output_text  # NOT .choices[0].message.content
```

The `mock_openai` fixture in `tests/conftest.py` mocks `mock_client.responses.create` and sets `mock_response.output_text`. When writing new tests that touch LLM calls, mock this path — not `chat.completions.create`.

## Key Implementation Notes

- **No hard threshold** — all students are returned with their risk score; the frontend sorts high→low
- **Auto-prediction** — prediction runs automatically when the opleiding/klas filter changes; `_run_voorspelling()` does one bulk `/rank_students` call; results cached in `st.session_state.risicostudenten`
- **Features determined dynamically** from `backend/model_features.json` (written by student-signal at training time); fallback to `shared/data.csv` columns if JSON is absent
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
- `scikit-learn` is pinned to **exact** `==1.6.1` (not a range) to match the version the bundled `backend/model.joblib` was serialized on. Loading on a different version emits `InconsistentVersionWarning` and risks silent prediction drift. Unpin only after retraining or replacing the model.
- Model source: [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) — `models/random_forest_regressor.joblib`
- Data source: [cedanl/Uitnodigingsregel](https://github.com/cedanl/Uitnodigingsregel) — `data/raw/synth_data_pred.csv`
- Research basis for EduPlan prompts: `eduplan/docs/uitval/uitval_en_interventies.md`; source PDFs in the same folder (`Eegdeman.pdf`, `De-Uitnodigingsregel-Literatuuroverzicht-en-interventies.pdf`, `Proces_Instroom_Hutspot_highres-1.pdf`)
- Frontend extras: `streamlit-extras` (UI helpers) and `pillow` (image handling) are in `pyproject.toml` and may be used when extending the UI
