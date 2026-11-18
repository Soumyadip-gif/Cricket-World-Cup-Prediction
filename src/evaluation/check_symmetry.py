
import pandas as pd
import joblib
import numpy as np

from pathlib import Path

DATA = Path(r"C:\Users\HP\Documents\Cricket_datset\processed")

model = joblib.load(DATA / "Cricket_World_Cup_Prediction_Model.pkl")
df = pd.read_csv(DATA / "Model_Validation_Data.csv")

columns = ["FORMAT", "YEAR", "TEAM1", "TEAM2", "VENUE"]

X = df[columns].copy()
X_swapped = X.copy()

X_swapped["TEAM1"], X_swapped["TEAM2"] = (
    X["TEAM2"].values, X["TEAM1"].values
)

p1 = model.predict_proba(X)[:, 1]
p2 = model.predict_proba(X_swapped)[:, 1]

print("MEAN SYMMETRY ERROR:", round(np.mean(np.abs(p1 + p2 - 1)), 4))
print("MAX SYMMETRY ERROR:", round(np.max(np.abs(p1 + p2 - 1)), 4))
print("PERFECTLY SYMMETRIC:", np.allclose(p1 + p2, 1))
