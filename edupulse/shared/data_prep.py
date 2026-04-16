"""data_prep.py

Download synthetische data en Random Forest model van Uitnodigingsregel
(https://github.com/cedanl/Uitnodigingsregel).

Uitvoeren vanuit de projectroot:
    python shared/data_prep.py
"""

import random
import urllib.request

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

PRED_URL = "https://raw.githubusercontent.com/cedanl/Uitnodigingsregel/main/data/raw/synth_data_pred.csv"
MODEL_URL = "https://raw.githubusercontent.com/MondriaanBI/Uitnodigingsregel/main/models/random_forest_regressor.joblib"

print("Bezig met downloaden van data en model...")
urllib.request.urlretrieve(PRED_URL, "shared/synth_data_pred.csv")
urllib.request.urlretrieve(MODEL_URL, "backend/model.joblib")
print("Download klaar.")

df = pd.read_csv("shared/synth_data_pred.csv", sep="\t")
print(f"Kolommen ({len(df.columns)}): {list(df.columns)}")
print(f"Rijen: {len(df)}")

# Leid Opleiding af uit de sector-kolommen (één-hete codering)
sector_map = {
    "Economie": "Economie",
    "Landbouw": "Landbouw",
    "Techniek": "Techniek",
    "DSV": "DSV",
    "Zorgenwelzijn": "Zorg & Welzijn",
    "Anders": "Anders",
}


def get_opleiding(row):
    for col, label in sector_map.items():
        if col in row.index and row[col] == 1:
            return label
    return "Overig"


df["Opleiding"] = df.apply(get_opleiding, axis=1)

# Voeg synthetische weergave-kolommen toe (Naam, Klas, Mentor)
voornamen = [
    "Julia",
    "Arantxa",
    "Maddox",
    "Nova",
    "Shane",
    "Richard",
    "Paolo",
    "Aisha",
    "Edith",
    "Edwin",
    "Steven",
    "Sam",
    "Lisa",
    "Mohammed",
    "Ali",
    "Koen",
    "Eva",
    "Tessa",
    "Daan",
    "Ameen",
    "Lucas",
    "Fatima",
    "Nour",
    "Mehmet",
    "Emma",
    "Lars",
]
achternamen = [
    "de Vries",
    "Boussata",
    "Abu-Hanna",
    "Benjamins",
    "Bos",
    "Jansen",
    "Pietersen",
    "Massaro",
    "Luyendijk",
    "van Vleuten",
    "de Vries",
    "Hol",
    "Mulder",
    "Sanchez",
    "Jansen",
    "Bakker",
    "Sterk",
    "Noordenbos",
    "Groen",
    "Smit",
    "Kuiper",
    "De Groot",
]
klassen = ["1A", "1B", "2A", "2B", "3A", "3B"]
mentoren = [
    "mev. Smit",
    "mev. Safon",
    "mev. Hulsema",
    "dhr. Hanna",
    "dhr. Benjamins",
    "dhr. Mulder",
    "mev. Kuiper",
    "dhr. De Groot",
]

n = len(df)
df["Naam"] = [f"{random.choice(voornamen)} {random.choice(achternamen)}" for _ in range(n)]
df["Klas"] = [random.choice(klassen) for _ in range(n)]
df["Mentor"] = [random.choice(mentoren) for _ in range(n)]

df.to_csv("shared/data.csv", index=False)
print(f"\nshared/data.csv opgeslagen ({n} studenten).")
print("backend/model.joblib gedownload.")
print(f"\nKolommen in data.csv: {list(df.columns)}")
