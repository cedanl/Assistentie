import pytest
from sqlalchemy import inspect
from backend.database import engine, Base
from backend.models import StudentDB, HistorischStudentDB, AgentLogDB


def test_student_table_heeft_alle_kolommen():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    kolommen = {c["name"] for c in inspector.get_columns("studenten")}
    verwacht = {
        "studentnummer", "naam", "email", "leeftijd", "geslacht",
        "vooropleiding", "sector", "opleiding", "crebocode", "cohort",
        "niveau", "leerweg", "intakedatum", "aanwezigheid", "voortgang",
        "bsa_studiepunten", "cijfer_nederlands", "cijfer_rekenen",
        "mentor_naam", "mentor_email"
    }
    assert verwacht.issubset(kolommen)


def test_historisch_student_heeft_uitgevallen_kolom():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    kolommen = {c["name"] for c in inspector.get_columns("historische_studenten")}
    assert "uitgevallen" in kolommen


def test_agent_log_tabel_bestaat():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    assert "agent_log" in inspector.get_table_names()
