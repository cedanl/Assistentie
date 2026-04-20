import hashlib
import time
from collections import defaultdict
from datetime import datetime, timezone
from backend.models import AgentLogDB

MAX_CALLS_PER_SESSIE = 60

class Harness:
    """
    Governance wrapper om agent tool-calls:
    - Whitelist: alleen geregistreerde tools
    - Rate limiting per sessie
    - Logging naar agent_log tabel (PII gehashed)
    """

    def __init__(self, handlers: dict, db):
        self.handlers = handlers
        self.db = db
        self._teller: dict[str, int] = defaultdict(int)

    def execute(self, tool_naam: str, inputs: dict, sessie_id: str) -> dict:
        if tool_naam not in self.handlers:
            return {"error": f"Tool '{tool_naam}' staat niet op de whitelist."}

        if self._teller[sessie_id] >= MAX_CALLS_PER_SESSIE:
            return {"error": "Rate limit bereikt voor deze sessie."}

        start = time.monotonic()
        self._teller[sessie_id] += 1

        try:
            result = self.handlers[tool_naam](**inputs)
        except Exception as e:
            result = {"error": str(e)}

        duur_ms = int((time.monotonic() - start) * 1000)
        self._log(tool_naam, inputs, result, sessie_id, duur_ms)
        return result

    def _hash_pii(self, tekst: str) -> str:
        return hashlib.sha256(tekst.encode()).hexdigest()[:12]

    def _log(self, tool_naam: str, inputs: dict, result: dict,
             sessie_id: str, duur_ms: int):
        input_str = str(inputs)
        input_hash = self._hash_pii(input_str)
        output_summary = str(result)[:200]
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
            pass
