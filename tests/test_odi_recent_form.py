import pandas as pd
import pytest

from src.features.odi_recent_form import generate_odi_recent_form


@pytest.fixture
def history():
    return pd.DataFrame({
        "MATCH_DATE": pd.to_datetime([
            "2024-01-01",
            "2024-02-01",
            "2024-03-01",
            "2025-01-01",
            "2026-01-01",
        ]),
        "TEAM1": ["India", "Australia", "India", "Australia", "India"],
        "TEAM2": ["Australia", "India", "Australia", "India", "Australia"],
        "WINNER": ["India", "Australia", "India", "Australia", "India"],
    })


def test_future_matches_are_excluded(history):
    result = generate_odi_recent_form(
        history, "India", "Australia", "2025-06-01"
    )

    assert result.loc[0, "TEAM1_ODI_MATCHES"] == 4
    assert result.loc[0, "TEAM2_ODI_MATCHES"] == 4


def test_recent_form_values(history):
    result = generate_odi_recent_form(
        history, "India", "Australia", "2025-06-01"
    )

    assert result.loc[0, "TEAM1_LAST_5_WIN_RATE"] == 0.5
    assert result.loc[0, "TEAM2_LAST_5_WIN_RATE"] == 0.5


def test_team_swap_reverses_differences(history):
    first = generate_odi_recent_form(
        history, "India", "Australia", "2025-06-01"
    )
    second = generate_odi_recent_form(
        history, "Australia", "India", "2025-06-01"
    )

    for column in [
        "LAST_5_WIN_RATE_DIFF",
        "LAST_10_WIN_RATE_DIFF",
        "LAST_20_WIN_RATE_DIFF",
        "ODI_MATCHES_DIFF",
        "ODI_WINS_DIFF",
        "ODI_WIN_RATE_DIFF",
        "MATCHES_LAST_365_DAYS_DIFF",
    ]:
        assert first.loc[0, column] == pytest.approx(
            -second.loc[0, column]
        )


def test_no_missing_values(history):
    result = generate_odi_recent_form(
        history, "India", "Australia", "2025-06-01"
    )

    assert not result.isna().any().any()


def test_same_team_is_rejected(history):
    with pytest.raises(ValueError):
        generate_odi_recent_form(
            history, "India", "India", "2025-06-01"
        )
