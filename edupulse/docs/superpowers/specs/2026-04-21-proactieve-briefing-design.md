# Proactieve Briefing — Design Spec

**Datum:** 2026-04-21
**Sprint:** EduClaw Sprint 2

---

## Doel

Een MBO-begeleider selecteert zijn/haar mentorgroep via een dropdown en ziet bovenaan de "Uitvalrisico check" pagina een dagelijkse briefing: de top-10 meest risicovolle studenten uit die groep, elk met een korte LLM-toelichting (1–2 zinnen).

## Architectuur

```
Sidebar dropdown (mentor_email)
        │
        ▼
GET /mentoren          → lijst unieke mentors uit studenten-tabel
GET /brief/{email}     → top-10 risicovolle studenten + LLM-toelichting
        │
        ├── DB query: studenten WHERE mentor_email = {email}
        ├── ML bulk: RisicoPredictor.predict() per student
        ├── Sorteren op uitval_kans DESC, kappen op 10
        └── Claude (één call): prompt met alle 10 studenten
                                → toelichting per student
```

## Backend

### `GET /mentoren`
Geeft lijst van `{mentor_naam: str, mentor_email: str}` — unieke paren uit de `studenten`-tabel, gesorteerd op naam.

### `GET /brief/{mentor_email}`
**Parameters:** `mentor_email` (URL-encoded)

**Stappen:**
1. Query alle studenten met `mentor_email` uit de `studenten`-tabel
2. Roep `RisicoPredictor.predict()` aan voor elke student
3. Sorteer op `uitval_kans` aflopend, neem de top 10
4. Bouw één prompt met per student: naam, uitval_kans, SHAP-top-1-factor, aanwezigheid, BSA-studiepunten
5. Één Claude-call (`claude-sonnet-4-6`) met die prompt → structured output: lijst van toelichtingen
6. Combineer ML-resultaten + LLM-toelichtingen

**Response:**
```json
[
  {
    "studentnummer": "20240042",
    "naam": "Youssef El Amrani",
    "uitval_kans": 0.81,
    "toelichting": "Hoge uitvalkans door zeer lage aanwezigheid (54%) en achterstand op BSA-punten (18). Directe aandacht gewenst."
  },
  ...
]
```

**Foutafhandeling:**
- Mentor niet gevonden (0 studenten): HTTP 404
- Claude-call mislukt: HTTP 503 met uitleggende `detail`-string
- Lege top-10 (alle studenten laag risico): lege lijst teruggeven, geen fout

### Prompt-structuur
```
Je bent een onderwijsassistent. Geef per student één tot twee zinnen toelichting
voor de begeleider. Wees concreet: noem de belangrijkste risicofactor.
Schrijf in het Nederlands. Geef geen adviezen.

Studenten:
1. Youssef El Amrani — uitvalkans 81%, belangrijkste factor: aanwezigheid (bijdrage 0.42), aanwezigheid 54%, BSA 18 punten
2. ...

Geef de toelichtingen terug als JSON-lijst in dezelfde volgorde:
[{"studentnummer": "...", "toelichting": "..."}, ...]
```

## Frontend

### Sidebar (`uitvalrisico.py`)
- Bestaand student-zoekblok blijft staan
- Nieuw blok "Mijn mentorgroep" eronder: `st.selectbox` gevuld via `GET /mentoren`
- Keuze opgeslagen in `st.session_state.mentor_email` en `st.session_state.mentor_naam`
- Geen mentor geselecteerd → briefing-blok niet getoond

### Briefing-blok (`uitvalrisico.py`)
- `st.expander(f"📋 Dagelijkse briefing — {mentor_naam}", expanded=False)`
- Bij uitklappen: spinner + call naar `GET /brief/{mentor_email}`
- Resultaat gecached in `st.session_state.briefing_cache[mentor_email]` (één call per sessie)
- Per student: een rij met:
  - Naam (klikbaar → vult `geselecteerde_student`)
  - Uitvalkans-badge (rood als > 0.5, oranje als 0.35–0.5)
  - LLM-toelichting in lichtgrijs
- "Ververs briefing"-knop onderaan om cache te wissen

### Volgorde op pagina
1. Briefing-expander (nieuw, bovenaan)
2. Student-kaart (bestaand, alleen als student geselecteerd)
3. Divider
4. Agent-chatvenster (bestaand)

## Bestanden

| Bestand | Wijziging |
|---------|-----------|
| `backend/main.py` | Voeg `GET /mentoren` en `GET /brief/{mentor_email}` toe |
| `backend/models.py` | Voeg `BriefingStudentSchema` en `MentorSchema` toe |
| `frontend/pages/uitvalrisico.py` | Sidebar-dropdown + briefing-expander |

Geen nieuwe bestanden nodig. Geen wijzigingen aan ML-pipeline, agent-kernel of database.

## Niet in scope (Sprint 2)

- Authenticatie — mentor kiest zichzelf via dropdown, geen wachtwoord
- Push-notificaties of e-mail
- Persistente cache (briefing leeft alleen in sessie)
- Meerdere mentorgroepen per begeleider
