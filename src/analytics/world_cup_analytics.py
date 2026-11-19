from functools import lru_cache

import pandas as pd

from config import COMBINED_DATASET
from src.data.team_mapper import normalize_team_columns, normalize_team_name


@lru_cache(maxsize=1)
def load_matches():
    """Load and normalize the combined World Cup dataset."""
    df = pd.read_csv(COMBINED_DATASET)
    df = normalize_team_columns(df)

    df["FORMAT"] = df["FORMAT"].astype(str).str.upper().str.strip()
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce")
    return df


def filtered_matches(match_format="ALL"):
    match_format = str(match_format).upper().strip()

    if match_format not in {"ALL", "ODI", "T20I"}:
        raise ValueError("Format must be ALL, ODI or T20I.")

    df = load_matches()

    if match_format != "ALL":
        df = df[df["FORMAT"] == match_format]

    return df.copy()


def decided_matches(df):
    return df[
        df["WINNER"].notna()
        & (
            (df["WINNER"] == df["TEAM1"])
            | (df["WINNER"] == df["TEAM2"])
        )
    ].copy()


def get_overview(match_format="ALL"):
    df = filtered_matches(match_format)
    decided = decided_matches(df)

    teams = set(df["TEAM1"].dropna()) | set(df["TEAM2"].dropna())
    years = df["YEAR"].dropna()

    return {
        "format": match_format.upper(),
        "total_matches": int(len(df)),
        "decided_matches": int(len(decided)),
        "unresolved_matches": int(len(df) - len(decided)),
        "teams_count": len(teams),
        "tournaments_count": int(df[["YEAR", "FORMAT"]].dropna().drop_duplicates().shape[0]),
        "first_year": int(years.min()) if not years.empty else None,
        "latest_year": int(years.max()) if not years.empty else None,
    }


def get_team_statistics(match_format="ALL"):
    df = filtered_matches(match_format)
    decided = decided_matches(df)

    teams = sorted(set(df["TEAM1"].dropna()) | set(df["TEAM2"].dropna()))
    results = []

    for team in teams:
        played = df[
            (df["TEAM1"] == team) | (df["TEAM2"] == team)
        ]

        team_decided = decided[
            (decided["TEAM1"] == team) | (decided["TEAM2"] == team)
        ]

        wins = int((team_decided["WINNER"] == team).sum())
        matches_decided = len(team_decided)
        losses = matches_decided - wins

        results.append({
            "team": team,
            "matches": int(len(played)),
            "wins": wins,
            "losses": losses,
            "unresolved": int(len(played) - matches_decided),
            "win_rate": round(wins / matches_decided * 100, 2)
                if matches_decided else 0.0,
        })

    return sorted(
        results,
        key=lambda item: (item["win_rate"], item["matches"]),
        reverse=True,
    )


def get_team_details(team, match_format="ALL"):
    team = normalize_team_name(team)
    df = filtered_matches(match_format)

    teams = set(df["TEAM1"].dropna()) | set(df["TEAM2"].dropna())

    if team not in teams:
        raise ValueError(f"No World Cup records found for {team}.")

    played = df[
        (df["TEAM1"] == team) | (df["TEAM2"] == team)
    ].copy()

    decided = decided_matches(played)
    wins = int((decided["WINNER"] == team).sum())

    tournament_history = []

    for (year, fmt), group in played.groupby(["YEAR", "FORMAT"]):
        group_decided = decided_matches(group)
        group_wins = int((group_decided["WINNER"] == team).sum())

        tournament_history.append({
            "year": int(year),
            "format": fmt,
            "matches": int(len(group)),
            "wins": group_wins,
            "losses": int(len(group_decided) - group_wins),
        })

    tournament_history.sort(key=lambda item: (item["year"], item["format"]))

    return {
        "team": team,
        "format": match_format.upper(),
        "matches": int(len(played)),
        "decided_matches": int(len(decided)),
        "wins": wins,
        "losses": int(len(decided) - wins),
        "unresolved": int(len(played) - len(decided)),
        "win_rate": round(wins / len(decided) * 100, 2)
            if len(decided) else 0.0,
        "tournament_history": tournament_history,
    }


def get_head_to_head(team1, team2, match_format="ALL"):
    team1 = normalize_team_name(team1)
    team2 = normalize_team_name(team2)

    if not team1 or not team2 or team1 == team2:
        raise ValueError("Select two different teams.")

    df = filtered_matches(match_format)

    matches = df[
        (
            (df["TEAM1"] == team1) & (df["TEAM2"] == team2)
        ) | (
            (df["TEAM1"] == team2) & (df["TEAM2"] == team1)
        )
    ].copy()

    decided = decided_matches(matches)

    wins1 = int((decided["WINNER"] == team1).sum())
    wins2 = int((decided["WINNER"] == team2).sum())

    return {
        "team1": team1,
        "team2": team2,
        "format": match_format.upper(),
        "matches": int(len(matches)),
        "team1_wins": wins1,
        "team2_wins": wins2,
        "unresolved": int(len(matches) - len(decided)),
        "history": [
            {
                "year": int(row.YEAR) if pd.notna(row.YEAR) else None,
                "format": row.FORMAT,
                "venue": row.VENUE if pd.notna(row.VENUE) else "Unknown",
                "winner": row.WINNER if pd.notna(row.WINNER) else None,
            }
            for row in matches.sort_values("YEAR").itertuples()
        ],
    }


def get_tournament_history(match_format="ALL"):
    df = filtered_matches(match_format)
    results = []

    for (year, fmt), group in df.groupby(["YEAR", "FORMAT"]):
        decided = decided_matches(group)

        results.append({
            "year": int(year),
            "format": fmt,
            "matches": int(len(group)),
            "decided_matches": int(len(decided)),
            "teams": int(
                len(set(group["TEAM1"].dropna()) | set(group["TEAM2"].dropna()))
            ),
        })

    return sorted(results, key=lambda item: (item["year"], item["format"]))
