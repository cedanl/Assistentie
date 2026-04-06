# Backend

FastAPI backend voor de EduPulse applicatie.

## Endpoints

| Endpoint | Input | Functie |
|----------|-------|---------|
| `POST /predict_dropout` | Studentkenmerken + `use_default_model` | Uitvalkans als continue score (0–1) via RandomForestRegressor |
| `POST /explain_risk` | Studentdata + uitvalkans + `use_default_model` | Nederlandstalige AI-uitleg via GPT-4.1; berekent SHAP intern en stuurt top-5 risicofactoren mee |
| `POST /feature_importance` | Studentdata + `use_default_model` | SHAP-waarden per feature (TreeExplainer) — gebruikt door de UI-staafgrafiek |
| `POST /summarize` | CSV-string of vrije vraag | Managementsamenvatting of Q&A via GPT-4.1 (OpenAI Responses API met code interpreter) |
| `POST /map_columns` | Geüploade + vereiste kolomnamen | LLM-gebaseerde kolomnaam-mapping bij CSV-uploads met afwijkende headers |
| `POST /train_model` | Studentdata met `Dropout`-kolom + optioneel `rf_parameters` | Start asynchroon GridSearchCV-training; retourneert direct `{"status": "started"}` |
| `GET /train_status` | — | Geeft huidige trainingsstatus terug: `idle` / `training` / `done` / `failed` |
| `DELETE /reset_model` | — | Verwijdert `model_custom.joblib` en laadt het standaardmodel opnieuw |

### `use_default_model`-vlag

`/predict_dropout`, `/explain_risk` en `/feature_importance` accepteren een optionele boolean `use_default_model` (standaard `false`). De frontend stuurt `true` mee wanneer de synthetische demo-data actief is, zodat altijd het originele Uitnodigingsregel-model wordt gebruikt — ook als er een instellingsmodel aanwezig is.

## Modellen

De backend laadt bij opstarten altijd beide modellen:

| Bestand | Gebruik |
|---------|---------|
| `backend/model.joblib` | Standaardmodel — altijd aanwezig; gebruikt bij demo-data |
| `backend/model_custom.joblib` | Instellingsmodel — aangemaakt via `/train_model`; persistent na herstart |

Als `model_custom.joblib` ontbreekt, is het instellingsmodel een alias op het standaardmodel.

## Belangrijke bestanden

- `main.py` — FastAPI applicatie met alle endpoints en dual-model logica
- `trainer.py` — Pure traininglogica: `train_model()` wraps GridSearchCV voor de RandomForestRegressor
- `model.joblib` — Voorgetraind standaardmodel (Uitnodigingsregel, MondriaanBI)
- `model_custom.joblib` — Instellingsspecifiek model (aangemaakt na training; niet ingecheckt in git)

## Starten

```bash
uv run uvicorn --host 127.0.0.1 --port 8000 backend.main:app --reload
# of via shellscript:
./1_start_fastapi.sh
```
