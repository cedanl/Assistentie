# Frontend

Streamlit frontend voor de EduPulse / Uitnodigingsregel applicatie.

## Bestanden

| Bestand | Functie |
|---------|---------|
| `app.py` | Streamlit app — alle schermen, logica en API-calls |
| `styles.py` | CSS-strings (`START_CSS`, `MAIN_CSS`) en kleurconstanten (`TERRACOTTA`, `ROZE_BG`, `ROZE_LICHT`) |

## Schermstructuur

### Startscherm (`page = "start"`)

- Welkomsttekst en uitleg over de Uitnodigingsregel
- Upload-veld voor `.csv` of `.xlsx` met automatische kolomkoppeling:
  - Fuzzy-matching op kolomnamen (case/underscore/spatie-insensitief)
  - LLM-fallback via `/map_columns` voor resterende ontbrekende kolommen
  - Uitvalkolom wordt ook herkend onder synoniemen (`Uitval`, `Uitgevallen`, `Gestopt`, etc.) en automatisch hernoemd naar `Dropout`
- **Modeltraining-panel** (alleen bij geüploade data met `Dropout`-kolom ≥ 30 rijen):
  - Knop "Train model op jouw data" — start `/train_model` asynchroon
  - Live voortgang: verstreken tijd + contextgevoelig fasebericht
  - Polling via één statuscheck per render-cyclus (`st.rerun()`-gebaseerd, geen blokkerende loop)
  - Succes- en foutafhandeling met optie tot reset naar standaardmodel
- Zoekbalk om een opleiding te selecteren + **START**-knop
- Snelkeuze-pills: de eerste **4 opleidingen** (alfabetisch) zijn direct zichtbaar
- Knop **"Meer ↓"** toont alle overige opleidingen
- Footer met CC-licentiemelding

### Hoofdscherm (`page = "main"`)

**Header** (lichtroze achtergrond `#fae8e8`, sticky, volle schermbreedte)
- CEDA-logo links
- Navigatietabs rechts: **UITNODIGINGSREGEL** en **EDUPLAN**
  - Actieve tab: witte pill met zwarte rand (`div.nav-actief`)
  - Inactieve tab: transparant, geen rand (`div.nav-inactief`)
- Badge "instellingsmodel" zichtbaar in de kaart-header als `model_custom.joblib` actief is

**Kaart** (witte container met schaduw)
- Normale modus: opleiding-naam + KLAS-dropdown + potlood-knop (✏) om van opleiding te wisselen
- Zoek-modus (na klik op ✏): zoekbalk + ZOEK-knop

**Terracotta banner**
- "Toon mij **X** lerenden met het hoogste risico om uit te vallen."
- Slider om het aantal te tonen studenten aan te passen (default: **10**)

**UITNODIGINGSREGEL-tab**
- Horizontale staafgrafiek (Plotly) — studenten gesorteerd hoog→laag op uitvalkans
- Kleurgradient van donker naar lichter terracotta

**EDUPLAN-tab**
- Dropdown: selecteer een lerende uit de top-N risicolijst
- Knop **TOON EDUPLAN** — roept `/explain_risk` en `/feature_importance` aan
- EduPlan-header: witte kaart met 🚦-icoon en studentnaam
- EduPlan-inhoud: lichtroze achtergrond (`ROZE_LICHT`), vrij zwevend met `border-radius`
- Knop **PRINT** — native HTML-knop met `window.parent.print()`
- Knop **DOWNLOAD** — Word `.docx` export via `st.download_button`

**Footer**
- CC ShareAlike 4.0 licentiemelding

## Modelkeuze

De frontend stuurt `use_default_model: true` mee naar alle voorspel-endpoints wanneer de synthetische demo-data actief is (`gebruik_demo_data = True`). Zo wordt bij eigen geüploade data automatisch het instellingsmodel gebruikt, en bij demo-data altijd het originele Uitnodigingsregel-model.

## Technische details

- **CSS gescheiden van logica**: alle opmaak staat in `styles.py`; `app.py` importeert `START_CSS`, `MAIN_CSS` en de kleurconstanten
- **Full-width header**: de sticky nav-rij breekt visueel uit de `max-width: 900px` container via `box-shadow` spread + `clip-path` — de kolomindeling blijft intact
- **Automatische voorspelling**: zodra een opleiding/klas-filter wijzigt, worden alle studenten via `/predict_dropout` beoordeeld en gesorteerd
- **Session state** slaat risicoresultaten op (`risicostudenten`) zodat Streamlit-reruns geen herberekening veroorzaken
- **Features** worden dynamisch bepaald uit `shared/data.csv` — alle kolommen behalve `Dropout`, `Naam`, `Opleiding`, `Klas`, `Mentor`
- **XSS-beveiliging**: studentnamen worden via `html.escape()` gesaniteerd vóór rendering met `unsafe_allow_html=True`
- **PRINT-knop**: geïmplementeerd als HTML `<button onclick="(window.parent||window).print()">` omdat een Streamlit button een rerun veroorzaakt

## Starten

```bash
uv run streamlit run --server.port 8502 frontend/app.py
# of via shellscript:
./2_start_streamlit.sh
```
