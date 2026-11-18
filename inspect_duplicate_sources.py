import pandas as pd
from config import COMBINED_DATASET

df = pd.read_csv(COMBINED_DATASET)

cases = [
    ("ODI", 1975, "AUS", "WI"),
    ("T20I", 2010, "Australia", "Pakistan"),
]

columns = [
    "FORMAT", "YEAR", "MATCH_DATE", "TEAM1", "TEAM2",
    "WINNER", "VENUE", "MATCH_ID", "SOURCE_FILE"
]

for fmt, year, team1, team2 in cases:
    mask = (
        (df["FORMAT"] == fmt)
        & (df["YEAR"] == year)
        & (
            ((df["TEAM1"] == team1) & (df["TEAM2"] == team2))
            | ((df["TEAM1"] == team2) & (df["TEAM2"] == team1))
        )
    )

    print(f"\n--- {fmt} {year}: {team1} vs {team2} ---")
    print(df.loc[mask, columns].to_string(index=False))
