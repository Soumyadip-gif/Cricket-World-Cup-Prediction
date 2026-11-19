import pandas as pd

from src.data.team_mapper import normalize_team_name


def load_odi_history(path="data/external_mens_odi_matches.csv"):
    """Load and validate decided men's ODI match history."""
    df = pd.read_csv(path)

    required = {
        "MATCH_DATE", "TEAM1", "TEAM2", "WINNER"
    }
    missing = required.difference(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["MATCH_DATE"] = pd.to_datetime(
        df["MATCH_DATE"], errors="coerce"
    )

    for column in ["TEAM1", "TEAM2", "WINNER"]:
        df[column] = df[column].apply(normalize_team_name)

    df = df.dropna(
        subset=["MATCH_DATE", "TEAM1", "TEAM2", "WINNER"]
    ).copy()

    df = df[
        (df["WINNER"] == df["TEAM1"])
        | (df["WINNER"] == df["TEAM2"])
    ].copy()

    return df.sort_values("MATCH_DATE").reset_index(drop=True)


def generate_odi_recent_form(
    history, team1, team2, match_date
):
    """Generate ODI form using only matches before the target date."""

    if normalize_team_name(team1) == normalize_team_name(team2):
        raise ValueError("Team 1 and Team 2 must be different.")

    target_date = pd.Timestamp(match_date)

    if pd.isna(target_date):
        raise ValueError("A valid target match date is required.")

    team1 = normalize_team_name(team1)
    team2 = normalize_team_name(team2)

    past = history[
        (history["MATCH_DATE"] < target_date)
        & (history["WINNER"].notna())
    ].copy()

    features = {}

    for team, prefix in [
        (team1, "TEAM1"),
        (team2, "TEAM2"),
    ]:
        matches = past[
            (past["TEAM1"] == team)
            | (past["TEAM2"] == team)
        ].sort_values("MATCH_DATE")

        wins = matches[matches["WINNER"] == team]

        for window in [5, 10, 20]:
            recent = matches.tail(window)
            recent_wins = (recent["WINNER"] == team).sum()

            features[f"{prefix}_LAST_{window}_WIN_RATE"] = (
                recent_wins / len(recent) if len(recent) else 0.5
            )

        features[f"{prefix}_ODI_MATCHES"] = len(matches)
        features[f"{prefix}_ODI_WINS"] = len(wins)
        features[f"{prefix}_ODI_WIN_RATE"] = (
            (len(wins) + 1) / (len(matches) + 2)
        )

        recent_activity = matches[
            matches["MATCH_DATE"] >= (
                target_date - pd.Timedelta(days=365)
            )
        ]

        features[f"{prefix}_MATCHES_LAST_365_DAYS"] = len(
            recent_activity
        )

    for column in [
        "LAST_5_WIN_RATE",
        "LAST_10_WIN_RATE",
        "LAST_20_WIN_RATE",
        "ODI_MATCHES",
        "ODI_WINS",
        "ODI_WIN_RATE",
        "MATCHES_LAST_365_DAYS",
    ]:
        features[f"{column}_DIFF"] = (
            features[f"TEAM1_{column}"]
            - features[f"TEAM2_{column}"]
        )

    return pd.DataFrame([features])
