"""data_prep.py

Voorbeeld mockup data generatie script in python 
Eventueel te gebruiken als we extra variabelen + data willen introduceren

"""

import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
import pickle

def generate_student_data(n=200):
    opleidingen = ["ICT", "Zorg", "Techniek", "Economie", "Handel"]
    klassen = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]
    mentoren = ["mev. Smit", "mev. Safon", "mev. Hulsema", "dhr. Hanna", "dhr. Benjamins", "dhr. Mulder", "mev. Kuiper", "dhr. De Groot"]
    data = []
    for i in range(1001, 1001+n):
        cijfer = np.round(np.random.normal(6.5, 1.0), 1)
        aanwezigheid = np.round(np.random.uniform(70, 100), 1)
        waarschuwingen = np.random.poisson(1)
        ec = np.random.randint(20, 61)
        opleiding = random.choice(opleidingen)
        klas = random.choice(klassen)
        mentor = random.choice(mentoren)
        naam = random.choice(["Julia", "Aisha", "Edith","Edwin", "Steven", "Sam", "Lisa", "Mohammed", "Ali", "Koen", "Eva", "Tessa", "Daan", "Ameen", "Lucas", "Fatima"]) + " " + random.choice(["de Vries", "Boussata", "Abu-Hanna", "Benjamins", "Mulder", "Sanchez", "Jansen", "Bakker", "Bousme", "Sterk", "Noordenbos", "Rijkaard", "van Someren", "Groen", "Smit", "Kuiper", "Mulder", "De Groot"])
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
            "Schooljaar": "2025-2026"
        })
    return pd.DataFrame(data)

df = generate_student_data(500)
df.to_csv("../shared/data.csv", index=False)

features = ["Cijfer", "Aanwezigheid", "Waarschuwingen", "EC"]
X = df[features]
y = df["Uitgevallen"]
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)
with open("../backend/model.pkl", "wb") as f:
    pickle.dump(clf, f)
