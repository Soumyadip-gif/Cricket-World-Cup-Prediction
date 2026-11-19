
import pandas as pd

from src.data.team_mapper import normalize_team_name


MODEL_FEATURE_COLUMNS = [
    "FORMAT",
    "YEAR",
    "VENUE",
    "WIN_RATE_DIFF",
    "MATCHES_DIFF",
    "WINS_DIFF",
    "H2H_WIN_DIFF",
    "H2H_MATCHES",
]


def generate_upcoming_match_features(
    historical_data,
    team1,
    team2,
    match_format,
    year,
    venue,
):
    """
    Generate pre-match features for an upcoming World Cup match.

    Only decided matches from earlier years and the same format
    are used. Matches from the target year are excluded.
    """

    if not team1 or not team2:
        raise ValueError("Both team names are required.")

    if normalize_team_name(team1) == normalize_team_name(team2):
        raise ValueError("Both teams must be different.")

    year = int(year)
    match_format = str(match_format).strip().upper()

    if match_format not in {"ODI", "T20I"}:
        raise ValueError("Format must be ODI or T20I.")

    team1 = normalize_team_name(team1)
    team2 = normalize_team_name(team2)

    df = historical_data.copy()

    required_columns = {
        "YEAR", "FORMAT", "TEAM1", "TEAM2", "WINNER"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Historical dataset is missing columns: {sorted(missing_columns)}"
        )

    for column in ["TEAM1", "TEAM2", "WINNER"]:
        df[column] = df[column].apply(normalize_team_name)

    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce")

    # Only earlier years and the requested format are eligible.
    history = df[
        (df["FORMAT"].astype(str).str.upper() == match_format)
        & (df["YEAR"] < year)
        & df["WINNER"].notna()
        & (
            (df["WINNER"] == df["TEAM1"])
            | (df["WINNER"] == df["TEAM2"])
        )
    ].copy()

    def team_statistics(team):
        matches = (
            (history["TEAM1"] == team)
            | (history["TEAM2"] == team)
        )

        team_matches = history[matches]

        wins = int((team_matches["WINNER"] == team).sum())
        total_matches = len(team_matches)

        win_rate = (wins + 1) / (total_matches + 2)

        return total_matches, wins, win_rate

    team1_matches, team1_wins, team1_rate = (
        team_statistics(team1)
    )

    team2_matches, team2_wins, team2_rate = (
        team_statistics(team2)
    )

    # Historical head-to-head records between these teams.
    h2h = history[
        (
            (history["TEAM1"] == team1)
            & (history["TEAM2"] == team2)
        )
        |
        (
            (history["TEAM1"] == team2)
            & (history["TEAM2"] == team1)
        )
    ]

    h2h_matches = len(h2h)

    team1_h2h_wins = int((h2h["WINNER"] == team1).sum())
    team2_h2h_wins = int((h2h["WINNER"] == team2).sum())

    features = {
        "FORMAT": match_format,
        "YEAR": year,
        "VENUE": str(venue).strip() if venue else "Unknown",
        "WIN_RATE_DIFF": team1_rate - team2_rate,
        "MATCHES_DIFF": team1_matches - team2_matches,
        "WINS_DIFF": team1_wins - team2_wins,
        "H2H_WIN_DIFF": team1_h2h_wins - team2_h2h_wins,
        "H2H_MATCHES": h2h_matches,
    }

    return pd.DataFrame(
        [features],
        columns=MODEL_FEATURE_COLUMNS,
    )
