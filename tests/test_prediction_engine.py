from src.prediction.predict_match import predict_match


def test_prediction_returns_valid_probabilities():
    result = predict_match(
        "India", "Australia", "ODI", 2027, "Unknown"
    )

    assert 0 <= result["team1_win_probability"] <= 100
    assert 0 <= result["team2_win_probability"] <= 100

    assert (
        result["team1_win_probability"]
        + result["team2_win_probability"]
    ) == 100


def test_prediction_is_symmetric_when_teams_are_swapped():
    first = predict_match(
        "India", "Australia", "ODI", 2027, "Unknown"
    )

    second = predict_match(
        "Australia", "India", "ODI", 2027, "Unknown"
    )

    assert (
        first["team1_win_probability"]
        == second["team2_win_probability"]
    )

    assert (
        first["team2_win_probability"]
        == second["team1_win_probability"]
    )


def test_prediction_preserves_team_names():
    result = predict_match(
        "India", "Australia", "ODI", 2027, "Unknown"
    )

    assert result["team1"] == "India"
    assert result["team2"] == "Australia"
