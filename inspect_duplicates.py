import pandas as pd
from config import PREDICTION_DATASET, TRAINING_DATASET

for name, path in [
    ("PREDICTION", PREDICTION_DATASET),
    ("TRAINING", TRAINING_DATASET),
]:
    df = pd.read_csv(path)
    duplicates = df[df.duplicated(keep=False)]

    print(f"\n--- {name} DUPLICATES ---")
    print(duplicates.to_string(index=False))
