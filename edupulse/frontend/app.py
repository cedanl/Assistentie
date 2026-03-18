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


"""frontend/app.py
### STREAMLIT FRONTEND

Gebruikt data en model van Uitnodigingsregel (cedanl/Uitnodigingsregel).
"""

#-------------------------------------------------
# Imports
#-------------------------------------------------

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from docx import Document
from docx.shared import Pt, RGBColor
from io import BytesIO
from datetime import datetime
from PIL import Image


#-------------------------------------------------
# Data & features laden
#-------------------------------------------------

df = pd.read_csv("shared/data.csv")

# Features zijn alle kolommen behalve weergave- en doelkolommen
NON_FEATURES = {"Dropout", "Naam", "Opleiding", "Klas", "Mentor"}
features = [col for col in df.columns if col not in NON_FEATURES]

image      = Image.open("assets/npuls_logo.png")
logo_image = Image.open("assets/npuls_logo.png")


#-------------------------------------------------
# Paginaconfiguratie
#-------------------------------------------------

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/cedanl/Assistentie/blob/main/edupulse/CLAUDE.md',
        'Report a bug': "mailto:ed.defeber@surf.nl",
        'About': "# EduPulse App 2026 by Ed, Edwin and Steven"
    },
    page_icon="🧮",
    page_title="Edupulse",
)


col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(
        """
                #### :blue[**Studentuitval Signalering en Interventie**]\n
                # 🧮 :blue[**Edupulse**]"""
    )
with col2:
    if image is not None:
        st.image(image, caption=None, width=320, clamp=True,
                 channels="RGB", output_format="auto")
    else:
        st.warning("Afbeelding kon niet worden geladen.")

st.logo(image=logo_image, size="small", icon_image="assets/npuls_logo.png")


#-------------------------------------------------
# Zijbalk: filters
#-------------------------------------------------

with st.sidebar:
    st.markdown("#### 🎯**Kies een opleiding, klas en/of mentor**")
    opleiding = st.selectbox("Opleiding", ["Alle"] + sorted(df["Opleiding"].unique().tolist()))
    klas      = st.selectbox("Klas",      ["Alle"] + sorted(df["Klas"].unique().tolist()))
    mentor    = st.selectbox("Mentor",    ["Alle"] + sorted(df["Mentor"].unique().tolist()))

    dff = df.copy()
    if opleiding != "Alle":
        dff = dff[dff["Opleiding"] == opleiding]
    if klas != "Alle":
        dff = dff[dff["Klas"] == klas]
    if mentor != "Alle":
        dff = dff[dff["Mentor"] == mentor]


#-------------------------------------------------
# Session state & automatische voorspelling
#-------------------------------------------------

if 'risicostudenten' not in st.session_state:
    st.session_state.risicostudenten = []
if 'laatste_analyse' not in st.session_state:
    st.session_state.laatste_analyse = None
if 'filter_key' not in st.session_state:
    st.session_state.filter_key = None

filter_key = (opleiding, klas, mentor)

if st.session_state.filter_key != filter_key and len(dff) > 0:
    st.session_state.filter_key = filter_key
    st.session_state.laatste_analyse = None
    with st.spinner("Bezig met voorspellen..."):
        risicostudenten = []
        for _, row in dff.iterrows():
            try:
                pred_response = requests.post(
                    "http://localhost:8000/predict_dropout",
                    json={"student": row[features].to_dict()}
                )
                risicostudenten.append((row, pred_response.json()))
            except Exception:
                pass
        risicostudenten.sort(key=lambda x: x[1]["probability"], reverse=True)
        st.session_state.risicostudenten = risicostudenten


st.write("--------------------------")

st.subheader("📊 :blue[**Studentenoverzicht**]")


#-------------------------------------------------
# Kengetallen
#-------------------------------------------------

col1, col2, col3 = st.columns(3)
col1.metric("Gem. Leeftijd",               f"{dff['StudentAge'].mean():.1f} jaar")
col2.metric("Gem. Ongeoorloofd verzuim",   f"{dff['absence_unauthorized'].mean():.1f} dagen")
if "absence_authorized" in dff.columns:
    col3.metric("Gem. Geoorloofd verzuim", f"{dff['absence_authorized'].mean():.1f} dagen")


#-------------------------------------------------
# Studenttabel
#-------------------------------------------------

display_cols = ["Studentnummer", "Naam", "Opleiding", "Klas", "StudentAge",
                "absence_unauthorized", "Mentor"]
if "absence_authorized" in dff.columns:
    display_cols.insert(6, "absence_authorized")

st.dataframe(
    dff[display_cols],
    key="studenten_overzicht",
    column_config={
        "Studentnummer":        st.column_config.NumberColumn(label="Student-ID", format="%d"),
        "Naam":                 st.column_config.TextColumn(label="Naam"),
        "Opleiding":            st.column_config.TextColumn(label="Opleiding"),
        "Klas":                 st.column_config.TextColumn(label="Klas"),
        "StudentAge":           st.column_config.NumberColumn(label="Leeftijd", format="%d jaar"),
        "absence_unauthorized": st.column_config.NumberColumn(
            label="Ongeoorl. verzuim", format="%.1f dagen",
            help="Aantal dagen ongeoorloofd verzuim"),
        "absence_authorized":   st.column_config.NumberColumn(
            label="Geoorl. verzuim", format="%.1f dagen",
            help="Aantal dagen geoorloofd verzuim"),
        "Mentor":               st.column_config.TextColumn(label="Mentor"),
    },
)

st.markdown(
    f"""##### 🔶**Opleiding:** :blue[**{opleiding if opleiding != 'Alle' else 'alle opleidingen'}**],  """
    f"""🔶**Klas:** :blue[**{klas if klas != 'Alle' else 'alle klassen'}**],  """
    f"""🔶**Mentor:** :blue[**{mentor if mentor != 'Alle' else 'alle mentoren'}**],  """
    f"""🔶**Aantal studenten:** :blue[**{len(dff)}**]"""
)

st.write("-------------------------------")


#-------------------------------------------------
# Trendgrafieken
#-------------------------------------------------

st.subheader("📊 :blue[**Trendgrafieken & spreiding**]")

col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(dff, x="StudentAge", nbins=15, title="Leeftijdsverdeling")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig2 = px.box(dff, x="Opleiding", y="absence_unauthorized", points="all",
                  title="Ongeoorloofd verzuim per Opleiding")
    st.plotly_chart(fig2, use_container_width=True)

if st.session_state.risicostudenten:
    top10 = st.session_state.risicostudenten[:10]
    namen  = [f"{row['Naam']} ({row['Klas']})" for row, _ in reversed(top10)]
    kansen = [result["probability"] for _, result in reversed(top10)]
    fig3 = px.bar(
        x=kansen,
        y=namen,
        orientation="h",
        title="Top 10 studenten met hoogste uitvalrisico",
        labels={"x": "Uitvalrisico", "y": "Student"},
        color=kansen,
        color_continuous_scale="Reds",
    )
    fig3.update_traces(
        text=[f"{k:.0%}" for k in kansen],
        textposition="outside",
    )
    fig3.update_layout(
        xaxis_tickformat=".0%",
        xaxis_range=[0, 1.1],
        coloraxis_showscale=False,
        yaxis_title=None,
    )
    st.plotly_chart(fig3, use_container_width=True)

st.download_button(
    "Download selectie als CSV",
    data=dff.to_csv(index=False).encode(),
    file_name="studentenselectie.csv",
    mime="text/csv"
)

st.write("-------------------------------")


#-------------------------------------------------
# Risico op uitval voorspellen
#-------------------------------------------------

st.subheader("📊 :blue[**Risico op uitval — gedetailleerde analyse**]")

if st.session_state.risicostudenten:
    student_namen = [
        f"{row['Naam']} - {row['Opleiding']} / {row['Klas']} ({result['probability']:.1%})"
        for row, result in st.session_state.risicostudenten
    ]

    geselecteerde_student = st.selectbox(
        "Selecteer een student voor gedetailleerde risicoanalyse:",
        options=range(len(student_namen)),
        format_func=lambda x: student_namen[x]
    )

    if st.button("Toon risicoanalyse"):
        row, result = st.session_state.risicostudenten[geselecteerde_student]

        with st.spinner(f"Bezig met genereren van analyse voor {row['Naam']}..."):
            exp_response = requests.post(
                "http://localhost:8000/explain_risk",
                json={
                    "student":      row[features].to_dict(),
                    "prediction":   result["prediction"],
                    "probability":  result["probability"]
                }
            )
            explanation = exp_response.json()["explanation"]

            fi_str  = ""
            fi_dict = {}
            try:
                fi_resp = requests.post(
                    "http://localhost:8000/feature_importance",
                    json={"student": row[features].to_dict()}
                )
                fi_dict = fi_resp.json()["feature_importance"]
                fi_str  = ", ".join([f"{k}: {v:.2f}" for k, v in fi_dict.items()])
            except Exception:
                fi_str = "Feature importance kon niet worden berekend"

            st.session_state.laatste_analyse = {
                "naam":                 row["Naam"],
                "opleiding":            row["Opleiding"],
                "klas":                 row["Klas"],
                "mentor":               row["Mentor"],
                "studentnummer":        int(row["Studentnummer"]),
                "leeftijd":             int(row["StudentAge"]),
                "ongeoorloofd_verzuim": float(row["absence_unauthorized"]),
                "geoorloofd_verzuim":   float(row.get("absence_authorized", 0)),
                "probability":          result["probability"],
                "explanation":          explanation,
                "feature_importance":   fi_str,
                "feature_importance_dict": fi_dict,
            }

            st.info(f"### Uitleg uitvalrisico {row['Naam']} ({row['Opleiding']} / {row['Klas']})")
            st.info(explanation)
            st.caption(f"Belangrijkste risicofactoren (SHAP): {fi_str}")

    #-------------------------------------------------
    # Export
    #-------------------------------------------------

    if st.session_state.laatste_analyse:
        st.write("---")
        st.subheader("Download risicoanalyse")

        analyse = st.session_state.laatste_analyse

        col1, col2 = st.columns(2)

        with col1:
            markdown_content = f"""# Risicoanalyse Studentuitval

**Student:** {analyse['naam']}
**Student-ID:** {analyse['studentnummer']}
**Opleiding:** {analyse['opleiding']}
**Klas:** {analyse['klas']}
**Mentor:** {analyse['mentor']}
**Datum:** {datetime.now().strftime('%d-%m-%Y %H:%M')}

---

## Studentgegevens

- **Leeftijd:** {analyse['leeftijd']} jaar
- **Ongeoorloofd verzuim:** {analyse['ongeoorloofd_verzuim']:.1f} dagen
- **Geoorloofd verzuim:** {analyse['geoorloofd_verzuim']:.1f} dagen
- **Voorspelde uitvalkans:** {analyse['probability']:.1%}

---

## Risicoanalyse

{analyse['explanation']}

---

## Belangrijkste risicofactoren (SHAP)

{analyse['feature_importance']}

---

*Gegenereerd door Edupulse - CEDA*
"""
            st.download_button(
                label="Download als Markdown (.md)",
                data=markdown_content.encode('utf-8'),
                file_name=f"risicoanalyse_{analyse['naam'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

        with col2:
            doc = Document()
            doc.add_heading('Risicoanalyse Studentuitval', 0)

            doc.add_heading('Studentgegevens', 1)
            info = doc.add_paragraph()
            for label, value in [
                ("Student", analyse['naam']),
                ("Student-ID", str(analyse['studentnummer'])),
                ("Opleiding", analyse['opleiding']),
                ("Klas", analyse['klas']),
                ("Mentor", analyse['mentor']),
                ("Datum", datetime.now().strftime('%d-%m-%Y %H:%M')),
            ]:
                info.add_run(f"{label}: ").bold = True
                info.add_run(f"{value}\n")

            doc.add_heading('Kengetallen', 2)
            kgn = doc.add_paragraph()
            kgn.add_run("Leeftijd: ").bold = True
            kgn.add_run(f"{analyse['leeftijd']} jaar\n")
            kgn.add_run("Ongeoorloofd verzuim: ").bold = True
            kgn.add_run(f"{analyse['ongeoorloofd_verzuim']:.1f} dagen\n")
            kgn.add_run("Geoorloofd verzuim: ").bold = True
            kgn.add_run(f"{analyse['geoorloofd_verzuim']:.1f} dagen\n")
            kgn.add_run("Voorspelde uitvalkans: ").bold = True
            kans_run = kgn.add_run(f"{analyse['probability']:.1%}\n")
            kans_run.font.color.rgb = RGBColor(255, 0, 0)
            kans_run.bold = True

            doc.add_heading('Risicoanalyse', 1)
            doc.add_paragraph(analyse['explanation'])

            doc.add_heading('Belangrijkste risicofactoren (SHAP)', 1)
            doc.add_paragraph(analyse['feature_importance'])

            doc.add_paragraph()
            footer = doc.add_paragraph()
            footer_run = footer.add_run('Gegenereerd door Edupulse - CEDA')
            footer_run.italic = True
            footer_run.font.size = Pt(9)

            bio = BytesIO()
            doc.save(bio)
            bio.seek(0)

            st.download_button(
                label="Download als Word (.docx)",
                data=bio,
                file_name=f"risicoanalyse_{analyse['naam'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

else:
    st.info("Pas de filters aan om studenten te analyseren.")


#-------------------------------------------------
# AI Q&A / managementsamenvatting
#-------------------------------------------------

st.subheader("📊 :blue[**AI Q&A: Stel een vraag over deze data**]")

q = st.text_input("Jouw vraag:")
if st.button("Stel vraag") and q:
    sample_csv = dff[display_cols].head(50).to_csv(index=False)
    prompt = f"Gegeven deze studentendata (in CSV-formaat):\n{sample_csv}\nAntwoord op de volgende vraag: {q}"
    resp = requests.post("http://localhost:8000/summarize", json={"data": prompt})
    st.write(resp.json()["summary"])

if st.button("Genereer managementsamenvatting"):
    csv_str = dff[display_cols].head(30).to_csv(index=False)
    response = requests.post("http://localhost:8000/summarize", json={"data": csv_str})
    st.write(response.json()["summary"])
