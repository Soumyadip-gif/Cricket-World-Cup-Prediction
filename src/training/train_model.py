
import pandas as pd
import joblib

from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


DATA_DIR = Path(r"C:\Users\HP\Documents\Cricket_datset\processed")
MODEL_DIR = Path(r"C:\Users\HP\Documents\Cricket-World-Cup-Prediction\models")

MODEL_DIR.mkdir(parents=True, exist_ok=True)

train = pd.read_csv(DATA_DIR / "Model_Training_Data.csv")
validation = pd.read_csv(DATA_DIR / "Model_Validation_Data.csv")

X_train = train.drop(columns=["TEAM1_WIN"])
y_train = train["TEAM1_WIN"]

X_val = validation.drop(columns=["TEAM1_WIN"])
y_val = validation["TEAM1_WIN"]

# Reverse team-relative features for augmentation
DIFF_COLUMNS = [
    "WIN_RATE_DIFF", "MATCHES_DIFF",
    "WINS_DIFF", "H2H_WIN_DIFF"
]

# Build features from the original training data
from src.features.feature_engineering import build_match_features
from src.features.symmetric_features import build_symmetric_features

master = pd.read_csv(
    DATA_DIR / "Combined_Cricket_World_Cup_Master_Dataset.csv"
)

features = build_match_features(master)
X_all, y_all = build_symmetric_features(features)

# Use chronological training years only
train_years = set(train["YEAR"].unique())
mask = features["YEAR"].isin(train_years)

X_train = X_all.loc[mask].reset_index(drop=True)
y_train = y_all.loc[mask].reset_index(drop=True)

X_swapped = X_train.copy()
for column in DIFF_COLUMNS:
    X_swapped[column] = -X_swapped[column]

X_augmented = pd.concat([X_train, X_swapped], ignore_index=True)
y_augmented = pd.concat([y_train, 1 - y_train], ignore_index=True)

categorical = ["FORMAT", "VENUE"]
numeric = [
    "YEAR", "WIN_RATE_DIFF", "MATCHES_DIFF",
    "WINS_DIFF", "H2H_WIN_DIFF", "H2H_MATCHES"
]

preprocessor = ColumnTransformer([
    ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
    ("numeric", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), numeric)
])

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced"))
])

model.fit(X_augmented, y_augmented)

joblib.dump(model, MODEL_DIR / "Cricket_World_Cup_Model.pkl")

print("TRAINING COMPLETED")
print("Original training rows:", len(X_train))
print("Augmented training rows:", len(X_augmented))
print("Validation rows reserved:", len(X_val))
print("Model saved:", MODEL_DIR / "Cricket_World_Cup_Model.pkl")
