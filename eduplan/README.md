# CEDA EduPlan — Uitnodigingsregel

Studentuitval-signalering en interventietool voor mbo-instellingen, ontwikkeld door CEDA.
Gebruikt een **Random Forest Regressor** van het [Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel)-project (MondriaanBI) om uitvalrisico te voorspellen, aangevuld met SHAP-uitleg en Nederlandstalige AI-adviezen via OpenAI GPT-4.1.

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
| `OPENAI_API_KEY` | Backend — GPT-4.1 voor EduPlan-uitleg en kolomkoppeling |
| `ANTHROPIC_API_KEY` | Alleen `main.py` (standalone Claude-agent CLI) |

## Interface

De app bestaat uit een **startscherm** en een **hoofdscherm**:

**Startscherm**
- Upload-veld voor eigen databestand (.csv of .xlsx)
- Automatische kolomkoppeling via fuzzy-matching en LLM (`/map_columns`)
- Detectie van uitvalkolom onder alternatieve namen (`Uitval`, `Uitgevallen`, etc.) — automatisch hernoemd naar `Dropout`
- Trainings-panel: als het geüploade bestand een `Dropout`-kolom bevat (≥ 30 ingevulde waarden), kan een instellingsspecifiek model getraind worden met live voortgangs- en tijdsindicatie
- Snelkeuze-pills: 4 opleidingen direct zichtbaar, overige via knop "Meer ↓"
- Roze achtergrond met compacte CC-licentietekst onderaan

**Hoofdscherm**
- Lichtroze header (sticky, volle breedte) met CEDA-logo en drie knoppen: **← TERUG**, **UITNODIGINGSREGEL**, **EDUPLAN**
  - Actieve tab: witte pill met zwarte rand; inactieve tab: transparant
  - Badge "instellingsmodel" zichtbaar als een getraind model actief is
- Witte kaart met opleiding + klas-filter + potlood-icoon (opleiding wijzigen)
- Terracotta banner: "Toon mij X lerenden met het hoogste risico om uit te vallen" (default: 10)
- **UITNODIGINGSREGEL-tab**: horizontale staafgrafiek — studenten gesorteerd hoog→laag op uitvalkans
- **EDUPLAN-tab**: selecteer een lerende → genereer Nederlandstalig AI-advies → download als Word (.docx)
- Compacte lichtroze footer onderaan met CC-licentiereferentie

## Model & data

Het ML-model en de basis synthetische studentdata zijn afkomstig van [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel).
Het model is een **RandomForestRegressor** getraind op ~26 features: leeftijd, vooropleidingsniveau, sector, aanmeldingen en verzuim.
De uitvalkans is een continue score (0–1); alle studenten worden gerangschikt van hoogste naar laagste risico.

Bij gebruik van de synthetische demo-data wordt altijd het originele `model.joblib` gebruikt, ook als er een instellingsmodel beschikbaar is.

## Modeltraining

Instellingen kunnen een eigen model trainen op historische data met bekende uitvalresultaten:

1. Upload een bestand met een `Dropout`-kolom (of synoniem)
2. Klik "Train model op jouw data" op het startscherm
3. De backend traint asynchroon een `RandomForestRegressor` via GridSearchCV (~15–60s)
4. Het getrainde model wordt opgeslagen als `backend/model_custom.joblib` en bij herstart automatisch geladen
5. Terugzetten naar het standaardmodel kan via de resetknop

## Technologieën

- **FastAPI** — Backend API
- **Streamlit** — Frontend interface
- **scikit-learn + joblib** — Random Forest Regressor (Uitnodigingsregel) + GridSearchCV voor training
- **SHAP** — Feature importance uitleg
- **OpenAI GPT-4.1** — Nederlandstalige risicoanalyse (EduPlan) en kolomkoppeling
- **Pandas & Plotly** — Data-analyse en visualisatie
- **python-docx** — Word-export van EduPlan

## Auteurs

Ed de Feber, Edwin Lieftink, Steven Ramondt (CEDA / SURF)
ML-model: Irene Eegdeman (MondriaanBI/Uitnodigingsregel)
