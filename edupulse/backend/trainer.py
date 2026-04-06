"""backend/trainer.py

Trainingslogica voor het instellingsspecifieke Random Forest-model.
Gebaseerd op de aanpak van cedanl/Uitnodigingsregel.
"""

import joblib
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

# Standaard hyperparameterraster — snel genoeg voor MBO-schaalgrootte (300–2000 rijen)
DEFAULT_PARAM_GRID: dict = {
    "n_estimators":      [100, 200],
    "max_depth":         [5, 10, None],
    "min_samples_split": [2, 5],
    "max_features":      ["sqrt", "log2"],
}


def train_model(
    df: pd.DataFrame,
    dropout_col: str,
    feature_cols: list[str],
    model_path: str,
    param_grid: dict | None = None,
    random_seed: int = 42,
) -> RandomForestRegressor:
    """Train een RandomForestRegressor op de meegegeven data en sla het op.

    Args:
        df:           DataFrame met features én doelkolom.
        dropout_col:  Naam van de uitval-doelkolom (bijv. "Dropout").
        feature_cols: Lijst met featurekolommen, in de volgorde die het model verwacht.
        model_path:   Pad waar het getrainde model wordt opgeslagen (.joblib).
        param_grid:   GridSearchCV-raster; gebruikt DEFAULT_PARAM_GRID indien None.
        random_seed:  Random state voor reproduceerbaarheid.

    Returns:
        Het getrainde RandomForestRegressor-model.

    Raises:
        ValueError: Als er te weinig trainingsrijen zijn na het verwijderen van NaN-waarden.
    """
    grid = param_grid or DEFAULT_PARAM_GRID

    # Alleen rijen met volledig ingevulde features én een bekend uitvalresultaat
    cols_needed = feature_cols + [dropout_col]
    df_train = df[cols_needed].dropna()

    if len(df_train) < 30:
        raise ValueError(
            f"Te weinig trainingsdata: {len(df_train)} rijen na verwijdering van ontbrekende waarden "
            f"(minimum: 30). Controleer of de kolom '{dropout_col}' voldoende gevulde waarden heeft."
        )

    # Kolommen expliciet in de verwachte volgorde ophalen (voorkomt stille feature-mismatch)
    X = df_train[feature_cols].values
    y = df_train[dropout_col].values

    rf = RandomForestRegressor(random_state=random_seed)
    grid_search = GridSearchCV(
        rf,
        param_grid=grid,
        cv=5,
        scoring="neg_mean_squared_error",
        n_jobs=1,          # n_jobs=1 voorkomt problemen met forking in een daemon-thread
        refit=True,
        verbose=0,
    )
    grid_search.fit(X, y)
    best_model = grid_search.best_estimator_

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, model_path)

    return best_model
