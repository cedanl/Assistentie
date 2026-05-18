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
