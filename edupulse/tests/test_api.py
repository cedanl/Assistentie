# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="module")
def client():
    with patch("backend.agent.kernel.AgentKernel.run", return_value="Test antwoord van agent."):
        from backend.main import app
        with TestClient(app) as c:
            yield c

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_list_students(client):
    r = client.get("/students?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_get_student_bestaat(client):
    studenten = client.get("/students?limit=1").json()
    if studenten:
        nr = studenten[0]["studentnummer"]
        r = client.get(f"/students/{nr}")
        assert r.status_code == 200
        assert r.json()["studentnummer"] == nr

def test_get_student_niet_gevonden(client):
    r = client.get("/students/BESTAATNIET")
    assert r.status_code == 404

def test_risk_endpoint(client):
    studenten = client.get("/students?limit=1").json()
    if studenten:
        nr = studenten[0]["studentnummer"]
        r = client.get(f"/risk/{nr}")
        assert r.status_code == 200
        assert "uitval_kans" in r.json()

def test_agent_chat(client):
    r = client.post("/agent/chat", json={"message": "Hoe staat student 20240001 ervoor?"})
    assert r.status_code == 200
    assert "response" in r.json()
    assert "session_id" in r.json()
