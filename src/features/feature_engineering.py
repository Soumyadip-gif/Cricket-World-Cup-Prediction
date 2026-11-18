import pandas as pd

from src.data.team_mapper import normalize_team_columns


def prepare_historical_matches(dataframe):
    """
    Prepare valid, decided World Cup matches
    for historical team performance analysis.
    """

    df = dataframe.copy()

    # Normalize team names before winner verification
    df = normalize_team_columns(df)

    # Keep only genuine decided matches
    valid = df[
        df["WINNER"].notna()
        & (
            (df["WINNER"] == df["TEAM1"])
            | (df["WINNER"] == df["TEAM2"])
        )
    ].copy()

    # Convert year into numeric format
    valid["YEAR"] = pd.to_numeric(
        valid["YEAR"], errors="coerce"
    )

    # Remove records without essential information
    valid = valid.dropna(
        subset=["YEAR", "FORMAT", "TEAM1", "TEAM2", "WINNER"]
    )

    return valid.reset_index(drop=True)

def calculate_team_performance(dataframe):
    """
    Calculate historical wins, losses and win percentage
    for every team in each World Cup format.
    """

    records = []

    for _, match in dataframe.iterrows():

        for team in [match["TEAM1"], match["TEAM2"]]:

            won = int(match["WINNER"] == team)

            records.append({
                "FORMAT": match["FORMAT"],
                "TEAM": team,
                "WINS": won,
                "MATCHES": 1
            })

    performance = pd.DataFrame(records)

    summary = (
        performance
        .groupby(["FORMAT", "TEAM"], as_index=False)
        .agg(
            MATCHES=("MATCHES", "sum"),
            WINS=("WINS", "sum")
        )
    )

    summary["LOSSES"] = summary["MATCHES"] - summary["WINS"]

    summary["WIN_PERCENTAGE"] = (
        summary["WINS"] / summary["MATCHES"] * 100
    ).round(2)

    return summary.sort_values(
        ["FORMAT", "WIN_PERCENTAGE"],
        ascending=[True, False]
    ).reset_index(drop=True)

def add_pre_match_team_features(dataframe):
    """
    Calculate team performance using only previous years.
    Matches from the current year are excluded.
    """

    df = dataframe.copy()
    df = df.sort_values(["FORMAT", "YEAR"]).reset_index(drop=True)

    history = {}
    records = []

    for (match_format, year), group in df.groupby(
        ["FORMAT", "YEAR"], sort=True
    ):

        # Calculate features before updating historical records
        for _, match in group.iterrows():

            row = match.to_dict()

            for position in ["TEAM1", "TEAM2"]:

                team = match[position]
                key = (match_format, team)

                matches = history.get(key, {}).get("MATCHES", 0)
                wins = history.get(key, {}).get("WINS", 0)

                row[f"{position}_HISTORICAL_MATCHES"] = matches
                row[f"{position}_HISTORICAL_WINS"] = wins

                # Neutral 50% when no previous matches exist
                row[f"{position}_HISTORICAL_WIN_RATE"] = (
                    (wins + 1) / (matches + 2)
                )

            records.append(row)

        # Update history only after processing the entire year
        for _, match in group.iterrows():

            for team in [match["TEAM1"], match["TEAM2"]]:

                key = (match_format, team)

                if key not in history:
                    history[key] = {
                        "MATCHES": 0,
                        "WINS": 0
                    }

                history[key]["MATCHES"] += 1

                if match["WINNER"] == team:
                    history[key]["WINS"] += 1

    return pd.DataFrame(records)

def add_head_to_head_features(dataframe):
    """
    Calculate previous World Cup head-to-head statistics.
    Only matches from earlier years are considered.
    """

    df = dataframe.copy()
    df = df.sort_values(["FORMAT", "YEAR"]).reset_index(drop=True)

    history = {}
    records = []

    for (match_format, year), group in df.groupby(
        ["FORMAT", "YEAR"], sort=True
    ):

        # Calculate historical head-to-head features
        for _, match in group.iterrows():

            team1 = match["TEAM1"]
            team2 = match["TEAM2"]

            pair = tuple(sorted([team1, team2]))
            key = (match_format, pair)

            stats = history.get(key, {
                "MATCHES": 0,
                team1: 0,
                team2: 0
            })

            row = match.to_dict()

            row["H2H_MATCHES"] = stats["MATCHES"]
            row["TEAM1_H2H_WINS"] = stats.get(team1, 0)
            row["TEAM2_H2H_WINS"] = stats.get(team2, 0)

            records.append(row)

        # Update history after processing the entire year
        for _, match in group.iterrows():

            team1 = match["TEAM1"]
            team2 = match["TEAM2"]

            pair = tuple(sorted([team1, team2]))
            key = (match_format, pair)

            if key not in history:
                history[key] = {
                    "MATCHES": 0,
                    team1: 0,
                    team2: 0
                }

            history[key]["MATCHES"] += 1
            history[key].setdefault(team1, 0)
            history[key].setdefault(team2, 0)

            history[key][match["WINNER"]] += 1

    return pd.DataFrame(records)

def build_match_features(dataframe):
    """
    Build all pre-match historical features.
    """

    df = prepare_historical_matches(dataframe)

    df = add_pre_match_team_features(df)

    df = add_head_to_head_features(df)

    return df