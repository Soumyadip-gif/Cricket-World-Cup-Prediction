
import pandas as pd


def inspect_missing_values(dataframe):
    """Return missing-value counts and percentages."""

    missing = dataframe.isnull().sum()

    return pd.DataFrame({
        "missing_values": missing,
        "missing_percentage": (
            missing / len(dataframe) * 100
        ).round(2) if len(dataframe) else 0,
    })


def inspect_duplicates(dataframe):
    """Return the number of duplicate rows."""

    return int(dataframe.duplicated().sum())


def inspect_teams(dataframe):
    """Return unique team names."""

    teams = set()

    for column in ["TEAM1", "TEAM2", "WINNER"]:
        if column in dataframe.columns:
            teams.update(
                dataframe[column].dropna().astype(str).unique()
            )

    return sorted(teams)


def inspect_formats(dataframe):
    """Return match counts by format."""

    if "FORMAT" not in dataframe.columns:
        return pd.Series(dtype="int64")

    return dataframe["FORMAT"].value_counts(dropna=False)


def inspect_dataset(dataframe, dataset_name):
    """Generate a complete inspection report."""

    return {
        "dataset": dataset_name,
        "records": len(dataframe),
        "columns": len(dataframe.columns),
        "duplicates": inspect_duplicates(dataframe),
        "teams": inspect_teams(dataframe),
        "formats": inspect_formats(dataframe).to_dict(),
        "missing_values": inspect_missing_values(dataframe),
    }
