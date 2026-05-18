"""Root conftest — patcht Anthropic vóór backend.main wordt geïmporteerd.

Nodig omdat ALL_PROXY een SOCKS-proxy instelt die httpx niet aankan
zonder het optionele 'socksio'-pakket. De mock voorkomt dat de echte
Anthropic-client überhaupt wordt aangemaakt tijdens tests.
"""

from unittest.mock import MagicMock, patch

# Patch anthropic.Anthropic vóór elke import van backend.main
_anthropic_patcher = patch("anthropic.Anthropic", return_value=MagicMock())
_anthropic_patcher.start()
