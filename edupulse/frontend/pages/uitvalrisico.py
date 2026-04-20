# frontend/pages/uitvalrisico.py
import requests
import streamlit as st

API = "http://localhost:8001"

st.title("Uitvalrisico check")
st.caption("Stel een vraag over een student of zoek een student op.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "sessie_id" not in st.session_state:
    st.session_state.sessie_id = None
if "geselecteerde_student" not in st.session_state:
    st.session_state.geselecteerde_student = None

# Sidebar: student zoeken
with st.sidebar:
    st.subheader("Student zoeken")
    zoek = st.text_input("Naam of studentnummer", placeholder="Bijv. Youssef of 20240001")
    if zoek:
        try:
            resp = requests.get(f"{API}/students?limit=100", timeout=10)
            resp.raise_for_status()
            studenten = resp.json()
            q = zoek.lower()
            treffer = [
                s for s in studenten
                if q in s["naam"].lower() or q in s["studentnummer"]
            ][:8]
            for s in treffer:
                if st.button(f"{s['naam']} ({s['studentnummer']})", key=s["studentnummer"]):
                    st.session_state.geselecteerde_student = s["studentnummer"]
        except Exception:
            st.error("API niet bereikbaar. Start de backend eerst.")

# Student kaart
if st.session_state.geselecteerde_student:
    nr = st.session_state.geselecteerde_student
    try:
        resp_s = requests.get(f"{API}/students/{nr}", timeout=10)
        resp_s.raise_for_status()
        student = resp_s.json()
        resp_r = requests.get(f"{API}/risk/{nr}", timeout=10)
        resp_r.raise_for_status()
        risico = resp_r.json()

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"### {student['naam']}")
            st.caption(f"{student['opleiding']} · {student['cohort']} · {student['leerweg']}")
        with col2:
            kleur = "dreiging" if risico["status"] == "dreiging" else "opkoers"
            label = "⚠ Dreiging" if risico["status"] == "dreiging" else "✓ Op koers"
            st.markdown(f"""
            <div class='metric-card' style='text-align:center;'>
              <div style='font-size:0.7rem;color:#AAA;text-transform:uppercase;letter-spacing:0.08em;'>
                Succeskans
              </div>
              <div class='{kleur}' style='font-size:2.5rem;'>{risico['succes_kans']*100:.0f}%</div>
              <div class='{kleur}'>{label}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Aanwezigheid", f"{student['aanwezigheid']*100:.0f}%")
            st.metric("BSA punten", student['bsa_studiepunten'])
            st.markdown("</div>", unsafe_allow_html=True)

        # SHAP top-3
        st.markdown("**Top-3 beïnvloedende factoren:**")
        for item in risico["shap_top3"]:
            richting = "🔴" if item["bijdrage"] < 0 else "🟢"
            st.markdown(f"{richting} **{item['feature']}** — bijdrage: `{item['bijdrage']:.3f}`")

    except Exception as e:
        st.error(f"Fout bij laden studentdata: {e}")

st.divider()

# Agent dialoogvenster
st.subheader("Vraag aan de agent")
for msg in st.session_state.chat_history:
    with st.chat_message(msg["rol"]):
        st.markdown(msg["tekst"])

vraag = st.chat_input("Stel een vraag, bijv. 'Hoe staat Youssef ervoor?' of een studentnummer")
if vraag:
    st.session_state.chat_history.append({"rol": "user", "tekst": vraag})
    with st.chat_message("user"):
        st.markdown(vraag)

    with st.chat_message("assistant"):
        with st.spinner("Agent denkt na..."):
            try:
                r = requests.post(
                    f"{API}/agent/chat",
                    json={"message": vraag, "session_id": st.session_state.sessie_id},
                    timeout=60,
                )
                data = r.json()
                antwoord = data["response"]
                st.session_state.sessie_id = data["session_id"]
            except Exception as e:
                antwoord = f"Fout: {e}. Is de backend actief op poort 8001?"
        st.markdown(antwoord)
    st.session_state.chat_history.append({"rol": "assistant", "tekst": antwoord})
