# Backend

FastAPI backend voor de Edupulse applicatie.

## Functionaliteit
- `/predict_dropout` - Voorspelt uitvalrisico op basis van studentkenmerken
- `/explain_risk` - Genereert AI-uitleg waarom een student risico loopt
- `/feature_importance` - Berekent SHAP-waarden voor feature importance
- `/summarize` - Genereert managementsamenvatting van data

## Belangrijke bestanden
- `main.py` - FastAPI applicatie met alle endpoints
- `model.pkl` - Getraind RandomForest model voor uitvalvoorspelling

## Starten
```bash
uvicorn backend.main:app --reload
```
