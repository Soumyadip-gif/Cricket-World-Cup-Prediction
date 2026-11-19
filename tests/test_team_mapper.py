import pytest
from src.data.team_mapper import normalize_team_name


@pytest.mark.parametrize("original, expected", [
    ("AFG", "Afghanistan"),
    ("AUS", "Australia"),
    ("BAN", "Bangladesh"),
    ("BER", "Bermuda"),
    ("CAN", "Canada"),
    ("EA", "East Africa"),
    ("ENG", "England"),
    ("IND", "India"),
    ("IRE", "Ireland"),
    ("KEN", "Kenya"),
    ("NAM", "Namibia"),
    ("NED", "Netherlands"),
    ("NZ", "New Zealand"),
    ("PAK", "Pakistan"),
    ("SA", "South Africa"),
    ("SCO", "Scotland"),
    ("SL", "Sri Lanka"),
    ("UAE", "United Arab Emirates"),
    ("WI", "West Indies"),
    ("ZIM", "Zimbabwe"),
    ("Hong Kong", "Hong Kong"),
    ("Nepal", "Nepal"),
    ("Oman", "Oman"),
    ("Papua New Guinea", "Papua New Guinea"),
    ("Uganda", "Uganda"),
    ("United States of America", "United States of America"),
])
def test_team_alias_normalization(original, expected):
    assert normalize_team_name(original) == expected


def test_normalized_names_are_idempotent():
    canonical_names = [
        "Afghanistan", "Australia", "Bangladesh", "Bermuda",
        "Canada", "East Africa", "England", "Hong Kong",
        "India", "Ireland", "Kenya", "Namibia", "Nepal",
        "Netherlands", "New Zealand", "Oman", "Pakistan",
        "Papua New Guinea", "Scotland", "South Africa",
        "Sri Lanka", "Uganda", "United Arab Emirates",
        "United States of America", "West Indies", "Zimbabwe",
    ]

    for name in canonical_names:
        assert normalize_team_name(name) == name
