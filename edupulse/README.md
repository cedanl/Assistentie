# CEDA EduPulse — Uitnodigingsregel

Studentuitval-signalering en interventietool voor mbo-instellingen, ontwikkeld door CEDA.
Gebruikt een **Random Forest Regressor** van het [Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel)-project (MondriaanBI) om uitvalrisico te voorspellen, aangevuld met SHAP-uitleg en Nederlandstalige AI-adviezen via OpenAI GPT-4o-mini.

## Installatie

```bash
uv sync
# of
pip install -r requirements.txt
```

## Gebruik

### Stap 1 — Data en model downloaden (eenmalig)

```bash
python shared/data_prep.py
```

Dit downloadt de synthetische studentdata en het voorgetrainde model van GitHub en slaat ze op als `shared/data.csv` en `backend/model.joblib`.

> De huidige `shared/data.csv` bevat **1.000 studenten** verdeeld over 11 opleidingen: Economie, Zorg & Welzijn, Overig, Kapper, Metselaar, Kok, Gastheer/Gastvrouw, Tandartsassistent, Junior Manager Logistiek, Verzorgende en Werktuigbouw.

### Stap 2 — Applicatie starten (twee terminals)

```bash
# Terminal 1 — FastAPI backend (poort 8000)
./1_start_fastapi.sh

# Terminal 2 — Streamlit frontend (poort 8502)
./2_start_streamlit.sh
```

## Omgevingsvariabelen

| Variabele | Gebruik |
|-----------|---------|
| `OPENAI_API_KEY` | Backend — GPT-4o-mini voor EduPlan-uitleg |
| `ANTHROPIC_API_KEY` | Alleen `main.py` (standalone Claude-agent CLI) |

## Interface

De app bestaat uit een **startscherm** en een **hoofdscherm**:

**Startscherm**
- Zoekbalk om een opleiding te selecteren
- Snelkeuze-pills: 4 opleidingen direct zichtbaar, overige via knop "Meer ↓"
- Optie om de gekozen opleiding te onthouden

**Hoofdscherm**
- Header met CEDA-logo en navigatietabs (UITNODIGINGSREGEL / EDUPLAN)
- Kaart met opleiding + klas-filter + potlood-icoon (opleiding wijzigen)
- Terracotta banner: "Toon mij X lerenden met het hoogste risico om uit te vallen" (default: 10)
- **UITNODIGINGSREGEL-tab**: horizontale staafgrafiek — studenten gesorteerd hoog→laag op uitvalkans
- **EDUPLAN-tab**: selecteer een lerende → genereer Nederlandstalig AI-advies → download als Word (.docx)

## Model & data

Het ML-model en de basis synthetische studentdata zijn afkomstig van [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel).
Het model is een **RandomForestRegressor** getraind op ~26 features: leeftijd, vooropleidingsniveau, sector, aanmeldingen en verzuim.
De uitvalkans is een continue score (0–1); alle studenten worden gerangschikt van hoogste naar laagste risico.

## Technologieën

- **FastAPI** — Backend API
- **Streamlit** — Frontend interface
- **scikit-learn + joblib** — Random Forest Regressor (Uitnodigingsregel)
- **SHAP** — Feature importance uitleg
- **OpenAI GPT-4o-mini** — Nederlandstalige risicoanalyse (EduPlan)
- **Pandas & Plotly** — Data-analyse en visualisatie
- **python-docx** — Word-export van EduPlan

## Auteurs

Ed de Feber, Edwin Lieftink, Steven Ramondt (CEDA / SURF)
ML-model: Irene Eegdeman (MondriaanBI/Uitnodigingsregel)
