
import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from src.features.feature_engineering import build_match_features
from src.features.symmetric_features import build_symmetric_features


DATA_DIR = Path(r"C:\Users\HP\Documents\Cricket_datset\processed")
MODEL_PATH = Path("models/Cricket_World_Cup_Model.pkl")

master = pd.read_csv(DATA_DIR / "Combined_Cricket_World_Cup_Master_Dataset.csv")
validation = pd.read_csv(DATA_DIR / "Model_Validation_Data.csv")

features = build_match_features(master)
X_all, y_all = build_symmetric_features(features)

# Select validation years only
mask = features["YEAR"].isin(validation["YEAR"].unique())
X_val = X_all.loc[mask].reset_index(drop=True)
y_val = y_all.loc[mask].reset_index(drop=True)

assert len(X_val) == len(validation), "Validation row count mismatch!"

model = joblib.load(MODEL_PATH)

# Team-order symmetric probabilities
X_swapped = X_val.copy()
for column in ["WIN_RATE_DIFF", "MATCHES_DIFF", "WINS_DIFF", "H2H_WIN_DIFF"]:
    X_swapped[column] = -X_swapped[column]

prob_original = model.predict_proba(X_val)[:, 1]
prob_swapped = model.predict_proba(X_swapped)[:, 1]
probabilities = (prob_original + 1 - prob_swapped) / 2

predictions = (probabilities >= 0.5).astype(int)

print("VALIDATION RESULTS")
print("Matches:", len(y_val))
print("Accuracy:", round(accuracy_score(y_val, predictions), 4))
print("Balanced Accuracy:", round(balanced_accuracy_score(y_val, predictions), 4))
print("ROC-AUC:", round(roc_auc_score(y_val, probabilities), 4))
print("\nConfusion Matrix:\n", confusion_matrix(y_val, predictions))
print("\nClassification Report:\n", classification_report(y_val, predictions))
