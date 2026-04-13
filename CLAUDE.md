# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**CEDAssistentie** is the CEDA (Centrum Educatieve Digitale Assistentie) monorepo exploring AI-powered digital assistance for Dutch MBO (secondary vocational) education. It contains two independent sub-projects:

- **`src/`** — A Streamlit multi-page app template for new CEDA projects
- **`edupulse/`** — A production EduPulse app for student dropout risk prediction (has its own `CLAUDE.md` with full details)

## Running the Template App (`src/`)

**Install dependencies:**
```bash
uv sync
# or: pip install -r requirements.txt
```

**Run a Streamlit page directly (no configured entry point yet):**
```bash
uv run streamlit run src/frontend/Overview/Home.py
```

**Run the standalone Claude agent CLI:**
```bash
uv run src/main.py  # requires ANTHROPIC_API_KEY
```

The root `pyproject.toml` manages the template's dependencies (`streamlit>=1.46.0`). Python >= 3.13 required.

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

## EduPulse Sub-Project

See `edupulse/CLAUDE.md` for full details on the dropout-risk app. Key env vars: `OPENAI_API_KEY` (backend) and optionally `ANTHROPIC_API_KEY` (standalone agent CLI). Both the FastAPI backend (port 8000) and Streamlit frontend (port 8502) must run simultaneously.

**Run EduPulse tests (from the `edupulse/` directory):**
```bash
cd edupulse && uv run pytest tests/
# Single test:
cd edupulse && uv run pytest tests/test_backend.py::test_factor_label_binary_value_1
```

Install dev dependencies first if needed: `cd edupulse && uv sync --extra dev`

## Repository-Wide Notes

- Package manager: **UV** (cache in `./.uv_cache/`); prefer `uv sync` / `uv run` over bare `pip`/`python`
- All user-facing text across both sub-projects is in **Dutch**
- `data/` at repo root contains shared input/output folders used by `src/` examples
