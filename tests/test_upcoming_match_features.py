import pandas as pd
import pytest

from src.features.upcoming_match_features import (
    MODEL_FEATURE_COLUMNS,
    generate_upcoming_match_features,
)


@pytest.fixture
def historical_data():
    return pd.DataFrame([
        {"YEAR": 2019, "FORMAT": "ODI", "TEAM1": "India", "TEAM2": "Australia", "WINNER": "India"},
        {"YEAR": 2020, "FORMAT": "ODI", "TEAM1": "India", "TEAM2": "England", "WINNER": "England"},
        {"YEAR": 2021, "FORMAT": "ODI", "TEAM1": "India", "TEAM2": "Australia", "WINNER": "Australia"},
        {"YEAR": 2025, "FORMAT": "ODI", "TEAM1": "India", "TEAM2": "Australia", "WINNER": "India"},
        {"YEAR": 2019, "FORMAT": "T20I", "TEAM1": "India", "TEAM2": "Australia", "WINNER": "Australia"},
    ])


def test_model_feature_schema(historical_data):
    result = generate_upcoming_match_features(
        historical_data, "India", "Australia", "ODI", 2027, "Test Venue"
    )
    assert list(result.columns) == MODEL_FEATURE_COLUMNS
    assert len(result.columns) == 8
    assert not result.isnull().any().any()


def test_prediction_year_and_format_are_excluded(historical_data):
    result = generate_upcoming_match_features(
        historical_data, "India", "Australia", "ODI", 2025, "Test Venue"
    )
    assert result.loc[0, "MATCHES_DIFF"] == 1
    assert result.loc[0, "WINS_DIFF"] == 0
    assert result.loc[0, "H2H_MATCHES"] == 2
    assert result.loc[0, "WIN_RATE_DIFF"] == pytest.approx(-0.1)


def test_team_swapping_reverses_difference_features(historical_data):
    first = generate_upcoming_match_features(
        historical_data, "India", "Australia", "ODI", 2027, "Test Venue"
    )
    swapped = generate_upcoming_match_features(
        historical_data, "Australia", "India", "ODI", 2027, "Test Venue"
    )

    for column in [
        "WIN_RATE_DIFF", "MATCHES_DIFF",
        "WINS_DIFF", "H2H_WIN_DIFF"
    ]:
        assert first.loc[0, column] == pytest.approx(
            -swapped.loc[0, column]
        )

    assert first.loc[0, "H2H_MATCHES"] == swapped.loc[0, "H2H_MATCHES"]


def test_unseen_teams_receive_neutral_features(historical_data):
    result = generate_upcoming_match_features(
        historical_data, "Unknown A", "Unknown B",
        "ODI", 2027, "Test Venue"
    )

    assert result.loc[0, "WIN_RATE_DIFF"] == 0
    assert result.loc[0, "MATCHES_DIFF"] == 0
    assert result.loc[0, "WINS_DIFF"] == 0
    assert result.loc[0, "H2H_MATCHES"] == 0


def test_team_aliases_are_normalized(historical_data):
    result = generate_upcoming_match_features(
        historical_data, "IND", "AUS", "ODI", 2027, "Test Venue"
    )
    assert result.loc[0, "MATCHES_DIFF"] == 1


def test_same_team_is_rejected(historical_data):
    with pytest.raises(ValueError):
        generate_upcoming_match_features(
            historical_data, "India", "IND", "ODI", 2027, "Test Venue"
        )


def test_invalid_format_is_rejected(historical_data):
    with pytest.raises(ValueError):
        generate_upcoming_match_features(
            historical_data, "India", "Australia", "Test", 2027, "Test Venue"
        )
