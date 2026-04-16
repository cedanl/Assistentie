# Agents

Deze map is gereserveerd voor toekomstige AI-agents en autonome componenten.

## Huidige agent — `main.py` (root)

De standalone Claude-agent CLI bevindt zich in `main.py` in de projectroot.
Het is een onafhankelijke tool, los van de FastAPI/Streamlit applicatie.

**Mogelijkheden:**
- Bestanden lezen (`read_file`)
- Bestanden oplijsten (`list_files`)
- Bestanden aanmaken en bewerken (`edit_file`)

**Starten:**
```bash
python main.py
# of met expliciete API-key:
python main.py --api-key sk-ant-...
```

Vereist `ANTHROPIC_API_KEY` als omgevingsvariabele of via `--api-key`.
Gebruikt een Claude Sonnet-model via de Anthropic API.
Logs worden weggeschreven naar `agent.log`.
