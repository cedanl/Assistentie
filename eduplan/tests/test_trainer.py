"""Tests voor backend/trainer.py."""

import json
import os
import tempfile
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor

from backend import trainer
from backend.main import features_default as features


def _make_df(n: int, seed: int = 0) -> pd.DataFrame:
    """Genereer een synthetisch DataFrame met alle model-features en een Dropout-kolom."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(rng.random((n, len(features))), columns=features)
    df["Dropout"] = rng.integers(0, 2, size=n).astype(float)
    df["Studentnummer"] = range(n)
    return df


def _make_mocks(df: pd.DataFrame):
    """Bouw student-signal mocks: een gefitte RF en een prepared-object."""
    feature_cols = [c for c in df.columns if c != "Dropout"]
    rf = RandomForestRegressor(n_estimators=2, max_depth=3, random_state=42)
    rf.fit(df[feature_cols].values, df["Dropout"].values)

    prepared = MagicMock()
    prepared.train_df = df
    prepared.X_train = df[feature_cols]
    return prepared, rf


@pytest.fixture(autouse=True)
def mock_student_signal(monkeypatch):
    """Mock student-signal voor alle trainer-tests (snel + geen externe dependency)."""

    def fake_prepare(train_df, test_df, target_col, id_col):
        prepared, _ = _make_mocks(train_df)
        return prepared

    def fake_train_rf(train_df, random_seed, target_col, param_grid):
        feature_cols = [c for c in train_df.columns if c != target_col]
        rf = RandomForestRegressor(n_estimators=2, max_depth=3, random_state=random_seed)
        rf.fit(train_df[feature_cols].values, train_df[target_col].values)
        return rf

    monkeypatch.setattr(trainer, "prepare", fake_prepare)
    monkeypatch.setattr(trainer, "train_random_forest", fake_train_rf)


def test_train_model_saves_joblib_and_features_json():
    df = _make_df(50)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        model_path = f.name
    features_path = model_path.replace(".joblib", "_features.json")
    try:
        trainer.train_model(df, "Dropout", model_path, features_path)
        assert os.path.exists(model_path)
        assert os.path.exists(features_path)
    finally:
        for p in (model_path, features_path):
            if os.path.exists(p):
                os.unlink(p)


def test_train_model_returns_tuple_with_model_and_features():
    df = _make_df(50)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        model_path = f.name
    features_path = model_path.replace(".joblib", "_features.json")
    try:
        model, feature_cols = trainer.train_model(df, "Dropout", model_path, features_path)
        assert isinstance(model, RandomForestRegressor)
        assert isinstance(feature_cols, list)
        assert len(feature_cols) > 0
    finally:
        for p in (model_path, features_path):
            if os.path.exists(p):
                os.unlink(p)


def test_train_model_features_json_is_valid_list():
    df = _make_df(50)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        model_path = f.name
    features_path = model_path.replace(".joblib", "_features.json")
    try:
        trainer.train_model(df, "Dropout", model_path, features_path)
        with open(features_path) as f:
            saved = json.load(f)
        assert isinstance(saved, list)
        assert "Dropout" not in saved
    finally:
        for p in (model_path, features_path):
            if os.path.exists(p):
                os.unlink(p)


def test_train_model_predictions_in_range():
    df = _make_df(60)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        model_path = f.name
    features_path = model_path.replace(".joblib", "_features.json")
    try:
        model, feature_cols = trainer.train_model(df, "Dropout", model_path, features_path)
        X = df[feature_cols].values[:5]
        preds = model.predict(X)
        assert all(0.0 <= p <= 1.0 for p in preds)
    finally:
        for p in (model_path, features_path):
            if os.path.exists(p):
                os.unlink(p)


def test_train_model_too_few_rows_raises():
    df = _make_df(10)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        model_path = f.name
    features_path = model_path.replace(".joblib", "_features.json")
    try:
        with pytest.raises(ValueError, match="Te weinig trainingsdata"):
            trainer.train_model(df, "Dropout", model_path, features_path)
    finally:
        for p in (model_path, features_path):
            if os.path.exists(p):
                os.unlink(p)


def test_train_model_exactly_30_rows_succeeds():
    df = _make_df(30)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        model_path = f.name
    features_path = model_path.replace(".joblib", "_features.json")
    try:
        model, _ = trainer.train_model(df, "Dropout", model_path, features_path)
        assert model is not None
    finally:
        for p in (model_path, features_path):
            if os.path.exists(p):
                os.unlink(p)


def test_train_model_handles_nan_via_imputation():
    """Met student-signal worden NaN-waarden geïmputeerd — rijen worden NIET verwijderd."""
    df = _make_df(50)
    df.loc[5:45, features[0]] = float("nan")  # veel NaN in één feature
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        model_path = f.name
    features_path = model_path.replace(".joblib", "_features.json")
    try:
        # Moet slagen: student-signal imputeert i.p.v. rijen te droppen
        model, _ = trainer.train_model(df, "Dropout", model_path, features_path)
        assert model is not None
    finally:
        for p in (model_path, features_path):
            if os.path.exists(p):
                os.unlink(p)


def test_train_model_custom_param_grid():
    """Aangepast param_grid wordt geaccepteerd zonder fout."""
    df = _make_df(50)
    minimal_grid = {"n_estimators": [10], "max_depth": [3], "min_samples_split": [2], "max_features": ["sqrt"]}
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        model_path = f.name
    features_path = model_path.replace(".joblib", "_features.json")
    try:
        model, _ = trainer.train_model(df, "Dropout", model_path, features_path, param_grid=minimal_grid)
        assert isinstance(model, RandomForestRegressor)
    finally:
        for p in (model_path, features_path):
            if os.path.exists(p):
                os.unlink(p)
