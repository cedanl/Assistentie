"""Tests voor backend/trainer.py."""

import os
import tempfile

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor

from backend.main import features
from backend import trainer


def _make_df(n: int, seed: int = 0) -> pd.DataFrame:
    """Genereer een synthetisch DataFrame met alle model-features en een Dropout-kolom."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        rng.random((n, len(features))), columns=features
    )
    df["Dropout"] = rng.integers(0, 2, size=n).astype(float)
    return df


def test_train_model_saves_file():
    df = _make_df(50)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name
    try:
        trainer.train_model(df, "Dropout", features, path)
        assert os.path.exists(path)
    finally:
        os.unlink(path)


def test_train_model_returns_random_forest():
    df = _make_df(50)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name
    try:
        model = trainer.train_model(df, "Dropout", features, path)
        assert isinstance(model, RandomForestRegressor)
    finally:
        os.unlink(path)


def test_train_model_predictions_in_range():
    df = _make_df(60)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name
    try:
        model = trainer.train_model(df, "Dropout", features, path)
        X = df[features].values[:5]
        preds = model.predict(X)
        assert all(0.0 <= p <= 1.0 for p in preds)
    finally:
        os.unlink(path)


def test_train_model_too_few_rows_raises():
    df = _make_df(10)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name
    try:
        with pytest.raises(ValueError, match="Te weinig trainingsdata"):
            trainer.train_model(df, "Dropout", features, path)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_train_model_exactly_30_rows_succeeds():
    df = _make_df(30)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name
    try:
        model = trainer.train_model(df, "Dropout", features, path)
        assert model is not None
    finally:
        os.unlink(path)


def test_train_model_drops_nan_rows():
    """NaN-rijen worden voor training verwijderd; te weinig over → ValueError."""
    df = _make_df(50)
    # Maak Dropout NaN voor alle rijen behalve 5
    df.loc[5:, "Dropout"] = float("nan")
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name
    try:
        with pytest.raises(ValueError, match="Te weinig trainingsdata"):
            trainer.train_model(df, "Dropout", features, path)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_train_model_custom_param_grid():
    """Aangepast param_grid wordt geaccepteerd zonder fout."""
    df = _make_df(50)
    minimal_grid = {"n_estimators": [10], "max_depth": [3], "min_samples_split": [2], "max_features": ["sqrt"]}
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name
    try:
        model = trainer.train_model(df, "Dropout", features, path, param_grid=minimal_grid)
        assert isinstance(model, RandomForestRegressor)
    finally:
        os.unlink(path)
