# EduPulse — Architectuur & Flow

## 1. Architectuur

```mermaid
graph TB
    subgraph Frontend["Frontend (poort 8502)"]
        APP["frontend/app.py\nStreamlit UI"]
    end

    subgraph Backend["Backend (poort 8000)"]
        API["backend/main.py\nFastAPI"]
        MODEL["backend/model.joblib\nRandomForestRegressor"]
        SHAP["SHAP TreeExplainer"]
        OPENAI["OpenAI GPT-4o-mini"]
    end

    subgraph Shared["Shared"]
        DATA["shared/data.csv\n1.000 studenten, 11 opleidingen"]
        PREP["shared/data_prep.py\nDownload data + model"]
    end

    subgraph Bron["Externe bronnen"]
        UITNODIG["MondriaanBI/Uitnodigingsregel\n(GitHub)"]
    end

    subgraph Standalone["Standalone CLI"]
        MAIN["main.py\nClaude Agent"]
        ANTHROPIC["Anthropic API"]
    end

    APP -->|"HTTP POST"| API
    API --> MODEL
    API --> SHAP
    API --> OPENAI
    PREP -->|"downloadt"| UITNODIG
    UITNODIG -->|"synth_data_pred.csv\nmodel.joblib"| PREP
    PREP -->|"genereert"| DATA
    PREP -->|"slaat op"| MODEL
    DATA -->|"laadt"| APP
    MAIN --> ANTHROPIC

    style Frontend fill:#dbeafe
    style Backend fill:#dcfce7
    style Shared fill:#fef9c3
    style Bron fill:#ede9fe
    style Standalone fill:#fce7f3
```

---

## 2. Flow & werking

```mermaid
sequenceDiagram
    actor Gebruiker
    participant FE as Streamlit Frontend
    participant BE as FastAPI Backend
    participant RF as RandomForestRegressor
    participant SHAP as SHAP Explainer
    participant GPT as OpenAI GPT-4o-mini

    Gebruiker->>FE: Startscherm — kies opleiding (zoekbalk of pill)
    FE->>FE: Navigeer naar hoofdscherm

    FE->>FE: Laad data.csv & filter op opleiding/klas
    note over FE: Automatisch bij filter-wijziging

    loop Per student in selectie
        FE->>BE: POST /predict_dropout (alle features)
        BE->>RF: predict() → continue risicoscore
        RF-->>BE: Score (0.0 – 1.0)
        BE-->>FE: Score als kans %
    end

    FE->>FE: Sorteer studenten hoog→laag op risico
    FE->>Gebruiker: Toon staafgrafiek top-N (default 10)

    Gebruiker->>FE: Ga naar EDUPLAN-tab, selecteer lerende
    FE->>BE: POST /feature_importance (studentdata)
    BE->>SHAP: shap_values() op RF Regressor
    SHAP-->>BE: Feature-bijdragen per kolom
    BE-->>FE: SHAP-waarden

    FE->>BE: POST /explain_risk (data + kans)
    BE->>GPT: Genereer Nederlandstalige uitleg + advies
    GPT-->>BE: EduPlan tekst
    BE-->>FE: AI-uitleg
    FE->>Gebruiker: Toon EduPlan

    Gebruiker->>FE: Download rapport
    FE->>Gebruiker: Word (.docx)
```

---

## 3. Schermstructuur

```
Startscherm
├── Zoekbalk + START-knop
├── Snelkeuze-pills (4 zichtbaar + "Meer ↓")
└── Footer (CC-licentie)

Hoofdscherm
├── Header: CEDA | UITNODIGINGSREGEL  EDUPLAN  (roze achtergrond, schaduw)
├── Witte kaart
│   ├── Kaart-header: [Opleiding]  [KLAS: ...]  [✏]
│   ├── Terracotta banner: "Toon mij X lerenden…" + slider
│   ├── Tab UITNODIGINGSREGEL → horizontale staafgrafiek
│   └── Tab EDUPLAN → student-selector + TOON EDUPLAN + EduPlan-kaart
│       └── PRINT  DOWNLOAD (.docx)
└── Footer (CC-licentie)
```
