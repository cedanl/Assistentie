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
import json
import re
import shap
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import backend.trainer as trainer

api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

client = OpenAI()

MODEL = "gpt-4.1"

# Modelpaden
MODEL_DEFAULT_PATH = "backend/model.joblib"
MODEL_CUSTOM_PATH  = "backend/model_custom.joblib"

# Features zijn alle kolommen uit data.csv behalve weergave- en doelkolommen
_df = pd.read_csv("shared/data.csv")
NON_FEATURES = {"Dropout", "Naam", "Opleiding", "Klas", "Mentor"}
features = [col for col in _df.columns if col not in NON_FEATURES]

# Standaardmodel — altijd geladen, gebruikt bij demo-data
clf_default      = joblib.load(MODEL_DEFAULT_PATH)
explainer_default = shap.TreeExplainer(clf_default)

# Instellingsmodel — geladen indien beschikbaar; anders alias op standaard
if os.path.exists(MODEL_CUSTOM_PATH):
    clf_custom      = joblib.load(MODEL_CUSTOM_PATH)
    explainer_custom = shap.TreeExplainer(clf_custom)
else:
    clf_custom      = clf_default
    explainer_custom = explainer_default

# Actief model (voor /train_model en /reset_model)
clf      = clf_custom
explainer = explainer_custom


def _get_model(use_default: bool):
    """Geef het juiste (clf, explainer)-paar terug op basis van de vlag."""
    if use_default:
        return clf_default, explainer_default
    return clf, explainer


# ── Trainingstoestand ─────────────────────────────────────────────────────────

@dataclass
class _TrainingState:
    status:  str = "idle"   # idle | training | done | failed
    message: str = ""
    lock: threading.Lock = field(default_factory=threading.Lock)

_training = _TrainingState()


def _reload_model(path: str) -> None:
    """Laad model en explainer opnieuw en vervang de globale referenties atomisch."""
    global clf, explainer
    new_clf      = joblib.load(path)
    new_explainer = shap.TreeExplainer(new_clf)
    # Python-naam-toewijzing is atomisch onder de GIL; beide globals worden samen vervangen
    clf      = new_clf
    explainer = new_explainer


class StudentData(BaseModel):
    student:           dict
    use_default_model: bool = False

class SummaryRequest(BaseModel):
    data: str

class ExplainRequest(BaseModel):
    student:           dict
    prediction:        int
    probability:       float
    use_default_model: bool = False

class MapColumnsRequest(BaseModel):
    uploaded_columns: list[str]
    required_columns: list[str]

class TrainRequest(BaseModel):
    data:             list[dict]
    dropout_column:   str        = "Dropout"
    rf_parameters:    dict | None = None


# Nederlandse labels voor modelfeatures (voor leesbare SHAP-toelichting)
FEATURE_LABELS: dict[str, str] = {
    "StudentAge":             "Leeftijd (jaar)",
    "StudentGender":          "Geslacht",
    "Aanmel_aantal":          "Aantal aanmeldingen",
    "max1studie":             "Slechts één studie ooit",
    "ROCMondriaan":           "Eerder bij ROC Mondriaan",
    "Richting_nan":           "Opleidingsrichting onbekend",
    "absence_unauthorized":   "Ongeoorloofd verzuim (dagen)",
    "absence_authorized":     "Geoorloofd verzuim (dagen)",
    "Economie":               "Sector: Economie",
    "Landbouw":               "Sector: Landbouw",
    "Techniek":               "Sector: Techniek",
    "DSV":                    "Sector: DSV",
    "Zorgenwelzijn":          "Sector: Zorg & Welzijn",
    "Anders":                 "Sector: Anders",
    "VooroplNiveau_HAVO":     "Vooropleiding: HAVO",
    "VooroplNiveau_MBO":      "Vooropleiding: MBO",
    "VooroplNiveau_basis":    "Vooropleiding: Basisonderwijs",
    "VooroplNiveau_educatie": "Vooropleiding: Educatie",
    "VooroplNiveau_prak":     "Vooropleiding: Praktijkonderwijs",
    "VooroplNiveau_VMBO_BB":  "Vooropleiding: VMBO-BB",
    "VooroplNiveau_VMBO_GL":  "Vooropleiding: VMBO-GL",
    "VooroplNiveau_VMBO_KB":  "Vooropleiding: VMBO-KB",
    "VooroplNiveau_VMBO_TL":  "Vooropleiding: VMBO-TL",
    "VooroplNiveau_nan":      "Vooropleiding: onbekend",
    "VooroplNiveau_VWOplus":  "Vooropleiding: VWO of hoger",
    "VooroplNiveau_other":    "Vooropleiding: anders",
}

# Features die geen inhoudelijke risicofactor zijn (niet opnemen in SHAP-toelichting)
SHAP_EXCLUDE = {"Studentnummer"}


def _student_to_df(student: dict) -> pd.DataFrame:
    return pd.DataFrame([student])[features]


def _decode_student_profile(student: dict) -> str:
    """Vertaal ruwe modelfeatures naar leesbaar Nederlands profiel voor de prompt."""
    lines = []

    age = student.get("StudentAge", "?")
    gender_raw = student.get("StudentGender")
    gender = "Man" if gender_raw == 1 else ("Vrouw" if gender_raw == 0 else "Onbekend")

    lines.append(f"Leeftijd: {age} jaar")
    lines.append(f"Geslacht: {gender}")
    lines.append(f"Ongeoorloofd verzuim: {student.get('absence_unauthorized', 0):.1f} dagen")
    lines.append(f"Geoorloofd verzuim: {student.get('absence_authorized', 0):.1f} dagen")
    lines.append(f"Aantal aanmeldingen (voor deze opleiding): {int(student.get('Aanmel_aantal', 1))}")

    max1 = student.get("max1studie")
    if max1 == 1:
        lines.append("Studie-ervaring: dit is de enige inschrijving ooit (geen eerdere studies)")
    elif max1 == 0:
        lines.append("Studie-ervaring: eerder ingeschreven geweest (studieswitch of herhaling)")

    if student.get("ROCMondriaan") == 1:
        lines.append("Eerder ingeschreven bij ROC Mondriaan: ja")

    sector_cols = {
        "Economie": "Economie", "Landbouw": "Landbouw", "Techniek": "Techniek",
        "DSV": "DSV", "Zorgenwelzijn": "Zorg & Welzijn", "Anders": "Anders",
    }
    sector = next((label for col, label in sector_cols.items() if student.get(col) == 1), None)
    if sector:
        lines.append(f"Sector opleiding: {sector}")

    vooropl_map = {
        "VooroplNiveau_HAVO":     "HAVO",
        "VooroplNiveau_MBO":      "MBO",
        "VooroplNiveau_basis":    "Basisonderwijs",
        "VooroplNiveau_educatie": "Educatie",
        "VooroplNiveau_prak":     "Praktijkonderwijs",
        "VooroplNiveau_VMBO_BB":  "VMBO-BB (basisberoepsgericht)",
        "VooroplNiveau_VMBO_GL":  "VMBO-GL (gemengde leerweg)",
        "VooroplNiveau_VMBO_KB":  "VMBO-KB (kaderberoepsgericht)",
        "VooroplNiveau_VMBO_TL":  "VMBO-TL (theoretische leerweg)",
        "VooroplNiveau_nan":      "Onbekend",
        "VooroplNiveau_VWOplus":  "VWO of hoger",
        "VooroplNiveau_other":    "Anders",
    }
    vooropl = next((label for col, label in vooropl_map.items() if student.get(col) == 1), "Onbekend")
    lines.append(f"Vooropleiding: {vooropl}")

    if student.get("Richting_nan") == 1:
        lines.append("Opleidingsrichting: niet ingevuld / onbekend")

    return "\n".join(lines)


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
    model, _ = _get_model(request.use_default_model)
    X_pred = _student_to_df(request.student)
    score = float(model.predict(X_pred.values)[0])
    prediction = 1 if score >= 0.35 else 0
    return {"probability": score, "prediction": prediction}


@app.post("/explain_risk")
def explain_risk(request: ExplainRequest):
    student = request.student
    probability = request.probability

    # ── Risiconiveau ──────────────────────────────────────────────────────────
    if probability >= 0.65:
        risico_niveau = "HOOG"
        urgentie = "directe actie vereist (deze week)"
    elif probability >= 0.35:
        risico_niveau = "MATIG"
        urgentie = "actie aanbevolen binnen twee weken"
    else:
        risico_niveau = "LAAG"
        urgentie = "reguliere monitoring volstaat voorlopig"

    # ── Top risicofactoren via SHAP (intern berekend) ─────────────────────────
    _, exp = _get_model(request.use_default_model)
    X_pred = _student_to_df(student)
    shap_vals = exp.shap_values(X_pred.values)
    fi = {
        k: v for k, v in zip(features, shap_vals[0].tolist())
        if k not in SHAP_EXCLUDE
    }
    top_factors = sorted(fi.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
    top_factors_str = "\n".join(
        f"  {i + 1}. {FEATURE_LABELS.get(k, k)}"
        f" — waarde: {student.get(k, '?')}"
        f" — bijdrage aan risico: {'↑ verhogend' if v > 0 else '↓ verlagend'} ({abs(v):.3f})"
        for i, (k, v) in enumerate(top_factors)
    )

    # ── Leesbaar studentprofiel ───────────────────────────────────────────────
    profiel = _decode_student_profile(student)

    prompt = f"""Je bent een expert in studieloopbaanbegeleiding in het Nederlandse MBO-onderwijs.
Schrijf een EduPlan voor de mentor van de onderstaande student.
Het EduPlan is een professioneel begeleidingsdocument dat de mentor direct helpt bij een gericht gesprek en het inzetten van passende ondersteuning.

═══════════════════════════════════════
STUDENTPROFIEL
═══════════════════════════════════════
{profiel}

Voorspelde uitvalkans: {probability:.1%}
Risiconiveau: {risico_niveau} — {urgentie}

═══════════════════════════════════════
TOP 5 BEPALENDE FACTOREN (modelanalyse)
═══════════════════════════════════════
De onderstaande factoren dragen het meest bij aan het uitvalrisico voor déze student.
Gebruik deze als kern van je analyse — niet alle factoren hoeven negatief te zijn.

{top_factors_str}

═══════════════════════════════════════
INSTRUCTIES
═══════════════════════════════════════
Schrijf het EduPlan volledig in het Nederlands, in heldere professionele taal voor een MBO-mentor of SLB'er.
Gebruik uitsluitend de werkelijke waarden uit het studentprofiel en de modelanalyse hierboven — geen fictieve getallen.
Baseer adviezen op bewezen effectieve aanpakken uit de literatuur over MBO-uitval.

Structuur het EduPlan exact als volgt:

**🔍 RISICOPROFIEL**
Beschrijf in 4–6 zinnen welke factoren bij déze student samenhangen met het uitvalrisico.
Noem de concrete waarden (dagen verzuim, vooropleiding, aantal aanmeldingen etc.).
Leg uit waarom juist de combinatie van deze factoren zorgelijk is.
Benoem ook het risiconiveau ({risico_niveau}) en wat dat in de praktijk betekent voor urgentie.

**⚠️ SIGNALEN EN GESPREKSTHEMA'S**
Geef 4 concrete gespreksonderwerpen of vragen die de mentor in het eerste contact moet verkennen, afgestemd op dit specifieke profiel.
Denk aan: verzuimgeschiedenis vóór inschrijving, financiële of thuissituatieproblemen, motivatie en toekomstperspectief, eerdere studie-uitval of -switch.
Formuleer ze als directe gespreksstarters die een mentor kan gebruiken.

**🎯 INTERVENTIES OP MAAT**
Geef 3–5 concrete, gefaseerde interventies specifiek voor déze student.
Noem per interventie: wat, wie, wanneer en waarom (onderbouwing).
Stem de keuze af op het profiel: bij hoog verzuim prioriteit aan verzuimaanpak; bij meerdere aanmeldingen aandacht voor motivatie en studiekeuze; bij onbekende vooropleiding of praktijkachtergrond extra oriëntatie.

Gebruik bij voorkeur bewezen effectieve aanpakken:
- Vroeg persoonlijk motivatiegesprek (45 min): toekomstdoelen verkennen, autonomie en verbondenheid versterken — bewezen effectief bij vroege uitvalpreventie
- Verzuimaanpak: bij ongeoorloofd verzuim boven drempel direct contact (telefoon/mail), dan gesprek over oorzaak; bij herhaling of escalatie: leerplicht of LEC inschakelen
- Buddy-/rolmodelkoppeling: student koppelen aan een succesvolle medestudent uit dezelfde sector als sociaal anker
- Kortdurende motivatie-interventie: 2 sessies van 45 minuten gericht op tussendoelen stellen en studiegedrag verbinden aan toekomstperspectief (onderzoek: –31% uitvalkans)
- Domeinoverstijgende doorverwijzing: bij multiproblematiek (schulden, gezondheid, thuissituatie) doorverwijzen naar LEC, financieel spreekuur of jongerenwerk; aanpak moet holistisch zijn maar schoolse obstakels wegnemen staat voorop

**📋 ACTIEPUNTEN VOOR DE MENTOR**
Sluit af met een genummerde lijst van maximaal 5 actiepunten, gesorteerd op urgentie.
Maak expliciet onderscheid: wat doe je déze week, wat doe je déze maand.
"""

    response = client.responses.create(
        model=MODEL,
        store=False,
        input=[{"role": "user", "content": prompt}]
    )
    uitleg = response.output_text  # type: ignore
    return {"explanation": uitleg}


@app.post("/feature_importance")
def feature_importance(request: StudentData):
    _, exp = _get_model(request.use_default_model)
    X_pred = _student_to_df(request.student)
    # RF Regressor: shap_values() geeft shape (n_samples, n_features), geen lijst per klasse
    shap_vals = exp.shap_values(X_pred.values)
    fi = dict(zip(features, shap_vals[0].tolist()))
    return {"feature_importance": fi}


@app.post("/train_model")
def train_model_endpoint(request: TrainRequest):
    """Start modeltraining asynchroon op basis van geüploade historische data."""
    with _training.lock:
        if _training.status == "training":
            return {"status": "already_running"}
        _training.status  = "training"
        _training.message = ""

    def _run():
        try:
            df_train = pd.DataFrame(request.data)
            trainer.train_model(
                df=df_train,
                dropout_col=request.dropout_column,
                feature_cols=features,
                model_path=MODEL_CUSTOM_PATH,
                param_grid=request.rf_parameters,
            )
            _reload_model(MODEL_CUSTOM_PATH)
            with _training.lock:
                n = len(df_train.dropna(subset=[request.dropout_column]))
                _training.status  = "done"
                _training.message = f"Model getraind op {n} studenten."
        except Exception as e:
            with _training.lock:
                _training.status  = "failed"
                _training.message = str(e)

    ThreadPoolExecutor(max_workers=1).submit(_run)
    return {"status": "started"}


@app.get("/train_status")
def train_status():
    """Geef de huidige trainingsstatus terug (polling door de frontend)."""
    return {"status": _training.status, "message": _training.message}


@app.delete("/reset_model")
def reset_model():
    """Zet het standaardmodel terug en verwijder het instellingsmodel."""
    if os.path.exists(MODEL_CUSTOM_PATH):
        os.remove(MODEL_CUSTOM_PATH)
    _reload_model(MODEL_DEFAULT_PATH)
    with _training.lock:
        _training.status  = "idle"
        _training.message = ""
    return {"status": "reset"}


@app.post("/map_columns")
def map_columns(request: MapColumnsRequest):
    """Gebruik LLM om geüploade kolomnamen te koppelen aan vereiste kolomnamen."""
    prompt = (
        "Je krijgt twee lijsten met kolomnamen van datasets.\n\n"
        f"Geüploade kolommen: {request.uploaded_columns}\n"
        f"Vereiste kolommen: {request.required_columns}\n\n"
        "Geef een JSON-object terug waarbij de sleutels de VEREISTE kolomnamen zijn "
        "en de waarden de overeenkomende GEÜPLOADE kolomnamen. "
        "Neem alleen kolommen op waarbij je zeker bent van de overeenkomst op basis van "
        "betekenis of naamgelijkenis (bijv. 'leeftijd' → 'StudentAge', 'verzuim' → 'absence_unauthorized'). "
        "Geef uitsluitend het JSON-object terug, zonder uitleg of markdown.\n\n"
        "Voorbeeld: {\"StudentAge\": \"leeftijd\", \"absence_unauthorized\": \"ongeoorloofd_verzuim\"}"
    )
    response = client.responses.create(
        model=MODEL,
        store=False,
        input=[{"role": "user", "content": prompt}]
    )
    raw = response.output_text.strip()
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    try:
        mapping = json.loads(json_match.group()) if json_match else {}
    except Exception:
        mapping = {}
    return {"mapping": mapping}
