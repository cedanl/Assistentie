"""frontend/ui.py
### STREAMLIT FRONTEND (`frontend/ui.py`)

"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(layout="wide")
df = pd.read_csv("../shared/data.csv")
features = ["Cijfer", "Aanwezigheid", "Waarschuwingen", "EC"]

st.title("Edupulse - Signalering en interventie bij mogelijk studentuitval")


with st.sidebar:
    opleiding = st.selectbox("Opleiding", ["Alle"] + sorted(df["Opleiding"].unique().tolist()))
    klas = st.selectbox("Klas", ["Alle"] + sorted(df["Klas"].unique().tolist()))
    mentor = st.selectbox("Mentor", ["Alle"] + sorted(df["Mentor"].unique().tolist()))
    dff = df.copy()
    if opleiding != "Alle":
        dff = dff[dff["Opleiding"] == opleiding]
    if klas != "Alle":
        dff = dff[dff["Klas"] == klas]
    if mentor != "Alle":
        dff = dff[dff["Mentor"] == mentor]

col1, col2, col3 = st.columns(3)
col1.metric("Gemiddeld Cijfer", f"{dff['Cijfer'].mean():.2f}")
col2.metric("Gem. Aanwezigheid", f"{dff['Aanwezigheid'].mean():.1f}%")
col3.metric("Waarschuwingen (gem.)", f"{dff['Waarschuwingen'].mean():.2f}")

st.subheader("Studentenoverzicht")
st.dataframe(dff.head(30))

st.subheader("Trendgrafieken & spreiding")
col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(dff, x="Cijfer", nbins=15, title="Cijferverdeling")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig2 = px.box(dff, x="Opleiding", y="Aanwezigheid", points="all", title="Aanwezigheid per Opleiding")
    st.plotly_chart(fig2, use_container_width=True)

st.download_button(
    "Download selectie als CSV",
    data=dff.to_csv(index=False).encode(),
    file_name="studentenselectie.csv",
    mime="text/csv"
)

st.subheader("AI Q&A: Stel een vraag over deze data")
q = st.text_input("Jouw vraag:")
if st.button("Stel vraag") and q:
    sample_csv = dff.head(50).to_csv(index=False)
    prompt = f"Gegeven deze studentendata (in CSV-formaat):\n{sample_csv}\nAntwoord op de volgende vraag: {q}"
    resp = requests.post(
        "http://localhost:8000/summarize",
        json={"data": prompt}
    )
    st.write(resp.json()["summary"])

if st.button("Genereer managementsamenvatting"):
    csv_str = dff.head(30).to_csv(index=False)
    response = requests.post(
        "http://localhost:8000/summarize",
        json={"data": csv_str}
    )
    st.write(response.json()["summary"])

st.subheader("Risico op uitval voorspellen")
risicostudenten = []
for idx, row in dff.iterrows():
    student_dict = row[features].to_dict()
    pred_response = requests.post("http://localhost:8000/predict_dropout", json={"student": student_dict})
    result = pred_response.json()
    if result["prediction"] == 1:
        risicostudenten.append((row, result))

if risicostudenten:
    st.markdown(f"### Studenten met verhoogd risico ({len(risicostudenten)})")
    for row, result in risicostudenten:
        st.write(f"**{row['Naam']}** ({row['Opleiding']} / {row['Klas']}): Kans op uitval: {result['probability']:.1%}")
        exp_response = requests.post(
            "http://localhost:8000/explain_risk",
            json={
                "student": row[features].to_dict(),
                "prediction": result["prediction"],
                "probability": result["probability"]
            })
        st.info(exp_response.json()["explanation"])
        fi_resp = requests.post(
            "http://localhost:8000/feature_importance",
            json={"student": row[features].to_dict()}
        )
        fi = fi_resp.json()["feature_importance"]
        fi_str = ", ".join([f"{k}: {v:.2f}" for k,v in fi.items()])
        st.caption(f"Belangrijkste risicofactoren (SHAP): {fi_str}")
else:
    st.success("Geen risicostudenten in deze selectie!")