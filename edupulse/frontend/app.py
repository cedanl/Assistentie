# frontend/app.py
import streamlit as st
from streamlit_extras.bottom_container import bottom

st.set_page_config(
    page_title="EduPulse — Uitvalrisico",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CEDA huisstijl
st.markdown("""
<style>
  :root {
    --oranje: #DD784B;
    --blauw:  #3D68EC;
    --groen:  #00AF81;
    --geel:   #F4D74B;
    --roze:   #F4D9DC;
    --zwart:  #000000;
    --bg:     #F0F1F3;
  }
  .stApp { background: var(--bg); }

  /* Native Streamlit header zwart — toggle en Deploy-knop blijven werken */
  [data-testid="stHeader"] {
    background: #000 !important;
    border-bottom: none !important;
  }
  [data-testid="stHeader"] * {
    color: white !important;
  }
  [data-testid="stHeader"] svg {
    fill: white !important;
    stroke: white !important;
  }

  /* Native header is position:absolute height:3.75rem — zet block-container
     padding-top exact op header-hoogte zodat branding er direct onder zit
     (het padding-gebied ligt ACHTER de zwarte absolute header, dus geen grijs) */
  [data-testid="stMainBlockContainer"],
  .stMainBlockContainer,
  [data-testid="stMain"] .block-container {
    padding-top: 3.75rem !important;
  }

  /* Branding balk — direct onder de native header, geen tussenruimte.
     Negatieve margin-top compenseert de flex-gap tussen de (onzichtbare)
     style-markdown en deze branding-markdown. */
  .edupulse-branding {
    background: #000;
    padding: 10px 28px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-left: calc(-50vw + 50%);
    margin-right: calc(-50vw + 50%);
    width: 100vw;
    margin-top: -1rem;
    margin-bottom: 24px;
  }

  /* Sidebar */
  [data-testid="stSidebar"] { background: var(--zwart) !important; }
  [data-testid="stSidebar"] * { color: white !important; }
  [data-testid="stSidebar"] input { color: #111 !important; background: white !important; }
  [data-testid="stSidebar"] input::placeholder { color: #888 !important; }

  .stButton > button {
    background: var(--oranje) !important;
    color: white !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 10px !important;
  }
  .stButton > button:hover {
    background: #c5683e !important;
    transform: translateY(-1px);
  }
  .metric-card {
    background: white; border-radius: 14px;
    padding: 20px; box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  }
  .dreiging { color: #DD784B; font-weight: 800; }
  .opkoers  { color: #00AF81; font-weight: 800; }

  /* Footer: volle breedte */
  .edupulse-footer {
    margin-left: calc(-50vw + 50%);
    margin-right: calc(-50vw + 50%);
    width: 100vw;
    background: #000;
    padding: 10px 28px;
  }
</style>
""", unsafe_allow_html=True)

# Branding balk — direct onder de zwarte native header
st.markdown("""
<div class="edupulse-branding">
  <span style="color:#DD784B;font-size:1.3rem;">◉</span>
  <span style="color:white;font-weight:700;">Npuls</span>
  <div style="width:1px;height:20px;background:rgba(255,255,255,0.2);margin:0 4px;"></div>
  <span style="color:white;font-weight:800;">Edu<span style="color:#F4D74B;">Pulse</span></span>
  <span style="color:#DD784B;font-size:0.6rem;font-weight:700;letter-spacing:0.09em;text-transform:uppercase;">
    Moving Education.
  </span>
</div>
""", unsafe_allow_html=True)

paginas = [
    st.Page("pages/uitvalrisico.py", title="Uitvalrisico check", icon="🎯"),
    st.Page("pages/geschiedenis.py", title="Eerdere berekeningen", icon="📋"),
]
nav = st.navigation(paginas)
nav.run()

with bottom():
    st.markdown("""
    <div class="edupulse-footer">
      <p style="text-align:center;font-size:0.55rem;font-weight:500;color:#aaa;
                font-family:'General Sans',sans-serif;margin:0;">
        <img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg"
             style="max-width:1.2em;max-height:1.2em;margin:0 .1em;vertical-align:middle;">
        <img src="https://mirrors.creativecommons.org/presskit/icons/by.svg"
             style="max-width:1.2em;max-height:1.2em;margin:0 .2em 0 .1em;vertical-align:middle;">
        Op deze analytics tool is de Creative Commons Naamsvermelding 4.0-licentie van toepassing.
        Maak bij gebruik van dit werk vermelding van de volgende referentie:
        <em>AI en data waarde(n)vol inzetten: CEDA 2026 – EduPulse. Utrecht: Npuls</em>
      </p>
    </div>
    """, unsafe_allow_html=True)
