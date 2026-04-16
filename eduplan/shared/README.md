# Shared

Gedeelde data tussen frontend en backend.

## Inhoud

- `data.csv` — Synthetische studentdata (1.000 studenten, 11 opleidingen)
- `data_prep.py` — Downloadt basisdata en model van Uitnodigingsregel, voegt weergavekolommen toe
- `synth_data_pred.csv` — Ruwe download van cedanl/Uitnodigingsregel (tussenstap)

## Data genereren / model downloaden

```bash
python shared/data_prep.py
```

Dit script:
1. Downloadt `synth_data_pred.csv` van [cedanl/Uitnodigingsregel](https://github.com/cedanl/Uitnodigingsregel)
2. Downloadt `random_forest_regressor.joblib` van [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) en slaat het op als `backend/model.joblib`
3. Voegt synthetische `Naam`, `Klas` en `Mentor` kolommen toe
4. Slaat het resultaat op als `shared/data.csv`

> Na het draaien van `data_prep.py` zijn er 150 basisstudenten. De huidige `data.csv` bevat **1.000 studenten** — de extra 850 zijn handmatig gegenereerd en toegevoegd met een Python-script.

## Opleidingen in data.csv

| Opleiding | Sector-kolom | Aantal |
|-----------|-------------|--------|
| Economie | Economie=1 | ~40 |
| Zorg & Welzijn | Zorgenwelzijn=1 | ~40 |
| Overig | Richting_nan=1 | ~20 |
| Kapper | Economie=1 | 107 |
| Metselaar | Techniek=1 | 107 |
| Kok | DSV=1 | 106 |
| Gastheer/Gastvrouw | DSV=1 | 106 |
| Tandartsassistent | Zorgenwelzijn=1 | 106 |
| Junior Manager Logistiek | Economie=1 | 106 |
| Verzorgende | Zorgenwelzijn=1 | 106 |
| Werktuigbouw | Techniek=1 | 106 |

## Datavelden

| Kolom | Type | Bron |
|-------|------|------|
| `Studentnummer` | int | Uitnodigingsregel / gegenereerd |
| `StudentAge` | int | Uitnodigingsregel / gegenereerd |
| `Dropout` | binary (0/1) | Uitnodigingsregel / gegenereerd |
| `Aanmel_aantal` | float | Uitnodigingsregel / gegenereerd |
| `max1studie` | float | Uitnodigingsregel / gegenereerd |
| `absence_unauthorized` | float | Uitnodigingsregel / gegenereerd |
| `absence_authorized` | float | Uitnodigingsregel / gegenereerd |
| `VooroplNiveau_*` | binary (0/1) | Uitnodigingsregel / gegenereerd |
| `Economie`, `Techniek`, `DSV`, `Zorgenwelzijn`, … | binary (0/1) | Uitnodigingsregel / gegenereerd |
| `StudentGender` | binary (0/1) | Uitnodigingsregel / gegenereerd |
| `ROCMondriaan` | binary (0/1) | Uitnodigingsregel / gegenereerd |
| `Opleiding` | tekst | Naam van de opleiding (direct opgeslagen) |
| `Naam`, `Klas`, `Mentor` | tekst | Synthetisch gegenereerd |
