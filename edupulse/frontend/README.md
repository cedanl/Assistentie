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
- Zoekbalk om een opleiding in te typen + **START**-knop
- Snelkeuze-pills: de eerste **4 opleidingen** (alfabetisch) zijn direct zichtbaar
- Knop **"Meer ↓"** toont alle overige opleidingen; **"Minder ↑"** verbergt ze weer
- Checkbox "Onthoud mijn opleiding" (persisteert via session state)
- Footer met CC-licentiemelding

### Hoofdscherm (`page = "main"`)

**Header** (roze achtergrond, schaduw onderaan)
- CEDA-logo links
- Navigatietabs rechts: **UITNODIGINGSREGEL** en **EDUPLAN** (pill-stijl, actieve tab gemarkeerd)

**Kaart** (witte container met schaduw)
- Normale modus: opleiding-naam + KLAS-dropdown + potlood-knop (✏) om van opleiding te wisselen
- Zoek-modus (na klik op ✏): zoekbalk + ZOEK-knop

**Terracotta banner**
- "Toon mij **X** lerenden met het hoogste risico om uit te vallen."
- Slider om het aantal te tonen studenten aan te passen (default: **10**)

**UITNODIGINGSREGEL-tab**
- Horizontale staafgrafiek (Plotly) — studenten gesorteerd hoog→laag op uitvalkans
- Lege staat: lichtroze placeholder

**EDUPLAN-tab**
- Dropdown: selecteer een lerende uit de top-N risicolijst
- Knop **TOON EDUPLAN** — roept `/explain_risk` en `/feature_importance` aan
- EduPlan-kaart: 🚦-icoon + studentnaam, gevolgd door Nederlandstalige AI-uitleg
- Knop **PRINT** — native HTML-knop met `window.parent.print()` (geen Streamlit rerun)
- Knop **DOWNLOAD** — Word `.docx` export via `st.download_button`

**Footer**
- CC ShareAlike 4.0 licentiemelding

## Technische details

- **CSS gescheiden van logica**: alle opmaak staat in `styles.py`; `app.py` importeert `START_CSS`, `MAIN_CSS` en de kleurconstanten
- **Automatische voorspelling**: zodra een opleiding/klas-filter wijzigt, worden alle studenten via `/predict_dropout` beoordeeld en gesorteerd
- **Session state** slaat risicoresultaten op (`risicostudenten`) zodat Streamlit-reruns geen herberekening veroorzaken
- **Features** worden dynamisch bepaald uit `shared/data.csv` — alle kolommen behalve `Dropout`, `Naam`, `Opleiding`, `Klas`, `Mentor`
- **PRINT-knop**: geïmplementeerd als HTML `<button onclick="(window.parent||window).print()">` omdat een Streamlit button een rerun veroorzaakt waardoor de print-dialog niet opent

## Starten

```bash
uv run streamlit run --server.port 8502 frontend/app.py
# of via shellscript:
./2_start_streamlit.sh
```
