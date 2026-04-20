# backend/ml/predict.py
import json
import joblib
import numpy as np
import pandas as pd
import shap

DREMPEL = 0.35  # >= 35% kans = dreiging

class RisicoPredictor:
    def __init__(
        self,
        model_path: str = "data/model.pkl",
        feature_path: str = "data/feature_list.json"
    ):
        artefact = joblib.load(model_path)
        self.model = artefact["model"]
        self.encoders = artefact["encoders"]
        with open(feature_path) as f:
            meta = json.load(f)
        self.features = meta["features"]
        self.categorisch = meta["categorisch"]
        self.explainer = shap.TreeExplainer(self.model)

    def _prep(self, student: dict) -> pd.DataFrame:
        row = {f: student.get(f) for f in self.features}
        df = pd.DataFrame([row])
        for col in self.categorisch:
            le = self.encoders[col]
            val = str(df[col].iloc[0])
            if val in le.classes_:
                df[col] = le.transform([val])
            else:
                df[col] = 0
        return df.fillna(0)

    def predict(self, student: dict) -> dict:
        df = self._prep(student)
        kans = float(self.model.predict_proba(df)[0][1])

        shap_values = self.explainer.shap_values(df)
        if isinstance(shap_values, list):
            # Oude SHAP API: lijst van arrays per klasse
            sv = shap_values[1][0]
        elif shap_values.ndim == 3:
            # Nieuwe SHAP API voor RandomForest: (samples, features, classes)
            sv = shap_values[0, :, 1]
        else:
            # XGBoost: (samples, features)
            sv = shap_values[0]

        top_idx = np.argsort(np.abs(sv))[::-1][:3].tolist()
        shap_top3 = [
            {"feature": self.features[i], "bijdrage": round(float(sv[i]), 4)}
            for i in top_idx
        ]

        return {"kans": round(kans, 4), "shap_top3": shap_top3}
