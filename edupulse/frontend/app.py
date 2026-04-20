# frontend/app.py
import streamlit as st

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
  [data-testid="stSidebar"] { background: var(--zwart) !important; }
  [data-testid="stSidebar"] * { color: white !important; }
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
</style>
""", unsafe_allow_html=True)

# Topbalk
st.markdown("""
<div style="background:#000;padding:12px 28px;display:flex;align-items:center;gap:10px;margin-bottom:24px;">
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
