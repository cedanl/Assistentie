from abc import ABC, abstractmethod
from typing import Any
import anthropic


class LLMProvider(ABC):
    """Model-agnostische interface — swap Claude voor Ollama/lokaal zonder agent-logica te wijzigen."""

    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict], system: str) -> Any: ...


class ClaudeLLMProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic()
        self.model = model

    def chat(self, messages: list[dict], tools: list[dict], system: str) -> Any:
        return self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            tools=tools if tools else anthropic.NOT_GIVEN,
            messages=messages,
        )
