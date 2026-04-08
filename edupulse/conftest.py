"""Root conftest — patcht OpenAI vóór backend.main wordt geïmporteerd.

Nodig omdat ALL_PROXY een SOCKS-proxy instelt die httpx niet aankan
zonder het optionele 'socksio'-pakket. De mock voorkomt dat de echte
OpenAI-client überhaupt wordt aangemaakt tijdens tests.
"""

from unittest.mock import MagicMock, patch

# Patch openai.OpenAI vóór elke import van backend.main
_openai_patcher = patch("openai.OpenAI", return_value=MagicMock())
_openai_patcher.start()
