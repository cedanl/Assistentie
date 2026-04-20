# backend/seed.py
"""Vul de SQLite database met synthetische studenten."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from backend.database import engine, Base, SessionLocal
from backend.models import StudentDB
from backend.ml.generate_data import genereer_actieve_studenten

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(StudentDB).count() == 0:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        csv = os.path.join(data_dir, "actieve_studenten.csv")
        if not os.path.exists(csv):
            print("CSV niet gevonden, genereer data...")
            df = genereer_actieve_studenten(1000)
            df.to_csv(csv, index=False)
        else:
            df = pd.read_csv(csv)

        df["intakedatum"] = pd.to_datetime(df["intakedatum"]).dt.date
        records = df.to_dict("records")
        db.bulk_insert_mappings(StudentDB, records)
        db.commit()
        print(f"{len(records)} actieve studenten ingevoegd.")
    else:
        print("Database al gevuld — overgeslagen.")

    db.close()

if __name__ == "__main__":
    seed()
