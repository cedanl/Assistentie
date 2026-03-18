# Frontend

Streamlit frontend voor de EduPulse applicatie.

## Functionaliteit

- **Dashboard** — Studentenoverzicht met filters op Opleiding, Klas en Mentor
- **Kengetallen** — Gemiddelde leeftijd, ongeoorloofd verzuim, geoorloofd verzuim
- **Visualisaties** — Leeftijdsverdeling (histogram), verzuim per opleiding (boxplot)
- **Risico-voorspelling** — Alle studenten gesorteerd van hoogste naar laagste uitvalkans
- **Risicoanalyse** — SHAP feature importance + Nederlandstalige AI-uitleg per student
- **Export** — Risicorapport als Markdown (`.md`) of Word (`.docx`)
- **AI Q&A** — Vrije vragen over de studentendata
- **Managementsamenvatting** — Automatisch gegenereerd via OpenAI

## Features

De features die naar de backend worden gestuurd worden dynamisch bepaald vanuit `shared/data.csv`.
Dit zijn alle kolommen behalve de weergavekolommen (`Naam`, `Opleiding`, `Klas`, `Mentor`) en de doelkolom (`Dropout`).

De data en weergavekolommen zijn afkomstig van [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel), aangevuld met synthetische `Naam`, `Klas` en `Mentor` kolommen.

## Starten

```bash
uv run streamlit run --server.port 8502 frontend/app.py
# of via shellscript:
./2_start_streamlit.sh
```
