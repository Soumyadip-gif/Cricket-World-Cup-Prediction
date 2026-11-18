
import pandas as pd


REQUIRED_COLUMNS = [
    "FORMAT",
    "YEAR",
    "VENUE",
    "WINNER",
    "TEAM1",
    "TEAM2",
    "TEAM1_HISTORICAL_MATCHES",
    "TEAM1_HISTORICAL_WINS",
    "TEAM1_HISTORICAL_WIN_RATE",
    "TEAM2_HISTORICAL_MATCHES",
    "TEAM2_HISTORICAL_WINS",
    "TEAM2_HISTORICAL_WIN_RATE",
    "H2H_MATCHES",
    "TEAM1_H2H_WINS",
    "TEAM2_H2H_WINS",
]


def build_symmetric_features(dataframe):
    """
    Build team-order symmetric pre-match features.

    Post-match information is used only to create the target.
    It is never included among model input features.
    """

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df = dataframe.copy()

    df["TEAM1_WIN"] = (
        df["WINNER"] == df["TEAM1"]
    ).astype(int)

    features = pd.DataFrame(index=df.index)

    # Team-order invariant features
    features["FORMAT"] = df["FORMAT"]
    features["YEAR"] = df["YEAR"]
    features["VENUE"] = df["VENUE"]

    # Relative historical performance
    features["WIN_RATE_DIFF"] = (
        df["TEAM1_HISTORICAL_WIN_RATE"]
        - df["TEAM2_HISTORICAL_WIN_RATE"]
    )

    features["MATCHES_DIFF"] = (
        df["TEAM1_HISTORICAL_MATCHES"]
        - df["TEAM2_HISTORICAL_MATCHES"]
    )

    features["WINS_DIFF"] = (
        df["TEAM1_HISTORICAL_WINS"]
        - df["TEAM2_HISTORICAL_WINS"]
    )

    # Relative head-to-head performance
    features["H2H_WIN_DIFF"] = (
        df["TEAM1_H2H_WINS"]
        - df["TEAM2_H2H_WINS"]
    )

    features["H2H_MATCHES"] = df["H2H_MATCHES"]

    # Target is kept separate from model inputs
    target = df["TEAM1_WIN"].copy()

    return features.reset_index(drop=True), target.reset_index(drop=True)
