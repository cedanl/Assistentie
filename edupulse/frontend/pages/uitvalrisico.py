# frontend/pages/uitvalrisico.py
import requests
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

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
            treffer = [s for s in studenten if q in s["naam"].lower() or q in s["studentnummer"]][
                :8
            ]
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

        naam_col, m1, m2, m3, m4 = st.columns([2, 1, 1, 1, 1])
        with naam_col:
            st.markdown(f"### {student['naam']}")
            st.caption(f"{student['opleiding']} · {student['cohort']} · {student['leerweg']}")
        status_label = "⚠️ Dreiging" if risico["status"] == "dreiging" else "✅ Op koers"
        aanw = student["aanwezigheid"]
        bsa = student["bsa_studiepunten"]

        with m1:
            st.metric("🎯 Succeskans", f"{risico['succes_kans'] * 100:.0f}%", status_label)
        with m2:
            st.metric("⚠️ Uitvalkans", f"{risico['uitval_kans'] * 100:.0f}%", status_label)
        with m3:
            aanw_label = "✅ Voldoende" if aanw >= 0.80 else "⚠️ Te laag"
            st.metric("📅 Aanwezigheid", f"{aanw * 100:.0f}%", aanw_label)
        with m4:
            bsa_label = "✅ Op schema" if bsa >= 40 else "⚠️ Achterstand"
            st.metric("📚 BSA punten", bsa, bsa_label)

        style_metric_cards(border_left_color="#DD784B", box_shadow=True)

        # SHAP top-3
        st.markdown("**Top-3 beïnvloedende factoren:**")
        for item in risico["shap_top3"]:
            richting = "🔴" if item["bijdrage"] > 0 else "🟢"
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
                if not r.ok:
                    antwoord = f"⚠️ Backend fout ({r.status_code}): {data.get('detail', r.text)}"
                else:
                    antwoord = data["response"]
                    st.session_state.sessie_id = data["session_id"]
            except Exception as e:
                antwoord = f"Fout: {e}. Is de backend actief op poort 8001?"
        st.markdown(antwoord)
    st.session_state.chat_history.append({"rol": "assistant", "tekst": antwoord})
