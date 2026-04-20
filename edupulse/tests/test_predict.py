import pytest
from backend.ml.train import train_model
from backend.ml.predict import RisicoPredictor

@pytest.fixture(scope="module")
def getraind_model(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("model")
    model_path = str(tmp / "model.pkl")
    feature_path = str(tmp / "features.json")
    from backend.ml.generate_data import genereer_historische_studenten
    df = genereer_historische_studenten(n=500)
    metrics = train_model(df, model_path=model_path, feature_path=feature_path)
    return model_path, feature_path, metrics

def test_model_accuracy_boven_drempel(getraind_model):
    _, _, metrics = getraind_model
    assert metrics["accuracy"] >= 0.60, f"Accuracy {metrics['accuracy']:.2f} te laag"

def test_voorspelling_retourneert_kans(getraind_model):
    model_path, feature_path, _ = getraind_model
    predictor = RisicoPredictor(model_path=model_path, feature_path=feature_path)
    student = {
        "aanwezigheid": 0.45, "voortgang": 0.40, "bsa_studiepunten": 20,
        "cijfer_nederlands": 5.0, "cijfer_rekenen": 4.5,
        "leeftijd": 19, "niveau": 3, "leerweg": "BOL",
        "sector": "Techniek", "vooropleiding": "VMBO-T"
    }
    result = predictor.predict(student)
    assert 0.0 <= result["kans"] <= 1.0
    assert len(result["shap_top3"]) == 3

def test_hoge_aanwezigheid_geeft_lager_risico(getraind_model):
    model_path, feature_path, _ = getraind_model
    predictor = RisicoPredictor(model_path=model_path, feature_path=feature_path)
    basis = {"aanwezigheid": 0.95, "voortgang": 0.90, "bsa_studiepunten": 55,
             "cijfer_nederlands": 8.0, "cijfer_rekenen": 7.5,
             "leeftijd": 19, "niveau": 4, "leerweg": "BOL",
             "sector": "Economie", "vooropleiding": "HAVO"}
    laag_risico = {"aanwezigheid": 0.30, "voortgang": 0.25, "bsa_studiepunten": 10,
                   "cijfer_nederlands": 4.5, "cijfer_rekenen": 4.0,
                   "leeftijd": 19, "niveau": 4, "leerweg": "BOL",
                   "sector": "Economie", "vooropleiding": "HAVO"}
    assert predictor.predict(basis)["kans"] < predictor.predict(laag_risico)["kans"]
