# CEDA EduPulse App

Studentuitval-signalering en -interventietool voor onderwijsinstellingen, ontwikkeld door CEDA.
Gebruikt een **Random Forest Regressor** van het [Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel)-project (MondriaanBI) om uitvalrisico te voorspellen, aangevuld met SHAP-uitleg en Nederlandstalige AI-adviezen via OpenAI GPT-4o-mini.

## Installatie

```bash
uv sync
# of
pip install -r requirements.txt
```

## Gebruik

### Stap 1 — Data en model downloaden

```bash
python shared/data_prep.py
```

Dit downloadt de synthetische studentdata en het voorgetrainde model van GitHub en slaat ze op als `shared/data.csv` en `backend/model.joblib`.

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
| `OPENAI_API_KEY` | Backend — GPT-4o-mini voor uitleg en samenvatting |
| `ANTHROPIC_API_KEY` | Alleen `main.py` (standalone Claude-agent CLI) |

## Model & data

Het ML-model en de synthetische studentdata zijn afkomstig van [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel).
Het model is een **RandomForestRegressor** getraind op ~26 features waaronder leeftijd, vooropleidingsniveau, sector, inschrijvingen en verzuim.
De uitvalkans is een continue score (0–1); alle studenten worden gerangschikt van hoogste naar laagste risico.

## Technologieën

- **FastAPI** — Backend API
- **Streamlit** — Frontend interface
- **scikit-learn + joblib** — Random Forest Regressor (Uitnodigingsregel)
- **SHAP** — Feature importance uitleg
- **OpenAI GPT-4o-mini** — Nederlandstalige risicoanalyse
- **Pandas & Plotly** — Data-analyse en visualisatie

## Auteurs

Ed de Feber, Edwin Lieftink, Steven Ramondt (CEDA / SURF)
ML-model: Irene Eegdeman (MondriaanBI/Uitnodigingsregel)
