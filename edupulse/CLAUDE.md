# CLAUDE.md — edupulse

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
