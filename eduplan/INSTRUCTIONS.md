# EduPlan — Gebruikshandleiding

Deze handleiding beschrijft hoe je EduPlan installeert, start en gebruikt als mentor of coördinator binnen een mbo-instelling.

---

## Vereisten

- Python 3.13 of hoger
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (aanbevolen pakketbeheerder)
- Een geldige `OPENAI_API_KEY`

---

## Eenmalige installatie

### 1. Afhankelijkheden installeren

Voer dit uit vanuit de `eduplan/`-map:

```bash
uv sync
```

### 2. Data en model downloaden

```bash
python shared/data_prep.py
```

Dit downloadt:
- Synthetische studentdata → `shared/data.csv`
- Voorgetraind Random Forest-model → `backend/model.joblib`

### 3. Omgevingsvariabele instellen

Maak een `.env`-bestand aan in de `eduplan/`-map (of exporteer de variabele):

```bash
OPENAI_API_KEY=sk-...
```

---

## Applicatie starten

EduPlan bestaat uit twee processen die tegelijk moeten draaien. Open twee terminals vanuit de `eduplan/`-map.

**Terminal 1 — Backend (FastAPI, poort 8000):**

```bash
./1_start_fastapi.sh
```

**Terminal 2 — Frontend (Streamlit, poort 8502):**

```bash
./2_start_streamlit.sh
```

Open daarna je browser op **http://localhost:8502**.

> Op Windows gebruik je de `.bat`-varianten: `1_start_fastapi.bat` en `2_start_streamlit.bat`.

---

## Eigen data uploaden

EduPlan werkt standaard met de meegeleverde synthetische data (`shared/data.csv`). Je kunt ook een eigen databestand uploaden:

1. Klik op het upload-veld op het startscherm.
2. Upload een `.csv`- of `.xlsx`-bestand.
3. Als de kolomnamen afwijken, koppelt de app ze automatisch via een AI-mapping (`/map_columns`).

**Minimaal vereiste kolommen:**

| Kolom | Beschrijving |
|-------|-------------|
| `Naam` | Volledige naam van de student |
| `Opleiding` | Naam van de opleiding |
| `Klas` | Klasgroep |
| `StudentAge` | Leeftijd |
| `absence_unauthorized` | Ongeoorloofd verzuim (dagen) |
| `absence_authorized` | Geoorloofd verzuim (dagen) |
| Sectorkolommen | `Economie`, `Techniek`, `DSV`, `Zorgenwelzijn`, `Anders` (één per student) |
| Vooropleidingskolommen | `VooroplNiveau_HAVO`, `VooroplNiveau_MBO`, etc. |

Zie [`shared/README.md`](shared/README.md) voor de volledige lijst van kolommen en hun betekenis.

---

## Gebruik: Uitnodigingsregel-tab

1. Kies op het **startscherm** een opleiding via de zoekbalk of de snelkeuze-pills.
2. Klik op **START** — het hoofdscherm opent.
3. Gebruik de **KLAS**-dropdown om te filteren op een specifieke klas.
4. Verstel de slider ("Toon mij X lerenden…") om het aantal studenten in de grafiek aan te passen.
5. De horizontale staafgrafiek toont studenten gesorteerd van hoogste naar laagste uitvalrisico.

Risiconiveaus:
- **LAAG** — uitvalkans < 35%
- **MATIG** — uitvalkans 35–65%
- **HOOG** — uitvalkans ≥ 65%

---

## Gebruik: EduPlan-tab

1. Klik op de **EDUPLAN**-tab in het hoofdscherm.
2. Selecteer een student uit de dropdown.
3. Klik op **TOON EDUPLAN** — de app genereert een Nederlandstalig advies via GPT-4.1.

Het EduPlan bevat:
- **Risicoprofiel** — toelichting op de specifieke risicofactoren van de student
- **Signalen en gespreksthema's** — concrete aanknopingspunten voor het eerste gesprek
- **Interventies op maat** — evidence-based aanpak (motivatiegesprek, verzuimaanpak, buddy-koppeling, etc.)
- **Actiepunten** — genummerde lijst gesorteerd op urgentie

4. Klik op **PRINT** om het EduPlan af te drukken.
5. Klik op **DOWNLOAD** om het EduPlan als Word-document (`.docx`) op te slaan.

---

## Opleiding wisselen

- Klik op het **potlood-icoon (✏)** naast de opleidingsnaam in de kaart.
- Typ een nieuwe opleiding in de zoekbalk en bevestig.
- Klik op **← TERUG** in de header om terug te gaan naar het startscherm.

---

## Veelgestelde vragen

**De app start niet / backend reageert niet**
Controleer of beide processen (FastAPI én Streamlit) actief zijn. De backend moet bereikbaar zijn op poort 8000 voordat de frontend werkt.

**Kolomnamen worden niet herkend**
De app probeert kolomnamen automatisch te koppelen via `/map_columns`. Controleer de console-uitvoer van de backend als de mapping mislukt, en pas de kolomnamen in je bestand aan.

**Het EduPlan wordt niet gegenereerd**
Controleer of `OPENAI_API_KEY` correct is ingesteld. Raadpleeg de backend-logs (terminal 1) voor foutmeldingen.

---

## Licentie

De applicatiecode valt onder de [Creative Commons CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.nl)-licentie.
Het ML-model en de synthetische data zijn afkomstig van [MondriaanBI/Uitnodigingsregel](https://github.com/MondriaanBI/Uitnodigingsregel) en [cedanl/Uitnodigingsregel](https://github.com/cedanl/Uitnodigingsregel).
