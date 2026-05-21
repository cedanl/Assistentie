import numpy as np
import pandas as pd
from faker import Faker
from datetime import date

fake = Faker("nl_NL")
rng = np.random.default_rng(42)

SECTOREN = {
    "Techniek": [
        ("Software Developer", "25604", 4),
        ("Netwerkbeheerder", "93200", 4),
        ("Elektrotechniek", "25160", 3),
        ("Installatiemonteur", "25480", 2),
    ],
    "Zorg": [
        ("Verpleegkundige", "99070", 4),
        ("Verzorgende IG", "93500", 3),
        ("Helpende Zorg & Welzijn", "92640", 2),
        ("Doktersassistent", "34576", 4),
    ],
    "Economie": [
        ("Commercieel medewerker", "90111", 3),
        ("Financieel administrateur", "90370", 4),
        ("Logistiek medewerker", "90640", 3),
        ("Manager handel", "90202", 4),
    ],
    "Dienstverlening": [
        ("Kok", "25185", 2),
        ("Gastvrouw/-heer", "90191", 3),
        ("Kapper", "97460", 3),
    ],
    "Groen": [
        ("Dierverzorger", "97730", 3),
        ("Medewerker voedsel", "97590", 2),
        ("Tuin- en landschapsbeheer", "97252", 3),
    ],
}

VOOROPLEIDINGEN = ["VMBO-T", "VMBO-K", "VMBO-B", "HAVO", "MBO niveau 2", "MBO niveau 3"]
COHORTEN = ["2022-2023", "2023-2024", "2024-2025"]
LEERWEGEN = ["BOL", "BBL"]
GESLACHTEN = ["M", "V", "X"]
MENTOREN = [
    ("Jan de Vries", "j.devries@roc.nl"),
    ("Fatima El Amrani", "f.elamrani@roc.nl"),
    ("Peter Smit", "p.smit@roc.nl"),
    ("Anita Jansen", "a.jansen@roc.nl"),
    ("Mohammed Boukhari", "m.boukhari@roc.nl"),
]


def _genereer_student(idx: int, cohort: str) -> dict:
    sector = rng.choice(list(SECTOREN.keys()))
    opleiding, crebo, niveau = SECTOREN[sector][rng.integers(len(SECTOREN[sector]))]
    leerweg = rng.choice(LEERWEGEN, p=[0.75, 0.25])
    leeftijd = int(np.clip(rng.normal(20, 3), 16, 35))
    vooropleiding = rng.choice(VOOROPLEIDINGEN)
    geslacht = rng.choice(GESLACHTEN, p=[0.48, 0.48, 0.04])
    mentor = MENTOREN[rng.integers(len(MENTOREN))]

    if geslacht == "M":
        naam = fake.name_male()
    elif geslacht == "V":
        naam = fake.name_female()
    else:
        naam = fake.name()

    # Basis aanwezigheid: beta-distributie
    aanwezigheid = float(np.clip(rng.beta(5, 2), 0.0, 1.0))
    # Voortgang correlated met aanwezigheid
    voortgang = float(np.clip(aanwezigheid * 0.6 + rng.beta(4, 2) * 0.4, 0.0, 1.0))
    # BSA-punten: max 60, correlated met voortgang
    bsa_studiepunten = int(np.clip(voortgang * 45 + rng.normal(8, 5), 0, 60))
    # Cijfers: normaal verdeeld, licht gecorreleerd met voortgang
    cijfer_nl = float(np.clip(rng.normal(6.3, 1.2) + voortgang * 0.5, 1.0, 10.0))
    cijfer_re = float(np.clip(rng.normal(6.0, 1.4) + voortgang * 0.4, 1.0, 10.0))

    jaar = int(cohort[:4])
    intakedatum = date(jaar, 9, 1)

    fn, ln = naam.split(" ", 1) if " " in naam else (naam, "")
    email = f"{fn[0].lower()}.{ln.lower().replace(' ', '')}@student.roc.nl"

    return {
        "studentnummer": f"{jaar}{idx:04d}",
        "naam": naam,
        "email": email,
        "leeftijd": leeftijd,
        "geslacht": geslacht,
        "vooropleiding": vooropleiding,
        "sector": sector,
        "opleiding": opleiding,
        "crebocode": crebo,
        "cohort": cohort,
        "niveau": int(niveau),
        "leerweg": str(leerweg),
        "intakedatum": intakedatum,
        "aanwezigheid": round(aanwezigheid, 3),
        "voortgang": round(voortgang, 3),
        "bsa_studiepunten": bsa_studiepunten,
        "cijfer_nederlands": round(cijfer_nl, 1),
        "cijfer_rekenen": round(cijfer_re, 1),
        "mentor_naam": mentor[0],
        "mentor_email": mentor[1],
    }


def genereer_actieve_studenten(n: int = 1000) -> pd.DataFrame:
    cohort = "2024-2025"
    rows = [_genereer_student(i + 1, cohort) for i in range(n)]
    return pd.DataFrame(rows)


def genereer_historische_studenten(n: int = 10000) -> pd.DataFrame:
    rows = []
    for i in range(n):
        cohort = rng.choice(COHORTEN[:2])  # alleen afgesloten cohorten
        student = _genereer_student(i + 1, cohort)
        # Uitval kans: hoog als aanwezigheid + cijfers laag zijn
        # Formule: combinatie van negatieve factoren resulteert in uitvalrisico
        attendance_factor = (1 - student["aanwezigheid"]) * 0.20
        progress_factor = (1 - student["voortgang"]) * 0.15
        grade_factor = (
            max(0, (6.0 - student["cijfer_rekenen"]) / 10.0) * 0.08
            + max(0, (6.0 - student["cijfer_nederlands"]) / 10.0) * 0.08
        )
        # Basiskans + factoren + ruis
        uitval_kans = (
            0.08 + attendance_factor + progress_factor + grade_factor + rng.normal(0, 0.03)
        )
        uitval_kans = float(np.clip(uitval_kans, 0.0, 1.0))
        student["uitgevallen"] = bool(rng.random() < uitval_kans)
        rows.append(student)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import os

    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    print("Genereer 1.000 actieve studenten...")
    actief = genereer_actieve_studenten(1000)
    actief.to_csv(f"{data_dir}/actieve_studenten.csv", index=False)

    print("Genereer 10.000 historische studenten...")
    hist = genereer_historische_studenten(10000)
    hist.to_csv(f"{data_dir}/historische_studenten.csv", index=False)

    print(f"Klaar. Uitvalpercentage historisch: {hist['uitgevallen'].mean():.1%}")
