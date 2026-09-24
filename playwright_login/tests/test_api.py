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