"""Tests voor backend/main.py — helperfuncties en FastAPI-endpoints."""

import time
from unittest.mock import MagicMock

import pytest

import backend.main as main_mod
from backend.main import (
    BINARY_LABELS,
    FEATURE_LABELS,
    _build_risicoprofiel_html,
    _factor_label,
    _get_model,
    features,
)

# ─────────────────────────────────────────────────────────────────────────────
# Helperfuncties
# ─────────────────────────────────────────────────────────────────────────────


def test_factor_label_binary_value_1():
    pos, _ = BINARY_LABELS["StudentGender"]
    assert _factor_label("StudentGender", 1) == pos


def test_factor_label_binary_value_0():
    _, neg = BINARY_LABELS["StudentGender"]
    assert _factor_label("StudentGender", 0) == neg


def test_factor_label_continuous_uses_feature_label():
    label = _factor_label("StudentAge", 22)
    assert FEATURE_LABELS["StudentAge"] in label
    assert "22" in label


def test_factor_label_unknown_key_falls_back_to_key():
    label = _factor_label("onbekend_kenmerk", 3.5)
    assert "onbekend_kenmerk" in label
    assert "3.5" in label


def test_build_risicoprofiel_hoog_bevat_risiconiveau():
    html = _build_risicoprofiel_html(
        student={
            "StudentAge": 20,
            "StudentGender": 1,
            "absence_unauthorized": 10.0,
            "absence_authorized": 0.0,
            "Aanmel_aantal": 1.0,
        },
        probability=0.75,
        risico_niveau="HOOG",
        urgentie="directe actie vereist (deze week)",
        top_factors=[("absence_unauthorized", 0.12)],
        imputed_set=set(),
        model_name="gpt-4.1",
    )
    assert "HOOG" in html
    assert "75%" in html


def test_build_risicoprofiel_matig():
    html = _build_risicoprofiel_html(
        student={"StudentAge": 22},
        probability=0.50,
        risico_niveau="MATIG",
        urgentie="actie aanbevolen binnen twee weken",
        top_factors=[],
        imputed_set=set(),
        model_name="gpt-4.1",
    )
    assert "MATIG" in html


def test_build_risicoprofiel_imputed_field_toont_niet_beschikbaar():
    html = _build_risicoprofiel_html(
        student={},
        probability=0.40,
        risico_niveau="MATIG",
        urgentie="actie aanbevolen binnen twee weken",
        top_factors=[],
        imputed_set={"StudentAge", "absence_unauthorized"},
        model_name="gpt-4.1",
    )
    assert "niet beschikbaar" in html


def test_build_risicoprofiel_data_onvoldoende_toont_waarschuwing():
    html = _build_risicoprofiel_html(
        student={},
        probability=0.30,
        risico_niveau="LAAG",
        urgentie="reguliere monitoring volstaat",
        top_factors=[("StudentAge", 0.001)],
        imputed_set={"StudentAge"},
        model_name="gpt-4.1",
        data_onvoldoende=True,
    )
    assert "Datakwaliteit" in html or "onvoldoende" in html.lower()


def test_get_model_default_returns_default_model():
    clf, exp = _get_model(use_default=True)
    assert clf is main_mod.clf_default
    assert exp is main_mod.explainer_default


def test_get_model_non_default_returns_active_model():
    clf, exp = _get_model(use_default=False)
    assert clf is main_mod.clf
    assert exp is main_mod.explainer


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints — voorspellingen (geen LLM nodig)
# ─────────────────────────────────────────────────────────────────────────────


def test_predict_dropout_probability_in_range(client, demo_student):
    resp = client.post("/predict_dropout", json={"student": demo_student})
    assert resp.status_code == 200
    data = resp.json()
    assert 0.0 <= data["probability"] <= 1.0
    assert data["prediction"] in (0, 1)


def test_predict_dropout_high_absence_higher_probability(client, demo_student):
    """Student met veel ongeoorloofd verzuim heeft hogere risicoscore dan weinig verzuim."""
    low = dict(demo_student, absence_unauthorized=0.0)
    high = dict(demo_student, absence_unauthorized=200.0)
    prob_low = client.post("/predict_dropout", json={"student": low}).json()["probability"]
    prob_high = client.post("/predict_dropout", json={"student": high}).json()["probability"]
    assert prob_high >= prob_low


def test_predict_dropout_uses_default_model_flag(client, demo_student):
    resp = client.post(
        "/predict_dropout",
        json={"student": demo_student, "use_default_model": True},
    )
    assert resp.status_code == 200
    assert "probability" in resp.json()


def test_feature_importance_returns_all_features(client, demo_student):
    resp = client.post("/feature_importance", json={"student": demo_student})
    assert resp.status_code == 200
    fi = resp.json()["feature_importance"]
    assert set(fi.keys()) == set(features)


def test_feature_importance_values_are_floats(client, demo_student):
    resp = client.post("/feature_importance", json={"student": demo_student})
    fi = resp.json()["feature_importance"]
    assert all(isinstance(v, float) for v in fi.values())


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints — uitleg (LLM gemockt)
# ─────────────────────────────────────────────────────────────────────────────


def test_explain_risk_returns_sectie1_html(client, demo_student, mock_openai):
    payload = {
        "student": demo_student,
        "prediction": 1,
        "probability": 0.70,
        "imputed_columns": [],
    }
    resp = client.post("/explain_risk", json=payload)
    assert resp.status_code == 200
    explanation = resp.json()["explanation"]
    assert "RISICOPROFIEL" in explanation
    assert "HOOG" in explanation


def test_explain_risk_llm_called_when_shap_sufficient(client, demo_student, mock_openai, monkeypatch):
    """Als SHAP-waarden informatief zijn (max >= 0.01), wordt de LLM aangeroepen."""
    import numpy as np

    import backend.main as main_mod

    # Overschrijf de SHAP-explainer zodat er altijd informatieve waarden terugkomen
    mock_exp = MagicMock()
    shap_array = np.zeros((1, len(main_mod.features)))
    # features[0] = Studentnummer zit in SHAP_EXCLUDE; gebruik index 1 (StudentAge)
    shap_array[0, 1] = 0.5  # één significante factor
    mock_exp.shap_values.return_value = shap_array
    monkeypatch.setattr(main_mod, "explainer", mock_exp)
    monkeypatch.setattr(main_mod, "explainer_default", mock_exp)

    payload = {
        "student": demo_student,
        "prediction": 1,
        "probability": 0.70,
        "imputed_columns": [],
    }
    client.post("/explain_risk", json=payload)
    assert mock_openai.responses.create.called


def test_explain_risk_data_onvoldoende_skips_llm(client, demo_student, mock_openai):
    """Als alle kolommen geïmputeerd zijn, wordt de LLM niet aangeroepen."""
    payload = {
        "student": demo_student,
        "prediction": 0,
        "probability": 0.30,
        "imputed_columns": features,  # alles geïmputeerd
    }
    resp = client.post("/explain_risk", json=payload)
    assert resp.status_code == 200
    assert not mock_openai.responses.create.called
    assert "Geen gepersonaliseerd advies" in resp.json()["explanation"]


def test_explain_risk_laag_risico(client, demo_student, mock_openai):
    payload = {
        "student": demo_student,
        "prediction": 0,
        "probability": 0.20,
        "imputed_columns": [],
    }
    resp = client.post("/explain_risk", json=payload)
    assert resp.status_code == 200
    assert "LAAG" in resp.json()["explanation"]


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints — LLM-afhankelijke endpoints
# ─────────────────────────────────────────────────────────────────────────────


def test_summarize_returns_summary(client, mock_openai):
    resp = client.post("/summarize", json={"data": "student1,student2"})
    assert resp.status_code == 200
    assert "summary" in resp.json()
    assert resp.json()["summary"] == "Gemockte LLM-uitvoer"


def test_map_columns_returns_mapping(client, mock_openai):
    mock_openai.responses.create.return_value.output_text = (
        '{"StudentAge": "leeftijd", "absence_unauthorized": "verzuim"}'
    )
    resp = client.post(
        "/map_columns",
        json={
            "uploaded_columns": ["leeftijd", "verzuim"],
            "required_columns": ["StudentAge", "absence_unauthorized"],
        },
    )
    assert resp.status_code == 200
    mapping = resp.json()["mapping"]
    assert mapping.get("StudentAge") == "leeftijd"


def test_map_columns_invalid_json_returns_empty(client, mock_openai):
    """Ongeldige LLM-output levert een leeg mapping-object op (geen crash)."""
    mock_openai.responses.create.return_value.output_text = "geen json hier"
    resp = client.post(
        "/map_columns",
        json={"uploaded_columns": ["x"], "required_columns": ["StudentAge"]},
    )
    assert resp.status_code == 200
    assert resp.json()["mapping"] == {}


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints — modeltraining en -beheer
# ─────────────────────────────────────────────────────────────────────────────


def test_train_status_returns_status(client):
    resp = client.get("/train_status")
    assert resp.status_code == 200
    assert resp.json()["status"] in ("idle", "training", "done", "failed")


def test_reset_model_returns_reset(client):
    resp = client.delete("/reset_model")
    assert resp.status_code == 200
    assert resp.json()["status"] == "reset"


def test_reset_model_sets_status_idle(client):
    client.delete("/reset_model")
    resp = client.get("/train_status")
    assert resp.json()["status"] == "idle"


def test_train_model_endpoint_starts(client, demo_student):
    """Training start asynchroon; endpoint geeft direct 'started' of 'already_running' terug."""
    rows = [dict(demo_student, Dropout=float(i % 2)) for i in range(35)]
    payload = {"data": rows, "dropout_column": "Dropout"}
    resp = client.post("/train_model", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] in ("started", "already_running")

    try:
        # Wacht max 60 seconden tot training klaar is
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            status_resp = client.get("/train_status")
            if status_resp.json()["status"] in ("done", "failed"):
                break
            time.sleep(1)
        else:
            pytest.fail("Training voltooide niet binnen 60 seconden")
    finally:
        # Altijd terugzetten naar standaardmodel, ook bij testfout
        client.delete("/reset_model")
