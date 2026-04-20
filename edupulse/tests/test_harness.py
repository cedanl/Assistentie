# tests/test_harness.py
from unittest.mock import MagicMock, patch
from backend.agent.harness import Harness, MAX_CALLS_PER_SESSIE

def maak_harness(handlers=None):
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    if handlers is None:
        handlers = {"test_tool": lambda **kw: {"ok": True}}
    return Harness(handlers=handlers, db=db)

def test_bekende_tool_wordt_uitgevoerd():
    h = maak_harness()
    result = h.execute("test_tool", {}, "sessie-1")
    assert result == {"ok": True}

def test_onbekende_tool_geeft_fout():
    h = maak_harness()
    result = h.execute("niet_bestaand", {}, "sessie-1")
    assert "error" in result

def test_onbekende_tool_wordt_gelogd():
    h = maak_harness()
    h.execute("niet_bestaand", {}, "sessie-1")
    h.db.add.assert_called()

def test_rate_limit_na_max_calls():
    h = maak_harness()
    for _ in range(MAX_CALLS_PER_SESSIE):
        h.execute("test_tool", {}, "sessie-2")
    result = h.execute("test_tool", {}, "sessie-2")
    assert "error" in result
    assert "rate limit" in result["error"].lower() or "Rate limit" in result["error"]

def test_rate_limit_per_sessie_onafhankelijk():
    h = maak_harness()
    for _ in range(MAX_CALLS_PER_SESSIE):
        h.execute("test_tool", {}, "sessie-A")
    result = h.execute("test_tool", {}, "sessie-B")
    assert result == {"ok": True}
