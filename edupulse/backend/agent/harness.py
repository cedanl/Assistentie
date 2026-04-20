import hashlib
import time
from collections import defaultdict
from datetime import datetime, timezone
from backend.models import AgentLogDB

MAX_CALLS_PER_SESSIE = 60

# Module-level counter zodat rate limiting werkt over meerdere HTTP-requests heen.
_sessie_teller: dict[str, int] = defaultdict(int)


class Harness:
    """
    Governance wrapper om agent tool-calls:
    - Whitelist: alleen geregistreerde tools
    - Rate limiting per sessie (persistent over requests)
    - Logging naar agent_log tabel (PII gehashed, output geanonimiseerd)
    """

    def __init__(self, handlers: dict, db):
        self.handlers = handlers
        self.db = db

    def execute(self, tool_naam: str, inputs: dict, sessie_id: str) -> dict:
        if tool_naam not in self.handlers:
            result = {"error": f"Tool '{tool_naam}' staat niet op de whitelist."}
            self._log(tool_naam, inputs, result, sessie_id, 0, status="geblokkeerd")
            return result

        if _sessie_teller[sessie_id] >= MAX_CALLS_PER_SESSIE:
            result = {"error": "Rate limit bereikt voor deze sessie."}
            self._log(tool_naam, inputs, result, sessie_id, 0, status="rate_limit")
            return result

        start = time.monotonic()
        _sessie_teller[sessie_id] += 1

        try:
            result = self.handlers[tool_naam](**inputs)
            status = "ok"
        except Exception as e:
            result = {"error": str(e)}
            status = "error"

        duur_ms = int((time.monotonic() - start) * 1000)
        self._log(tool_naam, inputs, result, sessie_id, duur_ms, status=status)
        return result

    def _hash_pii(self, tekst: str) -> str:
        return hashlib.sha256(tekst.encode()).hexdigest()[:12]

    def _log(self, tool_naam: str, inputs: dict, result: dict,
             sessie_id: str, duur_ms: int, status: str = "ok"):
        import json
        import logging
        input_str = str(inputs)
        input_hash = self._hash_pii(input_str)
        # Sla geen PII op in output_summary — alleen type en omvang van het resultaat.
        output_summary = json.dumps({
            "status": status,
            "items": len(result) if isinstance(result, list) else (0 if "error" in result else 1),
        })
        try:
            log = AgentLogDB(
                timestamp=datetime.now(timezone.utc),
                sessie_id=sessie_id,
                gebruiker="system",
                tool_naam=tool_naam,
                input_hash=input_hash,
                output_summary=output_summary,
                duur_ms=duur_ms,
            )
            self.db.add(log)
            self.db.commit()
        except Exception:
            logging.exception("AgentLogDB write mislukt voor sessie %s", sessie_id)
