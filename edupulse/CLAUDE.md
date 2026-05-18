# CLAUDE.md — edupulse

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


EduPulse is the EduClaw Sprint 1 app: a harnessed agentic uitvalrisico-check for MBO begeleiders.
FastAPI backend (port 8001) + Streamlit frontend (port 8503) + Claude agent kernel.

## Setup

```bash
uv sync
```

## Data & model (eerste keer)

```bash
# Genereer synthetische data en train ML-model
uv run python -m backend.ml.generate_data   # schrijft data/actieve_studenten.csv + historische_studenten.csv
uv run python -m backend.ml.train           # schrijft data/model.pkl + data/feature_list.json

# Seed database (1000 actieve studenten)
uv run python -m backend.seed
```

## Draaien

```bash
# Terminal 1 — backend
uv run uvicorn backend.main:app --port 8001

# Terminal 2 — frontend
uv run streamlit run frontend/app.py --server.port 8503
```

Vereist: `ANTHROPIC_API_KEY` in de omgeving voor de agent kernel.

## Tests

```bash
uv run pytest tests/ -v
# Enkel bestand:
uv run pytest tests/test_harness.py -v
```

Install dev dependencies eerst: `uv sync --extra dev`

## Lint

```bash
uv run ruff check backend/ frontend/ tests/
uv run ruff format backend/ frontend/ tests/
```

## Architectuur

```
backend/
├── database.py          SQLAlchemy engine + SessionLocal + Base
├── models.py            ORM (StudentDB, HistorischStudentDB, AgentLogDB) + Pydantic schemas
├── seed.py              Vult studenten tabel vanuit CSV
├── main.py              FastAPI app + endpoints
├── ml/
│   ├── generate_data.py Synthetische MBO-studenten (Faker + numpy)
│   ├── train.py         GridSearchCV RF vs XGBoost, SHAP, sla model.pkl op
│   └── predict.py       RisicoPredictor: kans + SHAP top-3
└── agent/
    ├── llm.py           LLMProvider ABC + ClaudeLLMProvider (model-agnostisch)
    ├── tools.py         ToolRegistry: 5 tools (get_student_data, predict_dropout_risk, ...)
    ├── harness.py       Governance: whitelist, rate-limiting, AVG-logging
    └── kernel.py        Agent loop: LLM → tool calls → antwoord (max 10 stappen)
```

## Niet in scope (Sprint 1)

Authenticatie, meerdere rollen, lokale LLM, productie-database (PostgreSQL), real SIS-koppeling.
