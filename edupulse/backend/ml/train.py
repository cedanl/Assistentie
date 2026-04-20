# backend/ml/train.py
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

CATEGORISCHE_FEATURES = ["leerweg", "sector", "vooropleiding"]
NUMERIEKE_FEATURES = [
    "aanwezigheid", "voortgang", "bsa_studiepunten",
    "cijfer_nederlands", "cijfer_rekenen", "leeftijd", "niveau"
]
ALLE_FEATURES = NUMERIEKE_FEATURES + CATEGORISCHE_FEATURES

def _encode(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = df.copy()
    encoders = {}
    for col in CATEGORISCHE_FEATURES:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    return df, encoders

def train_model(
    df: pd.DataFrame,
    model_path: str = "data/model.pkl",
    feature_path: str = "data/feature_list.json"
) -> dict:
    df_enc, encoders = _encode(df)
    X = df_enc[ALLE_FEATURES].fillna(df_enc[ALLE_FEATURES].median(numeric_only=True))
    y = df_enc["uitgevallen"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rf = GridSearchCV(
        RandomForestClassifier(random_state=42),
        {"n_estimators": [100, 200], "max_depth": [5, 10]},
        cv=3, scoring="accuracy", n_jobs=-1
    )
    xgb = GridSearchCV(
        XGBClassifier(random_state=42, eval_metric="logloss", verbosity=0),
        {"n_estimators": [100, 200], "max_depth": [3, 5], "learning_rate": [0.1, 0.05]},
        cv=3, scoring="accuracy", n_jobs=-1
    )

    rf.fit(X_train, y_train)
    xgb.fit(X_train, y_train)

    rf_acc = accuracy_score(y_test, rf.predict(X_test))
    xgb_acc = accuracy_score(y_test, xgb.predict(X_test))

    best_model = xgb.best_estimator_ if xgb_acc >= rf_acc else rf.best_estimator_
    best_acc = max(xgb_acc, rf_acc)
    model_naam = "XGBoost" if xgb_acc >= rf_acc else "RandomForest"

    joblib.dump({"model": best_model, "encoders": encoders}, model_path)
    with open(feature_path, "w") as f:
        json.dump({"features": ALLE_FEATURES, "categorisch": CATEGORISCHE_FEATURES}, f)

    print(f"Beste model: {model_naam} | Accuracy: {best_acc:.3f}")
    return {"accuracy": best_acc, "model_naam": model_naam}

if __name__ == "__main__":
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    df = pd.read_csv(f"{data_dir}/historische_studenten.csv")
    df["intakedatum"] = pd.to_datetime(df["intakedatum"])
    train_model(df, model_path=f"{data_dir}/model.pkl", feature_path=f"{data_dir}/feature_list.json")
