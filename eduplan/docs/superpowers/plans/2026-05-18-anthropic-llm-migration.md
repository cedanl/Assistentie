# EduPlan: Migrate Backend LLM from OpenAI to Anthropic (Sonnet 4.6) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Also invoke `claude-api` skill when touching SDK call sites — it triggers on `import anthropic` and documents prompt caching + Messages API patterns.

**Goal:** Replace OpenAI Responses API calls in `eduplan/backend/main.py` (3 endpoints) with Anthropic Messages API calls using `claude-sonnet-4-6`, preserving Dutch output quality and all existing test behavior.

**Architecture:** Dual-client during migration. Add an `anthropic_client = Anthropic()` next to the existing `client = OpenAI()`. Migrate one endpoint at a time so the suite stays green at every checkpoint. After all three endpoints are on Anthropic, remove the OpenAI client, the dep, and the legacy mock fixture in a single cleanup task.

**Tech Stack:** Python 3.13, FastAPI, `anthropic` SDK (new dep), pytest with `fastapi.testclient.TestClient`, `monkeypatch` for client swap, UV for env management.

**Constraints from the codebase (verified before writing this plan):**
- Three call sites in `backend/main.py`: `/summarize` (line ~435), `/explain_risk` (line ~576), `/map_columns` (line ~666). All use `client.responses.create(...)` and read `response.output_text`.
- Test fixture `mock_openai` in `tests/conftest.py:30-40` patches `client.responses.create.return_value.output_text`. Seven tests in `tests/test_backend.py` use this fixture; two of them assert `mock_openai.responses.create.called`.
- Root `conftest.py` patches `openai.OpenAI` **before** `backend.main` imports (required because `ALL_PROXY` SOCKS proxy breaks real client construction at import time). Adding `Anthropic()` at module level requires an equivalent root-level patch, otherwise the test suite fails to collect.
- `pyproject.toml` pins `scikit-learn==1.6.1` exactly (model compatibility). Do not touch this. `openai>=2.26.0` will be removed in the final cleanup task.

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `eduplan/pyproject.toml` | modify | Add `anthropic` dep (Task 1); remove `openai` dep (Task 5). |
| `eduplan/conftest.py` | modify | Add `patch("anthropic.Anthropic", ...)` next to existing OpenAI patch (Task 1); remove OpenAI patch (Task 5). |
| `eduplan/tests/conftest.py` | modify | Add `mock_anthropic` fixture (Task 1); remove `mock_openai` fixture (Task 5). |
| `eduplan/backend/main.py` | modify | Add `anthropic_client = Anthropic()` and `ANTHROPIC_MODEL` constant (Task 1); migrate `/summarize` (Task 2), `/map_columns` (Task 3), `/explain_risk` (Task 4); remove OpenAI client + `MODEL` (Task 5). |
| `eduplan/tests/test_backend.py` | modify | Per-endpoint, swap `mock_openai` → `mock_anthropic` in the migrated endpoint's tests (Tasks 2–4); remove residual `mock_openai` references (Task 5). |
| `eduplan/CLAUDE.md` | modify | Update LLM provider notes + env var requirement (Task 6). |
| `CLAUDE.md` (repo root) | modify | Update sub-project description re: provider (Task 6). |

---

## Task 1: Add Anthropic side-by-side (deps + conftest patches + mock fixture + client init)

**Files:**
- Modify: `eduplan/pyproject.toml` (add anthropic to dependencies)
- Modify: `eduplan/conftest.py` (add Anthropic patch before backend.main import)
- Modify: `eduplan/tests/conftest.py` (add mock_anthropic fixture)
- Modify: `eduplan/backend/main.py` (import + client construction; do NOT touch endpoints yet)

- [ ] **Step 1.1: Add anthropic dependency**

Edit `eduplan/pyproject.toml`, add `"anthropic>=0.43.0",` to the `dependencies` list (alphabetically, after `"openai>=2.26.0",`). The full list of dependencies should now include both providers — OpenAI stays during the migration.

- [ ] **Step 1.2: Run uv sync to install**

```bash
cd eduplan && uv sync --extra dev
```

Expected: completes without error; lockfile updates to include `anthropic` and its transitive deps (`httpx`, `pydantic`, etc. — already pinned).

- [ ] **Step 1.3: Patch Anthropic in root conftest BEFORE backend.main import**

Edit `eduplan/conftest.py` to look exactly like this:

```python
"""Root conftest — patcht OpenAI én Anthropic vóór backend.main wordt geïmporteerd.

Nodig omdat ALL_PROXY een SOCKS-proxy instelt die httpx niet aankan
zonder het optionele 'socksio'-pakket. De mocks voorkomen dat de echte
clients überhaupt worden aangemaakt tijdens tests.
"""

from unittest.mock import MagicMock, patch

# Patch openai.OpenAI vóór elke import van backend.main
_openai_patcher = patch("openai.OpenAI", return_value=MagicMock())
_openai_patcher.start()

# Patch anthropic.Anthropic vóór elke import van backend.main
_anthropic_patcher = patch("anthropic.Anthropic", return_value=MagicMock())
_anthropic_patcher.start()
```

- [ ] **Step 1.4: Add the Anthropic client + model constant to backend/main.py**

In `eduplan/backend/main.py`, find the line `from openai import OpenAI` (around line 43) and add directly below it:

```python
from anthropic import Anthropic
```

Find the lines `client = OpenAI()` and `MODEL = "gpt-5.4-mini-2026-03-17"` (around lines 51–53) and add directly below them:

```python
anthropic_client = Anthropic()
ANTHROPIC_MODEL = "claude-sonnet-4-6"
```

Do NOT modify any endpoint code in this task. Both clients now co-exist.

- [ ] **Step 1.5: Add mock_anthropic fixture in tests/conftest.py**

Edit `eduplan/tests/conftest.py` to add this fixture **below** the existing `mock_openai` fixture (do not remove `mock_openai` yet):

```python
@pytest.fixture
def mock_anthropic(monkeypatch) -> MagicMock:
    """Vervangt de Anthropic-client in backend.main door een mock."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Gemockte LLM-uitvoer")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    import backend.main as main_mod

    monkeypatch.setattr(main_mod, "anthropic_client", mock_client)
    return mock_client
```

- [ ] **Step 1.6: Run full test suite to confirm nothing broke**

```bash
cd eduplan && uv run pytest tests/ -v
```

Expected: all existing tests pass (still using `mock_openai`, since no endpoint code changed). If any test fails at collection time with `anthropic.Anthropic` errors, Step 1.3 was not applied correctly.

- [ ] **Step 1.7: Commit**

```bash
cd eduplan && git add pyproject.toml uv.lock conftest.py tests/conftest.py backend/main.py
git commit -m "$(cat <<'EOF'
eduplan: add Anthropic client alongside OpenAI for migration

Introduce anthropic dep, dual-patch in root conftest, and a parallel mock_anthropic fixture. No endpoint behavior changes yet.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Migrate `/summarize` endpoint (smallest, no JSON parsing)

**Files:**
- Modify: `eduplan/backend/main.py` (the `summarize` function, around lines 432–437)
- Modify: `eduplan/tests/test_backend.py` (`test_summarize_returns_summary`, line ~236)

- [ ] **Step 2.1: Swap test fixture from mock_openai to mock_anthropic**

In `eduplan/tests/test_backend.py`, change the test signature from:

```python
def test_summarize_returns_summary(client, mock_openai):
    resp = client.post("/summarize", json={"data": "student1,student2"})
    assert resp.status_code == 200
    assert "summary" in resp.json()
    assert resp.json()["summary"] == "Gemockte LLM-uitvoer"
```

to:

```python
def test_summarize_returns_summary(client, mock_anthropic):
    resp = client.post("/summarize", json={"data": "student1,student2"})
    assert resp.status_code == 200
    assert "summary" in resp.json()
    assert resp.json()["summary"] == "Gemockte LLM-uitvoer"
```

- [ ] **Step 2.2: Run the test to confirm it FAILS (endpoint still uses OpenAI)**

```bash
cd eduplan && uv run pytest tests/test_backend.py::test_summarize_returns_summary -v
```

Expected: FAIL (the endpoint still calls `client.responses.create`, and the mock_anthropic fixture didn't intercept it, so the real OpenAI mock returns a MagicMock object whose `.output_text` is a MagicMock, not the string `"Gemockte LLM-uitvoer"`).

- [ ] **Step 2.3: Migrate the endpoint code**

In `eduplan/backend/main.py`, find the `summarize` function and replace it with:

```python
@app.post("/summarize")
def summarize(request: SummaryRequest):
    prompt = f"Vat deze BI-data samen voor het management (max 5 regels):\n{request.data}\nSamenvatting:"
    response = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    summary = response.content[0].text
    return {"summary": summary}
```

- [ ] **Step 2.4: Run the test — expect PASS**

```bash
cd eduplan && uv run pytest tests/test_backend.py::test_summarize_returns_summary -v
```

Expected: PASS.

- [ ] **Step 2.5: Run full suite to confirm no regression**

```bash
cd eduplan && uv run pytest tests/ -v
```

Expected: all tests still green.

- [ ] **Step 2.6: Commit**

```bash
cd eduplan && git add backend/main.py tests/test_backend.py
git commit -m "$(cat <<'EOF'
eduplan: migrate /summarize to Anthropic Sonnet 4.6

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Migrate `/map_columns` endpoint (JSON output — use assistant prefill)

**Files:**
- Modify: `eduplan/backend/main.py` (the `map_columns` function, around lines 652–673)
- Modify: `eduplan/tests/test_backend.py` (`test_map_columns_returns_mapping` line ~243 and `test_map_columns_invalid_json_returns_empty` line ~259)

- [ ] **Step 3.1: Swap fixtures and update mock attribute paths in both tests**

In `eduplan/tests/test_backend.py`, replace `test_map_columns_returns_mapping` with:

```python
def test_map_columns_returns_mapping(client, mock_anthropic):
    mock_anthropic.messages.create.return_value.content = [
        MagicMock(text='"StudentAge": "leeftijd", "absence_unauthorized": "verzuim"}')
    ]
    resp = client.post(
        "/map_columns",
        json={
            "uploaded_columns": ["leeftijd", "verzuim"],
            "required_columns": ["StudentAge", "absence_unauthorized"],
        },
    )
    assert resp.status_code == 200
    mapping = resp.json()["mapping"]
    assert mapping.get("StudentAge") == "leeftijd"
```

Note: the mocked text starts with `"StudentAge"...` (no leading `{`) because the endpoint will use assistant prefill — see Step 3.2. The endpoint prepends `{` before parsing.

Replace `test_map_columns_invalid_json_returns_empty` with:

```python
def test_map_columns_invalid_json_returns_empty(client, mock_anthropic):
    """Ongeldige LLM-output levert een leeg mapping-object op (geen crash)."""
    mock_anthropic.messages.create.return_value.content = [MagicMock(text="geen json hier")]
    resp = client.post(
        "/map_columns",
        json={"uploaded_columns": ["x"], "required_columns": ["StudentAge"]},
    )
    assert resp.status_code == 200
    assert resp.json()["mapping"] == {}
```

- [ ] **Step 3.2: Migrate the endpoint code with assistant-prefill JSON pattern**

In `eduplan/backend/main.py`, replace the `map_columns` function with:

```python
@app.post("/map_columns")
def map_columns(request: MapColumnsRequest):
    """Gebruik LLM om geüploade kolomnamen te koppelen aan vereiste kolomnamen."""
    prompt = (
        "Je krijgt twee lijsten met kolomnamen van datasets.\n\n"
        f"Geüploade kolommen: {request.uploaded_columns}\n"
        f"Vereiste kolommen: {request.required_columns}\n\n"
        "Geef een JSON-object terug waarbij de sleutels de VEREISTE kolomnamen zijn "
        "en de waarden de overeenkomende GEÜPLOADE kolomnamen. "
        "Neem alleen kolommen op waarbij je zeker bent van de overeenkomst op basis van "
        "betekenis of naamgelijkenis (bijv. 'leeftijd' → 'StudentAge', 'verzuim' → 'absence_unauthorized'). "
        "Geef uitsluitend het JSON-object terug, zonder uitleg of markdown.\n\n"
        'Voorbeeld: {"StudentAge": "leeftijd", "absence_unauthorized": "ongeoorloofd_verzuim"}'
    )
    response = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "{"},
        ],
    )
    raw = "{" + response.content[0].text.strip()
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    try:
        mapping = json.loads(json_match.group()) if json_match else {}
    except Exception:
        mapping = {}
    return {"mapping": mapping}
```

The `{"role": "assistant", "content": "{"}` prefill forces the model to continue with valid JSON; we prepend the `{` ourselves when parsing.

- [ ] **Step 3.3: Run both map_columns tests — expect PASS**

```bash
cd eduplan && uv run pytest tests/test_backend.py::test_map_columns_returns_mapping tests/test_backend.py::test_map_columns_invalid_json_returns_empty -v
```

Expected: both PASS.

- [ ] **Step 3.4: Run full suite to confirm no regression**

```bash
cd eduplan && uv run pytest tests/ -v
```

Expected: all green.

- [ ] **Step 3.5: Commit**

```bash
cd eduplan && git add backend/main.py tests/test_backend.py
git commit -m "$(cat <<'EOF'
eduplan: migrate /map_columns to Anthropic with assistant-prefill JSON

Uses assistant-turn prefill ("{") to force well-formed JSON output from Sonnet 4.6.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Migrate `/explain_risk` endpoint (largest, 4 tests touch it)

**Files:**
- Modify: `eduplan/backend/main.py` (the LLM call inside `explain_risk`, around lines 573–582)
- Modify: `eduplan/tests/test_backend.py` (4 tests: `test_explain_risk_returns_sectie1_html`, `test_explain_risk_llm_called_when_shap_sufficient`, `test_explain_risk_data_onvoldoende_skips_llm`, `test_explain_risk_laag_risico`)

- [ ] **Step 4.1: Swap fixtures + the .called assertion in all 4 explain_risk tests**

In `eduplan/tests/test_backend.py`, find every `mock_openai` parameter in the four `test_explain_risk_*` functions and rename to `mock_anthropic`. Also update the two assertions that check `.responses.create.called`:

- Line ~202: `assert mock_openai.responses.create.called` → `assert mock_anthropic.messages.create.called`
- Line ~215: `assert not mock_openai.responses.create.called` → `assert not mock_anthropic.messages.create.called`

- [ ] **Step 4.2: Run the 4 explain_risk tests — expect FAIL on the LLM-called assertions**

```bash
cd eduplan && uv run pytest tests/test_backend.py -k explain_risk -v
```

Expected: at least `test_explain_risk_llm_called_when_shap_sufficient` FAILS because the endpoint still uses `client.responses.create`, not `anthropic_client.messages.create`.

- [ ] **Step 4.3: Migrate the LLM call in explain_risk**

In `eduplan/backend/main.py`, find the block (currently around lines 573–582):

```python
    response = client.responses.create(
        model=MODEL,
        store=False,
        temperature=0.2,
        input=[{"role": "user", "content": prompt}],
    )
    sectie2_4 = response.output_text  # type: ignore

    # Converteer markdown naar HTML zodat de frontend het correct kan renderen
    sectie2_4_html = _markdown_to_html(sectie2_4)
```

Replace with:

```python
    response = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2048,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    sectie2_4 = response.content[0].text

    # Converteer markdown naar HTML zodat de frontend het correct kan renderen
    sectie2_4_html = _markdown_to_html(sectie2_4)
```

- [ ] **Step 4.4: Run the 4 explain_risk tests — expect PASS**

```bash
cd eduplan && uv run pytest tests/test_backend.py -k explain_risk -v
```

Expected: all 4 PASS.

- [ ] **Step 4.5: Run full suite to confirm no regression**

```bash
cd eduplan && uv run pytest tests/ -v
```

Expected: all tests green. `mock_openai` fixture should now be unused by any test, but is still defined; that's fine — Task 5 removes it.

- [ ] **Step 4.6: Commit**

```bash
cd eduplan && git add backend/main.py tests/test_backend.py
git commit -m "$(cat <<'EOF'
eduplan: migrate /explain_risk to Anthropic Sonnet 4.6

Last of three LLM endpoints migrated. mock_openai fixture is now unused and will be removed in cleanup.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Cleanup — remove OpenAI client, dep, mock fixture, and root patch

**Files:**
- Modify: `eduplan/backend/main.py` (drop OpenAI import + client + MODEL constant)
- Modify: `eduplan/conftest.py` (drop OpenAI patch)
- Modify: `eduplan/tests/conftest.py` (drop mock_openai fixture)
- Modify: `eduplan/pyproject.toml` (drop openai dep)

- [ ] **Step 5.1: Verify no remaining references to OpenAI in code**

```bash
cd eduplan && grep -rn "openai\|OpenAI\|client\.responses\|output_text\|mock_openai" backend/ tests/ conftest.py
```

Expected: matches only in `conftest.py`, `tests/conftest.py` (the fixture and root patch) and `backend/main.py` (`from openai import OpenAI` + `client = OpenAI()` + `MODEL = ...`). If anything else shows up, fix it before continuing.

- [ ] **Step 5.2: Remove OpenAI import + client + MODEL from backend/main.py**

In `eduplan/backend/main.py`, delete the line `from openai import OpenAI`. Delete the lines `client = OpenAI()` and `MODEL = "gpt-5.4-mini-2026-03-17"`. Optionally rename `anthropic_client` → `client` for brevity (recommended — fewer renames are clearer). If renaming:
- Find all `anthropic_client.messages.create` (3 sites) and replace with `client.messages.create`.
- In `eduplan/tests/conftest.py`, change the `monkeypatch.setattr(main_mod, "anthropic_client", mock_client)` line in the `mock_anthropic` fixture to `monkeypatch.setattr(main_mod, "client", mock_client)`.

- [ ] **Step 5.3: Remove the OpenAI patch from root conftest.py**

Edit `eduplan/conftest.py` to:

```python
"""Root conftest — patcht Anthropic vóór backend.main wordt geïmporteerd.

Nodig omdat ALL_PROXY een SOCKS-proxy instelt die httpx niet aankan
zonder het optionele 'socksio'-pakket. De mock voorkomt dat de echte
Anthropic-client überhaupt wordt aangemaakt tijdens tests.
"""

from unittest.mock import MagicMock, patch

# Patch anthropic.Anthropic vóór elke import van backend.main
_anthropic_patcher = patch("anthropic.Anthropic", return_value=MagicMock())
_anthropic_patcher.start()
```

- [ ] **Step 5.4: Remove the mock_openai fixture from tests/conftest.py**

In `eduplan/tests/conftest.py`, delete the entire `mock_openai` fixture (the `@pytest.fixture\ndef mock_openai(monkeypatch) -> MagicMock:` block and its body).

- [ ] **Step 5.5: Remove openai dep from pyproject.toml**

In `eduplan/pyproject.toml`, remove the line `"openai>=2.26.0",` from `[project].dependencies`.

- [ ] **Step 5.6: Re-sync to drop openai from the lockfile**

```bash
cd eduplan && uv sync --extra dev
```

Expected: `openai` and its transitive deps are uninstalled; lockfile updates.

- [ ] **Step 5.7: Run full suite to confirm nothing regressed**

```bash
cd eduplan && uv run pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 5.8: Confirm import surface is clean**

```bash
cd eduplan && uv run python -c "import backend.main; print('OK')"
```

Expected: prints `OK`. No `ImportError` for `openai`.

- [ ] **Step 5.9: Commit**

```bash
cd eduplan && git add backend/main.py conftest.py tests/conftest.py pyproject.toml uv.lock
git commit -m "$(cat <<'EOF'
eduplan: drop OpenAI dep — fully migrated to Anthropic Sonnet 4.6

Removes openai import, client init, MODEL constant, mock_openai fixture, root OpenAI patch, and the dep itself.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Update documentation

**Files:**
- Modify: `eduplan/CLAUDE.md`
- Modify: `CLAUDE.md` (repo root)

- [ ] **Step 6.1: Update eduplan/CLAUDE.md provider references**

In `eduplan/CLAUDE.md`, find every reference to OpenAI / gpt-5.4-mini and adjust:

- Project Overview line "It uses a **RandomForestRegressor** … via an OpenAI model (the `MODEL` constant in `backend/main.py`)" → replace `OpenAI model (the `MODEL` constant ...)` with `Anthropic model (`claude-sonnet-4-6`, set via `ANTHROPIC_MODEL` in `backend/main.py`)`.
- Required Environment Variables section: change `OPENAI_API_KEY` line to `ANTHROPIC_API_KEY — used by the backend for LLM explanations (model set via the `ANTHROPIC_MODEL` constant in `backend/main.py`)`. Remove the separate `ANTHROPIC_API_KEY` line about `main.py` only — that one is now redundant because the same key powers both.
- "OpenAI Client" section heading and the code example: rename to "Anthropic Client" and update the example to:

  ```python
  response = client.messages.create(model=ANTHROPIC_MODEL, max_tokens=2048, ...)
  text = response.content[0].text  # NOT .output_text
  ```

  Update the trailing paragraph about the `mock_openai` fixture: replace with a description of `mock_anthropic` that mocks `mock_client.messages.create` and sets `mock_response.content = [MagicMock(text=...)]`.

- The bullet about `eduplan/conftest.py` patching `openai.OpenAI` → update to `anthropic.Anthropic`.

- [ ] **Step 6.2: Update root CLAUDE.md sub-project description**

In `CLAUDE.md` (repo root), find the EduPlan Sub-Project section. Change "Env vars: `OPENAI_API_KEY` (backend GPT-4.1 via Responses API), `ANTHROPIC_API_KEY` (standalone agent CLI only)" to: "Env vars: `ANTHROPIC_API_KEY` (backend Sonnet 4.6 via Messages API; also used by the standalone agent CLI)".

- [ ] **Step 6.3: Commit**

```bash
cd eduplan && git add CLAUDE.md ../CLAUDE.md
git commit -m "$(cat <<'EOF'
docs: update CLAUDE.md after Anthropic migration

Update provider references, env-var requirements, and client examples to reflect Sonnet 4.6 via Messages API.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Manual quality verification against real Anthropic API

This is the only task that actually validates the user's "met behoud van kwaliteit" requirement. The mock-based tests pass regardless of provider.

**Setup:**
- Confirm `ANTHROPIC_API_KEY` is set in the shell.
- Confirm backend default model file (`backend/model.joblib`) is present.

- [ ] **Step 7.1: Capture an "old" sample before merging (optional but recommended)**

If you can still run the OpenAI version (e.g., from `main` before merge):

```bash
git stash  # if uncommitted; or check out the pre-migration commit in a worktree
cd eduplan && ./1_start_fastapi.sh &
./2_start_streamlit.sh &
```

Pick 3 demo students from `shared/data.csv` at LAAG (<35%), MATIG (35–65%), and HOOG (≥65%) risk. Generate the EduPlan for each via the UI (UITNODIGINGSREGEL → select student → EDUPLAN → TOON EDUPLAN). Save the rendered explanation HTML to `/tmp/eduplan_openai_<risico>.html`.

Stop both processes; restore the branch.

- [ ] **Step 7.2: Start backend + frontend on the migrated branch**

```bash
cd eduplan && ./1_start_fastapi.sh
# In separate terminal:
cd eduplan && ./2_start_streamlit.sh
```

Backend: `http://localhost:8000` (docs at `/docs`). Frontend: `http://localhost:8502`.

- [ ] **Step 7.3: Smoke-test each endpoint via the Streamlit UI using chrome-devtools-mcp**

Per the user's standing preference (see memory `feedback_ui_smoke_test_after_migration.md`), pytest green ≠ feature working after provider swaps. Use chrome-devtools-mcp:

1. `mcp__plugin_chrome-devtools-mcp_chrome-devtools__new_page` → `http://localhost:8502`
2. Select an opleiding from the start screen.
3. UITNODIGINGSREGEL tab: confirm the ranking bar chart renders (this exercises `/rank_students` — no LLM, but verifies the app still works end-to-end).
4. EDUPLAN tab: pick the HOOG-risk student → click TOON EDUPLAN → wait for response (`/explain_risk` real API call). Confirm:
   - Section 1 (deterministic) renders correctly.
   - Sections 2–4 render with **rendered** headings (`<h2>`/`<h3>`), bold, lists — not raw markdown. (This was the previous regression — verify the heading fix from commit `8cd5cf1` still works.)
   - Dutch is natural, professional, and references only the listed factors (no hallucinated age/gender/verzuim numbers).
5. Repeat for MATIG and LAAG students.
6. Upload a CSV (use `shared/data.csv`) to trigger `/map_columns`. Confirm the column mapping JSON is parsed correctly.
7. Trigger `/summarize` if a UI path exists for it.

- [ ] **Step 7.4: Side-by-side quality eyeball (if Step 7.1 was done)**

Open `/tmp/eduplan_openai_<risico>.html` next to the new Anthropic output. Compare on:
- **Factor-grounding:** Does the new output stick to the listed SHAP factors, or hallucinate?
- **Dutch fluency:** Idiomatic? Professional MBO register?
- **Concreteness:** Are gespreksstarters and interventions specific, or vague?
- **Length:** Roughly equivalent? (max_tokens=2048 should be enough; if outputs are truncated, raise to 3072 in `explain_risk`.)

Record findings in a brief note. If quality is materially worse, this task does NOT pass — iterate on `max_tokens`, prompt phrasing, or fall back. If quality is on-par or better, proceed.

- [ ] **Step 7.5: Final commit (if any prompt/max_tokens adjustments were needed)**

```bash
cd eduplan && git add backend/main.py
git commit -m "$(cat <<'EOF'
eduplan: tune Sonnet 4.6 max_tokens / prompt after quality check

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 7.6: Push the full migration**

```bash
cd eduplan && git push
```

---

## Self-Review (against the spec)

**Spec coverage:**
- "Omzetten naar Anthropic Sonnet 4.6" → Tasks 1–5 (every callsite migrated, OpenAI dep removed). ✓
- "Met behoud van kwaliteit" → Task 7 (real-API quality check, side-by-side eyeball). ✓
- "Niet triviaal — drie callsites + tests + conftest patches" → addressed in Tasks 2–4 (one endpoint each) and Task 1 (dual conftest patch). ✓
- JSON-output endpoint (`/map_columns`) reliability with Anthropic → Task 3 uses assistant-prefill pattern. ✓
- Test suite must stay green at every checkpoint → each task ends with a full-suite run before commit. ✓

**Placeholders:** None. Every step has exact paths, exact code, and exact commands.

**Type consistency:** `ANTHROPIC_MODEL` (constant name) and `anthropic_client` (variable) — used consistently across Tasks 1–4. Task 5 optionally renames `anthropic_client` → `client`; that rename is explicit (3 callsites + 1 fixture line).

**Risk:** the optional rename in Step 5.2 could be skipped to reduce diff size. If it is skipped, Step 5.4 must NOT remove the `monkeypatch.setattr(main_mod, "anthropic_client", mock_client)` line — only `mock_openai` is removed.

---

## Execution Handoff

Plan complete and saved to `eduplan/docs/superpowers/plans/2026-05-18-anthropic-llm-migration.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration. Each task is small enough (~5–15 min) to dispatch independently.

**2. Inline Execution** — execute tasks in this session using executing-plans, with checkpoints between Tasks 1, 4, 5, and 7 for review.

Which approach?
