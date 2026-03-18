# Shared

Gedeelde data tussen frontend en backend.

## Inhoud

- `data.csv` — Synthetische studentdata (gegenereerd door `data_prep.py`)
- `data_prep.py` — Downloadt data en model van Uitnodigingsregel, voegt weergavekolommen toe
- `synth_data_pred.csv` — Ruwe download van MondriaanBI/Uitnodigingsregel (tussenstap)

## Data genereren / model downloaden

```bash
python shared/data_prep.py
```

Dit script:
1. Downloadt `synth_data_pred.csv` van [cedanl/Uitnodigingsregel](https://github.com/cedanl/Uitnodigingsregel)
2. Downloadt `random_forest_regressor.joblib` van [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) en slaat het op als `backend/model.joblib`
3. Leidt `Opleiding` af uit de één-hete sector-kolommen (Economie, Techniek, etc.)
4. Voegt synthetische `Naam`, `Klas` en `Mentor` kolommen toe
5. Slaat het resultaat op als `shared/data.csv`

## Datavelden

| Kolom | Type | Bron |
|-------|------|------|
| `Studentnummer` | int | Uitnodigingsregel |
| `StudentAge` | int | Uitnodigingsregel |
| `absence_unauthorized` | float | Uitnodigingsregel |
| `absence_authorized` | float | Uitnodigingsregel |
| `VooroplNiveau_*` | binary (0/1) | Uitnodigingsregel |
| `Economie`, `Techniek`, … | binary (0/1) | Uitnodigingsregel |
| `StudentGender` | binary (0/1) | Uitnodigingsregel |
| `Opleiding` | tekst | Afgeleid uit sectorkolommen |
| `Naam`, `Klas`, `Mentor` | tekst | Synthetisch toegevoegd |
