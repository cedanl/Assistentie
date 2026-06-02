# EduPlan streaming — design

**Datum:** 2026-06-01
**Doel:** Het genereren van een EduPlan voelt traag omdat de UI blanco blijft tot één
blokkerende LLM-call (~2048 tokens, ~8–20s) klaar is. We tonen Sectie 1
(deterministisch, SHAP = 0.2ms) direct en streamen secties 2–4 token-voor-token.

## Waarom dit werkt

De volledige wachttijd is één `client.messages.create`. Sectie 1 is deterministisch
maar wacht nu achter het LLM. Gemeten: SHAP op één rij = 0.2ms; explainer wordt bij
startup gebouwd. Eerste content kan dus in ~1s verschijnen i.p.v. na de hele generatie.

## Backend (`backend/main.py`)

1. **Refactor** gedeelde logica uit `explain_risk` naar een helper:
   `_prepare_explanation(request) -> (sectie1_html, prompt | None, data_onvoldoende)`.
   Doet risiconiveau, SHAP, top_factors, `data_onvoldoende`, Sectie 1 HTML en de prompt.
2. **Behoud** `POST /explain_risk` ongewijzigd qua gedrag (tests + non-streaming fallback);
   roept nu de helper aan.
3. **Nieuw** `POST /explain_risk_stream` → `StreamingResponse` van **NDJSON**-regels:
   - `{"type":"section1","html": <sectie1>}` — direct
   - bij `data_onvoldoende`: `{"type":"warning","html": ...}` en klaar (geen LLM)
   - anders `client.messages.stream(...)` en per delta `{"type":"delta","text": <ruwe markdown>}`
   - na de deltas: `{"type":"final_html","html": <_markdown_to_html(volledige tekst)>}`
     zodat markdown→HTML-conversie de single source of truth in de backend blijft.

## Frontend (`frontend/app.py`, `_genereer_eduplan`)

Streaming-render draait op de **main script thread** (`st.*` vanuit een ThreadPool-worker
rendert stil niets).

1. Start `_fetch_fi()` in een thread *vóór* het streamen, `.result()` erna — blijft
   concurrent, geen `st.*` in de worker.
2. POST naar `/explain_risk_stream` met `stream=True`, itereer NDJSON via `iter_lines()`:
   - `section1` → render één keer in de bestaande styled HTML-wrapper
   - generator van `delta`-`text` → `full = st.write_stream(gen)` (transient markdown — prima)
   - `warning` → render, geen stream
   - `final_html` → bewaren
3. Na de stream: `explanation = sectie1_html + final_html`, docx bouwen, `st.rerun()` →
   `_render_eduplan_content` toont de definitieve gestylede versie.

## Error handling

- Connectiefout / non-200 → bestaande `_error_html`-pad, opslaan als `explanation`, rerun.
- `data_onvoldoende` → `warning`-regel, geen LLM.

## Testing

- Nieuwe test voor `/explain_risk_stream`: mock `client.messages.stream` (context manager
  die delta-events levert) — andere vorm dan de bestaande `mock_anthropic` (`messages.create`).
  Nieuwe fixture `mock_anthropic_stream` in `conftest.py`.
- Bestaande `/explain_risk`-tests blijven groen.

## Scope

Twee bestanden + één conftest-fixture + één test. Oud endpoint en docx-flow onaangetast.
