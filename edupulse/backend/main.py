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

MODEL = "gpt-4.1"

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


def _student_to_df(student: dict) -> pd.DataFrame:
    return pd.DataFrame([student])[features]


@app.post("/summarize")
def summarize(request: SummaryRequest):
    prompt = f"Vat deze BI-data samen voor het management (max 5 regels):\n{request.data}\nSamenvatting:"
    response = client.responses.create(
        model=MODEL,
        store=False,
        input=[{"role": "user", "content": prompt}]
    )
    summary = response.output_text  # type: ignore
    return {"summary": summary}


@app.post("/predict_dropout")
def predict_dropout(request: StudentData):
    X_pred = _student_to_df(request.student)
    score = float(clf.predict(X_pred.values)[0])
    # Drempel 0.35 markeert risicostudenten
    prediction = 1 if score >= 0.35 else 0
    return {"probability": score, "prediction": prediction}


@app.post("/explain_risk")
def explain_risk(request: ExplainRequest):
    student = request.student
    probability = request.probability
    feature_str = ", ".join(f"{k}: {v}" for k, v in student.items())
    prompt = (
        f"Studentgegevens: {feature_str}.\n"
        f"Voorspelde kans op uitval: {probability:.2%}.\n"
        f"Licht uitgebreid, in heldere managementtaal, toe waarom deze student risico loopt op uitval, "
        f"waarbij je je richt op deze drie elementen: 'Afwezigheid', 'Opleidingsachtergrond', en 'Aanmeldingsgeschiedenis'. "
        f"Geef daarnaast gericht advies aan de mentor. Gebruik de onderstaande opmaak van het voorbeeld. "
        f"Gebruik uitsluitend de bovenstaande studentgegevens; de getallen in het voorbeeld zijn fictief.\n\n"
        f"<VOORBEELD>\n"
        f"👩🏽‍💻ANALYSE VAN RISICO OP UITVAL\n\n"
        f"**✅ 1. Afwezigheid** De student heeft een aanzienlijke afwezigheid met [X] niet-gemelde en [Y] gemelde afwezigheden. "
        f"Dit kan leiden tot een verminderd leerresultaat en een afname van betrokkenheid bij de opleiding.\n\n"
        f"**🎯Advies:** De mentor moet proactief het contact met de student zoeken om te achterhalen wat de oorzaken van de afwezigheid zijn.\n\n"
        f"**✅ 2. Opleidingsachtergrond** De student komt uit een [vooropleiding]-achtergrond, wat betekent dat de student "
        f"mogelijk minder voorbereiding heeft gehad op de uitdagingen van het voortgezet onderwijs.\n\n"
        f"**🎯 Advies:** Het is belangrijk dat de mentor samen met docenten goed kijkt naar de studiemethoden van de student.\n\n"
        f"**✅ 3. Aanmeldingsgeschiedenis** De student heeft een aanmeldingsgeschiedenis van [Z], wat kan wijzen op "
        f"een beperkte betrokkenheid bij het onderwijs.\n\n"
        f"**🎯 Advies:** De mentor kan een gesprek aangaan om de interesses en lange-termijndoelen van de student in kaart te brengen.\n\n"
        f"### Conclusie\n\n"
        f"Gezien deze drie elementen loopt deze student risico op uitval. "
        f"Door een ondersteunende aanpak en open communicatie kan de mentor helpen om de student op koers te houden.\n"
        f"</VOORBEELD>"
    )
    response = client.responses.create(
        model=MODEL,
        store=False,
        input=[{"role": "user", "content": prompt}]
    )
    uitleg = response.output_text  # type: ignore
    return {"explanation": uitleg}


@app.post("/feature_importance")
def feature_importance(request: StudentData):
    X_pred = _student_to_df(request.student)
    # RF Regressor: shap_values() geeft shape (n_samples, n_features), geen lijst per klasse
    shap_vals = explainer.shap_values(X_pred.values)
    fi = dict(zip(features, shap_vals[0].tolist()))
    return {"feature_importance": fi}
