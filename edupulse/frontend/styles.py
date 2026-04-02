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
[data-testid="stHeader"] { background-color: #e8c8c8 !important; }
.block-container { padding-top: 0rem; padding-bottom: 2rem; }

/* ── Bestand uploaden ── */
[data-testid="stFileUploader"] {
    background: #f2e4e4 !important;
    border-radius: 12px !important;
    padding: 4px 12px !important;
}
[data-testid="stFileUploaderDropzone"] {
    border: none !important;
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background-color: #1a1a1a !important;
    color: white !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border: none !important;
    letter-spacing: 0.06em !important;
}

/* ── START DE UITNODIGINGSREGEL knop ── */
[data-testid="stBaseButton-primary"] {
    background-color: #1a1a1a !important;
    color: white !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    font-size: 17px !important;
    height: 60px !important;
    width: 100% !important;
    border: none !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stBaseButton-primary"]:hover { background-color: #333 !important; }
[data-testid="stBaseButton-primary"]:disabled { background-color: #aaa !important; cursor: not-allowed !important; }

/* ── Demo-data checkbox ── */
[data-testid="stCheckbox"] label p {
    font-size: 15px !important;
    font-weight: 500 !important;
    color: #1a1a1a !important;
}

/* ── Opleidingen-pills ── */
[data-testid="stBaseButton-secondary"] {
    background-color: white !important;
    border-radius: 50px !important;
    border: none !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.20) !important;
    font-size: 15px !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    background-color: #e8c8c8 !important;
    font-color: #1a1a1a;
    box-shadow: 0 10px 28px rgba(0,0,0,0.25) !important;
}

/* ── Bottom bar startscherm (roze) ── */
[data-testid="stBottom"] { background-color: #e8c8c8 !important; }
[data-testid="stBottomBlockContainer"] { background-color: #e8c8c8 !important; }
</style>
"""

# ─────────────────────────────────────────────
# CSS — Hoofdscherm
# ─────────────────────────────────────────────

MAIN_CSS = """
<style>
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap');

[data-testid="stApp"]      { background-color: #e8c8c8; font-family: 'General Sans', sans-serif; }
[data-testid="stHeader"]   { background-color: #f2e4e4 !important; z-index: 998 !important; }
[data-testid="stToolbar"]  { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none; }
.block-container           { padding-top: 0 !important; max-width: 900px; margin: 0 auto; }

/* ── Header-rij: lichtroze, sticky ── */
div.block-container > [data-testid="stVerticalBlock"] > div:has(> [data-testid="stHorizontalBlock"]) {
    background-color: #f2e4e4 !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 9999 !important;
    padding: 0px 0 !important;
    box-shadow: 0 6px 12px rgba(0,0,0,0.08) !important;
}

/* ── Witte card ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important;
    border-radius: 20px !important;
    border: none !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.37);
    padding: 4px 8px !important;
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

/* ── Bottom bar (licht roze, net als header) ── */
[data-testid="stBottom"] {
    background-color: #f2e4e4 !important;
}
[data-testid="stBottomBlockContainer"] {
    background-color: #f2e4e4 !important;
}

/* ── Download-knop ── */
[data-testid="stDownloadButton"] button {
    background-color: #1a1a1a !important;
    color: white !important;
    border-radius: 50px !important;
    border: none !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.07em !important;
    white-space: nowrap !important;
    width: 100% !important;
}
</style>
"""
