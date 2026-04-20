"""data_prep.py

Download synthetische data en Random Forest model van Uitnodigingsregel
(https://github.com/cedanl/Uitnodigingsregel).

Uitvoeren vanuit de projectroot:
    python shared/data_prep.py
"""

import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

_cfg = yaml.safe_load((Path(__file__).parent.parent / "config.yaml").read_text())

rng = np.random.default_rng(42)

PRED_URL = _cfg["downloads"]["data_url"]
MODEL_URL = _cfg["downloads"]["model_url"]

print("Bezig met downloaden van data en model...")
urllib.request.urlretrieve(PRED_URL, _cfg["downloads"]["raw_data_path"])
urllib.request.urlretrieve(MODEL_URL, _cfg["model"]["default_path"])
print("Download klaar.")

df = pd.read_csv(_cfg["downloads"]["raw_data_path"], sep="\t")
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


sector_cols = [c for c in sector_map if c in df.columns]
df["Opleiding"] = (
    df[sector_cols].idxmax(axis=1).map(sector_map).where(df[sector_cols].eq(1).any(axis=1), other="Overig")
)

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
df["Naam"] = [f"{v} {a}" for v, a in zip(rng.choice(voornamen, size=n), rng.choice(achternamen, size=n))]
df["Klas"] = rng.choice(klassen, size=n)
df["Mentor"] = rng.choice(mentoren, size=n)

df.to_csv(_cfg["data"]["path"], index=False)
print(f"\nshared/data.csv opgeslagen ({n} studenten).")
print("backend/model.joblib gedownload.")
print(f"\nKolommen in data.csv: {list(df.columns)}")
