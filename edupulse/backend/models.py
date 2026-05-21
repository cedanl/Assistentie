from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String
from pydantic import BaseModel, ConfigDict
from backend.database import Base


class StudentDB(Base):
    __tablename__ = "studenten"
    studentnummer = Column(String, primary_key=True, index=True)
    naam = Column(String, nullable=False)
    email = Column(String, nullable=False)
    leeftijd = Column(Integer, nullable=False)
    geslacht = Column(String, nullable=False)
    vooropleiding = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    opleiding = Column(String, nullable=False)
    crebocode = Column(String, nullable=False)
    cohort = Column(String, nullable=False)
    niveau = Column(Integer, nullable=False)
    leerweg = Column(String, nullable=False)
    intakedatum = Column(Date, nullable=False)
    aanwezigheid = Column(Float, nullable=False)
    voortgang = Column(Float, nullable=False)
    bsa_studiepunten = Column(Integer, nullable=False)
    cijfer_nederlands = Column(Float, nullable=False)
    cijfer_rekenen = Column(Float, nullable=False)
    mentor_naam = Column(String, nullable=False)
    mentor_email = Column(String, nullable=False)


class HistorischStudentDB(Base):
    __tablename__ = "historische_studenten"
    id = Column(Integer, primary_key=True, autoincrement=True)
    studentnummer = Column(String, index=True)
    naam = Column(String)
    email = Column(String)
    leeftijd = Column(Integer)
    geslacht = Column(String)
    vooropleiding = Column(String)
    sector = Column(String)
    opleiding = Column(String)
    crebocode = Column(String)
    cohort = Column(String)
    niveau = Column(Integer)
    leerweg = Column(String)
    intakedatum = Column(Date)
    aanwezigheid = Column(Float)
    voortgang = Column(Float)
    bsa_studiepunten = Column(Integer)
    cijfer_nederlands = Column(Float)
    cijfer_rekenen = Column(Float)
    mentor_naam = Column(String)
    mentor_email = Column(String)
    uitgevallen = Column(Boolean, nullable=False)


class AgentLogDB(Base):
    __tablename__ = "agent_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sessie_id = Column(String, index=True)
    gebruiker = Column(String)
    tool_naam = Column(String)
    input_hash = Column(String)
    output_summary = Column(String)
    duur_ms = Column(Integer)


# Pydantic schemas
class StudentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    studentnummer: str
    naam: str
    email: str
    leeftijd: int
    geslacht: str
    vooropleiding: str
    sector: str
    opleiding: str
    crebocode: str
    cohort: str
    niveau: int
    leerweg: str
    intakedatum: date
    aanwezigheid: float
    voortgang: float
    bsa_studiepunten: int
    cijfer_nederlands: float
    cijfer_rekenen: float
    mentor_naam: str
    mentor_email: str


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str


class RisicoPredictie(BaseModel):
    studentnummer: str
    uitval_kans: float
    succes_kans: float
    status: str
    shap_top3: list[dict]
