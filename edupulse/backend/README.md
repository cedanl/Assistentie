# Backend

FastAPI backend voor de EduPulse applicatie.

## Endpoints

| Endpoint | Input | Functie |
|----------|-------|---------|
| `POST /predict_dropout` | Studentkenmerken (dict) | Uitvalkans als continue score (0–1); alle studenten worden teruggegeven, gesorteerd van hoog naar laag risico |
| `POST /explain_risk` | Studentdata + kans | Nederlandstalige AI-uitleg via GPT-4o-mini |
| `POST /feature_importance` | Studentdata | SHAP-waarden per feature (TreeExplainer) |
| `POST /summarize` | CSV-string of vraag | Managementsamenvatting of Q&A via GPT-4o-mini |

## Belangrijke bestanden

- `main.py` — FastAPI applicatie met alle endpoints
- `model.joblib` — Voorgetraind RandomForestRegressor model (Uitnodigingsregel, MondriaanBI)

## Model

Het model is een **RandomForestRegressor** gedownload van [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel).
Het is getraind zonder feature-namen (numpy arrays), dus de backend geeft `.values` door om sklearn-waarschuwingen te vermijden.
Features worden dynamisch bepaald vanuit `shared/data.csv` (alle kolommen behalve `Dropout`, `Naam`, `Opleiding`, `Klas`, `Mentor`).

## Starten

```bash
uv run uvicorn --host 127.0.0.1 --port 8000 backend.main:app --reload
# of via shellscript:
./1_start_fastapi.sh
```
