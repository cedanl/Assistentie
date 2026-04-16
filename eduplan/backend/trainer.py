"""backend/trainer.py

Trainingslogica voor het instellingsspecifieke Random Forest-model.
Gebruikt student-signal voor data-voorbereiding (KNN-imputation, encoding)
en modeltraining (GridSearchCV).
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from student_signal import prepare
from student_signal.modeling.train import train_random_forest


def train_model(
    df: pd.DataFrame,
    dropout_col: str,
    model_path: str | Path,
    features_path: str,
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
        param_grid:    GridSearchCV-raster; gebruikt student-signal standaard indien None.
        random_seed:   Random state voor reproduceerbaarheid.

    Returns:
        Tuple van (getraind model, feature-lijst).

    Raises:
        ValueError: Als er te weinig trainingsrijen zijn.
    """
    if len(df) < 30:
        raise ValueError(
            f"Te weinig trainingsdata: {len(df)} rijen "
            f"(minimum: 30). Controleer of de kolom '{dropout_col}' voldoende gevulde waarden heeft."
        )

    # Zorg voor een id-kolom (vereist door student-signal's prepare)
    id_col = "Studentnummer" if "Studentnummer" in df.columns else "__id__"
    if id_col == "__id__":
        df = df.copy()
        df["__id__"] = range(len(df))

    # student-signal: KNN-imputation, encoding, scaling — alles gefitst op traindata
    prepared = prepare(df, df, target_col=dropout_col, id_col=id_col)

    rf_params = param_grid or {
        "n_estimators":      [100, 200],
        "max_depth":         [5, 10, None],
        "min_samples_split": [2, 5],
        "max_features":      ["sqrt", "log2"],
    }

    model = train_random_forest(prepared.train_df, random_seed, dropout_col, rf_params)

    feature_cols = list(prepared.X_train.columns)

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    with open(features_path, "w") as f:
        json.dump(feature_cols, f)

    return model, feature_cols
