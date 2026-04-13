"""Gedeelde fixtures voor EduPulse tests.

Voer tests uit vanuit de edupulse/ map:
    cd edupulse && uv run pytest tests/
"""

from unittest.mock import MagicMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def demo_student() -> dict:
    """Eerste rij uit demo-data als volledig geldige student-dict."""
    df = pd.read_csv("shared/data.csv")
    NON_FEATURES = {"Dropout", "Naam", "Opleiding", "Klas", "Mentor"}
    feat_cols = [c for c in df.columns if c not in NON_FEATURES]
    return df[feat_cols].iloc[0].to_dict()


@pytest.fixture
def mock_openai(monkeypatch) -> MagicMock:
    """Vervangt de OpenAI-client in backend.main door een mock."""
    mock_response = MagicMock()
    mock_response.output_text = "Gemockte LLM-uitvoer"
    mock_client = MagicMock()
    mock_client.responses.create.return_value = mock_response
    import backend.main as main_mod
    monkeypatch.setattr(main_mod, "client", mock_client)
    return mock_client
