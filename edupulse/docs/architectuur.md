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
        OPENAI["OpenAI GPT-4.1"]
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
    participant GPT as OpenAI GPT-4.1

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

    FE->>BE: POST /explain_risk (data + kans + imputed_columns)
    note over BE: Sectie 1: deterministisch HTML<br>vanuit echte studentdata (geen LLM)
    BE->>SHAP: shap_values() — geïmputeerde kolommen uitgesloten
    SHAP-->>BE: Top-5 risicofactoren
    alt Voldoende data (max SHAP ≥ 0.01)
        BE->>GPT: Secties 2–4: alleen risiconiveau + SHAP-factoren
        GPT-->>BE: Begeleidingstekst (geen studentprofiel)
    else Onvoldoende data (max SHAP < 0.01)
        BE-->>FE: Waarschuwing — geen advies mogelijk
    end
    BE-->>FE: Sectie 1 (HTML) + secties 2–4 (LLM)
    FE->>Gebruiker: Toon EduPlan

    Gebruiker->>FE: Download rapport
    FE->>Gebruiker: Word (.docx)
```

---

## 3. Schermstructuur

```
Startscherm  (roze achtergrond #f0d4d4)
├── Upload-veld (.csv / .xlsx) — auto-detectie scheidingsteken
├── Demo-data checkbox
├── START DE UITNODIGINGSREGEL knop
├── Snelkeuze-pills (4 zichtbaar + "Meer ↓")
└── Footer — compact, roze, sticky onderaan

Hoofdscherm  (roze achtergrond #f0d4d4)
├── Header (lichtroze #fae8e8, sticky, schaduw)
│   ├── CEDA  (logo links)
│   └── [← TERUG]  [UITNODIGINGSREGEL*]  [EDUPLAN]  (knoppen rechts)
│       * actieve tab heeft witte achtergrond + zwarte rand
├── Witte kaart
│   ├── Kaart-header: [Opleiding]  [KLAS: ...]  [✏]
│   ├── Terracotta banner: "Toon mij X lerenden…" + slider (default 10)
│   ├── Tab UITNODIGINGSREGEL → horizontale staafgrafiek (hoog→laag)
│   └── Tab EDUPLAN → student-selector + TOON EDUPLAN + EduPlan-kaart
│       ├── Sectie 1: deterministisch risicoprofiel (HTML, geen LLM)
│       │   └── Ontbrekende kolommen getoond als "niet beschikbaar"
│       ├── Secties 2–4: AI-begeleidingstekst (GPT-4.1)
│       └── PRINT  DOWNLOAD (.docx)
└── Footer — compact, lichtroze (#fae8e8), sticky onderaan
    © 2026 CEDA — CC BY-SA 4.0
```
