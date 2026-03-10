"""backend/main.py

FastAPI backend 

"""

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import openai
import pickle
import os
import shap

openai.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

# Laden van ML-model
with open("model.pkl", "rb") as f:
    clf = pickle.load(f)
	
	
features = ["Cijfer", "Aanwezigheid", "Waarschuwingen", "EC"]
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
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    summary = response.choices[0].message["content"]
    return {"summary": summary}

@app.post("/predict_dropout")
def predict_dropout(request: StudentData):
    X_pred = pd.DataFrame([request.student])[features]
    prob = float(clf.predict_proba(X_pred)[0][1])
    label = int(prob > 0.35)
    return {"probability": prob, "prediction": label}

@app.post("/explain_risk")
def explain_risk(request: ExplainRequest):
    student = request.student
    prediction = request.prediction
    probability = request.probability
    feature_str = ", ".join([f"{k}: {v}" for k,v in student.items()])
    prompt = (
        f"Studentgegevens: {feature_str}.\n"
        f"Voorspelde kans op uitval: {probability:.2%}.\n"
        f"Licht in heldere managementtaal toe waarom deze student risico loopt op uitval, en geef gericht advies aan de mentor."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    uitleg = response.choices[0].message["content"]
    return {"explanation": uitleg}

@app.post("/feature_importance")
def feature_importance(request: StudentData):
    X_pred = pd.DataFrame([request.student])[features]
    shap_vals = explainer.shap_values(X_pred)[1]
    fi = dict(zip(features, shap_vals[0].tolist()))
    return {"feature_importance": fi}