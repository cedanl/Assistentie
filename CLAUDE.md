# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**CEDAssistentie** is the CEDA (Centrum Educatieve Digitale Assistentie) monorepo exploring AI-powered digital assistance for Dutch MBO (secondary vocational) education. It contains three independent sub-projects:

- **`src/`** — A Streamlit multi-page app template for new CEDA projects
- **`eduplan/`** — A production EduPlan app for student dropout risk prediction (has its own `CLAUDE.md` with full details)
- **`edupulse/`** — EduClaw Sprint 1 app: a harnessed agentic uitvalrisico-check for MBO begeleiders. FastAPI backend (port 8001) + Streamlit frontend (port 8503) + Claude agent kernel. Has its own `CLAUDE.md`. Distinct from `eduplan/` — different ports, uses Anthropic (not OpenAI) for the agent kernel, has its own SQLite DB and ML pipeline (`backend/ml/`).

## Running the Template App (`src/`)

**Install dependencies:**
```bash
uv sync
```

**Run a Streamlit page directly (no configured entry point yet):**
```bash
uv run streamlit run src/frontend/Overview/Home.py
```

**Run the standalone Claude agent CLI:**
```bash
uv run src/main.py  # requires ANTHROPIC_API_KEY
```

**Lint and format (`src/`):**
```bash
uv run ruff check src/
uv run ruff format src/
```

The root `pyproject.toml` manages the template's dependencies (`streamlit>=1.46.0`, `ruff>=0.15.10`). Python >= 3.13 required. Ruff config (`[tool.ruff]`) is defined in root `pyproject.toml`.

## Template Architecture (`src/`)

### Page Configuration Pattern
New Streamlit apps register pages in an entry `main.py` using `st.navigation` / `st.Page`. Each page file exposes `title` and `icon` variables at module level. The current `src/main.py` is not a Streamlit entry point — it is the standalone Claude agent CLI (see below).

### Directory Conventions
```
src/
├── main.py               # Standalone Claude agent CLI (Anthropic SDK)
├── frontend/
│   ├── Overview/         # Landing/home pages
│   ├── Modules/          # Feature pages (business logic UI)
│   ├── Files/            # File upload/management pages
│   └── utils/            # Shared frontend helpers
└── backend/
    └── *.py              # Business logic, data transformations, model calls
```

Frontend pages import from `backend/` for data processing. Keep UI code in `frontend/` and computation in `backend/`. Use `@st.cache_data` for data loading, `@st.cache_resource` for models/connections, and `st.session_state` for cross-page state.

### Standalone Claude Agent (`src/main.py`)
Interactive CLI with file tools: `read_file`, `list_files`, `edit_file`. Requires `ANTHROPIC_API_KEY`. Logs to `agent.log`.

## EduPlan Sub-Project

See `eduplan/CLAUDE.md` for full details on the dropout-risk app. Key points:
- Env vars: `OPENAI_API_KEY` (backend GPT-4.1 via Responses API), `ANTHROPIC_API_KEY` (standalone agent CLI only)
- Both the FastAPI backend (port 8000) and Streamlit frontend (port 8502) must run simultaneously
- SVG branding assets live in `eduplan/frontend/static/`
- Training uses **[student-signal](https://github.com/cedanl/student-signal)** (KNN-imputation + GridSearchCV); feature lists are stored as JSON next to each model file

**Run EduPlan tests (from the `eduplan/` directory):**
```bash
cd eduplan && uv run pytest tests/
# Single test:
cd eduplan && uv run pytest tests/test_backend.py::test_factor_label_binary_value_1
```

Install dev dependencies first if needed: `cd eduplan && uv sync --extra dev`

## Repository-Wide Notes

- Package manager: **UV** (cache in `./.uv_cache/`); prefer `uv sync` / `uv run` over bare `pip`/`python`
- Linter/formatter: **ruff** — configured in both root `pyproject.toml` (`src/`) and `eduplan/pyproject.toml`
- All user-facing text across both sub-projects is in **Dutch**
- `data/` at repo root contains shared input/output folders used by `src/` examples
