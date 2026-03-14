# Shared

Gedeelde data en utilities tussen frontend en backend.

## Inhoud
- `data.csv` - Mock studentendata met kenmerken en uitvalstatus
- `data_prep.py` - Script voor genereren van mock data en trainen van ML-model

## Data genereren
```bash
python shared/data_prep.py
```

Dit genereert nieuwe `data.csv` en traint een nieuw `model.pkl` voor de backend.
