import joblib
import numpy as np
import pandas as pd
from pathlib import Path


def test_improved_model_accepts_eight_features():
    model_path = Path("models/Cricket_World_Cup_Model.pkl")

    assert model_path.is_file()

    model = joblib.load(model_path)

    expected_features = [
        "FORMAT",
        "YEAR",
        "VENUE",
        "WIN_RATE_DIFF",
        "MATCHES_DIFF",
        "WINS_DIFF",
        "H2H_WIN_DIFF",
        "H2H_MATCHES",
    ]

    assert list(model.feature_names_in_) == expected_features
    assert model.n_features_in_ == 8
    assert list(model.named_steps["classifier"].classes_) == [0, 1]


def test_improved_model_returns_valid_probabilities():
    model = joblib.load("models/Cricket_World_Cup_Model.pkl")

    sample = pd.DataFrame([{
        "FORMAT": "ODI",
        "YEAR": 2027,
        "VENUE": "London",
        "WIN_RATE_DIFF": 0.15,
        "MATCHES_DIFF": 10,
        "WINS_DIFF": 6,
        "H2H_WIN_DIFF": 2,
        "H2H_MATCHES": 5,
    }])

    probabilities = model.predict_proba(sample)

    assert probabilities.shape == (1, 2)
    assert np.isfinite(probabilities).all()
    assert np.all(probabilities >= 0)
    assert np.all(probabilities <= 1)
    assert np.isclose(probabilities.sum(), 1.0)
