import pandas as pd

from src.features.feature_engineering import (
    prepare_historical_matches,
    add_pre_match_team_features,
    add_head_to_head_features,
)
from src.features.symmetric_features import build_symmetric_features


def sample_matches():
    return pd.DataFrame([
        {
            "YEAR": 2020, "FORMAT": "ODI",
            "TEAM1": "AUS", "TEAM2": "IND",
            "WINNER": "AUS", "VENUE": "London"
        },
        {
            "YEAR": 2021, "FORMAT": "ODI",
            "TEAM1": "Australia", "TEAM2": "India",
            "WINNER": "India", "VENUE": "Mumbai"
        },
        {
            "YEAR": 2022, "FORMAT": "ODI",
            "TEAM1": "Australia", "TEAM2": "India",
            "WINNER": None, "VENUE": "Delhi"
        },
    ])


def test_prepare_historical_matches_normalizes_and_filters():
    result = prepare_historical_matches(sample_matches())

    assert len(result) == 2
    assert result.iloc[0]["TEAM1"] == "Australia"
    assert result.iloc[0]["TEAM2"] == "India"
    assert result["WINNER"].notna().all()


def test_team_features_use_only_previous_years():
    historical = prepare_historical_matches(sample_matches())
    result = add_pre_match_team_features(historical)

    first_year = result[result["YEAR"] == 2020].iloc[0]
    second_year = result[result["YEAR"] == 2021].iloc[0]

    assert first_year["TEAM1_HISTORICAL_MATCHES"] == 0
    assert first_year["TEAM1_HISTORICAL_WIN_RATE"] == 0.5

    assert second_year["TEAM1_HISTORICAL_MATCHES"] == 1
    assert second_year["TEAM1_HISTORICAL_WINS"] == 1
    assert second_year["TEAM2_HISTORICAL_MATCHES"] == 1
    assert second_year["TEAM2_HISTORICAL_WINS"] == 0


def test_head_to_head_uses_only_previous_years():
    historical = prepare_historical_matches(sample_matches())
    result = add_head_to_head_features(historical)

    first_year = result[result["YEAR"] == 2020].iloc[0]
    second_year = result[result["YEAR"] == 2021].iloc[0]

    assert first_year["H2H_MATCHES"] == 0
    assert second_year["H2H_MATCHES"] == 1
    assert second_year["TEAM1_H2H_WINS"] == 1
    assert second_year["TEAM2_H2H_WINS"] == 0


def test_symmetric_features_have_expected_model_inputs():
    dataframe = pd.DataFrame([{
        "FORMAT": "ODI",
        "YEAR": 2023,
        "VENUE": "London",
        "WINNER": "Australia",
        "TEAM1": "Australia",
        "TEAM2": "India",
        "TEAM1_HISTORICAL_MATCHES": 10,
        "TEAM1_HISTORICAL_WINS": 7,
        "TEAM1_HISTORICAL_WIN_RATE": 0.7,
        "TEAM2_HISTORICAL_MATCHES": 8,
        "TEAM2_HISTORICAL_WINS": 4,
        "TEAM2_HISTORICAL_WIN_RATE": 0.5,
        "H2H_MATCHES": 5,
        "TEAM1_H2H_WINS": 3,
        "TEAM2_H2H_WINS": 2,
    }])

    features, target = build_symmetric_features(dataframe)

    expected_columns = [
        "FORMAT", "YEAR", "VENUE", "WIN_RATE_DIFF",
        "MATCHES_DIFF", "WINS_DIFF", "H2H_WIN_DIFF",
        "H2H_MATCHES",
    ]

    assert list(features.columns) == expected_columns
    assert features.shape == (1, 8)
    assert abs(features.iloc[0]["WIN_RATE_DIFF"] - 0.2) < 1e-9
    assert features.iloc[0]["MATCHES_DIFF"] == 2
    assert features.iloc[0]["WINS_DIFF"] == 3
    assert features.iloc[0]["H2H_WIN_DIFF"] == 1
    assert target.tolist() == [1]
