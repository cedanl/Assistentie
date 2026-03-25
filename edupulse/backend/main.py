# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anthropic",
#     "pydantic",
#     "streamlit",
#     "pandas",
#     "scikit-learn",
#     "fastapi",
#     "uvicorn",
#     "openai",
#     "requests",
#     "plotly",
#     "shap",
#     "joblib"
# ]
# ///

# -----------------------------------------------------------------------------
# Organization: CEDA
# Original Authors: Ed. de Feber, Edwin Lieftink
# -----------------------------------------------------------------------------


"""backend/main.py

FastAPI backend — gebruikt Random Forest Regressor van Uitnodigingsregel.

"""

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from openai import OpenAI
import joblib
import os
import shap

api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

client = OpenAI()

MODEL = "gpt-4o"

# Laden van ML-model (RandomForestRegressor van Uitnodigingsregel)
clf = joblib.load("backend/model.joblib")

# Features zijn alle kolommen uit data.csv behalve weergave- en doelkolommen
_df = pd.read_csv("shared/data.csv")
NON_FEATURES = {"Dropout", "Naam", "Opleiding", "Klas", "Mentor"}
features = [col for col in _df.columns if col not in NON_FEATURES]

explainer = shap.TreeExplainer(clf)


class StudentData(BaseModel):
    student: dict

class SummaryRequest(BaseModel):
    data: str

class ExplainRequest(BaseModel):
    student: dict
    prediction: int
    probability: float


@app.post("/summarize")
def summarize(request: SummaryRequest):
    prompt = f"Vat deze BI-data samen voor het management (max 5 regels):\n{request.data}\nSamenvatting:"
    response = client.responses.create(
        model=MODEL,
        store=False,
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
        tool_choice="auto",
        input=[{"role": "user", "content": prompt}]
    )
    summary = response.output_text  # type: ignore
    return {"summary": summary}


@app.post("/predict_dropout")
def predict_dropout(request: StudentData):
    X_pred = pd.DataFrame([request.student])[features]
    # RF Regressor geeft een continue score (0–1); drempel 0.35 markeert risicostudenten
    score = float(clf.predict(X_pred.values)[0])
    return {"probability": score, "prediction": 1}


@app.post("/explain_risk")
def explain_risk(request: ExplainRequest):
    student = request.student
    probability = request.probability
    feature_str = ", ".join([f"{k}: {v}" for k, v in student.items()])
    prompt = (
        f"Studentgegevens: {feature_str}.\n"
        f"Voorspelde kans op uitval: {probability:.2%}.\n"
        f"Licht in heldere managementtaal toe waarom deze student risico loopt op uitval, "
        f"en geef gericht advies aan de mentor."
    )
    response = client.responses.create(
        model=MODEL,
        store=False,
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
        tool_choice="auto",
        input=[{"role": "user", "content": prompt}]
    )
    uitleg = response.output_text  # type: ignore
    return {"explanation": uitleg}


@app.post("/feature_importance")
def feature_importance(request: StudentData):
    X_pred = pd.DataFrame([request.student])[features]
    # RF Regressor: shap_values() geeft shape (n_samples, n_features), geen lijst per klasse
    shap_vals = explainer.shap_values(X_pred.values)
    fi = dict(zip(features, shap_vals[0].tolist()))
    return {"feature_importance": fi}
