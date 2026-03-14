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



"""frontend/ui.py
### STREAMLIT FRONTEND (`frontend/ui.py`)

"""

#-------------------------------------------------
# Imports dependencies
#-------------------------------------------------

import streamlit as st
import pandas as pd
import requests
import plotly
import plotly.express as px
from docx import Document
from docx.shared import Pt, RGBColor
from io import BytesIO
from datetime import datetime
from PIL import Image


#-------------------------------------------------
# Constants                                         
#-------------------------------------------------
features = ["Cijfer", "Aanwezigheid", "Waarschuwingen", "EC"]
image = Image.open("assets/achtergrond.png")

# Load the dataset
# Ensure the CSV file is in the correct path relative to this script
# @st.cache_data(ttl=3600, show_spinner=True)
df = pd.read_csv("shared/data.csv")


#-------------------------------------------------
# Page configuration 
#-------------------------------------------------
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None,
    page_icon="🧮",
    page_title="Edupulse - Studentuitval Signalering en Interventie",
)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(
        """
                #### :blue[**Studentuitval Signalering en Interventie**]\n
                ## 📊:blue[**Edupulse**]"""
    )

with col2:
    if image is not None:
        st.image(
            image,
            caption=None,
            width=220,
            clamp=True,
            channels="RGB",
            output_format="auto",
        )
    else:
        st.warning("Afbeelding kon niet worden geladen.")


with st.sidebar:
    st.markdown("##### 🎯**Kies een opleiding, klas en/of mentor**")
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

st.subheader(
        f"📊 :blue[**Studentenoverzicht**]"
)

st.markdown(
    f"""###### 🔶**Opleiding:** :blue[**{opleiding.strip() if opleiding.strip() != "Alle" else 'alle opleidingen'}**],   🔶**Klas:** :blue[**{klas.strip() if klas.strip() != "Alle" else 'alle klassen'}**],   🔶**Mentor:** :blue[**{mentor if mentor != "Alle" else 'alle mentoren'}**],   🔶**Aantal studenten:** :blue[**{len(dff)}**]"""
)

col1, col2, col3 = st.columns(3)
col1.metric("Gemiddeld Cijfer", f"{dff['Cijfer'].mean():.2f}")
col2.metric("Gem. Aanwezigheid", f"{dff['Aanwezigheid'].mean():.1f}%")
col3.metric("Waarschuwingen (gem.)", f"{dff['Waarschuwingen'].mean():.2f}")


# Maak een kopie voor weergave met styling
display_df = dff.head(30).copy()

# Functie voor kleurcodering van cijfers
def color_cijfer(val):
    if val < 5.5:
        return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
    elif val < 6.5:
        return 'background-color: #fff4cc; color: #996600'
    else:
        return 'background-color: #ccffcc; color: #006600'

# Functie voor kleurcodering van aanwezigheid
def color_aanwezigheid(val):
    if val < 75:
        return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
    elif val < 85:
        return 'background-color: #fff4cc; color: #996600'
    else:
        return 'background-color: #ccffcc; color: #006600'

# Functie voor kleurcodering van waarschuwingen
def color_waarschuwingen(val):
    if val >= 3:
        return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
    elif val >= 1:
        return 'background-color: #fff4cc; color: #996600'
    else:
        return 'background-color: #ccffcc; color: #006600'

# Functie voor kleurcodering van EC
def color_ec(val):
    if val < 30:
        return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
    elif val < 45:
        return 'background-color: #fff4cc; color: #996600'
    else:
        return 'background-color: #ccffcc; color: #006600'



st.dataframe(
    dff,
    key="studenten_overzicht",
    # on_change=change_data,
    column_config={
        "Student-ID": st.column_config.NumberColumn(
            label="Student-ID", format="%d", help="Unieke ID van de student"
        ),
        "Naam": st.column_config.TextColumn(label="Naam", help="Naam van de student"),
        "Opleiding": st.column_config.TextColumn(
            label="Opleiding", help="Naam van de opleiding"
        ),
        "Klas": st.column_config.TextColumn(label="Klas", help="Klas van de student"),
        "Mentor": st.column_config.TextColumn(
            label="Mentor", help="Mentor van de student"
        ),
        "Cijfer": st.column_config.NumberColumn(
            label="Cijfer", format="%.2f", help="Gemiddeld cijfer"
        ),
        "Aanwezigheid": st.column_config.ProgressColumn(
            label="Aanwezigheid",
            format="%.1f%%",
            min_value=0,
            max_value=100,
            help="Aanwezigheid percentage",
        ),
        "Waarschuwingen": st.column_config.NumberColumn(
            label="Waarschuwingen", format="%d", help="Aantal waarschuwingen"
        ),
        "EC": st.column_config.ProgressColumn(
            label="EC",
            format="%d",
            min_value=0,
            max_value=60,
            help="Aantal behaalde EC's",
        ),
    },
)

# Pas styling toe
# styled_df = display_df.style.format({
    # 'Cijfer': '{:.1f}',
    # 'Aanwezigheid': '{:.1f}%',
    # 'EC': '{:.0f}'
# }).applymap(color_cijfer, subset=['Cijfer'])\
  # .applymap(color_aanwezigheid, subset=['Aanwezigheid'])\
  # .applymap(color_waarschuwingen, subset=['Waarschuwingen'])\
  # .applymap(color_ec, subset=['EC'])\
  # .bar(subset=['Aanwezigheid'], color='#5fba7d', vmin=0, vmax=100)\
  # .bar(subset=['EC'], color='#4d9de0', vmin=0, vmax=60)
# 
# st.dataframe(styled_df, use_container_width=True, height=600)

st.subheader(
        f"📊 :blue[**Trendgrafieken & spreiding**]"
)

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

st.subheader(
        f"📊 :blue[**AI Q&A: Stel een vraag over deze data**]"
)

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

st.subheader(
        f"📊 :blue[**Risico op uitval voorspellen**]"
)
# Initialiseer session state voor risicostudenten
if 'risicostudenten' not in st.session_state:
    st.session_state.risicostudenten = []
if 'laatste_analyse' not in st.session_state:
    st.session_state.laatste_analyse = None

if st.button("Voorspel uitval"):
    st.session_state.risicostudenten = []
    with st.spinner("Bezig met voorspellen..."):
        for idx, row in dff.iterrows():
            student_dict = row[features].to_dict()
            pred_response = requests.post("http://localhost:8000/predict_dropout", json={"student": student_dict})
            result = pred_response.json()
            if result["prediction"] == 1:
                st.session_state.risicostudenten.append((row, result))
    
if st.session_state.risicostudenten:
    st.markdown(f"### Studenten met verhoogd risico ({len(st.session_state.risicostudenten)})")
    
    # Toon lijst van risicostudenten
    for idx, (row, result) in enumerate(st.session_state.risicostudenten):
        st.markdown(f":red[**{row['Naam']}**] ({row['Opleiding']} / {row['Klas']}): Hoge kans op uitval: {result['probability']:.1%}")
    
    st.write("---")
    
    # Selecteer student voor gedetailleerde analyse
    student_namen = [f"{row['Naam']} - {row['Opleiding']} / {row['Klas']} ({result['probability']:.1%})" 
                     for row, result in st.session_state.risicostudenten]
    
    geselecteerde_student = st.selectbox(
        "Selecteer een student voor gedetailleerde risicoanalyse:",
        options=range(len(student_namen)),
        format_func=lambda x: student_namen[x]
    )
    
    if st.button("Toon risicoanalyse"):
        row, result = st.session_state.risicostudenten[geselecteerde_student]
        
        with st.spinner(f"Bezig met genereren van analyse voor {row['Naam']}..."):
            # Uitleg ophalen
            exp_response = requests.post(
                "http://localhost:8000/explain_risk",
                json={
                    "student": row[features].to_dict(),
                    "prediction": result["prediction"],
                    "probability": result["probability"]
                })
            
            explanation = exp_response.json()["explanation"]
            
            # Feature importance ophalen
            fi_str = ""
            fi_dict = {}
            try:
                fi_resp = requests.post(
                    "http://localhost:8000/feature_importance",
                    json={"student": row[features].to_dict()}
                )
                fi_dict = fi_resp.json()["feature_importance"]
                fi_str = ", ".join([f"{k}: {v:.2f}" for k,v in fi_dict.items()])
            except:
                fi_str = "Feature importance kon niet worden berekend"
            
            # Bewaar analyse in session state
            st.session_state.laatste_analyse = {
                "naam": row['Naam'],
                "opleiding": row['Opleiding'],
                "klas": row['Klas'],
                "mentor": row['Mentor'],
                "cijfer": row['Cijfer'],
                "aanwezigheid": row['Aanwezigheid'],
                "waarschuwingen": row['Waarschuwingen'],
                "ec": row['EC'],
                "probability": result['probability'],
                "explanation": explanation,
                "feature_importance": fi_str,
                "feature_importance_dict": fi_dict
            }
            
            st.info(f"### Uitleg uitvalrisico {row['Naam']} ({row['Opleiding']} / {row['Klas']})")
            st.info(explanation)
            st.caption(f"Belangrijkste risicofactoren (SHAP): {fi_str}")
    
    # Toon downloadknoppen als er een analyse is gegenereerd
    if st.session_state.laatste_analyse:
        st.write("---")
        st.subheader("Download risicoanalyse")
        
        analyse = st.session_state.laatste_analyse
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Markdown export
            markdown_content = f"""# Risicoanalyse Studentuitval

**Student:** {analyse['naam']}  
**Opleiding:** {analyse['opleiding']}  
**Klas:** {analyse['klas']}  
**Mentor:** {analyse['mentor']}  
**Datum:** {datetime.now().strftime('%d-%m-%Y %H:%M')}

---

## Studentgegevens

- **Cijfer:** {analyse['cijfer']}
- **Aanwezigheid:** {analyse['aanwezigheid']}%
- **Waarschuwingen:** {analyse['waarschuwingen']}
- **EC (studiepunten):** {analyse['ec']}
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
            # DOCX export
            doc = Document()
            
            # Titel
            title = doc.add_heading('Risicoanalyse Studentuitval', 0)
            
            # Studentinfo
            doc.add_heading('Studentgegevens', 1)
            student_info = doc.add_paragraph()
            student_info.add_run(f"Student: ").bold = True
            student_info.add_run(f"{analyse['naam']}\n")
            student_info.add_run(f"Opleiding: ").bold = True
            student_info.add_run(f"{analyse['opleiding']}\n")
            student_info.add_run(f"Klas: ").bold = True
            student_info.add_run(f"{analyse['klas']}\n")
            student_info.add_run(f"Mentor: ").bold = True
            student_info.add_run(f"{analyse['mentor']}\n")
            student_info.add_run(f"Datum: ").bold = True
            student_info.add_run(f"{datetime.now().strftime('%d-%m-%Y %H:%M')}\n")
            
            # Kengetallen
            doc.add_heading('Kengetallen', 2)
            kengetallen = doc.add_paragraph()
            kengetallen.add_run(f"Cijfer: ").bold = True
            kengetallen.add_run(f"{analyse['cijfer']}\n")
            kengetallen.add_run(f"Aanwezigheid: ").bold = True
            kengetallen.add_run(f"{analyse['aanwezigheid']}%\n")
            kengetallen.add_run(f"Waarschuwingen: ").bold = True
            kengetallen.add_run(f"{analyse['waarschuwingen']}\n")
            kengetallen.add_run(f"EC (studiepunten): ").bold = True
            kengetallen.add_run(f"{analyse['ec']}\n")
            kengetallen.add_run(f"Voorspelde uitvalkans: ").bold = True
            kans_run = kengetallen.add_run(f"{analyse['probability']:.1%}\n")
            kans_run.font.color.rgb = RGBColor(255, 0, 0)
            kans_run.bold = True
            
            # Analyse
            doc.add_heading('Risicoanalyse', 1)
            doc.add_paragraph(analyse['explanation'])
            
            # Feature importance
            doc.add_heading('Belangrijkste risicofactoren (SHAP)', 1)
            doc.add_paragraph(analyse['feature_importance'])
            
            # Footer
            doc.add_paragraph()
            footer = doc.add_paragraph()
            footer_run = footer.add_run('Gegenereerd door Edupulse - CEDA')
            footer_run.italic = True
            footer_run.font.size = Pt(9)
            
            # Save to BytesIO
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
    if st.session_state.get('risicostudenten') is not None and len(st.session_state.risicostudenten) == 0:
        st.success("Geen risicostudenten in deze selectie!")
        
