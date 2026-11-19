
import joblib
import pandas as pd
from pathlib import Path

from config import COMBINED_DATASET
from src.features.upcoming_match_features import (
    generate_upcoming_match_features,
)

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "Cricket_World_Cup_Model.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Improved model not found: {MODEL_PATH}"
    )

if not Path(COMBINED_DATASET).exists():
    raise FileNotFoundError(
        f"Historical dataset not found: {COMBINED_DATASET}"
    )

model = joblib.load(MODEL_PATH)
historical_data = pd.read_csv(COMBINED_DATASET)


def predict_match(team1, team2, match_format, year, venue):
    """
    Predict an upcoming World Cup match using the improved
    eight-feature Logistic Regression model.
    """

    features = generate_upcoming_match_features(
        historical_data=historical_data,
        team1=team1,
        team2=team2,
        match_format=match_format,
        year=year,
        venue=venue,
    )

    # Create the reversed fixture to enforce prediction symmetry.
    swapped_features = features.copy()

    difference_columns = [
        "WIN_RATE_DIFF",
        "MATCHES_DIFF",
        "WINS_DIFF",
        "H2H_WIN_DIFF",
    ]

    for column in difference_columns:
        swapped_features[column] = -swapped_features[column]

    # Model class 1 represents TEAM1_WIN.
    p1 = float(model.predict_proba(features)[0][1])
    p2 = float(model.predict_proba(swapped_features)[0][1])

    # Average both prediction directions.
    team1_probability = (p1 + 1 - p2) / 2
    team1_probability = max(0.0, min(1.0, team1_probability))

    team2_probability = 1 - team1_probability

    return {
        "team1": team1,
        "team2": team2,
        "team1_win_probability": round(
            team1_probability * 100, 2
        ),
        "team2_win_probability": round(
            team2_probability * 100, 2
        ),
    }
