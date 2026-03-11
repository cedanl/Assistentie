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
#     "shap"
# ]
# ///

# -----------------------------------------------------------------------------
# Organization: CEDA
# Original Authors: Ed. de Feber, Edwin Lieftink
# -----------------------------------------------------------------------------


"""backend/main.py

FastAPI backend 

"""

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from openai import OpenAI
import pickle
import os
import shap

api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

client = OpenAI()

MODEL = "gpt-4o-mini"

# Laden van ML-model
with open("backend/model.pkl", "rb") as f:
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
    response = client.responses.create(
        model=MODEL, 
        store=False, 
        tools=[
            {
                "type": "code_interpreter",
                "container": {"type": "auto"},
            }
        ],
        tool_choice="auto",  # Let the model use the code interpreter tool  
        # input=history,  # type: ignore
        input=[{"role": "user", "content": prompt}]
    )
    
    summary = response.output_text  # type: ignore
    print(summary)  # type: ignore
    
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
    
    response = client.responses.create(
        model=MODEL, 
        store=False, 
        tools=[
            {
                "type": "code_interpreter",
                "container": {"type": "auto"},
            }
        ],
        tool_choice="auto",  # Let the model use the code interpreter tool  
        # input=history,  # type: ignore
        input=[{"role": "user", "content": prompt}]
    )
    
    # response = openai.ChatCompletion.create(
        # model="gpt-4o",
        # messages=[{"role": "user", "content": prompt}]
    # )
    uitleg = response.output_text  # type: ignore
    return {"explanation": uitleg}

@app.post("/feature_importance")
def feature_importance(request: StudentData):
    X_pred = pd.DataFrame([request.student])[features]
    try:
        shap_vals = explainer.shap_values(X_pred)[1]
        print(shap_vals)
    except:
        shap_vals = explainer.shap_values(X_pred)[0]
        print(shap_vals)
    
    fi = dict(zip(features, shap_vals[0].tolist()))
    if fi:
        return {"feature_importance": fi}
    else:
        return {"feature_importance": "fi"}
        
    