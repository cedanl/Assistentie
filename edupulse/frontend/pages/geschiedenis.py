# frontend/pages/geschiedenis.py
import requests
import streamlit as st

API = "http://localhost:8001"

st.title("Eerdere berekeningen")
st.caption("Overzicht van alle studenten en hun uitvalrisico.")

try:
    resp = requests.get(f"{API}/students?limit=1000", timeout=10)
    resp.raise_for_status()
    studenten = resp.json()
except Exception:
    st.error("API niet bereikbaar. Start de backend eerst.")
    st.stop()

# Filters
col1, col2 = st.columns(2)
with col1:
    filter_status = st.selectbox("Filter op status", ["Alle", "Dreiging", "Op koers"])
with col2:
    filter_opleiding = st.selectbox(
        "Filter op opleiding", ["Alle"] + sorted(list({s["opleiding"] for s in studenten}))
    )

# Haal risico's op voor eerste 50 (performance sprint 1)
weergave = studenten[:50]
if filter_opleiding != "Alle":
    weergave = [s for s in weergave if s["opleiding"] == filter_opleiding]

risicos = []
mislukt = 0
for s in weergave:
    try:
        resp_r = requests.get(f"{API}/risk/{s['studentnummer']}", timeout=10)
        resp_r.raise_for_status()
        risicos.append({**s, **resp_r.json()})
    except Exception:
        mislukt += 1

if mislukt:
    st.warning(f"{mislukt} student(en) konden niet worden geladen.")

if filter_status == "Dreiging":
    risicos = [r for r in risicos if r.get("status") == "dreiging"]
elif filter_status == "Op koers":
    risicos = [r for r in risicos if r.get("status") == "op_koers"]

# Samenvatting
if risicos:
    totaal = len(risicos)
    dreiging = sum(1 for r in risicos if r.get("status") == "dreiging")
    gem = sum(r.get("succes_kans", 0) for r in risicos) / totaal

    c1, c2, c3 = st.columns(3)
    c1.metric("Studenten", totaal)
    c2.metric("⚠ Dreiging", dreiging)
    c3.metric("Gem. succeskans", f"{gem * 100:.0f}%")

    st.divider()

    for r in sorted(risicos, key=lambda x: x.get("succes_kans", 1)):
        kleur = "🔴" if r.get("status") == "dreiging" else "🟢"
        label = "⚠ Dreiging" if r.get("status") == "dreiging" else "✓ Op koers"
        with st.expander(
            f"{kleur} {r['naam']} ({r['studentnummer']}) — "
            f"{r.get('succes_kans', 0) * 100:.0f}% succeskans — {label}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Opleiding:** {r['opleiding']}")
                st.write(f"**Cohort:** {r['cohort']}")
                st.write(f"**Aanwezigheid:** {r['aanwezigheid'] * 100:.0f}%")
                st.write(f"**BSA punten:** {r['bsa_studiepunten']}")
            with col2:
                st.write(f"**Nederlands:** {r['cijfer_nederlands']}")
                st.write(f"**Rekenen:** {r['cijfer_rekenen']}")
                st.write(f"**Mentor:** {r['mentor_naam']}")
                st.write(f"**Mentor email:** {r['mentor_email']}")
else:
    st.info("Geen studenten gevonden voor dit filter.")
