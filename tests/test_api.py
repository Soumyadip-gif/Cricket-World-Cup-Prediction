import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_prediction_endpoint(client):
    response = client.post(
        "/api/predict",
        json={
            "team1": "India",
            "team2": "Australia",
            "format": "ODI",
            "year": 2027,
            "venue": "Unknown",
        },
    )

    assert response.status_code == 200

    result = response.get_json()

    assert result["team1"] == "India"
    assert result["team2"] == "Australia"
    assert (
        result["team1_win_probability"]
        + result["team2_win_probability"]
    ) == 100


def test_missing_fields(client):
    response = client.post(
        "/api/predict",
        json={"team1": "India"},
    )
    assert response.status_code == 400


def test_same_team_rejected(client):
    response = client.post(
        "/api/predict",
        json={
            "team1": "India",
            "team2": "India",
            "format": "ODI",
            "year": 2027,
            "venue": "Unknown",
        },
    )
    assert response.status_code == 400


def test_invalid_format_rejected(client):
    response = client.post(
        "/api/predict",
        json={
            "team1": "India",
            "team2": "Australia",
            "format": "TEST",
            "year": 2027,
            "venue": "Unknown",
        },
    )
    assert response.status_code == 400
