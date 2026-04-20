# backend/main.py
import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import get_db, engine, Base
from backend.models import StudentDB, StudentSchema, ChatRequest, ChatResponse, RisicoPredictie
from backend.agent.llm import ClaudeLLMProvider
from backend.agent.tools import ToolRegistry
from backend.agent.harness import Harness
from backend.agent.kernel import AgentKernel
from backend.ml.predict import RisicoPredictor, DREMPEL

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")
FEATURE_PATH = os.path.join(DATA_DIR, "feature_list.json")

predictor: RisicoPredictor | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    Base.metadata.create_all(bind=engine)
    if os.path.exists(MODEL_PATH):
        predictor = RisicoPredictor(model_path=MODEL_PATH, feature_path=FEATURE_PATH)
    app.state.llm = ClaudeLLMProvider()
    yield

app = FastAPI(title="EduPulse API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8503", "http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _get_kernel(request: Request, db: Session = Depends(get_db)) -> AgentKernel:
    if predictor is None:
        raise HTTPException(503, "Model nog niet geladen — run train.py eerst.")
    registry = ToolRegistry(db=db, predictor=predictor)
    harness = Harness(handlers=registry.get_handlers(), db=db)
    return AgentKernel(llm=request.app.state.llm, harness=harness)

@app.get("/health")
def health():
    return {"status": "ok", "model_geladen": predictor is not None}

@app.get("/students", response_model=list[StudentSchema])
def list_students(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(StudentDB).offset(skip).limit(limit).all()

@app.get("/students/{studentnummer}", response_model=StudentSchema)
def get_student(studentnummer: str, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter_by(studentnummer=studentnummer).first()
    if not student:
        raise HTTPException(404, f"Student {studentnummer!r} niet gevonden.")
    return student

@app.get("/risk/{studentnummer}", response_model=RisicoPredictie)
def get_risk(studentnummer: str, db: Session = Depends(get_db)):
    if predictor is None:
        raise HTTPException(503, "Model nog niet geladen — run train.py eerst.")
    student = db.query(StudentDB).filter_by(studentnummer=studentnummer).first()
    if not student:
        raise HTTPException(404, f"Student {studentnummer!r} niet gevonden.")
    data = StudentSchema.model_validate(student).model_dump()
    result = predictor.predict(data)
    return RisicoPredictie(
        studentnummer=studentnummer,
        uitval_kans=result["kans"],
        succes_kans=round(1 - result["kans"], 4),
        status="dreiging" if result["kans"] >= DREMPEL else "op_koers",
        shap_top3=result["shap_top3"],
    )

@app.post("/agent/chat", response_model=ChatResponse)
def agent_chat(chat_request: ChatRequest, kernel: AgentKernel = Depends(_get_kernel)):
    sessie_id = chat_request.session_id or str(uuid.uuid4())
    try:
        antwoord = kernel.run(chat_request.message, sessie_id=sessie_id)
    except Exception:
        import logging
        logging.exception("Agent fout voor sessie %s", sessie_id)
        raise HTTPException(503, "Agent tijdelijk niet beschikbaar.")
    return ChatResponse(session_id=sessie_id, response=antwoord)
