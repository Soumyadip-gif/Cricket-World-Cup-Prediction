
import pandas as pd
from pathlib import Path

from src.features.feature_engineering import build_match_features
from src.data.team_mapper import normalize_team_columns


DATA_DIR = Path(r"C:\Users\HP\Documents\Cricket_datset\processed")

MATCH_COLUMNS = [
    "FORMAT", "YEAR", "TEAM1", "TEAM2", "VENUE", "TEAM1_WIN"
]


def main():
    master = pd.read_csv(
        DATA_DIR / "Combined_Cricket_World_Cup_Master_Dataset.csv"
    )

    features = build_match_features(master)
    features["TEAM1_WIN"] = (
        features["WINNER"] == features["TEAM1"]
    ).astype(int)

    filenames = [
        "Model_Training_Data.csv",
        "Model_Validation_Data.csv",
        "Model_Test_Data.csv",
    ]

    splits = pd.concat(
        [
            normalize_team_columns(pd.read_csv(DATA_DIR / filename))
            for filename in filenames
        ],
        ignore_index=True
    )

    feature_counts = features.groupby(
        MATCH_COLUMNS, dropna=False
    ).size()

    split_counts = splits.groupby(
        MATCH_COLUMNS, dropna=False
    ).size()

    comparison = pd.concat(
        [
            feature_counts.rename("FEATURE_COUNT"),
            split_counts.rename("SPLIT_COUNT"),
        ],
        axis=1
    ).fillna(0)

    mismatches = comparison[
        comparison["FEATURE_COUNT"] != comparison["SPLIT_COUNT"]
    ]

    print("FEATURE ROWS:", len(features))
    print("COMBINED SPLIT ROWS:", len(splits))
    print("DUPLICATE COUNT MISMATCHES:", len(mismatches))

    if mismatches.empty:
        print("FEATURE ALIGNMENT: PASSED")
    else:
        print(mismatches.to_string())


if __name__ == "__main__":
    main()
