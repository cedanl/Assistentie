"""backend/trainer.py

Trainingslogica voor het instellingsspecifieke Random Forest-model.
Gebruikt student-signal voor data-voorbereiding (KNN-imputation, encoding)
en modeltraining (GridSearchCV).
"""

import json
from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestRegressor
from student_signal import prepare
from student_signal.modeling.train import train_random_forest

_cfg = yaml.safe_load((Path(__file__).parent.parent / "config.yaml").read_text())


def train_model(
    df: pd.DataFrame,
    dropout_col: str,
    model_path: str | Path,
    features_path: str,
    imputer_path: str | None = None,
    scaler_path: str | None = None,
    param_grid: dict | None = None,
    random_seed: int = 42,
) -> tuple[RandomForestRegressor, list[str]]:
    """Train een RandomForestRegressor via student-signal en sla op.

    Gebruikt KNN-imputation via student-signal's prepare() in plaats van
    rijen met ontbrekende waarden te verwijderen. De feature-lijst die na
    prepare() overblijft wordt naast het model opgeslagen als JSON.

    Args:
        df:            DataFrame met features én doelkolom.
        dropout_col:   Naam van de uitval-doelkolom (bijv. "Dropout").
        model_path:    Pad voor het getrainde model (.joblib).
        features_path: Pad voor de bijbehorende feature-lijst (.json).
        imputer_path:  Pad voor de fitted KNNImputer (.joblib). Indien None: niet opgeslagen.
        scaler_path:   Pad voor de fitted MinMaxScaler (.joblib). Indien None: niet opgeslagen.
        param_grid:    GridSearchCV-raster; gebruikt student-signal standaard indien None.
        random_seed:   Random state voor reproduceerbaarheid.

    Returns:
        Tuple van (getraind model, feature-lijst).

    Raises:
        ValueError: Als er te weinig trainingsrijen zijn.
    """
    min_rows = _cfg["model"]["min_training_rows"]
    if len(df) < min_rows:
        raise ValueError(
            f"Te weinig trainingsdata: {len(df)} rijen "
            f"(minimum: {min_rows}). Controleer of de kolom '{dropout_col}' voldoende gevulde waarden heeft."
        )

    # Zorg voor een id-kolom (vereist door student-signal's prepare)
    id_col = _cfg["data"]["id_column"] if _cfg["data"]["id_column"] in df.columns else "__id__"
    if id_col == "__id__":
        df = df.copy()
        df["__id__"] = range(len(df))

    # student-signal: KNN-imputation, encoding, scaling — alles gefitst op traindata
    prepared = prepare(df, df, target_col=dropout_col, id_col=id_col)

    rf_params = param_grid or _cfg["training"]["rf_parameters"]

    model = train_random_forest(prepared.train_df, random_seed, dropout_col, rf_params)

    feature_cols = list(prepared.X_train.columns)

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    with open(features_path, "w") as f:
        json.dump(feature_cols, f)
    if imputer_path:
        joblib.dump(prepared.imputer, imputer_path)
    if scaler_path:
        joblib.dump(prepared.scaler, scaler_path)

    return model, feature_cols
