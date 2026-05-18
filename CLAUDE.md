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
- Env vars: `ANTHROPIC_API_KEY` (backend Sonnet 4.6 via Messages API; also used by the standalone agent CLI)
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
