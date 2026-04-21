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

import html as html_module
import json
import re
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import pandas as pd
import shap
import yaml
from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.ensemble import RandomForestRegressor

import backend.trainer as trainer

load_dotenv()

app = FastAPI()

client = Anthropic()

# Centrale deployment-configuratie (paden, kolomnamen, drempels, LLM-model).
_cfg = yaml.safe_load((Path(__file__).parent.parent / "config.yaml").read_text())

ANTHROPIC_MODEL = _cfg["llm"]["model"]


def _call_llm(
    prompt: str,
    *,
    max_tokens: int,
    temperature: float | None = None,
    prefill: str | None = None,
) -> str:
    """Roep het Anthropic Messages API aan en geef de gegenereerde tekst terug.

    Met optionele assistant-prefill om de output te starten (handig voor JSON of
    andere structured output). De prefill wordt vooraan aan de response geplakt.
    """
    messages: list[dict] = [{"role": "user", "content": prompt}]
    if prefill is not None:
        messages.append({"role": "assistant", "content": prefill})
    kwargs: dict = {"model": ANTHROPIC_MODEL, "max_tokens": max_tokens, "messages": messages}
    if temperature is not None:
        kwargs["temperature"] = temperature
    response = client.messages.create(**kwargs)
    text = response.content[0].text
    return (prefill + text) if prefill is not None else text

# Modelpaden
MODEL_DEFAULT_PATH = _cfg["model"]["default_path"]
MODEL_CUSTOM_PATH = _cfg["model"]["custom_path"]
MODEL_DEFAULT_FEATURES_PATH = _cfg["model"]["default_features_path"]
MODEL_CUSTOM_FEATURES_PATH = _cfg["model"]["custom_features_path"]
MODEL_CUSTOM_IMPUTER_PATH = _cfg["model"]["custom_imputer_path"]
MODEL_CUSTOM_SCALER_PATH = _cfg["model"]["custom_scaler_path"]

# Voorspellingsdrempels
_THRESHOLD_HIGH = _cfg["prediction"]["risk_threshold_high"]
_THRESHOLD_MOD = _cfg["prediction"]["risk_threshold_moderate"]
_SHAP_QUALITY = _cfg["prediction"]["shap_quality_threshold"]
_SHAP_TOP_N = _cfg["prediction"]["shap_top_factors"]

_FEATURES_PATH: dict[str, str] = {
    MODEL_DEFAULT_PATH: MODEL_DEFAULT_FEATURES_PATH,
    MODEL_CUSTOM_PATH: MODEL_CUSTOM_FEATURES_PATH,
}


def _load_features(path: str) -> list[str]:
    """Laad feature-lijst uit JSON; val terug op shared/data.csv als het bestand ontbreekt."""
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    _NON = set(_cfg["data"]["exclude_columns"]) | {_cfg["data"]["target_column"]}
    return [c for c in pd.read_csv(_cfg["data"]["path"]).columns if c not in _NON]


# Features per model — dynamisch bepaald door student-signal bij training
features_default = _load_features(MODEL_DEFAULT_FEATURES_PATH)
features_custom = (
    _load_features(MODEL_CUSTOM_FEATURES_PATH) if Path(MODEL_CUSTOM_FEATURES_PATH).exists() else features_default
)
features = features_custom  # actieve feature-lijst

# Standaardmodel — altijd geladen, gebruikt bij demo-data
clf_default = joblib.load(MODEL_DEFAULT_PATH)
explainer_default = shap.TreeExplainer(clf_default)

# Instellingsmodel — geladen indien beschikbaar; anders alias op standaard
if Path(MODEL_CUSTOM_PATH).exists():
    clf_custom = joblib.load(MODEL_CUSTOM_PATH)
    explainer_custom = shap.TreeExplainer(clf_custom)
    imputer_custom = joblib.load(MODEL_CUSTOM_IMPUTER_PATH) if Path(MODEL_CUSTOM_IMPUTER_PATH).exists() else None
else:
    clf_custom = clf_default
    explainer_custom = explainer_default
    imputer_custom = None

# Actief model
clf = clf_custom
explainer = explainer_custom
imputer = imputer_custom


def _get_model(use_default: bool) -> tuple[RandomForestRegressor, shap.TreeExplainer]:
    """Geef het juiste (clf, explainer)-paar terug op basis van de vlag."""
    if use_default:
        return clf_default, explainer_default
    return clf, explainer


def _get_features(use_default: bool) -> list[str]:
    """Geef de feature-lijst voor het actieve model."""
    return features_default if use_default else features


# ── Trainingstoestand ─────────────────────────────────────────────────────────


@dataclass
class _TrainingState:
    status: str = "idle"  # idle | training | done | failed
    message: str = ""
    lock: threading.Lock = field(default_factory=threading.Lock)


_training = _TrainingState()


def _reload_model(path: str | Path) -> None:
    """Laad model, explainer, imputer en features opnieuw en vervang de globale referenties atomisch."""
    global clf, explainer, imputer, features, features_custom
    new_clf = joblib.load(path)
    new_explainer = shap.TreeExplainer(new_clf)
    new_features = _load_features(_FEATURES_PATH[str(path)])
    new_imputer = joblib.load(MODEL_CUSTOM_IMPUTER_PATH) if Path(MODEL_CUSTOM_IMPUTER_PATH).exists() else None
    # Python-naam-toewijzing is atomisch onder de GIL
    clf = new_clf
    explainer = new_explainer
    imputer = new_imputer
    features = new_features
    features_custom = new_features


class StudentData(BaseModel):
    student: dict
    use_default_model: bool = False


class SummaryRequest(BaseModel):
    data: str


class ExplainRequest(BaseModel):
    student: dict
    prediction: int
    probability: float
    use_default_model: bool = False
    imputed_columns: list[str] = []


class MapColumnsRequest(BaseModel):
    uploaded_columns: list[str]
    required_columns: list[str]


class TrainRequest(BaseModel):
    data: list[dict]
    dropout_column: str = "Dropout"
    rf_parameters: dict | None = None


class RankRequest(BaseModel):
    students: list[dict]
    use_default_model: bool = False


# Nederlandse labels voor modelfeatures (voor leesbare SHAP-toelichting)
FEATURE_LABELS: dict[str, str] = {
    "StudentAge": "Leeftijd (jaar)",
    "StudentGender": "Geslacht",
    "Aanmel_aantal": "Aantal aanmeldingen",
    "max1studie": "Slechts één studie ooit",
    "ROCMondriaan": "Eerder bij ROC Mondriaan",
    "Richting_nan": "Opleidingsrichting onbekend",
    "absence_unauthorized": "Ongeoorloofd verzuim (dagen)",
    "absence_authorized": "Geoorloofd verzuim (dagen)",
    "Economie": "Sector: Economie",
    "Landbouw": "Sector: Landbouw",
    "Techniek": "Sector: Techniek",
    "DSV": "Sector: DSV",
    "Zorgenwelzijn": "Sector: Zorg & Welzijn",
    "Anders": "Sector: Anders",
    "VooroplNiveau_HAVO": "Vooropleiding: HAVO",
    "VooroplNiveau_MBO": "Vooropleiding: MBO",
    "VooroplNiveau_basis": "Vooropleiding: Basisonderwijs",
    "VooroplNiveau_educatie": "Vooropleiding: Educatie",
    "VooroplNiveau_prak": "Vooropleiding: Praktijkonderwijs",
    "VooroplNiveau_VMBO_BB": "Vooropleiding: VMBO-BB",
    "VooroplNiveau_VMBO_GL": "Vooropleiding: VMBO-GL",
    "VooroplNiveau_VMBO_KB": "Vooropleiding: VMBO-KB",
    "VooroplNiveau_VMBO_TL": "Vooropleiding: VMBO-TL",
    "VooroplNiveau_nan": "Vooropleiding: onbekend",
    "VooroplNiveau_VWOplus": "Vooropleiding: VWO of hoger",
    "VooroplNiveau_other": "Vooropleiding: anders",
}

# Features die geen inhoudelijke risicofactor zijn (niet opnemen in SHAP-toelichting)
SHAP_EXCLUDE = set(_cfg["shap"]["exclude_columns"])

# Binaire features: (label_bij_waarde_1, label_bij_waarde_0)
# Enkelvoudige bron zodat positief en negatief label altijd synchroon blijven.
BINARY_LABELS: dict[str, tuple[str, str]] = {
    "StudentGender": ("Geslacht: Man", "Geslacht: Vrouw"),
    "max1studie": (
        "Enige inschrijving ooit: ja",
        "Enige inschrijving ooit: nee (eerder ingeschreven)",
    ),
    "ROCMondriaan": ("Eerder bij ROC Mondriaan: ja", "Eerder bij ROC Mondriaan: nee"),
    "Richting_nan": ("Opleidingsrichting onbekend: ja", "Opleidingsrichting: bekend"),
    "Economie": ("Sector: Economie", "Sector is niet Economie"),
    "Landbouw": ("Sector: Landbouw", "Sector is niet Landbouw"),
    "Techniek": ("Sector: Techniek", "Sector is niet Techniek"),
    "DSV": ("Sector: DSV", "Sector is niet DSV"),
    "Zorgenwelzijn": ("Sector: Zorg & Welzijn", "Sector is niet Zorg & Welzijn"),
    "Anders": ("Sector: Anders", "Sector is niet Anders"),
    "VooroplNiveau_HAVO": ("Vooropleiding: HAVO", "Vooropleiding is niet HAVO"),
    "VooroplNiveau_MBO": ("Vooropleiding: MBO", "Vooropleiding is niet MBO"),
    "VooroplNiveau_basis": (
        "Vooropleiding: Basisonderwijs",
        "Vooropleiding is niet Basisonderwijs",
    ),
    "VooroplNiveau_educatie": (
        "Vooropleiding: Educatie",
        "Vooropleiding is niet Educatie",
    ),
    "VooroplNiveau_prak": (
        "Vooropleiding: Praktijkonderwijs",
        "Vooropleiding is niet Praktijkonderwijs",
    ),
    "VooroplNiveau_VMBO_BB": (
        "Vooropleiding: VMBO-BB",
        "Vooropleiding is niet VMBO-BB",
    ),
    "VooroplNiveau_VMBO_GL": (
        "Vooropleiding: VMBO-GL",
        "Vooropleiding is niet VMBO-GL",
    ),
    "VooroplNiveau_VMBO_KB": (
        "Vooropleiding: VMBO-KB",
        "Vooropleiding is niet VMBO-KB",
    ),
    "VooroplNiveau_VMBO_TL": (
        "Vooropleiding: VMBO-TL",
        "Vooropleiding is niet VMBO-TL",
    ),
    "VooroplNiveau_nan": (
        "Vooropleiding: Onbekend",
        "Vooropleiding is bekend (niet ontbrekend)",
    ),
    "VooroplNiveau_VWOplus": (
        "Vooropleiding: VWO of hoger",
        "Vooropleiding is niet VWO of hoger",
    ),
    "VooroplNiveau_other": (
        "Vooropleiding: Anders",
        "Vooropleiding is geen anders/overig",
    ),
}

# Afgeleid van BINARY_LABELS zodat labels synchroon blijven met de LLM-factorteksten.
_SECTOR_COLS: dict[str, str] = {
    k: BINARY_LABELS[k][0].removeprefix("Sector: ")
    for k in ("Economie", "Landbouw", "Techniek", "DSV", "Zorgenwelzijn", "Anders")
}
_VOOROPL_MAP: dict[str, str] = {
    k: BINARY_LABELS[k][0].removeprefix("Vooropleiding: ")
    for k in (
        "VooroplNiveau_HAVO",
        "VooroplNiveau_MBO",
        "VooroplNiveau_basis",
        "VooroplNiveau_educatie",
        "VooroplNiveau_prak",
        "VooroplNiveau_VMBO_BB",
        "VooroplNiveau_VMBO_GL",
        "VooroplNiveau_VMBO_KB",
        "VooroplNiveau_VMBO_TL",
        "VooroplNiveau_nan",
        "VooroplNiveau_VWOplus",
        "VooroplNiveau_other",
    )
}


def _markdown_to_html(text: str) -> str:
    """Converteer eenvoudige markdown (bold, lijsten, regeleinden) naar HTML.

    Escapet eerst alle HTML-speciale tekens om XSS via LLM-output te voorkomen,
    daarna worden alleen de bekende markdown-patronen omgezet naar tags.
    """
    text = html_module.escape(text)
    # **bold** → <strong>bold</strong>
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # *italic* → <em>italic</em>
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Regels die beginnen met een cijfer + punt → <li>
    lines = text.split("\n")
    html_lines = []
    for line in lines:
        stripped = line.strip()
        if m := re.match(r"^(#{1,4})\s+(.*)$", stripped):
            level = min(max(len(m.group(1)) + 1, 2), 4)
            html_lines.append(f"<h{level}>{m.group(2).strip()}</h{level}>")
        elif re.match(r"^\d+\.\s", stripped):
            html_lines.append(f"<li>{stripped[stripped.index('.') + 2 :]}</li>")
        elif stripped.startswith("- "):
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif stripped == "":
            html_lines.append("<br>")
        else:
            html_lines.append(stripped)
    return "\n".join(html_lines)


def _factor_label(key: str, value: float) -> str:
    """Geef een voor het LLM ondubbelzinnige beschrijving van een binaire of continue factor."""
    if key in BINARY_LABELS:
        pos, neg = BINARY_LABELS[key]
        return pos if value == 1 else neg
    return f"{FEATURE_LABELS.get(key, key)}: {value}"


def _apply_imputer(df: pd.DataFrame) -> pd.DataFrame:
    """Pas de custom imputer toe op kolommen waarop hij gefitst is, indien beschikbaar.

    De inferentie-imputer is gefitst op de post-encoding feature-kolommen (zonder
    doelkolom). Dit werkt correct na reindex() naar active_features, omdat beide
    dezelfde kolomnamen delen.
    """
    if imputer is None:
        return df
    fitted_cols = list(imputer.feature_names_in_)
    missing = [c for c in fitted_cols if c not in df.columns]
    if missing:
        # Niet alle gefitte kolommen aanwezig — imputer kan niet worden toegepast.
        return df
    result = df.copy()
    result[fitted_cols] = imputer.transform(df[fitted_cols])
    return result


def _student_to_df(student: dict, feat: list[str] | None = None) -> pd.DataFrame:
    """Zet een student-dict om naar een DataFrame met de verwachte featurekolommen."""
    f = feat if feat is not None else features
    return pd.DataFrame([student]).reindex(columns=f, fill_value=0)


def _build_risicoprofiel_html(
    student: dict,
    probability: float,
    risico_niveau: str,
    urgentie: str,
    top_factors: list[tuple[str, float]],
    imputed_set: set[str],
    model_name: str,
    data_onvoldoende: bool = False,
) -> str:
    """Bouw sectie 1 (Risicoprofiel) volledig deterministisch — geen LLM betrokken.

    Toont uitsluitend waarden die daadwerkelijk aanwezig zijn in de geüploade data.
    Geïmputeerde velden worden gemarkeerd als 'niet beschikbaar'.
    """
    n_imputed = len(imputed_set)
    n_features = len(features)
    kleur_map = {"HOOG": "#c0392b", "MATIG": "#e67e22", "LAAG": "#27ae60"}
    kleur = kleur_map[risico_niveau]

    def _val(key: str, fmt: Callable[..., str] | None = None) -> str:
        if key in imputed_set or student.get(key) is None:
            return "<i style='color:#999;'>niet beschikbaar</i>"
        v = student[key]
        return fmt(v) if fmt else str(v)

    lines: list[str] = [
        f"<b>🔍 RISICOPROFIEL</b>"
        f"<span style='font-size:0.8em; color:#888; margin-left:8px;'>model: {model_name}</span>",
        f"<b>Risiconiveau:</b> "
        f"<span style='color:{kleur}; font-weight:700;'>{risico_niveau}</span> "
        f"({probability:.0%}) — {urgentie}",
        "",
        "<b>Studentgegevens uit de data:</b>",
        f"&nbsp;&nbsp;• Leeftijd: {_val('StudentAge', lambda v: f'{int(v)} jaar')}",
    ]

    lines.append(
        f"&nbsp;&nbsp;• Geslacht: "
        f"{_val('StudentGender', lambda v: 'Man' if v == 1 else ('Vrouw' if v == 0 else 'Onbekend'))}"
    )

    lines.append(f"&nbsp;&nbsp;• Ongeoorloofd verzuim: {_val('absence_unauthorized', lambda v: f'{v:.1f} dagen')}")
    lines.append(f"&nbsp;&nbsp;• Geoorloofd verzuim: {_val('absence_authorized', lambda v: f'{v:.1f} dagen')}")
    lines.append(f"&nbsp;&nbsp;• Aantal aanmeldingen: {_val('Aanmel_aantal', lambda v: str(int(v)))}")

    if "max1studie" not in imputed_set:
        max1 = student.get("max1studie")
        if max1 == 1:
            lines.append("&nbsp;&nbsp;• Studie-ervaring: enige inschrijving ooit")
        elif max1 == 0:
            lines.append("&nbsp;&nbsp;• Studie-ervaring: eerder ingeschreven geweest")

    if student.get("ROCMondriaan") == 1 and "ROCMondriaan" not in imputed_set:
        lines.append("&nbsp;&nbsp;• Eerder bij ROC Mondriaan: ja")

    if not all(c in imputed_set for c in _SECTOR_COLS):
        sector = next((lbl for col, lbl in _SECTOR_COLS.items() if student.get(col) == 1), None)
        if sector:
            lines.append(f"&nbsp;&nbsp;• Sector: {sector}")

    if not all(c in imputed_set for c in _VOOROPL_MAP):
        vooropl = next((lbl for col, lbl in _VOOROPL_MAP.items() if student.get(col) == 1), None)
        if vooropl:
            lines.append(f"&nbsp;&nbsp;• Vooropleiding: {vooropl}")

    if student.get("Richting_nan") == 1 and "Richting_nan" not in imputed_set:
        lines.append("&nbsp;&nbsp;• Opleidingsrichting: niet ingevuld / onbekend")

    lines.append("")
    lines.append("<b>Bepalende risicofactoren (modelanalyse):</b>")
    if top_factors and not data_onvoldoende:
        for i, (k, v) in enumerate(top_factors):
            richting = "↑ verhogend" if v > 0 else "↓ verlagend"
            label = _factor_label(k, student.get(k, 0))
            lines.append(f"&nbsp;&nbsp;{i + 1}. {label} — <b>{richting}</b> ({abs(v):.3f})")
    else:
        lines.append("&nbsp;&nbsp;<i>Onvoldoende informatieve gegevens om factoren te bepalen.</i>")

    if n_imputed > 0 and n_features > 0:
        pct = int(100 * n_imputed / n_features)
        lines.append("")
        if data_onvoldoende:
            lines.append(
                f"<span style='color:#c0392b;'>⚠️ <b>Datakwaliteit:</b> {n_imputed} van de {n_features} "
                f"benodigde modelkolommen ({pct}%) ontbreken in uw bestand en zijn vervangen door "
                f"gemiddelde waarden. Het model heeft geen bruikbare variatie kunnen detecteren. "
                f"Controleer of uw data de vereiste kolommen bevat.</span>"
            )
        else:
            lines.append(
                f"<span style='color:#e67e22;'>ℹ️ {n_imputed} van de {n_features} modelkolommen ({pct}%) "
                f"ontbraken en zijn aangevuld met gemiddelde waarden. "
                f"Resultaten zijn minder betrouwbaar.</span>"
            )

    lines.append("<hr style='border:none; border-top:1px solid #eee; margin:16px 0;'>")
    return "<br>".join(lines)


@app.post("/summarize")
def summarize(request: SummaryRequest):
    """Genereer een management-samenvatting van BI-data via het LLM."""
    prompt = f"Vat deze BI-data samen voor het management (max 5 regels):\n{request.data}\nSamenvatting:"
    summary = _call_llm(prompt, max_tokens=512)
    return {"summary": summary}


@app.post("/predict_dropout")
def predict_dropout(request: StudentData):
    model, _ = _get_model(request.use_default_model)
    X_pred = _student_to_df(request.student, _get_features(request.use_default_model))
    score = float(model.predict(X_pred.values)[0])
    prediction = 1 if score >= _THRESHOLD_MOD else 0
    return {"probability": score, "prediction": prediction}


@app.post("/rank_students")
def rank_students(request: RankRequest):
    """Rangschik alle studenten op uitvalrisico in één bulk-aanroep."""
    if not request.students:
        return []
    model, _ = _get_model(request.use_default_model)
    active_features = _get_features(request.use_default_model)

    pred_df = pd.DataFrame(request.students).reindex(columns=active_features, fill_value=0)
    pred_df = _apply_imputer(pred_df)
    scores = model.predict(pred_df.values).tolist()

    result = [
        {**student, "probability": float(score), "prediction": 1 if score >= _THRESHOLD_MOD else 0}
        for student, score in zip(request.students, scores)
    ]
    result.sort(key=lambda x: x["probability"], reverse=True)
    return result


@app.post("/explain_risk")
def explain_risk(request: ExplainRequest):
    student = request.student
    probability = request.probability

    # ── Risiconiveau ──────────────────────────────────────────────────────────
    if probability >= _THRESHOLD_HIGH:
        risico_niveau = "HOOG"
        urgentie = "directe actie vereist (deze week)"
    elif probability >= _THRESHOLD_MOD:
        risico_niveau = "MATIG"
        urgentie = "actie aanbevolen binnen twee weken"
    else:
        risico_niveau = "LAAG"
        urgentie = "reguliere monitoring volstaat voorlopig"

    # ── SHAP: top factoren op basis van werkelijke data (geïmputeerde features uitgesloten) ──
    _, exp = _get_model(request.use_default_model)
    active_features = _get_features(request.use_default_model)
    X_pred = _student_to_df(student, active_features)
    shap_vals = exp.shap_values(X_pred.values)
    imputed_set = set(request.imputed_columns)
    fi = {
        k: v for k, v in zip(active_features, shap_vals[0].tolist()) if k not in SHAP_EXCLUDE and k not in imputed_set
    }
    top_factors = sorted(fi.items(), key=lambda x: abs(x[1]), reverse=True)[:_SHAP_TOP_N]

    # Detecteer of alle SHAP-waarden nagenoeg nul zijn (geen informatieve factoren)
    max_shap = max((abs(v) for _, v in top_factors), default=0.0)
    data_onvoldoende = max_shap < _SHAP_QUALITY

    # ── Sectie 1: deterministisch risicoprofiel (geen LLM) ────────────────────
    sectie1 = _build_risicoprofiel_html(
        student,
        probability,
        risico_niveau,
        urgentie,
        top_factors,
        imputed_set,
        ANTHROPIC_MODEL,
        data_onvoldoende=data_onvoldoende,
    )

    # ── Sectie 2–4: LLM schrijft alleen begeleidingsadvies ───────────────────
    # Als alle SHAP-waarden ~0 zijn, heeft geen enkele kolom informatie opgeleverd.
    # In dat geval is gepersonaliseerd advies niet mogelijk.
    if data_onvoldoende:
        return {
            "explanation": sectie1
            + (
                "<br><b>⚠️ Geen gepersonaliseerd advies mogelijk</b><br>"
                "De geüploade kolommen bevatten te weinig informatie die het model herkent. "
                "Het model heeft geen variatie kunnen detecteren ten opzichte van de gemiddelde student. "
                "Controleer of uw databestand de juiste kolommen bevat (zoals verzuim, leeftijd, "
                "vooropleiding en aanmeldingshistorie) en upload opnieuw."
            )
        }

    # Het LLM krijgt UITSLUITEND de SHAP-factoren en het risiconiveau.
    # Binaire features worden ondubbelzinnig gelabeld (ja/nee) zodat het LLM
    # waarde 0 niet verwart met de aanwezigheid van het kenmerk.
    if top_factors:
        factoren_tekst = "\n".join(
            f"  {i + 1}. {_factor_label(k, student.get(k, 0))}"
            f" — {'↑ verhogend' if v > 0 else '↓ verlagend'} ({abs(v):.3f})"
            for i, (k, v) in enumerate(top_factors)
        )
    else:
        factoren_tekst = "  Onvoldoende beschikbare gegevens voor een factoranalyse."

    prompt = f"""Je bent expert in studieloopbaanbegeleiding in het Nederlandse MBO-onderwijs.
Schrijf de begeleidingssecties van een EduPlan voor een MBO-mentor of SLB'er.

RISICONIVEAU: {risico_niveau} ({probability:.0%}) — {urgentie}

BEPALENDE FACTOREN VOOR DÉZE STUDENT (modelanalyse):
{factoren_tekst}

OPDRACHT:
Schrijf precies de volgende drie secties in professioneel Nederlands.
Baseer je UITSLUITEND op de bepalende factoren hierboven en het risiconiveau.
Noem GEEN getallen, kenmerken of gegevens die niet expliciet in de factoren staan.
Verzin geen leeftijden, verzuimdagen, geslacht of andere studentgegevens.

**⚠️ SIGNALEN EN GESPREKSTHEMA'S**

Geef 4 concrete gespreksonderwerpen of vragen die de mentor in het eerste contact moet verkennen.
Leid de thema's direct af uit de bepalende factoren hierboven — niet uit aannames.
Formuleer als directe gespreksstarters die een mentor letterlijk kan gebruiken.

**🎯 INTERVENTIES OP MAAT**

Geef 3–5 concrete, gefaseerde interventies gebaseerd op de bepalende factoren.
Noem per interventie: wat, wie, wanneer en waarom (onderbouwing).
Kies alleen interventies die aansluiten bij de wél beschikbare factoren.
Bewezen effectieve aanpakken (gebruik alleen wat relevant is voor de factoren):
- Vroeg persoonlijk motivatiegesprek (45 min): toekomstdoelen verkennen, autonomie versterken
- Verzuimaanpak: direct contact bij drempeloverschrijding, bij herhaling leerplicht/LEC
- Buddy-/rolmodelkoppeling: sociaal anker via succesvolle medestudent
- Kortdurende motivatie-interventie: 2×45 min, tussendoelen en toekomstperspectief (–31% uitvalkans)
- Domeinoverstijgende doorverwijzing: bij multiproblematiek naar LEC/financieel spreekuur/jongerenwerk

**📋 ACTIEPUNTEN VOOR DE MENTOR**

Maximaal 5 genummerde actiepunten, gesorteerd op urgentie.
Maak expliciet onderscheid: déze week vs déze maand.
"""

    sectie2_4 = _call_llm(prompt, max_tokens=2048, temperature=0.2)

    # Converteer markdown naar HTML zodat de frontend het correct kan renderen
    sectie2_4_html = _markdown_to_html(sectie2_4)

    # Sectie 1 (deterministisch HTML) + sectie 2-4 (LLM) samenvoegen
    return {"explanation": sectie1 + sectie2_4_html}


@app.post("/feature_importance")
def feature_importance(request: StudentData):
    _, exp = _get_model(request.use_default_model)
    active_features = _get_features(request.use_default_model)
    X_pred = _student_to_df(request.student, active_features)
    # RF Regressor: shap_values() geeft shape (n_samples, n_features), geen lijst per klasse
    shap_vals = exp.shap_values(X_pred.values)
    fi = dict(zip(active_features, shap_vals[0].tolist()))
    return {"feature_importance": fi}


@app.post("/train_model")
def train_model_endpoint(request: TrainRequest):
    """Start modeltraining asynchroon op basis van geüploade historische data."""
    with _training.lock:
        if _training.status == "training":
            return {"status": "already_running"}
        _training.status = "training"
        _training.message = ""

    def _run():
        try:
            df_train = pd.DataFrame(request.data)
            _, feature_cols = trainer.train_model(
                df=df_train,
                dropout_col=request.dropout_column,
                model_path=MODEL_CUSTOM_PATH,
                features_path=MODEL_CUSTOM_FEATURES_PATH,
                imputer_path=MODEL_CUSTOM_IMPUTER_PATH,
                scaler_path=MODEL_CUSTOM_SCALER_PATH,
                param_grid=request.rf_parameters,
            )
            _reload_model(MODEL_CUSTOM_PATH)
            with _training.lock:
                _training.status = "done"
                _training.message = f"Model getraind op {len(df_train)} studenten ({len(feature_cols)} features)."
        except Exception as e:
            with _training.lock:
                _training.status = "failed"
                _training.message = str(e)

    threading.Thread(target=_run, daemon=True).start()
    return {"status": "started"}


@app.get("/train_status")
def train_status():
    """Geef de huidige trainingsstatus terug (polling door de frontend)."""
    return {"status": _training.status, "message": _training.message}


@app.delete("/reset_model")
def reset_model():
    """Zet het standaardmodel terug en verwijder het instellingsmodel."""
    for p in (MODEL_CUSTOM_PATH, MODEL_CUSTOM_FEATURES_PATH):
        Path(p).unlink(missing_ok=True)
    _reload_model(MODEL_DEFAULT_PATH)
    with _training.lock:
        _training.status = "idle"
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
        'Voorbeeld: {"StudentAge": "leeftijd", "absence_unauthorized": "ongeoorloofd_verzuim"}'
    )
    raw = _call_llm(prompt, max_tokens=1024, prefill="{").strip()
    try:
        mapping = json.loads(raw[: raw.rfind("}") + 1])
    except json.JSONDecodeError:
        mapping = {}
    return {"mapping": mapping}
