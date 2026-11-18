import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "data" / "Cricket_World_Cup_Prediction_Model.pkl"

model = joblib.load(MODEL_PATH)


def predict_match(team1, team2, match_format, year, venue):
    data = pd.DataFrame([{
        "FORMAT": match_format,
        "YEAR": year,
        "TEAM1": team1,
        "TEAM2": team2,
        "VENUE": venue
    }])

    swapped = data.copy()
    swapped["TEAM1"] = team2
    swapped["TEAM2"] = team1

    p1 = model.predict_proba(data)[0][1]
    p2 = model.predict_proba(swapped)[0][1]

    team1_probability = (p1 + 1 - p2) / 2

    return {
        "team1": team1,
        "team2": team2,
        "team1_win_probability": round(team1_probability * 100, 2),
        "team2_win_probability": round((1 - team1_probability) * 100, 2)
    }