"""frontend/styles.py — Alle CSS en kleurconstanten voor de EduPlan-frontend."""

# ─────────────────────────────────────────────
# Kleurconstanten
# ─────────────────────────────────────────────

TERRACOTTA = "#c8785a"
ROZE_BG    = "#e8c8c8"
ROZE_LICHT = "#f2e4e4"

# ─────────────────────────────────────────────
# CSS — Startscherm
# ─────────────────────────────────────────────

START_CSS = """
<style>
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap');

[data-testid="stApp"] { background-color: #e8c8c8; font-family: 'General Sans', sans-serif; font-weight: 500; }
[data-testid="stSidebarCollapsedControl"] { display: none; }
[data-testid="stHeader"] { background-color: #e8c8c8 !important;  }
.block-container { padding-top: 0rem; padding-bottom: 2rem; }

div[data-testid="stTextInput"] input {
    padding: 14px 24px !important; font-size: 17px !important;
    background-color: white !important; height: 56px;
    border: 2.5px solid #1a1a1a !important; border-radius: 5px !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #aaa; }
div[data-testid="stTextInput"] > label { display: none; }

div[data-testid="column"]:has(button[kind="primary"]) button {
    background-color: black !important; color: white !important;
    border-radius: 50px !important; font-weight: 700 !important;
    font-size: 17px !important; height: 56px !important; width: 100% !important;
    border: 2.5px solid #1a1a1a !important; border-radius: 5px !important;
}

[data-testid="stButton"] button[kind="secondary"] {
    background-color: white !important; border-radius: 50px !important;
    border: none !important; font-size: 15px !important;
    padding: 10px 20px !important; width: 100%;
    box-shadow: 0 8px 24px rgba(0,0,0,0.20) !important;
}
[data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #fff2f1 !important;
    box-shadow: 0 10px 28px rgba(0,0,0,0.25) !important;
}
[data-testid="stBaseButton-secondary"] {
    background-color: white !important; border-radius: 50px !important;
    border: none !important; box-shadow: 0 8px 24px rgba(0,0,0,0.20) !important;
}
</style>
"""

# ─────────────────────────────────────────────
# CSS — Hoofdscherm
# ─────────────────────────────────────────────

MAIN_CSS = """
<style>
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap');

[data-testid="stApp"]      { background-color: #e8c8c8; font-family: 'General Sans', sans-serif; }
[data-testid="stHeader"]   { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none; }
.block-container           { padding-top: 4rem !important; max-width: 900px; margin: 0 auto; }

/* ── Verborgen nav-knoppen: buiten kaart, in DOM voor JS ── */
div.block-container > div > [data-testid="stVerticalBlock"] > div:has(> [data-testid="stButton"]) {
    position: absolute !important;
    left: -9999px !important;
    top: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ── Witte card ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important;
    border-radius: 20px !important;
    border: none !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.37);
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
    white-space: nowrap !important;
    width: auto !important;
    min-width: max-content !important;
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
    white-space: nowrap !important;
    width: auto !important;
    min-width: max-content !important;
}
div.nav-actief [data-testid="stBaseButton-secondary"] p,
div.nav-actief [data-testid="stBaseButton-secondary"] span,
div.nav-actief button[kind="secondary"] p,
div.nav-actief button[kind="secondary"] span,
div.nav-inactief [data-testid="stBaseButton-secondary"] p,
div.nav-inactief [data-testid="stBaseButton-secondary"] span,
div.nav-inactief button[kind="secondary"] p,
div.nav-inactief button[kind="secondary"] span {
    white-space: nowrap !important;
    overflow: visible !important;
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
    padding: 0px 0px !important;
    color: #1a1a1a !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.37);
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
    background: white !important;
    border: none !important;
    color: #777 !important;
    font-size: 13px !important;
    padding: 0 !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.37);
}

/* ── Actie-knoppen (DOWNLOAD) ── */
div.actie-knoppen button,
div.actie-knoppen a,
div.actie-knoppen [data-testid="stBaseButton-secondary"],
div.actie-knoppen [data-testid="stDownloadButton"] > a {
    background-color: #1a1a1a !important;
    color: white !important;
    border-radius: 50px !important;
    border: none !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.07em !important;
    padding: 8px 24px !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}
</style>
"""
