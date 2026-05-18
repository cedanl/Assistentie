# tests/test_tools.py
import pytest
from datetime import date
from unittest.mock import MagicMock
from backend.agent.tools import ToolRegistry
from backend.models import StudentDB


@pytest.fixture
def mock_student():
    s = MagicMock(spec=StudentDB)
    s.studentnummer = "20240001"
    s.naam = "Test Student"
    s.email = "t.student@roc.nl"
    s.leeftijd = 20
    s.geslacht = "M"
    s.vooropleiding = "VMBO-T"
    s.sector = "Techniek"
    s.opleiding = "Software Developer"
    s.crebocode = "25604"
    s.cohort = "2024-2025"
    s.niveau = 4
    s.leerweg = "BOL"
    s.intakedatum = date(2024, 9, 1)
    s.aanwezigheid = 0.52
    s.voortgang = 0.61
    s.bsa_studiepunten = 34
    s.cijfer_nederlands = 6.2
    s.cijfer_rekenen = 5.8
    s.mentor_naam = "Jan de Vries"
    s.mentor_email = "j.devries@roc.nl"
    return s


@pytest.fixture
def registry(mock_student):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = mock_student
    db.query.return_value.all.return_value = [mock_student]
    # For filter().limit().all() chain in search_students:
    db.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_student]
    # For filter().all() chain in get_cohort_comparison:
    db.query.return_value.filter.return_value.all.return_value = [mock_student]
    predictor = MagicMock()
    predictor.predict.return_value = {
        "kans": 0.42,
        "shap_top3": [
            {"feature": "aanwezigheid", "bijdrage": -0.25},
            {"feature": "voortgang", "bijdrage": -0.15},
            {"feature": "cijfer_rekenen", "bijdrage": -0.08},
        ],
    }
    return ToolRegistry(db=db, predictor=predictor)


def test_get_student_data_geeft_profiel(registry):
    result = registry.get_student_data("20240001")
    assert result["studentnummer"] == "20240001"
    assert result["naam"] == "Test Student"


def test_predict_dropout_risk_geeft_kans(registry):
    result = registry.predict_dropout_risk("20240001")
    assert "uitval_kans" in result
    assert result["status"] == "dreiging"
    assert len(result["shap_top3"]) == 3


def test_get_mentor_info(registry):
    result = registry.get_mentor_info("20240001")
    assert result["mentor_naam"] == "Jan de Vries"
    assert result["mentor_email"] == "j.devries@roc.nl"


def test_student_niet_gevonden(registry):
    registry.db.query.return_value.filter_by.return_value.first.return_value = None
    result = registry.get_student_data("99999")
    assert "error" in result


def test_tool_handlers_volledig(registry):
    handlers = registry.get_handlers()
    for naam in [
        "get_student_data",
        "predict_dropout_risk",
        "get_cohort_comparison",
        "get_mentor_info",
        "search_students",
    ]:
        assert naam in handlers


def test_get_cohort_comparison(registry):
    result = registry.get_cohort_comparison("20240001")
    assert "cohortgemiddelde" in result
    assert "student" in result
    assert "aantal_cohortgenoten" in result


def test_search_students_geeft_resultaten(registry):
    result = registry.search_students("Test")
    assert isinstance(result, list)
    assert len(result) >= 1
    assert result[0]["studentnummer"] == "20240001"
