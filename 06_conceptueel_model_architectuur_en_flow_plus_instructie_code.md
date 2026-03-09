# Conceptueel model EduPulse

## Architectuur en Workflow

### Aanleiding
Onderwijsinstellingen worstelen al jaren om meer grip op uitval te krijgen. Steeds vaker wordt hierbij gebruik gemaakt van data over de studieontwikkeling van studenten.

In haar promotieonderzoek introduceerde Irene Eegdeman een methode om studenten met een verhoogd risico op uitval vroegtijdig te signaleren. Met behulp van studiedata en machine learning-modellen is de zogenaamde ‘uitnodigingsregel’ ontwikkeld. Deze methode biedt SLB’ers en mentoren een signaleringssysteem om uitvalpreventie en -interventies effectiever in te zetten.

### Doel
Een intelligente Agent als webservice die zelfstandig taken kan uitvoeren, en vragen kan beantwoorden, op basis van MBO studentdata. In de eerste fase ligt ***de focus op enerzijds het voorspellen, en signaleren van potentieel studentuitval. Anderzijds op het ondersteunen van interventies om uitval te voorkomen.*** 

We willen als uitgangspunt gebruik maken van het werk dat heeft geleid tot **"de Uitnodigingsregel"**. Bij het Uitnodigingsregel project wordt, op basis van voorspelmodellen, gesignaleerd welke studenten een hoge kans op uitval hebben, waarna deze studenten worden uitgenodigd voor een "interventie" gesprek met een SLB-er. De interventiemethodiek is ontworpen en onderzocht door Irene Eegdeman in haar promotieonderzoek uitnodigingsregel.

### Productschets 
     
Een agentic webservice/ app die zelfstandig taken kan uitvoeren, en vragen kan beantwoorden, op basis van MBO studentdata. Hierbij richten we ons in eerste instantie op het voorspellen van uitval, het verklaren van deze voorspelling, en het genereren van mogelijke interventies, gepresenteerd in een actieplan, om uitval van een student te voorkomen.

De agentic webservice/ app wordt gebouwd in python met als front-end/ interface Streamlit, en als backend FastAPI.

**Streamlit** gebruiken we om te prototypen omdat het snel en makkelijk te leren is, en gestandaardiseerd ontwerpen/ UI bevordert. Mogelijk nadeel kan schaalbaarheid zijn, dus wordt overwogen om voor de front-end in een later stadium bijvoorbeeld React.js te gebruiken.

**FastAPI** is snel en zeer schaalbaar en willen we inzetten als API-endpoint zodat voorspellingen, transacties, en LLM calls, zoveel mogelijk daar plaatsvinden los van de Streamlit omgeving.


### Conceptueel Model voor uitvalsignalering en interventie agent

Hieronder een compleet conceptueel model van wat de Agent(s) zouden kunnen gaan doen. 

In eerste instantie echter beperken we ons op het voorspellen van uitval, het verklaren van deze voorspelling, en het genereren van mogelijke interventies, gepresenteerd in een actieplan, om uitval van een student te voorkomen.  

1. **Dataverzameling**

    - **Bronnen:**
		- In eerste instantie maken we gebruik van bestaande databestanden uit het uitnodigingsregel project. Uit de e-learning module https://rise.articulate.com/share/SXE9aSbYGhLy5FN0JdHRtSjFWPNNIAbc#/lessons/55wztXarU6mvLcXnc1nZQyfUpqsui_A6 blijkt dat de volgende variabelen nodig zijn:
			- Leeftijd en geslacht
			- Vooropleidingsdata
			- Opleidingsdata
			- Code, Niveau en Leerweg
			- Intakedata
			- Presentie/ verzuimmelding
			- Behaalde resultaten
      	Later kunnen we deze uitbreiden met data uit:
			- Kernregistratiesysteem (Eduarte, Educator, Osiris) zoals summatieve resultaten, BSA, formatieve resultaten, mentor, opleiding, ... 
			- Leeromgeving (LMS) zoals inloggegevens, interacties, en contentgebruik
			- Toets resultaten en opdrachten
			- Demografische en achtergrondinformatie van studenten
			- Feedback en enquêtes
    - **Doel:** Alle relevante data verzamelen die inzicht geeft in uitval
	
2. **Data-integratie en Preprocessing Agent**
	- Zolang we ons beperken tot de datasets uit de uitnodigingsregel laten we deze stap rusten, later kunnen we denken aan:
		- **Integratie:** Data uit diverse bronnen samenbrengen in één centrale database.
		- **Schoonmaak en Aggregatie:** Onvolledige of inconsistente data opschonen en samenvatten tot bruikbare statistieken.
		- **Normalisatie:** Zorgen dat data vergelijkbaar is, zodat trends en patronen betrouwbaar worden herkend.

3. **Analytics Engine Agent**

    - **Descriptieve Analyse:** Overzicht geven van de huidige situatie
    - **Diagnostische Analyse:** Achterhalen waarom bepaalde trends optreden (waarom een student dreigt uit te vallen bijvoorbeeld).
    - **Predictieve Analyse:** Risico’s en toekomstige prestaties voorspellen, zoals het signaleren van uitvalstudenten die mogelijk extra ondersteuning nodig hebben.
    - **Prescriptieve Analyse:** Aanbevelingen doen voor interventies, zoals gepersonaliseerde leerpaden of tijdige interventies.
	
4. **Visualisatie en Interactie Agent**

    - **Visualisatie:** Interactieve grafieken, tabellen en heatmaps die trends en patronen visueel weergeven.
    - **Real-time updates:** Mogelijkheid om actuele data te tonen zodat beslissingen op basis van de meest recente informatie worden genomen.
    - **Drill-down Functionaliteit:** Gedetailleerde data bekijken door te klikken op een overzichtsitem, zodat bijvoorbeeld een docent kan inzoomen op de prestaties van een specifieke student of groep.
    - **Alert Mechanismen:** Automatische waarschuwingen bij afwijkingen of kritieke drempels, zodat er snel ingegrepen kan worden.
	
5. **Stakeholders en Feedback Loop**

    - **Gebruikers:**

        - Docenten/Mentoren/SLB-ers (voor gerichte interventies en aanpassingen in het onderwijs)
        - Studenten (voor zelfreflectie en het bijsturen van eigen leerproces)
        - Onderwijsadministratie (voor beleidsvorming en strategische planning)
    - **Feedback Loop:** Interventies en veranderingen worden weer gemonitord, zodat het model continu geoptimaliseerd kan worden
	
		
# **🏗️ Architectuur EduPulse met Agents en AI**

## **🔹 1. Dataverzameling & Preprocessing**

**Bronnen:**
- **Bestaande data:** uit het "Uitnodigingsregel" project
- **Externe bronnen**: Mockup SIS, DUO, CBS.

**Preprocessing Stappen:**

- **Data Cleaning**: Verwijderen van dubbele of irrelevante data.
- **Normalisatie**: Data consistent maken tussen verschillende bronnen.
- **Serialisatie**: Bestaand voorspelmodel uit de Uitnodigingsregel exporteren en importeren

* * *

## **🔹 2. Opslag en Data-Integratie**

| Component | Technologie |
| --- | --- |
| **Gestructureerde data** | .xlsx en .csv bestanden, .pkl model uit de Uitnodigingsregel |
| **Ongestructureerde data** | Proefschrift, Gesprekstechnieken, Interventiemethodiek in markdown formaat |

* * *

## **🔹 3. AI & Analytics Agent**

**🔹 Analytics functionaliteiten:**

1. **📊 Uitval Analytics**

    - Welke studenten lopen risico? (early warning signals)
    - Welke variabelen spelen hierbij een rol?
    - Per student/groep meten.
	
2. **🧠 Generatieve AI toepassingen**

    - **AI-gegenereerde samenvattingen** (GPT-4/Claude)
	- **RAG gebruiken voor kennisbronnen mbt interventies**
	- **Actieplan genereren en als docx bestand als download aanbieden 
    
**🔹 Gebruikte AI-Technieken:**

- **Predictive Modeling** (Scikit-learn, TensorFlow) → Voorspellen welke studenten risico lopen.
- **Generatieve AI (GPT-4, Claude) en RAG** → Gepersonaliseerde interventie en actieplan genereren.

* * *

## **🔹 4. Interactie**

**Gebruikers:**

- **Docenten/SLB-ers** (signalering, monitoring, interventies doen)
- **Studenten** (persoonlijke inzichten)
- **Onderwijsmanagement** (overzicht van trends en curriculumoptimalisatie)

🔹 **Functionaliteiten:**  
✅ **Studentenoverzicht** (prestaties, risicoprofielen)  
✅ **Adaptieve interventie aanbevelingen** (AI zoekt automatisch relevante inhoud uit materiaal afkomstig uit uitnodigingsregel)  
✅ **Real-time waarschuwingen** (bij hoge kans uitvallers)  
✅ **Chat mogelijkheid** (vragen kunnen in natuurlijke taal gesteld worden)

**Tech Stack:** Streamlit (later misschien React.js) (frontend), FastAPI (backend).

* * *

# **🖥️ Dataflow & Architectuurdiagram**

[Data Bronnen] --> [Preprocessing & Normalisatie] 
[Preprocessing & Normalisatie] --> Analytics Engine 
Analytics Engine --> AI Predictie van Studentensucces 
Analytics Engine --> AI Generatie van Leermateriaal 
Analytics Engine --> Adaptieve Aanbevelingen 
Analytics Engine --> Analytics Dashboard
Analytics Dashboard --> Real-time Student Voortgang
Analytics Dashboard --> AI-aangedreven Chat -->  Persoonlijke Aanbevelingen 
  

### Belangrijkste features:

- **BI-gedeelte:** Klassieke datavisualisaties (tabellen, grafieken) – denk aan sectoroverzicht, opleidingsoverzicht, mentor of klas overzichten, benchmarking, etc.
- **Agent(s) en Generatieve AI-tools:** Samenvattingen, trends, vragen stellen in natuurlijke taal over de data.
- **Synergie:** Laat zien hoe je met een Agent/AI BI versterkt (bijv. door signalering van studenten met hoge kans op uitval, met mogelijke interventies voor te stellen en deze aan te bieden in een te downloaden docx document, managementsamenvattingen, en een “vraag het de data” functionaliteit).

## **Code-structuur**

### **A. FastAPI backend (`backend/main.py`):**


- `/predict_dropout` (ML-model)
- `/explain_risk` (geeft belangrijkste risicofactoren terug per student, evt. via SHAP/LIME of simpele feature importance)
- `/summarize` (voor interventie en actieplan via Claude)
-  `/ask` (Chat over de data)

### **B. Streamlit frontend (`frontend/ui.py`):**

- Upload/generatie data (uit uitnodigingsregel)
- Filters (opleiding, klas, mentor)
- Grafieken/KPI’s (aantal risicostudenten, gemiddeld cijfer, etc.)
- Risicostudenten + toelichting
- “AI Agent” (samenvatting, advies, Q&A)


### Aanpak:

- **Streamlit:** Frontend/dashboard. Snel interactief, eenvoudig in gebruik.
- **FastAPI:** Backend die je AI-taken verwerkt en eventueel data ontsluit.
- **Claude API:** Agentic, Skills en Prompt-based interactie met je data (signalering, actieplan, samenvatten, Q&A, etc.).
- **Data:** Start met een Pandas DataFrame uit de uitnodigingsregel dataset; later kunnen we altijd extra variabelen en data inladen.
- **Voorspelmodel Uitnodigingsregel:** Exporteren en importeren van bestaand voorspelmodel uit de uitnodigingsregel als .pkl. En dit model gebruiken bij voorspellen van uitval op individueel niveau

* * *

### **Stappenplan (Kickstart):**

1. **Projectstructuur:**

    - `backend/` (FastAPI)
    - `frontend/` (Streamlit)
    - `shared/` (eventueel: data en utils)

2. **Backend: FastAPI**
	
	- Endpoint `/predict_dropout` voor voorspelling van individuele student of groep studenten.
	- Endpoint `/explain_risk` (geeft belangrijkste risicofactoren terug per student, evt. via SHAP/LIME of simpele feature importance)
    - Endpoint `/summarize` voor interventie en actieplan via Claude.
    - Endpoint `/ask` voor Q&A-functionaliteit (tekstvraag → AI → antwoord).
	
3. **Frontend: Streamlit**

    - Laad data (mock of echt), visualiseer met plotly/matplotlib.
    - Agent stuurt data, verzoek voorspelling of vragen via requests naar FastAPI.
	- Maakt downloadable actieplan in docx formaat
	
4. **Claude API-integratie:**
	- Agents en Skills
    - Prompt-engineering: data samenvatten, uitval signaleren, uitval uitleggen, etc.
	
### Projectstructuur

```
edupulse/
│
├── backend/
│   ├── main.py          # FastAPI backend: AI- & ML-endpoints
│   ├── model.pkl        # Getraind ML-model afkomstig uit de uitnodigingsregel
│   └── data_utils.py    # Data & ML hulpfuncties
│
├── frontend/
│   └── ui.py     # Streamlit User Interface
│
├── shared/
│   └── data.csv         # Data afkomstig uit de uitnodigingsregel (evt. automatisch gegenereerde extra variabelen)
│
|-- skills/
│   └── skills.py  		 # Domeinspecifieke kennis, processen en tools die de agent kan gebruiken 
|
├── requirements.txt
```

---

### Aanpak productiesetup

1. **Serialiseren (exporteren)**

    - Gebruik `joblib.dump(...)` om je getrainde model (`RandomForrestClassifier`), je `StandardScaler` en de lijst met dummy-kolomnamen op te slaan in `../../models`.
2. **Preprocess‐artefacten**

    - Bewaar de exacte lijst van dummy-kolommen (`dummy_columns.json`) en de geschaalde statistieken (`scaler.pkl`) zodat je in productie identiek dezelfde preprocessing kunt toepassen.
3. **Service‐laag**

    - Een micro-framework (FastAPI) om eenvoudig HTTP-endpoints zoals: `/predict_dropouts`, `/explain_risk`, `/summarize`, `ask` beschikbaar te stellen.
    - In de request handler:

        - Valideer inkomende JSON via Pydantic (in FastAPI).
        - Bouw een DataFrame, pas categorische → dummies → aanvullen ontbrekende kolommen → schalen toe.
        - Roep `model.predict_proba(...)` en `model.predict(...)` aan.
        - Geef resultaten terug in JSON.
4. **Deployment**

    - Je kunt de service draaien op een virtuele machine (VPS), of nog beter in een Docker-container (voor consistente omgeving).
    - Zet een reverse proxy (bv. Nginx) voor SSL‐terminatie en load balancing.
    - Monitor CPU/RAM, logs en API‐latency.
	
5. **Client-gebruik**

    - De klant kan via een HTTP‐client (`requests` in Python, `curl`, of een front‐end) JSON naar jouw endpoint sturen en ontvangt in de response meteen de kans op uitval en het geclassificeerde label.

Met deze aanpak heb je een duurzame productiesetup:

- Een duidelijk geserialiseerd model (+ preprocess-artefacten).
- Een eenvoudige, schaalbare API die klanten kunnen aanroepen.
- De mogelijkheid om later te upgraden (bijvoorbeeld andere voorspelmodellen, extra endpoint voor batch‐voorspellingen, authenticatie, etc.).

Mocht de server in de toekomst overbelast raken, dan kun je altijd horizontaal schalen (meerdere replica’s) of een cloud-managed oplossing bekijken (AWS SageMaker Endpoint, Azure ML, GCP AI Platform, etc.). 

## Voorbeeld scripts in python

#### REQUIREMENTS.TXT (voor de hele stack)

```requirements.txt
streamlit 
pandas 
scikit-learn 
fastapi 
uvicorn 
openai 
requests 
plotly 
shap
```

#### Voorbeeld mockup data generatie script in python 
Eventueel te gebruiken als we extra variabelen + data willen introduceren

```python
# data_prep.py (éénmalig draaien)
import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
import pickle

def generate_student_data(n=200):
    opleidingen = ["ICT", "Zorg", "Techniek", "Economie", "Handel"]
    klassen = ["A1", "B2", "C3", "D2"]
    mentoren = ["mev. Smit", "dhr. Mulder", "mev. Kuiper", "dhr. De Groot"]
    data = []
    for i in range(1001, 1001+n):
        cijfer = np.round(np.random.normal(6.5, 1.0), 1)
        aanwezigheid = np.round(np.random.uniform(70, 100), 1)
        waarschuwingen = np.random.poisson(1)
        ec = np.random.randint(20, 61)
        opleiding = random.choice(opleidingen)
        klas = random.choice(klassen)
        mentor = random.choice(mentoren)
        naam = random.choice(["Julia", "Sam", "Lisa", "Mohamed", "Eva", "Tessa", "Daan", "Hannah", "Lucas", "Fatima"]) + " " + random.choice(["de Vries", "Jansen", "Bakker", "Ali", "Groen", "Smit", "Kuiper", "Mulder", "De Groot"])
        risk_score = (7-cijfer)*0.4 + (85-aanwezigheid)*0.07 + waarschuwingen*0.6 + (30-ec)*0.05
        uitgevallen = np.random.rand() < min(max(risk_score/5, 0), 1)
        data.append({
            "Student-ID": i,
            "Naam": naam,
            "Opleiding": opleiding,
            "Klas": klas,
            "Cijfer": cijfer,
            "Aanwezigheid": aanwezigheid,
            "EC": ec,
            "Waarschuwingen": waarschuwingen,
            "Mentor": mentor,
            "Uitgevallen": int(uitgevallen),
            "Schooljaar": "2024-2025"
        })
    return pd.DataFrame(data)

df = generate_student_data(200)
df.to_csv("shared/data.csv", index=False)

features = ["Cijfer", "Aanwezigheid", "Waarschuwingen", "EC"]
X = df[features]
y = df["Uitgevallen"]
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)
with open("backend/model.pkl", "wb") as f:
    pickle.dump(clf, f)
```	

---

#### FASTAPI BACKEND (`backend/main.py`)

```python
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import openai
import pickle
import os
import shap

openai.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

# Laden van ML-model
with open("model.pkl", "rb") as f:
    clf = pickle.load(f)
	
	
features = ["Cijfer", "Aanwezigheid", "Waarschuwingen", "EC"]
explainer = shap.TreeExplainer(clf)

class StudentData(BaseModel):
    student: dict

class SummaryRequest(BaseModel):
    data: str

class ExplainRequest(BaseModel):
    student: dict
    prediction: int
    probability: float

@app.post("/summarize")
def summarize(request: SummaryRequest):
    prompt = f"Vat deze BI-data samen voor het management (max 5 regels):\n{request.data}\nSamenvatting:"
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    summary = response.choices[0].message["content"]
    return {"summary": summary}

@app.post("/predict_dropout")
def predict_dropout(request: StudentData):
    X_pred = pd.DataFrame([request.student])[features]
    prob = float(clf.predict_proba(X_pred)[0][1])
    label = int(prob > 0.35)
    return {"probability": prob, "prediction": label}

@app.post("/explain_risk")
def explain_risk(request: ExplainRequest):
    student = request.student
    prediction = request.prediction
    probability = request.probability
    feature_str = ", ".join([f"{k}: {v}" for k,v in student.items()])
    prompt = (
        f"Studentgegevens: {feature_str}.\n"
        f"Voorspelde kans op uitval: {probability:.2%}.\n"
        f"Licht in heldere managementtaal toe waarom deze student risico loopt op uitval, en geef gericht advies aan de mentor."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    uitleg = response.choices[0].message["content"]
    return {"explanation": uitleg}

@app.post("/feature_importance")
def feature_importance(request: StudentData):
    X_pred = pd.DataFrame([request.student])[features]
    shap_vals = explainer.shap_values(X_pred)[1]
    fi = dict(zip(features, shap_vals[0].tolist()))
    return {"feature_importance": fi}
	
```
Run FastAPI:

uvicorn backend.main:app --reload

---

### STREAMLIT FRONTEND (`frontend/ui.py`)

```python
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(layout="wide")
df = pd.read_csv("../shared/data.csv")
features = ["Cijfer", "Aanwezigheid", "Waarschuwingen", "EC"]

st.title("Edupulse - Signalering en interventie bij mogelijk studentuitval")


with st.sidebar:
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

col1, col2, col3 = st.columns(3)
col1.metric("Gemiddeld Cijfer", f"{dff['Cijfer'].mean():.2f}")
col2.metric("Gem. Aanwezigheid", f"{dff['Aanwezigheid'].mean():.1f}%")
col3.metric("Waarschuwingen (gem.)", f"{dff['Waarschuwingen'].mean():.2f}")

st.subheader("Studentenoverzicht")
st.dataframe(dff.head(30))

st.subheader("Trendgrafieken & spreiding")
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

st.subheader("AI Q&A: Stel een vraag over deze data")
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

st.subheader("Risico op uitval voorspellen")
risicostudenten = []
for idx, row in dff.iterrows():
    student_dict = row[features].to_dict()
    pred_response = requests.post("http://localhost:8000/predict_dropout", json={"student": student_dict})
    result = pred_response.json()
    if result["prediction"] == 1:
        risicostudenten.append((row, result))

if risicostudenten:
    st.markdown(f"### Studenten met verhoogd risico ({len(risicostudenten)})")
    for row, result in risicostudenten:
        st.write(f"**{row['Naam']}** ({row['Opleiding']} / {row['Klas']}): Kans op uitval: {result['probability']:.1%}")
        exp_response = requests.post(
            "http://localhost:8000/explain_risk",
            json={
                "student": row[features].to_dict(),
                "prediction": result["prediction"],
                "probability": result["probability"]
            })
        st.info(exp_response.json()["explanation"])
        fi_resp = requests.post(
            "http://localhost:8000/feature_importance",
            json={"student": row[features].to_dict()}
        )
        fi = fi_resp.json()["feature_importance"]
        fi_str = ", ".join([f"{k}: {v:.2f}" for k,v in fi.items()])
        st.caption(f"Belangrijkste risicofactoren (SHAP): {fi_str}")
else:
    st.success("Geen risicostudenten in deze selectie!")
	
```


---

#### Installeren en draaien


Maak de mappenstructuur aan, kopieer de scripts en voeg de OpenAI (of Claude) API-key als environment variable toe (**OPENAI\_API\_KEY**, of **CLAUDE\_API\_KEY**).

Installeer alles:
uv add -U -r requirements.txt

Voer éénmalig uit:
python data_prep.py

Start backend:
uvicorn backend.main:app --reload

Start frontend:
streamlit run frontend/ui.py

