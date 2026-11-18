
import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score

from src.features.feature_engineering import build_match_features
from src.features.symmetric_features import build_symmetric_features

DATA = Path(r"C:\Users\HP\Documents\Cricket_datset\processed")

baseline = joblib.load(DATA / "Cricket_World_Cup_Prediction_Model.pkl")
improved = joblib.load("models/Cricket_World_Cup_Model.pkl")

validation = pd.read_csv(DATA / "Model_Validation_Data.csv")

# Baseline predictions
X_base = validation[["FORMAT", "YEAR", "TEAM1", "TEAM2", "VENUE"]]
y = validation["TEAM1_WIN"]

base_prob = baseline.predict_proba(X_base)[:, 1]

# Improved model predictions
master = pd.read_csv(DATA / "Combined_Cricket_World_Cup_Master_Dataset.csv")
features = build_match_features(master)
X_all, y_all = build_symmetric_features(features)

mask = features["YEAR"].isin(validation["YEAR"].unique())
X_new = X_all.loc[mask].reset_index(drop=True)
y_new = y_all.loc[mask].reset_index(drop=True)

assert len(X_new) == len(validation)
assert y.equals(y_new), "Validation target order mismatch!"

X_swapped = X_new.copy()
for col in ["WIN_RATE_DIFF", "MATCHES_DIFF", "WINS_DIFF", "H2H_WIN_DIFF"]:
    X_swapped[col] *= -1

p1 = improved.predict_proba(X_new)[:, 1]
p2 = improved.predict_proba(X_swapped)[:, 1]
new_prob = (p1 + 1 - p2) / 2

print("MODEL COMPARISON — VALIDATION")
for name, prob in [("Baseline", base_prob), ("Improved", new_prob)]:
    pred = (prob >= 0.5).astype(int)
    print(f"\n{name}")
    print("Accuracy:", round(accuracy_score(y, pred), 4))
    print("Balanced Accuracy:", round(balanced_accuracy_score(y, pred), 4))
    print("ROC-AUC:", round(roc_auc_score(y, prob), 4))
