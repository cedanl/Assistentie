# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anthropic",
#     "pydantic",
#     "streamlit",
#     "pandas",
#     "requests",
#     "plotly",
#     "python-docx",
#     "Pillow",
# ]
# ///

# -----------------------------------------------------------------------------
# Organization: CEDA
# Original Authors: Ed. de Feber, Edwin Lieftink, Steven Ramondt
# -----------------------------------------------------------------------------

"""frontend/app.py — Streamlit frontend voor de Uitnodigingsregel."""

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from docx import Document
from docx.shared import Pt, RGBColor
from io import BytesIO
from datetime import datetime
from PIL import Image


# ─────────────────────────────────────────────
# Paginaconfiguratie  (moet als eerste Streamlit-aanroep staan)
# ─────────────────────────────────────────────

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://github.com/cedanl/Assistentie",
        "Report a bug": "mailto:ed.defeber@surf.nl",
        "About": "# Uitnodigingsregel — CEDA 2026",
    },
    page_icon="🧮",
    page_title="Uitnodigingsregel",
)


# ─────────────────────────────────────────────
# Data & features
# ─────────────────────────────────────────────

df = pd.read_csv("shared/data.csv")

NON_FEATURES = {"Dropout", "Naam", "Opleiding", "Klas", "Mentor"}
features = [col for col in df.columns if col not in NON_FEATURES]

logo_image = Image.open("assets/npuls_logo.png")
QUICK_OPLEIDINGEN = sorted(df["Opleiding"].unique().tolist())

TERRACOTTA = "#c8785a"
ROZE_BG    = "#e8c8c8"
ROZE_LICHT = "#f2e4e4"


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────

_defaults = {
    "page":                    "start",
    "selected_opleiding":      "Alle",
    "selected_klas":           "Alle",
    "actieve_tab":             "uitnodigingsregel",
    "toon_zoekbalk":           False,
    "top_n":                   4,
    "risicostudenten":         [],
    "filter_key":              None,
    "laatste_analyse":         None,
    "eduplan_genereren":       False,
    "geselecteerde_student":   0,
    "onthoud_opleiding":       False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

START_CSS = """
<style>
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap');

[data-testid="stApp"] { background-color: #e8c8c8; font-family: 'General Sans', sans-serif; }
[data-testid="stSidebarCollapsedControl"] { display: none; }
[data-testid="stHeader"] { background-color: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

div[data-testid="stTextInput"] input {
    border: 2.5px solid #1a1a1a !important; border-radius: 50px !important;
    padding: 14px 24px !important; font-size: 17px !important;
    background-color: white !important; height: 56px;
}
div[data-testid="stTextInput"] input::placeholder { color: #aaa; }
div[data-testid="stTextInput"] > label { display: none; }

div[data-testid="column"]:has(button[kind="primary"]) button {
    background-color: #1a1a1a !important; color: white !important;
    border-radius: 50px !important; font-weight: 700 !important;
    font-size: 17px !important; height: 56px !important; width: 100% !important;
    border: none !important;
}

[data-testid="stButton"] button[kind="secondary"] {
    background-color: white !important; border-radius: 50px !important;
    border: none !important; font-size: 15px !important;
    padding: 10px 20px !important; width: 100%;
    box-shadow: 0 8px 24px rgba(0,0,0,0.20) !important;
}
[data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #f5f5f5 !important;
    box-shadow: 0 10px 28px rgba(0,0,0,0.25) !important;
}
[data-testid="stBaseButton-secondary"] {
    background-color: white !important; border-radius: 50px !important;
    border: none !important; box-shadow: 0 8px 24px rgba(0,0,0,0.20) !important;
}
</style>
"""

MAIN_CSS = """
<style>
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap');

[data-testid="stApp"]      { background-color: #e8c8c8; font-family: 'General Sans', sans-serif; }
[data-testid="stHeader"]   { background-color: transparent; }
[data-testid="stSidebarCollapsedControl"] { display: none; }
.block-container           { padding-top: 0 !important; max-width: 900px; margin: 0 auto; }

/* ── Witte card ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important;
    border-radius: 20px !important;
    border: none !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    padding: 4px 8px !important;
}

/* ── Nav pills ── */
div.nav-actief [data-testid="stBaseButton-secondary"],
div.nav-actief button[kind="secondary"] {
    background: white !important;
    border: 2px solid #1a1a1a !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    letter-spacing: 0.07em !important;
    padding: 6px 18px !important;
    color: #1a1a1a !important;
    box-shadow: none !important;
}
div.nav-inactief [data-testid="stBaseButton-secondary"],
div.nav-inactief button[kind="secondary"] {
    background: transparent !important;
    border: 2px solid transparent !important;
    border-radius: 50px !important;
    font-size: 12px !important;
    letter-spacing: 0.07em !important;
    padding: 6px 18px !important;
    color: #555 !important;
    box-shadow: none !important;
}

/* ── Klas selectbox als pill ── */
div[data-testid="stSelectbox"] > div > div[data-baseweb="select"] > div {
    border-radius: 50px !important;
    border: 2px solid #1a1a1a !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    background: white !important;
    padding-left: 16px !important;
}

/* ── Potlood-knop ── */
div.potlood-btn button {
    background: transparent !important;
    border: none !important;
    font-size: 1.2rem !important;
    padding: 4px 8px !important;
    color: #1a1a1a !important;
    box-shadow: none !important;
}

/* ── Zoek-input in card ── */
div.card-zoek div[data-testid="stTextInput"] input {
    border: 2px solid #1a1a1a !important;
    border-radius: 50px !important;
    font-size: 15px !important;
    height: 48px !important;
    background: white !important;
}
div.card-zoek div[data-testid="stTextInput"] > label { display: none; }

/* ── Primaire knoppen (zwart) ── */
button[kind="primary"],
[data-testid="stBaseButton-primary"] {
    background-color: #1a1a1a !important;
    color: white !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    letter-spacing: 0.07em !important;
    border: none !important;
    font-size: 13px !important;
}

/* ── Student-selectbox ── */
div.student-sel div[data-testid="stSelectbox"] > div > div[data-baseweb="select"] > div {
    border-radius: 50px !important;
    border: 2px solid #1a1a1a !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    text-transform: uppercase !important;
    background: white !important;
}

/* ── Terug-link ── */
div.terug-link button {
    background: transparent !important;
    border: none !important;
    color: #777 !important;
    font-size: 13px !important;
    padding: 0 !important;
    box-shadow: none !important;
}

/* ── Actie-knoppen (PRINT / DOWNLOAD) ── */
div.actie-knoppen [data-testid="stBaseButton-secondary"],
div.actie-knoppen button[kind="secondary"] {
    background-color: #1a1a1a !important;
    color: white !important;
    border-radius: 50px !important;
    border: none !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.07em !important;
    padding: 8px 24px !important;
    box-shadow: none !important;
}
</style>
"""


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _klassen_voor(opleiding: str) -> list[str]:
    if opleiding == "Alle":
        return ["Alle"] + sorted(df["Klas"].unique().tolist())
    return ["Alle"] + sorted(df[df["Opleiding"] == opleiding]["Klas"].unique().tolist())


def _gefilterde_df():
    opl  = st.session_state.selected_opleiding
    klas = st.session_state.selected_klas
    d = df.copy()
    if opl  != "Alle": d = d[d["Opleiding"] == opl]
    if klas != "Alle": d = d[d["Klas"]      == klas]
    return d


def _build_word_doc(analyse: dict) -> BytesIO:
    doc = Document()
    doc.add_heading("EduPlan", 0)

    doc.add_heading("Studentgegevens", 1)
    info = doc.add_paragraph()
    for label, value in [
        ("Student",          analyse["naam"]),
        ("Student-ID",       str(analyse["studentnummer"])),
        ("Opleiding",        analyse["opleiding"]),
        ("Klas",             analyse["klas"]),
        ("Mentor",           analyse["mentor"]),
        ("Datum",            datetime.now().strftime("%d-%m-%Y %H:%M")),
    ]:
        info.add_run(f"{label}: ").bold = True
        info.add_run(f"{value}\n")

    doc.add_heading("Kengetallen", 2)
    kgn = doc.add_paragraph()
    kgn.add_run("Leeftijd: ").bold = True
    kgn.add_run(f"{analyse['leeftijd']} jaar\n")
    kgn.add_run("Ongeoorloofd verzuim: ").bold = True
    kgn.add_run(f"{analyse['ongeoorloofd_verzuim']:.1f} dagen\n")
    kgn.add_run("Geoorloofd verzuim: ").bold = True
    kgn.add_run(f"{analyse['geoorloofd_verzuim']:.1f} dagen\n")
    kgn.add_run("Uitvalkans: ").bold = True
    r = kgn.add_run(f"{analyse['probability']:.1%}\n")
    r.font.color.rgb = RGBColor(200, 120, 90)
    r.bold = True

    doc.add_heading("EduPlan", 1)
    doc.add_paragraph(analyse["explanation"])

    doc.add_heading("Risicofactoren (SHAP)", 1)
    doc.add_paragraph(analyse["feature_importance"])

    footer = doc.add_paragraph()
    r2 = footer.add_run("Gegenereerd door Uitnodigingsregel — CEDA")
    r2.italic = True
    r2.font.size = Pt(9)

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio


def _run_voorspelling(dff: pd.DataFrame):
    """Doe API-calls voor alle studenten in dff; sla op in session_state."""
    opl  = st.session_state.selected_opleiding
    klas = st.session_state.selected_klas
    key  = (opl, klas)

    if st.session_state.filter_key == key:
        return  # niets veranderd

    st.session_state.filter_key     = key
    st.session_state.laatste_analyse = None
    st.session_state.eduplan_genereren = False

    with st.spinner("Risico berekenen…"):
        resultaten = []
        for _, row in dff.iterrows():
            try:
                resp = requests.post(
                    "http://localhost:8000/predict_dropout",
                    json={"student": row[features].to_dict()},
                    timeout=10,
                )
                resultaten.append((row, resp.json()))
            except Exception:
                pass
        resultaten.sort(key=lambda x: x[1]["probability"], reverse=True)
        st.session_state.risicostudenten = resultaten
        # Standaard top_n: aantal studenten of max 10
        st.session_state.top_n = min(len(resultaten), 4)


def _genereer_eduplan():
    idx  = st.session_state.geselecteerde_student
    risico = st.session_state.risicostudenten
    if not risico or idx >= len(risico):
        return
    row, result = risico[idx]
    naam = row["Naam"]

    with st.spinner(f"Bezig met genereren van het EduPlan voor {naam}…"):
        try:
            exp = requests.post(
                "http://localhost:8000/explain_risk",
                json={
                    "student":     row[features].to_dict(),
                    "prediction":  result["prediction"],
                    "probability": result["probability"],
                },
                timeout=60,
            ).json()["explanation"]
        except Exception:
            exp = "Uitleg kon niet worden gegenereerd."

        fi_dict, fi_str = {}, ""
        try:
            fi_resp = requests.post(
                "http://localhost:8000/feature_importance",
                json={"student": row[features].to_dict()},
                timeout=10,
            )
            fi_dict = fi_resp.json()["feature_importance"]
            fi_str  = ", ".join(f"{k}: {v:.2f}" for k, v in fi_dict.items())
        except Exception:
            fi_str = "Niet beschikbaar."

        st.session_state.laatste_analyse = {
            "naam":                  naam,
            "opleiding":             row["Opleiding"],
            "klas":                  row["Klas"],
            "mentor":                row["Mentor"],
            "studentnummer":         int(row["Studentnummer"]),
            "leeftijd":              int(row["StudentAge"]),
            "ongeoorloofd_verzuim":  float(row["absence_unauthorized"]),
            "geoorloofd_verzuim":    float(row.get("absence_authorized", 0)),
            "probability":           result["probability"],
            "explanation":           exp,
            "feature_importance":    fi_str,
            "feature_importance_dict": fi_dict,
        }
        st.session_state.eduplan_genereren = False


# ─────────────────────────────────────────────
# Startscherm
# ─────────────────────────────────────────────

def show_start_screen():
    st.markdown(START_CSS, unsafe_allow_html=True)
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align:center; margin-bottom:8px; font-family:'General Sans',sans-serif;">
            <h1 style="font-size:3.2rem; font-weight:400; line-height:1.15; margin-bottom:4px;">
                Welkom bij de<br>Uitnodigingsregel
            </h1>
            <p style="font-size:1.3rem; color:#333; margin-top:0;">
                op tijd de juiste lerenden uitnodigen
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    _, col_m, _ = st.columns([1, 4, 1])
    with col_m:
        st.markdown(
            """<p style="text-align:center; font-size:1.1rem; color:#222; margin-bottom:24px;
                         font-family:'General Sans',sans-serif;">
                Voer de opleidingsrichting in om te zien of er nú lerenden zijn die
                mogelijk risico lopen om uit te vallen. We brengen ze voor jou in beeld.
            </p>""",
            unsafe_allow_html=True,
        )

        col_zoek, col_start = st.columns([6, 1.5])
        with col_zoek:
            zoekterm = st.text_input(
                "Zoek opleiding",
                placeholder="Bijv. Zorg & Welzijn, Economie, Techniek",
                label_visibility="collapsed",
                value=(
                    st.session_state.selected_opleiding
                    if st.session_state.onthoud_opleiding
                       and st.session_state.selected_opleiding != "Alle"
                    else ""
                ),
            )
        with col_start:
            start = st.button("START", type="primary", use_container_width=True)

        onthoud = st.checkbox(
            "Onthoud mijn opleiding", value=st.session_state.onthoud_opleiding
        )
        st.session_state.onthoud_opleiding = onthoud

        if start:
            gekozen = zoekterm.strip() if zoekterm.strip() else "Alle"
            match = next(
                (o for o in QUICK_OPLEIDINGEN if gekozen.lower() in o.lower()),
                gekozen,
            )
            st.session_state.selected_opleiding = match
            st.session_state.selected_klas      = "Alle"
            st.session_state.page               = "main"
            st.session_state.filter_key         = None
            st.rerun()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    _, col_m2, _ = st.columns([0.5, 6, 0.5])
    with col_m2:
        st.markdown("<div class='pill-row'>", unsafe_allow_html=True)
        pill_cols = st.columns(len(QUICK_OPLEIDINGEN))
        for i, opl in enumerate(QUICK_OPLEIDINGEN):
            with pill_cols[i]:
                if st.button(opl, key=f"pill_{opl}", use_container_width=True):
                    st.session_state.selected_opleiding = opl
                    st.session_state.selected_klas      = "Alle"
                    st.session_state.page               = "main"
                    st.session_state.filter_key         = None
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown(
        """<hr style="border:none; border-top:1px solid #ccc; margin:0 0 12px 0;">
        <p style="text-align:center; font-size:0.75rem; color:#555;">
            &#169; &#9432; Op deze analytics tool is de Creative Commons ShareAlike
            Naamsvermelding 4.0-licentie van toepassing. Maak bij gebruik van dit werk
            vermelding van de volgende referentie: AI en data waarde(n)vol inzetten: CEDA.
            Uitnodigingsregel – EduPlan. Utrecht: Npuls
        </p>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Hoofdscherm — header
# ─────────────────────────────────────────────

def _render_header():
    tab = st.session_state.actieve_tab
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    col_logo, col_gap, col_nav = st.columns([2, 4, 3])

    with col_logo:
        st.markdown(
            "<h2 style='font-weight:700; margin:0; padding:12px 0; "
            "font-family:\"General Sans\",sans-serif;'>CEDA</h2>",
            unsafe_allow_html=True,
        )

    with col_nav:
        c1, c2 = st.columns(2)
        with c1:
            cls = "nav-actief" if tab == "uitnodigingsregel" else "nav-inactief"
            st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
            if st.button("UITNODIGINGSREGEL", key="nav_ur"):
                st.session_state.actieve_tab = "uitnodigingsregel"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            cls = "nav-actief" if tab == "eduplan" else "nav-inactief"
            st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
            if st.button("EDUPLAN", key="nav_ep"):
                st.session_state.actieve_tab = "eduplan"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<hr style='margin:0 0 20px 0; border:none; border-top:1px solid rgba(0,0,0,0.15);'>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Hoofdscherm — kaart-header (opleiding + klas + potlood)
# ─────────────────────────────────────────────

def _render_card_header():
    opl = st.session_state.selected_opleiding

    if st.session_state.toon_zoekbalk:
        # Zoekbalk-modus (pencil geklikt)
        st.markdown("<div class='card-zoek'>", unsafe_allow_html=True)
        col_s, col_b = st.columns([5, 1])
        with col_s:
            zoek = st.text_input(
                "zoek",
                placeholder="🔍  Zoek een andere opleiding (b.v. Economie, Techniek)...",
                label_visibility="collapsed",
                key="card_zoek_input",
            )
        with col_b:
            if st.button("ZOEK", type="primary", use_container_width=True, key="card_zoek_btn"):
                if zoek.strip():
                    match = next(
                        (o for o in QUICK_OPLEIDINGEN if zoek.lower() in o.lower()),
                        zoek.strip(),
                    )
                    st.session_state.selected_opleiding  = match
                st.session_state.selected_klas       = "Alle"
                st.session_state.toon_zoekbalk        = False
                st.session_state.filter_key           = None
                st.session_state.risicostudenten      = []
                st.session_state.laatste_analyse      = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Normale modus
        klassen = _klassen_voor(opl)

        # Herstel klas naar "Alle" als de huidige klas niet meer bestaat
        if st.session_state.selected_klas not in klassen:
            st.session_state.selected_klas = "Alle"

        col_t, col_k, col_sp, col_p = st.columns([3, 2.5, 2.5, 0.5])

        with col_t:
            st.markdown(
                f"<h3 style='font-weight:700; margin:0; padding:6px 0;"
                f"font-family:\"General Sans\",sans-serif;'>{opl}</h3>",
                unsafe_allow_html=True,
            )

        with col_k:
            klas_idx = klassen.index(st.session_state.selected_klas) \
                if st.session_state.selected_klas in klassen else 0
            gekozen_klas = st.selectbox(
                "klas",
                klassen,
                index=klas_idx,
                label_visibility="collapsed",
                format_func=lambda x: f"KLAS:  {x}" if x != "Alle" else "KLAS:  Alle",
                key="klas_dropdown",
            )
            if gekozen_klas != st.session_state.selected_klas:
                st.session_state.selected_klas   = gekozen_klas
                st.session_state.filter_key      = None
                st.session_state.laatste_analyse = None
                st.rerun()

        with col_p:
            st.markdown("<div class='potlood-btn'>", unsafe_allow_html=True)
            if st.button("✏", key="potlood"):
                st.session_state.toon_zoekbalk = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Hoofdscherm — banner  "Toon mij X lerenden…"
# ─────────────────────────────────────────────

def _render_banner(n_geladen: int):
    risico = st.session_state.risicostudenten

    if not risico:
        label = "…"
    else:
        label = f"<u><b>{st.session_state.top_n}</b></u>"

    st.markdown(
        f"""<div style="background:{TERRACOTTA}; border-radius:12px; padding:14px 24px;
                        color:white; font-size:16px; font-weight:500;
                        text-align:center; margin:16px 0;
                        font-family:'General Sans',sans-serif;">
            Toon mij {label} lerenden met het hoogste risico om uit te vallen.
        </div>""",
        unsafe_allow_html=True,
    )

    if risico:
        # Slider voor top_n
        max_n = len(risico)
        nieuw_n = st.slider(
            "Aantal te tonen",
            min_value=1,
            max_value=max_n,
            value=min(st.session_state.top_n, max_n),
            label_visibility="collapsed",
            key="top_n_slider",
        )
        if nieuw_n != st.session_state.top_n:
            st.session_state.top_n = nieuw_n
            st.rerun()


# ─────────────────────────────────────────────
# Hoofdscherm — barchart
# ─────────────────────────────────────────────

def _render_barchart():
    risico = st.session_state.risicostudenten

    if not risico:
        st.markdown(
            f"""<div style="background:{ROZE_LICHT}; border-radius:14px;
                            height:260px; display:flex; align-items:center;
                            justify-content:center; color:#bbb; font-size:1.4rem;
                            margin:8px 0; letter-spacing:0.1em;">
                · · ·
            </div>""",
            unsafe_allow_html=True,
        )
        return

    top_n = st.session_state.top_n
    top   = risico[:top_n]
    n     = len(top)

    namen  = [row["Naam"]             for row, _      in reversed(top)]
    kansen = [result["probability"]   for _,   result in reversed(top)]

    # Terracotta-gradient: donkerste voor de hoogste risico-student (bovenste balk)
    def terracotta(i, total):
        t = i / max(total - 1, 1)
        r = int(0xa0 + (0xdf - 0xa0) * t)
        g = int(0x55 + (0x9a - 0x55) * t)
        b = int(0x35 + (0x75 - 0x35) * t)
        return f"rgb({r},{g},{b})"

    kleuren = [terracotta(i, n) for i in range(n)]

    fig = go.Figure(go.Bar(
        x=kansen,
        y=namen,
        orientation="h",
        marker_color=kleuren,
        text=[f"{k:.0%}" for k in kansen],
        textposition="outside",
        textfont=dict(size=14, color="#aaa"),
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 1.2], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=14, color="#1a1a1a")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=60, t=12, b=12),
        height=max(180, 60 + 56 * n),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
# Hoofdscherm — EduPlan-sectie
# ─────────────────────────────────────────────

def _render_eduplan_sectie():
    risico = st.session_state.risicostudenten
    top_n  = st.session_state.top_n

    if not risico:
        st.info("Laad eerst studenten via het UITNODIGINGSREGEL-tabblad.")
        return

    top = risico[:top_n]

    st.markdown(
        "<p style='font-size:14px; color:#444; margin:8px 0 4px 0;"
        "font-family:\"General Sans\",sans-serif;'>"
        "Selecteer een lerenden voor de uitleg van diens uitvalrisico</p>",
        unsafe_allow_html=True,
    )

    opties = [
        f"{row['Naam'].upper()} — UITVALKANS: {result['probability']:.0%}"
        for row, result in top
    ]

    col_sel, col_btn = st.columns([4, 2])
    with col_sel:
        st.markdown("<div class='student-sel'>", unsafe_allow_html=True)
        idx = st.selectbox(
            "student",
            options=range(len(opties)),
            format_func=lambda i: opties[i],
            label_visibility="collapsed",
            key="student_selector",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_btn:
        if st.button("TOON EDUPLAN", type="primary", use_container_width=True):
            st.session_state.geselecteerde_student = idx
            st.session_state.eduplan_genereren     = True
            st.session_state.laatste_analyse       = None
            st.session_state.actieve_tab           = "eduplan"
            st.rerun()

    # Laadstatus of resultaat
    if st.session_state.eduplan_genereren:
        naam = top[st.session_state.geselecteerde_student][0]["Naam"]
        st.markdown(
            f"""<div style="background:{ROZE_LICHT}; border-radius:14px;
                            padding:28px; text-align:center; margin-top:16px;
                            font-family:'General Sans',sans-serif; color:#555;">
                <span style="font-size:1.4rem;">↻</span>&nbsp;&nbsp;
                Bezig met genereren van het EduPlan voor <b>{naam}</b>
            </div>""",
            unsafe_allow_html=True,
        )
        _genereer_eduplan()
        st.rerun()

    if st.session_state.laatste_analyse:
        _render_eduplan_content()


def _render_eduplan_content():
    analyse = st.session_state.laatste_analyse
    naam    = analyse["naam"]

    # EduPlan header-card
    with st.container(border=True):
        st.markdown(
            f"""<div style="display:flex; align-items:center; gap:14px;
                            font-family:'General Sans',sans-serif;">
                <div style="background:#1a1a1a; color:white; border-radius:8px;
                            width:36px; height:36px; display:flex; align-items:center;
                            justify-content:center; font-size:16px; font-weight:700;
                            flex-shrink:0;">ℹ</div>
                <span style="font-size:1.25rem; font-weight:600;">EduPlan | {naam}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # EduPlan content-card
    with st.container(border=True):
        st.markdown(
            f"<div style='font-family:\"General Sans\",sans-serif; "
            f"font-size:15px; line-height:1.75; color:#1a1a1a;'>"
            f"{analyse['explanation'].replace(chr(10), '<br>')}"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # PRINT + DOWNLOAD knoppen (rechts uitgelijnd)
    _, col_p, col_d = st.columns([6, 1, 1])

    with col_p:
        st.markdown("<div class='actie-knoppen'>", unsafe_allow_html=True)
        if st.button("PRINT", key="print_btn", use_container_width=True):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown("<div class='actie-knoppen'>", unsafe_allow_html=True)
        bio = _build_word_doc(analyse)
        st.download_button(
            label="DOWNLOAD",
            data=bio,
            file_name=f"EduPlan_{naam.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="download_btn",
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Hoofdscherm — footer
# ─────────────────────────────────────────────

def _render_footer():
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    st.markdown(
        """<hr style="border:none; border-top:1px solid rgba(0,0,0,0.12); margin:0 0 10px 0;">
        <p style="text-align:center; font-size:0.72rem; color:#666;
                  font-family:'General Sans',sans-serif;">
            &#169; &#9432; Op deze analytics tool is de Creative Commons ShareAlike
            Naamsvermelding 4.0-licentie van toepassing. Maak bij gebruik van dit werk
            vermelding van de volgende referentie: AI en data waarde(n)vol inzetten: CEDA.
            Uitnodigingsregel – EduPlan. Utrecht: Npuls
        </p>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Hoofdscherm — samenstellen
# ─────────────────────────────────────────────

def show_main_screen():
    st.markdown(MAIN_CSS, unsafe_allow_html=True)

    _render_header()

    dff = _gefilterde_df()

    # Voorspelling uitvoeren als filter gewijzigd
    if len(dff) > 0:
        _run_voorspelling(dff)

    # Hoofdkaart
    with st.container(border=True):
        _render_card_header()

        tab = st.session_state.actieve_tab

        _render_banner(len(st.session_state.risicostudenten))

        if tab == "uitnodigingsregel":
            _render_barchart()
        else:
            _render_eduplan_sectie()

    _render_footer()


# ─────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────

if st.session_state.page == "start":
    show_start_screen()
else:
    show_main_screen()
