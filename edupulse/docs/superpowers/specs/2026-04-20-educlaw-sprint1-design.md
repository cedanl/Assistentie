# EduClaw Sprint 1 — Ontwerp

**Datum:** 2026-04-20
**Project:** EduAgent Studio (EduClaw) — EduPulse subproject
**Doel:** Harnessed agentic uitvalrisico-check voor IR-medewerkers en begeleiders in het MBO

---

## 1. Projectstructuur

```
Assistentie/
└── edupulse/
    ├── pyproject.toml
    ├── backend/
    │   ├── main.py              ← FastAPI app
    │   ├── database.py          ← SQLAlchemy + SQLite
    │   ├── models.py            ← ORM + Pydantic schemas
    │   ├── agent/
    │   │   ├── kernel.py        ← agent orchestratie (Claude tool-use)
    │   │   ├── tools.py         ← tools: get_student, predict_risk, …
    │   │   ├── harness.py       ← governance: logging, rate-limit, AVG
    │   │   └── llm.py           ← LLMProvider abstractie (Claude → lokaal)
    │   └── ml/
    │       ├── generate_data.py ← synthetische data (1k + 10k studenten)
    │       ├── train.py         ← model trainen op 10k historische data
    │       └── predict.py       ← dropout-risico voorspellen
    ├── frontend/
    │   ├── app.py               ← Streamlit entry point
    │   └── pages/
    │       ├── uitvalrisico.py  ← hoofdscherm (conform HTML-mockup)
    │       └── geschiedenis.py  ← eerdere berekeningen
    └── data/
        ├── studenten.db         ← SQLite database
        └── model.pkl            ← getraind voorspelmodel
```

---

## 2. Database Schema

### Tabel: `studenten` (1.000 actieve studenten)

| Kolom | Type | Omschrijving |
|---|---|---|
| studentnummer | TEXT PK | Uniek studentnummer |
| naam | TEXT | Volledige naam |
| email | TEXT | Studentmail |
| leeftijd | INTEGER | Leeftijd in jaren |
| geslacht | TEXT | M/V/X |
| vooropleiding | TEXT | VMBO-T, HAVO, etc. |
| sector | TEXT | Techniek, Zorg, Economie, etc. |
| opleiding | TEXT | Naam opleiding |
| crebocode | TEXT | CREBO-code |
| cohort | TEXT | Bijv. "2024-2025" |
| niveau | INTEGER | MBO-niveau 1–4 |
| leerweg | TEXT | BOL/BBL |
| intakedatum | DATE | Datum eerste inschrijving |
| aanwezigheid | FLOAT | 0.0–1.0 |
| voortgang | FLOAT | 0.0–1.0 |
| bsa_studiepunten | INTEGER | Behaalde BSA-punten |
| cijfer_nederlands | FLOAT | 1.0–10.0 |
| cijfer_rekenen | FLOAT | 1.0–10.0 |
| mentor_naam | TEXT | Naam mentor |
| mentor_email | TEXT | E-mail mentor |

### Tabel: `historische_studenten` (10.000 studenten voor training)

Zelfde schema + extra kolom:

| uitgevallen | BOOLEAN | True = uitgevallen, False = geslaagd/actief |

### Tabel: `agent_log` (governance/AVG)

| Kolom | Type |
|---|---|
| id | INTEGER PK |
| timestamp | DATETIME |
| sessie_id | TEXT |
| gebruiker | TEXT |
| tool_naam | TEXT |
| input_hash | TEXT (geanonimiseerd) |
| output_summary | TEXT |
| duur_ms | INTEGER |

---

## 3. ML-model

- **Algoritme:** GridSearchCV vergelijkt RandomForest vs. XGBoost; beste model wordt opgeslagen
- **Target:** `uitgevallen` (binaire classificatie)
- **Features:** aanwezigheid, voortgang, bsa_studiepunten, cijfer_nederlands, cijfer_rekenen, leeftijd, niveau, leerweg, sector, vooropleiding
- **Preprocessing:** KNN-imputation + label-encoding voor categorische kolommen
- **Uitlegbaarheid:** SHAP-waarden per voorspelling (top-3 factoren)
- **Output:** `predict_dropout_risk(student) → {"kans": float, "shap": dict}`
- **Drempelwaarde:** ≥ 0.35 risico = "dreiging" (instelbaar in config)
- **Artefacten:** `model.pkl` + `feature_list.json`

---

## 4. Agent Kernel & Harness

### LLMProvider (`llm.py`)
Model-agnostische abstractie. Sprint 1: Claude Anthropic. Interface:
```python
class LLMProvider:
    def chat(self, messages, tools) → response
```
Straks uitwisselbaar voor Ollama, OpenEuroLLM, GPT-NL zonder aanpassing aan agent-logica.

### Agent tools (`tools.py`)
Geregistreerde tools die de agent mag aanroepen:

| Tool | Omschrijving |
|---|---|
| `get_student_data(studentnummer)` | Haalt volledig studentprofiel op uit SQLite |
| `predict_dropout_risk(studentnummer)` | Roept ML-model aan, retourneert kans + SHAP |
| `get_cohort_comparison(studentnummer)` | Vergelijkt student met cohortgemiddelden |
| `get_mentor_info(studentnummer)` | Haalt mentor + e-mail op |
| `search_students(query)` | Zoekt student op naam of studentnummer |

### Harness (`harness.py`)
- Elke tool-aanroep gelogd in `agent_log`
- Rate limiting: max 60 requests/minuut per sessie
- PII wordt gehashed in logs (naam, email)
- Alleen geregistreerde tools beschikbaar (whitelist)
- Maximale agent-stappen per vraag: 10

### Agent kernel (`kernel.py`)
- Ontvangt gebruikersvraag
- Stuurt naar LLMProvider met tool-definities
- Voert tool-calls uit via harness
- Retourneert beredeneerd antwoord + gebruikte tools

---

## 5. FastAPI Endpoints

| Method | Pad | Omschrijving |
|---|---|---|
| GET | `/students` | Lijst van studenten (gepagineerd) |
| GET | `/students/{id}` | Studentprofiel |
| POST | `/agent/chat` | Stel een vraag aan de agent |
| GET | `/agent/sessions/{id}` | Gesprekshistorie |
| GET | `/risk/{id}` | Directe risicoscore (zonder agent) |
| GET | `/health` | Healthcheck |

---

## 6. Streamlit Frontend

Drie schermen conform HTML-mockup (`index.html`), CEDA huisstijl:

### Scherm 1: Uitvalrisico check
- Student zoeken (naam of nummer)
- Agent-dialoogvenster: begeleider typt vraag, agent antwoordt
- Sliders tonen automatisch ingevuld vanuit database (read-only, transparantie)
- Succeskans + drempel zichtbaar
- SHAP top-3 factoren getoond

### Scherm 2: Eerdere berekeningen
- Overzicht opgeslagen checks
- Filterbaar op opleiding / dreiging / op koers
- Samenvatting: totaal, gemiddelde score, dreiging vs. op koers

### Scherm 3: Agent-gesprek (nieuw t.o.v. mockup)
- Vrije dialoog met de agent over één of meerdere studenten
- Volledig gelogd (harness)

---

## 7. Technische keuzes

| Keuze | Beslissing | Reden |
|---|---|---|
| Database | SQLite | Lokaal, zero-infra, sprint 1 |
| AI-model | Claude (Anthropic) | Sterke tool-use, bestaande SDK |
| ML-model | XGBoost/RF via GridSearchCV | Best performer op tabeldata |
| Uitlegbaarheid | SHAP | Transparantie voor begeleiders |
| Frontend | Streamlit + CEDA huisstijl | Conform projectstandaard |
| Backend | FastAPI | Conform EduPlan-patroon |
| Abstractie | LLMProvider interface | Model-agnostisch voor EduClaw |

---

## 8. Niet in scope (sprint 1)

- Authenticatie / login
- Meerdere gebruikersrollen
- Lokale LLM-integratie (architectuur is klaar, model niet)
- Productie-database (PostgreSQL)
- Real data-koppeling (SIS/ERP)
