from sqlalchemy import inspect
from backend.models import StudentDB, HistorischStudentDB, AgentLogDB  # noqa: F401 — required for metadata registration


def test_student_table_heeft_alle_kolommen(test_engine):
    inspector = inspect(test_engine)
    kolommen = {c["name"] for c in inspector.get_columns("studenten")}
    verwacht = {
        "studentnummer",
        "naam",
        "email",
        "leeftijd",
        "geslacht",
        "vooropleiding",
        "sector",
        "opleiding",
        "crebocode",
        "cohort",
        "niveau",
        "leerweg",
        "intakedatum",
        "aanwezigheid",
        "voortgang",
        "bsa_studiepunten",
        "cijfer_nederlands",
        "cijfer_rekenen",
        "mentor_naam",
        "mentor_email",
    }
    assert verwacht.issubset(kolommen)


def test_historisch_student_heeft_uitgevallen_kolom(test_engine):
    inspector = inspect(test_engine)
    kolommen = {c["name"] for c in inspector.get_columns("historische_studenten")}
    assert "uitgevallen" in kolommen


def test_agent_log_tabel_bestaat(test_engine):
    inspector = inspect(test_engine)
    assert "agent_log" in inspector.get_table_names()
