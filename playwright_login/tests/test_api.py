import pytest
from playwright.sync_api import APIRequestContext


REQUIRED_PLAYER_FIELDS = {
    "id_player",
    "soprannome",
    "nome",
    "partiteGiocate",
    "primo",
    "secondo",
    "terzo",
    "punteggio",
    "media",
    "contatore",
    "partiteGiornaliere",
}


@pytest.mark.parametrize(
    "path",
    [
        "/api/getRankings",
        "/api/getLastMatch",
        "/api/refreshMonthlyPoints",
        "/api/getLatestHistorySnapshot",
        "/api/getAllMonths",
        "/api/getAllUsers",
        "/api/statistics",
    ],
)
def test_button_get_routes_are_reachable(
    api_request: APIRequestContext,
    path: str,
):
    response = api_request.get(path)

    assert response.status in {200, 204, 404}, (
        f"Unexpected status for GET {path}: {response.status} "
        f"body={response.text()[:200]}"
    )


def test_get_rankings_returns_players_with_expected_fields(
    api_request: APIRequestContext,
):
    response = api_request.get("/api/getRankings")

    assert response.ok
    players = response.json()
    assert isinstance(players, list)
    assert players
    assert all(REQUIRED_PLAYER_FIELDS <= player.keys() for player in players)
    assert len({player["id_player"] for player in players}) == len(players)


def test_refresh_monthly_points_returns_success(api_request: APIRequestContext):
    response = api_request.get("/api/refreshMonthlyPoints")

    assert response.ok
    assert response.json() == {"message": "OK"}