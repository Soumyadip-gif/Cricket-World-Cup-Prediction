
import pandas as pd


TEAM_NAME_MAPPING = {
    "AFG": "Afghanistan",
    "AUS": "Australia",
    "BAN": "Bangladesh",
    "BER": "Bermuda",
    "CAN": "Canada",
    "EA": "East Africa",
    "ENG": "England",
    "IND": "India",
    "IRE": "Ireland",
    "KEN": "Kenya",
    "NAM": "Namibia",
    "NED": "Netherlands",
    "NZ": "New Zealand",
    "PAK": "Pakistan",
    "SA": "South Africa",
    "SCO": "Scotland",
    "SL": "Sri Lanka",
    "UAE": "United Arab Emirates",
    "WI": "West Indies",
    "ZIM": "Zimbabwe",
}


def normalize_team_name(team_name):
    """Convert known team aliases to canonical names."""

    if pd.isna(team_name):
        return team_name

    team_name = str(team_name).strip()

    return TEAM_NAME_MAPPING.get(team_name.upper(), team_name)


def normalize_team_columns(dataframe):
    """Return a copy with normalized team names."""

    normalized = dataframe.copy()

    for column in ["TEAM1", "TEAM2", "WINNER"]:
        if column in normalized.columns:
            normalized[column] = normalized[column].apply(
                normalize_team_name
            )

    return normalized
