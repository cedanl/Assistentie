import json
import uuid
from backend.agent.llm import LLMProvider
from backend.agent.harness import Harness
from backend.agent.tools import TOOL_DEFINITIONS

MAX_STAPPEN = 10

SYSTEM_PROMPT = """Je bent EduAgent, een harnessed digitale assistent voor MBO begeleiders.

Je helpt begeleiders inzicht te geven in het uitvalrisico van studenten.
Je gebruikt alleen de beschikbare tools om studentdata op te halen — verzin niets.
Geef altijd een concrete, begrijpelijke uitleg in het Nederlands.
Vermeld bij dreiging altijd de mentor-contactgegevens.
Sluit af met een concreet advies.

Beperkingen:
- Gebruik alleen de aangeboden tools
- Houd rekening met privacy (AVG): deel nooit onnodige persoonsgegevens
- Reageer in het Nederlands"""

class AgentKernel:
    def __init__(self, llm: LLMProvider, harness: Harness):
        self.llm = llm
        self.harness = harness

    def run(self, user_message: str, sessie_id: str | None = None) -> str:
        if sessie_id is None:
            sessie_id = str(uuid.uuid4())

        messages = [{"role": "user", "content": user_message}]

        for _ in range(MAX_STAPPEN):
            response = self.llm.chat(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                system=SYSTEM_PROMPT,
            )

            if response.stop_reason == "end_turn":
                tekst = " ".join(b.text for b in response.content if hasattr(b, "text")) or "Geen antwoord ontvangen."
                return tekst

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self.harness.execute(
                            block.name, block.input, sessie_id
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False, default=str),
                        })
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            else:
                return f"Onverwachte stop_reason: {response.stop_reason!r}."

        return "Maximale stappen bereikt. Probeer een specifiekere vraag."
