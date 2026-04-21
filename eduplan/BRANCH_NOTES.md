# Branch notes: imputer-fix + config.yaml

## Aanpassingen in deze branch

### 1. `config.yaml` (nieuw bestand)
Alle hardcoded waarden uit de backend gehaald en centraal gezet:
paden naar model-bestanden, kolomnamen, drempelwaarden, LLM-model, download-URLs.

### 2. `backend/trainer.py`
- Metadata-kolommen (`Naam`, `Opleiding`, `Klas`, `Mentor`) worden vóór training uitgefilterd.
  Zonder dit werden namen one-hot encoded als modelfeatures (`Naam_307417`, etc.) — onzin.
- Sla na training een aparte **inferentie-imputer** op (gefitst op de feature-kolommen, zonder `Dropout`).
  De imputer van student-signal bevat ook de doelkolom en is daardoor niet bruikbaar bij voorspellen.

### 3. `backend/main.py`
- Laad de inferentie-imputer bij opstarten.
- `_apply_imputer()` past de imputer toe op exact de kolommen waarop hij gefitst is
  (via `imputer.feature_names_in_`). Eerder werd hij op de verkeerde kolommen gezet.
- Nieuwe constanten voor imputer- en scaler-paden via config.

### 4. `student-signal` (apart PR, al gemerged)
- `impute_missing_values()` geeft nu ook de fitted imputer terug.
- `PreparedData` heeft nu een `imputer`-veld.

---

## Openstaande productontwerpvraag

**EduPlan maakt nu geen onderscheid tussen trainingsdata en predictiedata.**

De bedoelde workflow is:
- **Historisch cohort** (vorig jaar, Dropout bekend) → model trainen
- **Huidig cohort** (dit jaar, Dropout onbekend) → model voorspelt wie risico loopt

In de huidige implementatie wordt dezelfde geüploade CSV voor beide gebruikt.
Dat is functioneel (de tool werkt), maar datascience-technisch niet correct
(trainen en scoren op dezelfde data geeft overfitte resultaten).

**Vraag:** Moet EduPlan twee aparte uploads ondersteunen?
- Upload 1: historische data met `Dropout`-kolom → trainen
- Upload 2: huidig cohort zonder `Dropout` → ranken

Dit heeft ook invloed op de imputer-logica: bij twee aparte datasets is de
inferentie-imputer juist essentieel.
