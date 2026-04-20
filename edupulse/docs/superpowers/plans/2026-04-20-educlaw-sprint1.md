# EduClaw Sprint 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bouw een harnessed agentic uitvalrisico-check app (Streamlit + FastAPI + Claude agent) voor MBO begeleiders, conform de EduClaw architectuur.

**Architecture:** FastAPI backend met SQLite database, scikit-learn + XGBoost voorspelmodel met SHAP-uitleg, en Claude-aangedreven agent kernel via model-agnostische LLMProvider. Streamlit frontend toont uitvalrisico via dialoog met de agent. Alle agent-acties zijn gelogd (harness).

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy, SQLite, scikit-learn, XGBoost, SHAP, Anthropic SDK (Claude Sonnet), Streamlit, uv, pytest, httpx, faker

---

## File Map

| Bestand | Verantwoordelijkheid |
|---|---|
| `pyproject.toml` | Dependencies + dev tools |
| `backend/__init__.py` | Package marker |
| `backend/database.py` | SQLAlchemy engine, session, Base |
| `backend/models.py` | ORM-tabellen + Pydantic schemas |
| `backend/ml/__init__.py` | Package marker |
| `backend/ml/generate_data.py` | Genereer 1k actieve + 10k historische studenten |
| `backend/ml/train.py` | Train RF + XGB via GridSearchCV, sla op als model.pkl |
| `backend/ml/predict.py` | Laad model, voorspel risico + SHAP top-3 |
| `backend/agent/__init__.py` | Package marker |
| `backend/agent/llm.py` | LLMProvider ABC + ClaudeLLMProvider |
| `backend/agent/tools.py` | ToolRegistry: 5 agent-tools + Anthropic schemas |
| `backend/agent/harness.py` | Harness: whitelist, logging, rate-limit |
| `backend/agent/kernel.py` | Agent loop: LLM → tool calls → antwoord |
| `backend/main.py` | FastAPI app + endpoints (port 8001) |
| `frontend/app.py` | Streamlit entry point + CEDA huisstijl |
| `frontend/pages/uitvalrisico.py` | Hoofdscherm: student zoeken + agent dialoog |
| `frontend/pages/geschiedenis.py` | Eerdere berekeningen |
| `tests/conftest.py` | sys.path fix + test DB fixture |
| `tests/test_models.py` | Database schema tests |
| `tests/test_generate_data.py` | Synthetische data validatie |
| `tests/test_predict.py` | ML model tests |
| `tests/test_tools.py` | Agent tools tests (mock DB) |
| `tests/test_api.py` | FastAPI endpoint tests |

---

## Task 1: Project scaffolding

**Files:**
- Create: `edupulse/pyproject.toml`
- Create: `edupulse/backend/__init__.py`
- Create: `edupulse/backend/agent/__init__.py`
- Create: `edupulse/backend/ml/__init__.py`
- Create: `edupulse/frontend/__init__.py`
- Create: `edupulse/frontend/pages/__init__.py`
- Create: `edupulse/tests/__init__.py`
- Create: `edupulse/data/.gitkeep`

- [ ] **Stap 1: Maak pyproject.toml aan**

```toml
# edupulse/pyproject.toml
[tool.uv]
cache-dir = "./.uv_cache"

[project]
name = "edupulse"
version = "0.1.0"
description = "EduClaw Sprint 1 — EduPulse Uitvalrisico Agent"
authors = [
    {name = "Ed de Feber", email = "ed.defeber@surf.nl"}
]
requires-python = ">=3.13"
dependencies = [
    "anthropic>=0.49.0",
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "streamlit>=1.46.0",
    "sqlalchemy>=2.0.0",
    "pandas>=2.2.0",
    "numpy>=2.0.0",
    "scikit-learn>=1.5.0",
    "xgboost>=2.1.0",
    "shap>=0.46.0",
    "faker>=30.0.0",
    "joblib>=1.4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

- [ ] **Stap 2: Installeer dependencies**

```bash
cd edupulse && uv sync --extra dev
```

Verwacht: `Resolved N packages` zonder errors.

- [ ] **Stap 3: Maak package markers en data-map aan**

```bash
touch backend/__init__.py backend/agent/__init__.py backend/ml/__init__.py
mkdir -p frontend/pages tests data
touch frontend/__init__.py frontend/pages/__init__.py tests/__init__.py data/.gitkeep
```

- [ ] **Stap 4: Commit**

```bash
git add edupulse/pyproject.toml edupulse/backend/__init__.py edupulse/backend/agent/__init__.py edupulse/backend/ml/__init__.py edupulse/frontend/__init__.py edupulse/frontend/pages/__init__.py edupulse/tests/__init__.py edupulse/data/.gitkeep
git commit -m "feat(edupulse): project scaffolding en dependencies"
```

---

## Task 2: Database layer

**Files:**
- Create: `edupulse/backend/database.py`
- Create: `edupulse/backend/models.py`
- Create: `edupulse/tests/conftest.py`
- Create: `edupulse/tests/test_models.py`

- [ ] **Stap 1: Schrijf de failing test**

```python
# edupulse/tests/test_models.py
import pytest
from sqlalchemy import inspect
from backend.database import engine, Base
from backend.models import StudentDB, HistorischStudentDB, AgentLogDB

def test_student_table_heeft_alle_kolommen():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    kolommen = {c["name"] for c in inspector.get_columns("studenten")}
    verwacht = {
        "studentnummer", "naam", "email", "leeftijd", "geslacht",
        "vooropleiding", "sector", "opleiding", "crebocode", "cohort",
        "niveau", "leerweg", "intakedatum", "aanwezigheid", "voortgang",
        "bsa_studiepunten", "cijfer_nederlands", "cijfer_rekenen",
        "mentor_naam", "mentor_email"
    }
    assert verwacht.issubset(kolommen)

def test_historisch_student_heeft_uitgevallen_kolom():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    kolommen = {c["name"] for c in inspector.get_columns("historische_studenten")}
    assert "uitgevallen" in kolommen

def test_agent_log_tabel_bestaat():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    assert "agent_log" in inspector.get_table_names()
```

- [ ] **Stap 2: Maak conftest.py aan**

```python
# edupulse/tests/conftest.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

- [ ] **Stap 3: Run test — verwacht FAIL**

```bash
cd edupulse && uv run pytest tests/test_models.py -v
```

Verwacht: `ImportError: No module named 'backend'` of `ImportError: No module named 'backend.database'`

- [ ] **Stap 4: Schrijf database.py**

```python
# edupulse/backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_PATH = os.getenv("EDUPULSE_DB", os.path.join(os.path.dirname(__file__), "..", "data", "studenten.db"))
DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Stap 5: Schrijf models.py**

```python
# edupulse/backend/models.py
from datetime import date, datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String
from pydantic import BaseModel, ConfigDict
from backend.database import Base

class StudentDB(Base):
    __tablename__ = "studenten"
    studentnummer   = Column(String, primary_key=True, index=True)
    naam            = Column(String, nullable=False)
    email           = Column(String, nullable=False)
    leeftijd        = Column(Integer, nullable=False)
    geslacht        = Column(String, nullable=False)
    vooropleiding   = Column(String, nullable=False)
    sector          = Column(String, nullable=False)
    opleiding       = Column(String, nullable=False)
    crebocode       = Column(String, nullable=False)
    cohort          = Column(String, nullable=False)
    niveau          = Column(Integer, nullable=False)
    leerweg         = Column(String, nullable=False)
    intakedatum     = Column(Date, nullable=False)
    aanwezigheid    = Column(Float, nullable=False)
    voortgang       = Column(Float, nullable=False)
    bsa_studiepunten = Column(Integer, nullable=False)
    cijfer_nederlands = Column(Float, nullable=False)
    cijfer_rekenen  = Column(Float, nullable=False)
    mentor_naam     = Column(String, nullable=False)
    mentor_email    = Column(String, nullable=False)

class HistorischStudentDB(Base):
    __tablename__ = "historische_studenten"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    studentnummer   = Column(String, index=True)
    naam            = Column(String)
    email           = Column(String)
    leeftijd        = Column(Integer)
    geslacht        = Column(String)
    vooropleiding   = Column(String)
    sector          = Column(String)
    opleiding       = Column(String)
    crebocode       = Column(String)
    cohort          = Column(String)
    niveau          = Column(Integer)
    leerweg         = Column(String)
    intakedatum     = Column(Date)
    aanwezigheid    = Column(Float)
    voortgang       = Column(Float)
    bsa_studiepunten = Column(Integer)
    cijfer_nederlands = Column(Float)
    cijfer_rekenen  = Column(Float)
    mentor_naam     = Column(String)
    mentor_email    = Column(String)
    uitgevallen     = Column(Boolean, nullable=False)

class AgentLogDB(Base):
    __tablename__ = "agent_log"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    timestamp      = Column(DateTime, default=datetime.utcnow)
    sessie_id      = Column(String, index=True)
    gebruiker      = Column(String)
    tool_naam      = Column(String)
    input_hash     = Column(String)
    output_summary = Column(String)
    duur_ms        = Column(Integer)

# Pydantic schemas
class StudentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    studentnummer: str
    naam: str
    email: str
    leeftijd: int
    geslacht: str
    vooropleiding: str
    sector: str
    opleiding: str
    crebocode: str
    cohort: str
    niveau: int
    leerweg: str
    intakedatum: date
    aanwezigheid: float
    voortgang: float
    bsa_studiepunten: int
    cijfer_nederlands: float
    cijfer_rekenen: float
    mentor_naam: str
    mentor_email: str

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    session_id: str
    response: str

class RisicoPredictie(BaseModel):
    studentnummer: str
    uitval_kans: float
    succes_kans: float
    status: str
    shap_top3: list[dict]
```

- [ ] **Stap 6: Run test — verwacht PASS**

```bash
cd edupulse && uv run pytest tests/test_models.py -v
```

Verwacht: 3 tests PASSED

- [ ] **Stap 7: Commit**

```bash
git add edupulse/backend/database.py edupulse/backend/models.py edupulse/tests/conftest.py edupulse/tests/test_models.py
git commit -m "feat(edupulse): database layer — SQLAlchemy models en Pydantic schemas"
```

---

## Task 3: Synthetische data

**Files:**
- Create: `edupulse/backend/ml/generate_data.py`
- Create: `edupulse/tests/test_generate_data.py`

- [ ] **Stap 1: Schrijf de failing tests**

```python
# edupulse/tests/test_generate_data.py
import pandas as pd
from backend.ml.generate_data import genereer_actieve_studenten, genereer_historische_studenten

def test_actieve_studenten_vorm():
    df = genereer_actieve_studenten(n=100)
    assert len(df) == 100
    assert "studentnummer" in df.columns
    assert "uitgevallen" not in df.columns

def test_historische_studenten_heeft_uitgevallen():
    df = genereer_historische_studenten(n=200)
    assert len(df) == 200
    assert "uitgevallen" in df.columns
    assert df["uitgevallen"].dtype == bool

def test_uitval_percentage_realistisch():
    df = genereer_historische_studenten(n=1000)
    pct = df["uitgevallen"].mean()
    assert 0.10 <= pct <= 0.35, f"Uitvalpercentage {pct:.1%} buiten verwacht bereik"

def test_aanwezigheid_range():
    df = genereer_actieve_studenten(n=200)
    assert df["aanwezigheid"].between(0.0, 1.0).all()

def test_cijfers_range():
    df = genereer_actieve_studenten(n=200)
    assert df["cijfer_nederlands"].between(1.0, 10.0).all()
    assert df["cijfer_rekenen"].between(1.0, 10.0).all()

def test_studentnummer_uniek():
    df = genereer_actieve_studenten(n=500)
    assert df["studentnummer"].is_unique
```

- [ ] **Stap 2: Run test — verwacht FAIL**

```bash
cd edupulse && uv run pytest tests/test_generate_data.py -v
```

Verwacht: `ImportError: cannot import name 'genereer_actieve_studenten'`

- [ ] **Stap 3: Schrijf generate_data.py**

```python
# edupulse/backend/ml/generate_data.py
import numpy as np
import pandas as pd
from faker import Faker
from datetime import date

fake = Faker("nl_NL")
rng = np.random.default_rng(42)

SECTOREN = {
    "Techniek": [
        ("Software Developer",     "25604", 4),
        ("Netwerkbeheerder",        "93200", 4),
        ("Elektrotechniek",         "25160", 3),
        ("Installatiemonteur",      "25480", 2),
    ],
    "Zorg": [
        ("Verpleegkundige",         "99070", 4),
        ("Verzorgende IG",          "93500", 3),
        ("Helpende Zorg & Welzijn", "92640", 2),
        ("Doktersassistent",        "34576", 4),
    ],
    "Economie": [
        ("Commercieel medewerker",  "90111", 3),
        ("Financieel administrateur", "90370", 4),
        ("Logistiek medewerker",    "90640", 3),
        ("Manager handel",         "90202", 4),
    ],
    "Dienstverlening": [
        ("Kok",                    "25185", 2),
        ("Gastvrouw/-heer",        "90191", 3),
        ("Kapper",                 "97460", 3),
    ],
    "Groen": [
        ("Dierverzorger",          "97730", 3),
        ("Medewerker voedsel",     "97590", 2),
        ("Tuin- en landschapsbeheer", "97252", 3),
    ],
}

VOOROPLEIDINGEN = ["VMBO-T", "VMBO-K", "VMBO-B", "HAVO", "MBO niveau 2", "MBO niveau 3"]
COHORTEN = ["2022-2023", "2023-2024", "2024-2025"]
LEERWEGEN = ["BOL", "BBL"]
GESLACHTEN = ["M", "V", "X"]
MENTOREN = [
    ("Jan de Vries",    "j.devries@roc.nl"),
    ("Fatima El Amrani","f.elamrani@roc.nl"),
    ("Peter Smit",      "p.smit@roc.nl"),
    ("Anita Jansen",    "a.jansen@roc.nl"),
    ("Mohammed Boukhari","m.boukhari@roc.nl"),
]

def _genereer_student(idx: int, cohort: str) -> dict:
    sector = rng.choice(list(SECTOREN.keys()))
    opleiding, crebo, niveau = SECTOREN[sector][rng.integers(len(SECTOREN[sector]))]
    leerweg = rng.choice(LEERWEGEN, p=[0.75, 0.25])
    leeftijd = int(rng.normal(20, 3).clip(16, 35))
    vooropleiding = rng.choice(VOOROPLEIDINGEN)
    geslacht = rng.choice(GESLACHTEN, p=[0.48, 0.48, 0.04])
    mentor = MENTOREN[rng.integers(len(MENTOREN))]

    if geslacht == "M":
        naam = fake.name_male()
    elif geslacht == "V":
        naam = fake.name_female()
    else:
        naam = fake.name()

    # Basis aanwezigheid: beta-distributie
    aanwezigheid = float(rng.beta(5, 2).clip(0.0, 1.0))
    # Voortgang correlated met aanwezigheid
    voortgang = float((aanwezigheid * 0.6 + rng.beta(4, 2) * 0.4).clip(0.0, 1.0))
    # BSA-punten: max 60, correlated met voortgang
    bsa_studiepunten = int((voortgang * 45 + rng.normal(8, 5)).clip(0, 60))
    # Cijfers: normaal verdeeld, licht gecorreleerd met voortgang
    cijfer_nl = float((rng.normal(6.3, 1.2) + voortgang * 0.5).clip(1.0, 10.0))
    cijfer_re = float((rng.normal(6.0, 1.4) + voortgang * 0.4).clip(1.0, 10.0))

    jaar = int(cohort[:4])
    intakedatum = date(jaar, 9, 1)

    fn, ln = naam.split(" ", 1) if " " in naam else (naam, "")
    email = f"{fn[0].lower()}.{ln.lower().replace(' ', '')}@student.roc.nl"

    return {
        "studentnummer": f"{jaar}{idx:04d}",
        "naam": naam,
        "email": email,
        "leeftijd": leeftijd,
        "geslacht": geslacht,
        "vooropleiding": vooropleiding,
        "sector": sector,
        "opleiding": opleiding,
        "crebocode": crebo,
        "cohort": cohort,
        "niveau": int(niveau),
        "leerweg": str(leerweg),
        "intakedatum": intakedatum,
        "aanwezigheid": round(aanwezigheid, 3),
        "voortgang": round(voortgang, 3),
        "bsa_studiepunten": bsa_studiepunten,
        "cijfer_nederlands": round(cijfer_nl, 1),
        "cijfer_rekenen": round(cijfer_re, 1),
        "mentor_naam": mentor[0],
        "mentor_email": mentor[1],
    }

def genereer_actieve_studenten(n: int = 1000) -> pd.DataFrame:
    cohort = "2024-2025"
    rows = [_genereer_student(i + 1, cohort) for i in range(n)]
    return pd.DataFrame(rows)

def genereer_historische_studenten(n: int = 10000) -> pd.DataFrame:
    rows = []
    for i in range(n):
        cohort = rng.choice(COHORTEN[:2])  # alleen afgesloten cohorten
        student = _genereer_student(i + 1, cohort)
        # Uitval kans: hoog als aanwezigheid + cijfers laag zijn
        uitval_score = (
            (1 - student["aanwezigheid"]) * 0.40
            + (1 - student["voortgang"]) * 0.30
            + max(0, (5.5 - student["cijfer_rekenen"]) / 5.5) * 0.15
            + max(0, (5.5 - student["cijfer_nederlands"]) / 5.5) * 0.15
        )
        uitval_kans = float((uitval_score + rng.normal(0, 0.08)).clip(0.0, 1.0))
        student["uitgevallen"] = bool(uitval_kans >= 0.40)
        rows.append(student)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    print("Genereer 1.000 actieve studenten...")
    actief = genereer_actieve_studenten(1000)
    actief.to_csv(f"{data_dir}/actieve_studenten.csv", index=False)

    print("Genereer 10.000 historische studenten...")
    hist = genereer_historische_studenten(10000)
    hist.to_csv(f"{data_dir}/historische_studenten.csv", index=False)

    print(f"Klaar. Uitvalpercentage historisch: {hist['uitgevallen'].mean():.1%}")
```

- [ ] **Stap 4: Run tests — verwacht PASS**

```bash
cd edupulse && uv run pytest tests/test_generate_data.py -v
```

Verwacht: 6 tests PASSED

- [ ] **Stap 5: Genereer CSV-bestanden**

```bash
cd edupulse && uv run python backend/ml/generate_data.py
```

Verwacht:
```
Genereer 1.000 actieve studenten...
Genereer 10.000 historische studenten...
Klaar. Uitvalpercentage historisch: ~18-22%
```

- [ ] **Stap 6: Commit**

```bash
git add edupulse/backend/ml/generate_data.py edupulse/tests/test_generate_data.py
git commit -m "feat(edupulse): synthetische data generatie (1k actief + 10k historisch)"
```

---

## Task 4: ML model — trainen en voorspellen

**Files:**
- Create: `edupulse/backend/ml/train.py`
- Create: `edupulse/backend/ml/predict.py`
- Create: `edupulse/tests/test_predict.py`

- [ ] **Stap 1: Schrijf de failing tests**

```python
# edupulse/tests/test_predict.py
import pytest
import os
import pandas as pd
from backend.ml.train import train_model
from backend.ml.predict import RisicoPredictor

@pytest.fixture(scope="module")
def getraind_model(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("model")
    model_path = str(tmp / "model.pkl")
    feature_path = str(tmp / "features.json")
    from backend.ml.generate_data import genereer_historische_studenten
    df = genereer_historische_studenten(n=500)
    metrics = train_model(df, model_path=model_path, feature_path=feature_path)
    return model_path, feature_path, metrics

def test_model_accuracy_boven_drempel(getraind_model):
    _, _, metrics = getraind_model
    assert metrics["accuracy"] >= 0.60, f"Accuracy {metrics['accuracy']:.2f} te laag"

def test_voorspelling_retourneert_kans(getraind_model):
    model_path, feature_path, _ = getraind_model
    predictor = RisicoPredictor(model_path=model_path, feature_path=feature_path)
    student = {
        "aanwezigheid": 0.45, "voortgang": 0.40, "bsa_studiepunten": 20,
        "cijfer_nederlands": 5.0, "cijfer_rekenen": 4.5,
        "leeftijd": 19, "niveau": 3, "leerweg": "BOL",
        "sector": "Techniek", "vooropleiding": "VMBO-T"
    }
    result = predictor.predict(student)
    assert 0.0 <= result["kans"] <= 1.0
    assert len(result["shap_top3"]) == 3

def test_hoge_aanwezigheid_geeft_lager_risico(getraind_model):
    model_path, feature_path, _ = getraind_model
    predictor = RisicoPredictor(model_path=model_path, feature_path=feature_path)
    basis = {"aanwezigheid": 0.95, "voortgang": 0.90, "bsa_studiepunten": 55,
             "cijfer_nederlands": 8.0, "cijfer_rekenen": 7.5,
             "leeftijd": 19, "niveau": 4, "leerweg": "BOL",
             "sector": "Economie", "vooropleiding": "HAVO"}
    laag_risico = {"aanwezigheid": 0.30, "voortgang": 0.25, "bsa_studiepunten": 10,
                   "cijfer_nederlands": 4.5, "cijfer_rekenen": 4.0,
                   "leeftijd": 19, "niveau": 4, "leerweg": "BOL",
                   "sector": "Economie", "vooropleiding": "HAVO"}
    assert predictor.predict(basis)["kans"] < predictor.predict(laag_risico)["kans"]
```

- [ ] **Stap 2: Run test — verwacht FAIL**

```bash
cd edupulse && uv run pytest tests/test_predict.py -v
```

Verwacht: `ImportError: cannot import name 'train_model'`

- [ ] **Stap 3: Schrijf train.py**

```python
# edupulse/backend/ml/train.py
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

CATEGORISCHE_FEATURES = ["leerweg", "sector", "vooropleiding"]
NUMERIEKE_FEATURES = [
    "aanwezigheid", "voortgang", "bsa_studiepunten",
    "cijfer_nederlands", "cijfer_rekenen", "leeftijd", "niveau"
]
ALLE_FEATURES = NUMERIEKE_FEATURES + CATEGORISCHE_FEATURES

def _encode(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = df.copy()
    encoders = {}
    for col in CATEGORISCHE_FEATURES:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    return df, encoders

def train_model(
    df: pd.DataFrame,
    model_path: str = "data/model.pkl",
    feature_path: str = "data/feature_list.json"
) -> dict:
    df_enc, encoders = _encode(df)
    X = df_enc[ALLE_FEATURES].fillna(df_enc[ALLE_FEATURES].median(numeric_only=True))
    y = df_enc["uitgevallen"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rf = GridSearchCV(
        RandomForestClassifier(random_state=42),
        {"n_estimators": [100, 200], "max_depth": [5, 10]},
        cv=3, scoring="accuracy", n_jobs=-1
    )
    xgb = GridSearchCV(
        XGBClassifier(random_state=42, eval_metric="logloss", verbosity=0),
        {"n_estimators": [100, 200], "max_depth": [3, 5], "learning_rate": [0.1, 0.05]},
        cv=3, scoring="accuracy", n_jobs=-1
    )

    rf.fit(X_train, y_train)
    xgb.fit(X_train, y_train)

    rf_acc = accuracy_score(y_test, rf.predict(X_test))
    xgb_acc = accuracy_score(y_test, xgb.predict(X_test))

    best_model = xgb.best_estimator_ if xgb_acc >= rf_acc else rf.best_estimator_
    best_acc = max(xgb_acc, rf_acc)
    model_naam = "XGBoost" if xgb_acc >= rf_acc else "RandomForest"

    joblib.dump({"model": best_model, "encoders": encoders}, model_path)
    with open(feature_path, "w") as f:
        json.dump({"features": ALLE_FEATURES, "categorisch": CATEGORISCHE_FEATURES}, f)

    print(f"Beste model: {model_naam} | Accuracy: {best_acc:.3f}")
    return {"accuracy": best_acc, "model_naam": model_naam}

if __name__ == "__main__":
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    df = pd.read_csv(f"{data_dir}/historische_studenten.csv")
    df["intakedatum"] = pd.to_datetime(df["intakedatum"])
    train_model(df, model_path=f"{data_dir}/model.pkl", feature_path=f"{data_dir}/feature_list.json")
```

- [ ] **Stap 4: Schrijf predict.py**

```python
# edupulse/backend/ml/predict.py
import json
import joblib
import numpy as np
import pandas as pd
import shap

DREMPEL = 0.35  # >= 35% kans = dreiging

class RisicoPredictor:
    def __init__(
        self,
        model_path: str = "data/model.pkl",
        feature_path: str = "data/feature_list.json"
    ):
        artefact = joblib.load(model_path)
        self.model = artefact["model"]
        self.encoders = artefact["encoders"]
        with open(feature_path) as f:
            meta = json.load(f)
        self.features = meta["features"]
        self.categorisch = meta["categorisch"]
        self.explainer = shap.TreeExplainer(self.model)

    def _prep(self, student: dict) -> pd.DataFrame:
        row = {f: student.get(f) for f in self.features}
        df = pd.DataFrame([row])
        for col in self.categorisch:
            le = self.encoders[col]
            val = str(df[col].iloc[0])
            if val in le.classes_:
                df[col] = le.transform([val])
            else:
                df[col] = 0
        return df.fillna(0)

    def predict(self, student: dict) -> dict:
        df = self._prep(student)
        kans = float(self.model.predict_proba(df)[0][1])

        shap_values = self.explainer.shap_values(df)
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]

        top_idx = np.argsort(np.abs(sv))[::-1][:3]
        shap_top3 = [
            {"feature": self.features[i], "bijdrage": round(float(sv[i]), 4)}
            for i in top_idx
        ]

        return {"kans": round(kans, 4), "shap_top3": shap_top3}
```

- [ ] **Stap 5: Run tests — verwacht PASS**

```bash
cd edupulse && uv run pytest tests/test_predict.py -v
```

Verwacht: 3 tests PASSED (kan ~15-20s duren door GridSearchCV)

- [ ] **Stap 6: Train model op volledige 10k dataset**

```bash
cd edupulse && uv run python backend/ml/train.py
```

Verwacht:
```
Beste model: XGBoost | Accuracy: 0.xxx
```

- [ ] **Stap 7: Commit**

```bash
git add edupulse/backend/ml/train.py edupulse/backend/ml/predict.py edupulse/tests/test_predict.py
git commit -m "feat(edupulse): ML model — GridSearchCV XGBoost/RF + SHAP uitlegbaarheid"
```

---

## Task 5: Database seeding

**Files:**
- Create: `edupulse/backend/seed.py`

- [ ] **Stap 1: Schrijf seed.py**

```python
# edupulse/backend/seed.py
"""Vul de SQLite database met synthetische studenten."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import date
from backend.database import engine, Base, SessionLocal
from backend.models import StudentDB, HistorischStudentDB
from backend.ml.generate_data import genereer_actieve_studenten, genereer_historische_studenten

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(StudentDB).count() == 0:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        csv = os.path.join(data_dir, "actieve_studenten.csv")
        if not os.path.exists(csv):
            print("CSV niet gevonden, genereer data...")
            df = genereer_actieve_studenten(1000)
            df.to_csv(csv, index=False)
        else:
            df = pd.read_csv(csv)

        df["intakedatum"] = pd.to_datetime(df["intakedatum"]).dt.date
        records = df.to_dict("records")
        db.bulk_insert_mappings(StudentDB, records)
        db.commit()
        print(f"{len(records)} actieve studenten ingevoegd.")
    else:
        print("Database al gevuld — overgeslagen.")

    db.close()

if __name__ == "__main__":
    seed()
```

- [ ] **Stap 2: Run seeder**

```bash
cd edupulse && uv run python backend/seed.py
```

Verwacht: `1000 actieve studenten ingevoegd.`

- [ ] **Stap 3: Commit**

```bash
git add edupulse/backend/seed.py
git commit -m "feat(edupulse): database seeding — 1000 actieve studenten"
```

---

## Task 6: LLMProvider abstractie

**Files:**
- Create: `edupulse/backend/agent/llm.py`

- [ ] **Stap 1: Schrijf llm.py**

```python
# edupulse/backend/agent/llm.py
from abc import ABC, abstractmethod
from typing import Any
import anthropic

class LLMProvider(ABC):
    """Model-agnostische interface — swap Claude voor Ollama/lokaal zonder agent-logica te wijzigen."""

    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict], system: str) -> Any:
        ...

class ClaudeLLMProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic()
        self.model = model

    def chat(self, messages: list[dict], tools: list[dict], system: str) -> Any:
        return self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            tools=tools if tools else anthropic.NOT_GIVEN,
            messages=messages,
        )
```

- [ ] **Stap 2: Commit**

```bash
git add edupulse/backend/agent/llm.py
git commit -m "feat(edupulse): LLMProvider abstractie — Claude + model-agnostische interface"
```

---

## Task 7: Agent tools

**Files:**
- Create: `edupulse/backend/agent/tools.py`
- Create: `edupulse/tests/test_tools.py`

- [ ] **Stap 1: Schrijf de failing tests**

```python
# edupulse/tests/test_tools.py
import pytest
from unittest.mock import MagicMock
from backend.agent.tools import ToolRegistry
from backend.models import StudentDB

@pytest.fixture
def mock_student():
    s = MagicMock(spec=StudentDB)
    s.studentnummer = "20240001"
    s.naam = "Test Student"
    s.email = "t.student@roc.nl"
    s.leeftijd = 20
    s.geslacht = "M"
    s.vooropleiding = "VMBO-T"
    s.sector = "Techniek"
    s.opleiding = "Software Developer"
    s.crebocode = "25604"
    s.cohort = "2024-2025"
    s.niveau = 4
    s.leerweg = "BOL"
    s.intakedatum = "2024-09-01"
    s.aanwezigheid = 0.52
    s.voortgang = 0.61
    s.bsa_studiepunten = 34
    s.cijfer_nederlands = 6.2
    s.cijfer_rekenen = 5.8
    s.mentor_naam = "Jan de Vries"
    s.mentor_email = "j.devries@roc.nl"
    return s

@pytest.fixture
def registry(mock_student):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = mock_student
    db.query.return_value.all.return_value = [mock_student]
    predictor = MagicMock()
    predictor.predict.return_value = {
        "kans": 0.42,
        "shap_top3": [
            {"feature": "aanwezigheid", "bijdrage": -0.25},
            {"feature": "voortgang", "bijdrage": -0.15},
            {"feature": "cijfer_rekenen", "bijdrage": -0.08},
        ]
    }
    return ToolRegistry(db=db, predictor=predictor)

def test_get_student_data_geeft_profiel(registry):
    result = registry.get_student_data("20240001")
    assert result["studentnummer"] == "20240001"
    assert result["naam"] == "Test Student"

def test_predict_dropout_risk_geeft_kans(registry):
    result = registry.predict_dropout_risk("20240001")
    assert "uitval_kans" in result
    assert result["status"] == "dreiging"
    assert len(result["shap_top3"]) == 3

def test_get_mentor_info(registry):
    result = registry.get_mentor_info("20240001")
    assert result["mentor_naam"] == "Jan de Vries"
    assert result["mentor_email"] == "j.devries@roc.nl"

def test_student_niet_gevonden(registry):
    registry.db.query.return_value.filter_by.return_value.first.return_value = None
    result = registry.get_student_data("99999")
    assert "error" in result

def test_tool_handlers_volledig(registry):
    handlers = registry.get_handlers()
    for naam in ["get_student_data", "predict_dropout_risk",
                 "get_cohort_comparison", "get_mentor_info", "search_students"]:
        assert naam in handlers
```

- [ ] **Stap 2: Run test — verwacht FAIL**

```bash
cd edupulse && uv run pytest tests/test_tools.py -v
```

Verwacht: `ImportError: cannot import name 'ToolRegistry'`

- [ ] **Stap 3: Schrijf tools.py**

```python
# edupulse/backend/agent/tools.py
from backend.models import StudentDB, StudentSchema
from backend.ml.predict import RisicoPredictor, DREMPEL

TOOL_DEFINITIONS = [
    {
        "name": "get_student_data",
        "description": "Haal het volledige profiel op van een student op basis van studentnummer of naam.",
        "input_schema": {
            "type": "object",
            "properties": {
                "studentnummer": {"type": "string", "description": "Het studentnummer (bijv. '20240001')"}
            },
            "required": ["studentnummer"]
        }
    },
    {
        "name": "predict_dropout_risk",
        "description": "Bereken het uitvalrisico voor een student en geef de top-3 beïnvloedende factoren.",
        "input_schema": {
            "type": "object",
            "properties": {
                "studentnummer": {"type": "string"}
            },
            "required": ["studentnummer"]
        }
    },
    {
        "name": "get_cohort_comparison",
        "description": "Vergelijk de student met het gemiddelde van zijn/haar cohort en opleiding.",
        "input_schema": {
            "type": "object",
            "properties": {
                "studentnummer": {"type": "string"}
            },
            "required": ["studentnummer"]
        }
    },
    {
        "name": "get_mentor_info",
        "description": "Geef naam en e-mail van de mentor van een student.",
        "input_schema": {
            "type": "object",
            "properties": {
                "studentnummer": {"type": "string"}
            },
            "required": ["studentnummer"]
        }
    },
    {
        "name": "search_students",
        "description": "Zoek studenten op naam of gedeeltelijk studentnummer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Naam of (deel van) studentnummer"}
            },
            "required": ["query"]
        }
    },
]

class ToolRegistry:
    def __init__(self, db, predictor: RisicoPredictor):
        self.db = db
        self.predictor = predictor

    def _student_of_fout(self, studentnummer: str):
        student = self.db.query(StudentDB).filter_by(studentnummer=studentnummer).first()
        if not student:
            return None, {"error": f"Student {studentnummer!r} niet gevonden."}
        return student, None

    def get_student_data(self, studentnummer: str) -> dict:
        student, err = self._student_of_fout(studentnummer)
        if err:
            return err
        return StudentSchema.model_validate(student).model_dump(mode="json")

    def predict_dropout_risk(self, studentnummer: str) -> dict:
        student, err = self._student_of_fout(studentnummer)
        if err:
            return err
        data = StudentSchema.model_validate(student).model_dump()
        result = self.predictor.predict(data)
        return {
            "studentnummer": studentnummer,
            "naam": student.naam,
            "uitval_kans": result["kans"],
            "succes_kans": round(1 - result["kans"], 4),
            "status": "dreiging" if result["kans"] >= DREMPEL else "op_koers",
            "shap_top3": result["shap_top3"],
        }

    def get_cohort_comparison(self, studentnummer: str) -> dict:
        student, err = self._student_of_fout(studentnummer)
        if err:
            return err
        cohortgenoten = (
            self.db.query(StudentDB)
            .filter_by(opleiding=student.opleiding, cohort=student.cohort)
            .all()
        )
        if not cohortgenoten:
            return {"error": "Geen cohortgenoten gevonden."}
        gem_aanw = round(sum(s.aanwezigheid for s in cohortgenoten) / len(cohortgenoten), 3)
        gem_voortgang = round(sum(s.voortgang for s in cohortgenoten) / len(cohortgenoten), 3)
        gem_bsa = round(sum(s.bsa_studiepunten for s in cohortgenoten) / len(cohortgenoten), 1)
        return {
            "opleiding": student.opleiding,
            "cohort": student.cohort,
            "aantal_cohortgenoten": len(cohortgenoten),
            "student": {
                "aanwezigheid": student.aanwezigheid,
                "voortgang": student.voortgang,
                "bsa_studiepunten": student.bsa_studiepunten,
            },
            "cohortgemiddelde": {
                "aanwezigheid": gem_aanw,
                "voortgang": gem_voortgang,
                "bsa_studiepunten": gem_bsa,
            },
        }

    def get_mentor_info(self, studentnummer: str) -> dict:
        student, err = self._student_of_fout(studentnummer)
        if err:
            return err
        return {
            "mentor_naam": student.mentor_naam,
            "mentor_email": student.mentor_email,
            "student_naam": student.naam,
            "student_email": student.email,
        }

    def search_students(self, query: str) -> list[dict]:
        alle = self.db.query(StudentDB).all()
        q = query.lower()
        treffer = [
            s for s in alle
            if q in s.naam.lower() or q in s.studentnummer.lower()
        ][:10]
        return [
            {"studentnummer": s.studentnummer, "naam": s.naam,
             "opleiding": s.opleiding, "cohort": s.cohort}
            for s in treffer
        ]

    def get_handlers(self) -> dict:
        return {
            "get_student_data": self.get_student_data,
            "predict_dropout_risk": self.predict_dropout_risk,
            "get_cohort_comparison": self.get_cohort_comparison,
            "get_mentor_info": self.get_mentor_info,
            "search_students": self.search_students,
        }
```

- [ ] **Stap 4: Run tests — verwacht PASS**

```bash
cd edupulse && uv run pytest tests/test_tools.py -v
```

Verwacht: 5 tests PASSED

- [ ] **Stap 5: Commit**

```bash
git add edupulse/backend/agent/tools.py edupulse/tests/test_tools.py
git commit -m "feat(edupulse): agent tools — ToolRegistry met 5 geregistreerde tools"
```

---

## Task 8: Harness + Agent kernel

**Files:**
- Create: `edupulse/backend/agent/harness.py`
- Create: `edupulse/backend/agent/kernel.py`

- [ ] **Stap 1: Schrijf harness.py**

```python
# edupulse/backend/agent/harness.py
import hashlib
import time
from collections import defaultdict
from datetime import datetime
from backend.models import AgentLogDB

MAX_CALLS_PER_SESSIE = 60

class Harness:
    """
    Governance wrapper om agent tool-calls:
    - Whitelist: alleen geregistreerde tools
    - Rate limiting per sessie
    - Logging naar agent_log tabel (PII gehashed)
    """

    def __init__(self, handlers: dict, db):
        self.handlers = handlers
        self.db = db
        self._teller: dict[str, int] = defaultdict(int)

    def execute(self, tool_naam: str, inputs: dict, sessie_id: str) -> dict:
        if tool_naam not in self.handlers:
            return {"error": f"Tool '{tool_naam}' staat niet op de whitelist."}

        if self._teller[sessie_id] >= MAX_CALLS_PER_SESSIE:
            return {"error": "Rate limit bereikt voor deze sessie."}

        start = time.monotonic()
        self._teller[sessie_id] += 1

        try:
            result = self.handlers[tool_naam](**inputs)
        except Exception as e:
            result = {"error": str(e)}

        duur_ms = int((time.monotonic() - start) * 1000)
        self._log(tool_naam, inputs, result, sessie_id, duur_ms)
        return result

    def _hash_pii(self, tekst: str) -> str:
        return hashlib.sha256(tekst.encode()).hexdigest()[:12]

    def _log(self, tool_naam: str, inputs: dict, result: dict,
             sessie_id: str, duur_ms: int):
        input_str = str(inputs)
        input_hash = self._hash_pii(input_str)
        output_summary = str(result)[:200]
        try:
            log = AgentLogDB(
                timestamp=datetime.utcnow(),
                sessie_id=sessie_id,
                gebruiker="system",
                tool_naam=tool_naam,
                input_hash=input_hash,
                output_summary=output_summary,
                duur_ms=duur_ms,
            )
            self.db.add(log)
            self.db.commit()
        except Exception:
            pass
```

- [ ] **Stap 2: Schrijf kernel.py**

```python
# edupulse/backend/agent/kernel.py
import uuid
from backend.agent.llm import LLMProvider
from backend.agent.harness import Harness
from backend.agent.tools import TOOL_DEFINITIONS

MAX_STAPPEN = 10

SYSTEM_PROMPT = """Je bent EduAgent, een harnessed digitale assistent voor MBO begeleiders.

Je helpt begeleiders inzicht te geven in het uitvalrisico van studenten.
Je gebruikt alleen de beschikbare tools om studentdata op te halen — verzin niets.
Geef altijd een concrete, begrijpelijke uitleg in het Nederlands.
Vermeld bij dreiging altijd de mentor-contactgegevens.
Sluit af met een concreet advies.

Beperkingen:
- Gebruik alleen de aangeboden tools
- Houd rekening met privacy (AVG): deel nooit onnodige persoonsgegevens
- Reageer in het Nederlands"""

class AgentKernel:
    def __init__(self, llm: LLMProvider, harness: Harness):
        self.llm = llm
        self.harness = harness

    def run(self, user_message: str, sessie_id: str | None = None) -> str:
        if sessie_id is None:
            sessie_id = str(uuid.uuid4())

        messages = [{"role": "user", "content": user_message}]

        for _ in range(MAX_STAPPEN):
            response = self.llm.chat(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                system=SYSTEM_PROMPT,
            )

            if response.stop_reason == "end_turn":
                tekst = next(
                    (b.text for b in response.content if hasattr(b, "text")),
                    "Geen antwoord ontvangen."
                )
                return tekst

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self.harness.execute(
                            block.name, block.input, sessie_id
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })

                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

        return "Maximale stappen bereikt. Probeer een specifiekere vraag."
```

- [ ] **Stap 3: Commit**

```bash
git add edupulse/backend/agent/harness.py edupulse/backend/agent/kernel.py
git commit -m "feat(edupulse): agent harness + kernel — tool-use loop met governance"
```

---

## Task 9: FastAPI backend

**Files:**
- Create: `edupulse/backend/main.py`
- Create: `edupulse/tests/test_api.py`

- [ ] **Stap 1: Schrijf de failing tests**

```python
# edupulse/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="module")
def client():
    with patch("backend.agent.kernel.AgentKernel.run", return_value="Test antwoord van agent."):
        from backend.main import app
        return TestClient(app)

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_list_students(client):
    r = client.get("/students?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_get_student_bestaat(client):
    studenten = client.get("/students?limit=1").json()
    if studenten:
        nr = studenten[0]["studentnummer"]
        r = client.get(f"/students/{nr}")
        assert r.status_code == 200
        assert r.json()["studentnummer"] == nr

def test_get_student_niet_gevonden(client):
    r = client.get("/students/BESTAATNIET")
    assert r.status_code == 404

def test_risk_endpoint(client):
    studenten = client.get("/students?limit=1").json()
    if studenten:
        nr = studenten[0]["studentnummer"]
        r = client.get(f"/risk/{nr}")
        assert r.status_code == 200
        assert "uitval_kans" in r.json()

def test_agent_chat(client):
    r = client.post("/agent/chat", json={"message": "Hoe staat student 20240001 ervoor?"})
    assert r.status_code == 200
    assert "response" in r.json()
    assert "session_id" in r.json()
```

- [ ] **Stap 2: Run test — verwacht FAIL**

```bash
cd edupulse && uv run pytest tests/test_api.py -v
```

Verwacht: `ImportError: cannot import name 'app'`

- [ ] **Stap 3: Schrijf main.py**

```python
# edupulse/backend/main.py
import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import get_db, engine, Base
from backend.models import StudentDB, StudentSchema, ChatRequest, ChatResponse, RisicoPredictie
from backend.agent.llm import ClaudeLLMProvider
from backend.agent.tools import ToolRegistry
from backend.agent.harness import Harness
from backend.agent.kernel import AgentKernel
from backend.ml.predict import RisicoPredictor

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")
FEATURE_PATH = os.path.join(DATA_DIR, "feature_list.json")

predictor: RisicoPredictor | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    Base.metadata.create_all(bind=engine)
    if os.path.exists(MODEL_PATH):
        predictor = RisicoPredictor(model_path=MODEL_PATH, feature_path=FEATURE_PATH)
    yield

app = FastAPI(title="EduPulse API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8503", "http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _get_kernel(db: Session = Depends(get_db)) -> AgentKernel:
    if predictor is None:
        raise HTTPException(503, "Model nog niet geladen — run train.py eerst.")
    registry = ToolRegistry(db=db, predictor=predictor)
    harness = Harness(handlers=registry.get_handlers(), db=db)
    llm = ClaudeLLMProvider()
    return AgentKernel(llm=llm, harness=harness)

@app.get("/health")
def health():
    return {"status": "ok", "model_geladen": predictor is not None}

@app.get("/students", response_model=list[StudentSchema])
def list_students(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(StudentDB).offset(skip).limit(limit).all()

@app.get("/students/{studentnummer}", response_model=StudentSchema)
def get_student(studentnummer: str, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter_by(studentnummer=studentnummer).first()
    if not student:
        raise HTTPException(404, f"Student {studentnummer!r} niet gevonden.")
    return student

@app.get("/risk/{studentnummer}", response_model=RisicoPredictie)
def get_risk(studentnummer: str, db: Session = Depends(get_db)):
    if predictor is None:
        raise HTTPException(503, "Model niet geladen.")
    student = db.query(StudentDB).filter_by(studentnummer=studentnummer).first()
    if not student:
        raise HTTPException(404, f"Student {studentnummer!r} niet gevonden.")
    data = StudentSchema.model_validate(student).model_dump()
    result = predictor.predict(data)
    from backend.ml.predict import DREMPEL
    return RisicoPredictie(
        studentnummer=studentnummer,
        uitval_kans=result["kans"],
        succes_kans=round(1 - result["kans"], 4),
        status="dreiging" if result["kans"] >= DREMPEL else "op_koers",
        shap_top3=result["shap_top3"],
    )

@app.post("/agent/chat", response_model=ChatResponse)
def agent_chat(request: ChatRequest, kernel: AgentKernel = Depends(_get_kernel)):
    sessie_id = request.session_id or str(uuid.uuid4())
    antwoord = kernel.run(request.message, sessie_id=sessie_id)
    return ChatResponse(session_id=sessie_id, response=antwoord)
```

- [ ] **Stap 4: Run tests — verwacht PASS**

```bash
cd edupulse && uv run pytest tests/test_api.py -v
```

Verwacht: 6 tests PASSED

- [ ] **Stap 5: Start API handmatig om te verifiëren**

```bash
cd edupulse && uv run uvicorn backend.main:app --port 8001 --reload
```

Open: `http://localhost:8001/health` → `{"status":"ok","model_geladen":true}`
Open: `http://localhost:8001/docs` → Swagger UI

Stop met Ctrl+C.

- [ ] **Stap 6: Commit**

```bash
git add edupulse/backend/main.py edupulse/tests/test_api.py
git commit -m "feat(edupulse): FastAPI backend — endpoints voor studenten, risico en agent-chat"
```

---

## Task 10: Streamlit frontend

**Files:**
- Create: `edupulse/frontend/app.py`
- Create: `edupulse/frontend/pages/uitvalrisico.py`
- Create: `edupulse/frontend/pages/geschiedenis.py`

- [ ] **Stap 1: Schrijf app.py (entry point + CEDA huisstijl)**

```python
# edupulse/frontend/app.py
import streamlit as st

st.set_page_config(
    page_title="EduPulse — Uitvalrisico",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CEDA huisstijl (conform HTML-mockup tokens)
st.markdown("""
<style>
  :root {
    --oranje: #DD784B;
    --blauw:  #3D68EC;
    --groen:  #00AF81;
    --geel:   #F4D74B;
    --roze:   #F4D9DC;
    --zwart:  #000000;
    --bg:     #F0F1F3;
  }
  .stApp { background: var(--bg); }
  [data-testid="stSidebar"] { background: var(--zwart) !important; }
  [data-testid="stSidebar"] * { color: white !important; }
  .stButton > button {
    background: var(--oranje) !important;
    color: white !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 10px !important;
  }
  .stButton > button:hover {
    background: #c5683e !important;
    transform: translateY(-1px);
  }
  .metric-card {
    background: white; border-radius: 14px;
    padding: 20px; box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  }
  .dreiging { color: #DD784B; font-weight: 800; }
  .opkoers  { color: #00AF81; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# Topbalk
st.markdown("""
<div style="background:#000;padding:12px 28px;display:flex;align-items:center;gap:10px;margin-bottom:24px;">
  <span style="color:#DD784B;font-size:1.3rem;">◉</span>
  <span style="color:white;font-weight:700;">Npuls</span>
  <div style="width:1px;height:20px;background:rgba(255,255,255,0.2);margin:0 4px;"></div>
  <span style="color:white;font-weight:800;">Edu<span style="color:#F4D74B;">Pulse</span></span>
  <span style="color:#DD784B;font-size:0.6rem;font-weight:700;letter-spacing:0.09em;text-transform:uppercase;">
    Moving Education.
  </span>
</div>
""", unsafe_allow_html=True)

paginas = [
    st.Page("pages/uitvalrisico.py", title="Uitvalrisico check", icon="🎯"),
    st.Page("pages/geschiedenis.py", title="Eerdere berekeningen", icon="📋"),
]
nav = st.navigation(paginas)
nav.run()
```

- [ ] **Stap 2: Schrijf pages/uitvalrisico.py**

```python
# edupulse/frontend/pages/uitvalrisico.py
import requests
import streamlit as st

API = "http://localhost:8001"

st.title("Uitvalrisico check")
st.caption("Stel een vraag over een student of zoek een student op.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "sessie_id" not in st.session_state:
    st.session_state.sessie_id = None
if "geselecteerde_student" not in st.session_state:
    st.session_state.geselecteerde_student = None

# Sidebar: student zoeken
with st.sidebar:
    st.subheader("Student zoeken")
    zoek = st.text_input("Naam of studentnummer", placeholder="Bijv. Youssef of 20240001")
    if zoek:
        try:
            studenten = requests.get(f"{API}/students?limit=100").json()
            q = zoek.lower()
            treffer = [
                s for s in studenten
                if q in s["naam"].lower() or q in s["studentnummer"]
            ][:8]
            for s in treffer:
                if st.button(f"{s['naam']} ({s['studentnummer']})", key=s["studentnummer"]):
                    st.session_state.geselecteerde_student = s["studentnummer"]
        except Exception:
            st.error("API niet bereikbaar. Start de backend eerst.")

# Student kaart
if st.session_state.geselecteerde_student:
    nr = st.session_state.geselecteerde_student
    try:
        student = requests.get(f"{API}/students/{nr}").json()
        risico = requests.get(f"{API}/risk/{nr}").json()

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"### {student['naam']}")
            st.caption(f"{student['opleiding']} · {student['cohort']} · {student['leerweg']}")
        with col2:
            kleur = "dreiging" if risico["status"] == "dreiging" else "opkoers"
            label = "⚠ Dreiging" if risico["status"] == "dreiging" else "✓ Op koers"
            st.markdown(f"""
            <div class='metric-card' style='text-align:center;'>
              <div style='font-size:0.7rem;color:#AAA;text-transform:uppercase;letter-spacing:0.08em;'>
                Succeskans
              </div>
              <div class='{kleur}' style='font-size:2.5rem;'>{risico['succes_kans']*100:.0f}%</div>
              <div class='{kleur}'>{label}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Aanwezigheid", f"{student['aanwezigheid']*100:.0f}%")
            st.metric("BSA punten", student['bsa_studiepunten'])
            st.markdown("</div>", unsafe_allow_html=True)

        # SHAP top-3
        st.markdown("**Top-3 beïnvloedende factoren:**")
        for item in risico["shap_top3"]:
            richting = "🔴" if item["bijdrage"] < 0 else "🟢"
            st.markdown(f"{richting} **{item['feature']}** — bijdrage: `{item['bijdrage']:.3f}`")

    except Exception as e:
        st.error(f"Fout bij laden studentdata: {e}")

st.divider()

# Agent dialoogvenster
st.subheader("Vraag aan de agent")
for msg in st.session_state.chat_history:
    with st.chat_message(msg["rol"]):
        st.markdown(msg["tekst"])

vraag = st.chat_input("Stel een vraag, bijv. 'Hoe staat Youssef ervoor?' of een studentnummer")
if vraag:
    st.session_state.chat_history.append({"rol": "user", "tekst": vraag})
    with st.chat_message("user"):
        st.markdown(vraag)

    with st.chat_message("assistant"):
        with st.spinner("Agent denkt na..."):
            try:
                r = requests.post(
                    f"{API}/agent/chat",
                    json={"message": vraag, "session_id": st.session_state.sessie_id},
                    timeout=60,
                )
                data = r.json()
                antwoord = data["response"]
                st.session_state.sessie_id = data["session_id"]
            except Exception as e:
                antwoord = f"Fout: {e}. Is de backend actief op poort 8001?"
        st.markdown(antwoord)
    st.session_state.chat_history.append({"rol": "assistant", "tekst": antwoord})
```

- [ ] **Stap 3: Schrijf pages/geschiedenis.py**

```python
# edupulse/frontend/pages/geschiedenis.py
import requests
import streamlit as st

API = "http://localhost:8001"

st.title("Eerdere berekeningen")
st.caption("Overzicht van alle studenten en hun uitvalrisico.")

try:
    studenten = requests.get(f"{API}/students?limit=1000").json()
except Exception:
    st.error("API niet bereikbaar. Start de backend eerst.")
    st.stop()

# Filters
col1, col2 = st.columns(2)
with col1:
    filter_status = st.selectbox("Filter op status", ["Alle", "Dreiging", "Op koers"])
with col2:
    filter_opleiding = st.selectbox(
        "Filter op opleiding",
        ["Alle"] + sorted(list({s["opleiding"] for s in studenten}))
    )

# Haal risico's op voor eerste 50 (performance sprint 1)
weergave = studenten[:50]
if filter_opleiding != "Alle":
    weergave = [s for s in weergave if s["opleiding"] == filter_opleiding]

risicos = []
for s in weergave:
    try:
        r = requests.get(f"{API}/risk/{s['studentnummer']}").json()
        risicos.append({**s, **r})
    except Exception:
        pass

if filter_status == "Dreiging":
    risicos = [r for r in risicos if r.get("status") == "dreiging"]
elif filter_status == "Op koers":
    risicos = [r for r in risicos if r.get("status") == "op_koers"]

# Samenvatting
if risicos:
    totaal = len(risicos)
    dreiging = sum(1 for r in risicos if r.get("status") == "dreiging")
    gem = sum(r.get("succes_kans", 0) for r in risicos) / totaal

    c1, c2, c3 = st.columns(3)
    c1.metric("Studenten", totaal)
    c2.metric("⚠ Dreiging", dreiging)
    c3.metric("Gem. succeskans", f"{gem*100:.0f}%")

    st.divider()

    for r in sorted(risicos, key=lambda x: x.get("succes_kans", 1)):
        kleur = "🔴" if r.get("status") == "dreiging" else "🟢"
        label = f"⚠ Dreiging" if r.get("status") == "dreiging" else "✓ Op koers"
        with st.expander(
            f"{kleur} {r['naam']} ({r['studentnummer']}) — "
            f"{r.get('succes_kans', 0)*100:.0f}% succeskans — {label}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Opleiding:** {r['opleiding']}")
                st.write(f"**Cohort:** {r['cohort']}")
                st.write(f"**Aanwezigheid:** {r['aanwezigheid']*100:.0f}%")
                st.write(f"**BSA punten:** {r['bsa_studiepunten']}")
            with col2:
                st.write(f"**Nederlands:** {r['cijfer_nederlands']}")
                st.write(f"**Rekenen:** {r['cijfer_rekenen']}")
                st.write(f"**Mentor:** {r['mentor_naam']}")
                st.write(f"**Mentor email:** {r['mentor_email']}")
else:
    st.info("Geen studenten gevonden voor dit filter.")
```

- [ ] **Stap 4: Commit**

```bash
git add edupulse/frontend/app.py edupulse/frontend/pages/uitvalrisico.py edupulse/frontend/pages/geschiedenis.py
git commit -m "feat(edupulse): Streamlit frontend — uitvalrisico check + geschiedenis pagina's"
```

---

## Task 11: Alle tests draaien + end-to-end verificatie

- [ ] **Stap 1: Voer alle tests uit**

```bash
cd edupulse && uv run pytest tests/ -v --tb=short
```

Verwacht: alle tests PASSED (test_api.py mock-based, rest echte database)

- [ ] **Stap 2: Start backend**

```bash
cd edupulse && uv run uvicorn backend.main:app --port 8001
```

(Laat draaien in terminal 1)

- [ ] **Stap 3: Start frontend**

```bash
cd edupulse && uv run streamlit run frontend/app.py --server.port 8503
```

(Laat draaien in terminal 2)

- [ ] **Stap 4: Manuele end-to-end test**

1. Open `http://localhost:8503`
2. Zoek een student in de sidebar
3. Controleer dat de succeskans en SHAP-factoren worden getoond
4. Typ in het chatvenster: *"Hoe staat deze student ervoor? Wat adviseert u?"*
5. Controleer dat de agent een beredeneerd antwoord geeft in het Nederlands
6. Navigeer naar "Eerdere berekeningen" en check de lijst

- [ ] **Stap 5: Sluit af met final commit**

```bash
cd edupulse && git add -A && git commit -m "feat(edupulse): sprint 1 complete — EduClaw harnessed agent voor uitvalrisico"
```
