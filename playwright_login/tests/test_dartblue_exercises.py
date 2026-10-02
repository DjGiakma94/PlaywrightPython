import json
from http import HTTPStatus

import pytest
from playwright.sync_api import APIRequestContext, Page

from config.settings import Env, get_base_url, get_env
from data.users import DEFAULT_USER, INVALID_USER, SIGNUP_USER, TEST_PLAYER_NAMES
from pages.login_page import LoginPage

USERNAME = get_env(Env.USERNAME, DEFAULT_USER["username"])
PASSWORD = get_env(Env.PASSWORD, DEFAULT_USER["password"])


# EXERCISE 1: verify the Dartblue player directory without modifying data.
def test_exercise_1_players_directory_is_readable(api_request: APIRequestContext):
    response = api_request.get("/api/getAllUsers")

    assert response.ok
    body = response.json()
    players = body.get("data")
    assert body.get("statusCode") == HTTPStatus.OK
    assert isinstance(players, list) and players
    assert all({"id", "nome", "soprannome", "role"} <= player.keys() for player in players)
    assert len({player["id"] for player in players}) == len(players)
    listed_names = {player["nome"].strip().upper() for player in players}
    assert set(TEST_PLAYER_NAMES) <= listed_names


# EXERCISE 2: open the main dashboard sections.
def test_exercise_2_dashboard_sections_are_clickable(page: Page):
    page.route("**/api/refreshMonthlyPoints", lambda route: _fulfill_json(route, {"message": "OK"}))
    dartblue_page = _open_home(page)

    dartblue_page.open_monthly_ranking()
    dartblue_page.close_monthly_ranking()

    dartblue_page.open_history()
    dartblue_page.close_history()

    dartblue_page.open_last_match()
    assert dartblue_page.last_match_dialog.is_visible()


# EXERCISE 3: select the players for the three match positions.
def test_exercise_3_match_form_selects_distinct_players(page: Page):
    dartblue_page = _open_home(page)
    _login(dartblue_page)

    dartblue_page.open_insert_match_form()
    available_players = {
        name.strip().upper(): name
        for name in dartblue_page.available_match_player_names()
    }
    assert set(TEST_PLAYER_NAMES) <= available_players.keys()
    selected_players = [available_players[name] for name in TEST_PLAYER_NAMES]
    dartblue_page.select_match_positions(*selected_players)

    assert dartblue_page.match_position_values() == selected_players


# EXERCISE 4: sort the ranking by player name in both directions.
def test_exercise_4_ranking_can_be_sorted_by_player_name(page: Page):
    dartblue_page = _open_home(page)
    initial_names = dartblue_page.ranking_names_in_display_order()

    dartblue_page.sort_ranking_by_player_name()
    assert dartblue_page.ranking_names_in_display_order() == sorted(
        initial_names, key=str.casefold
    )

    dartblue_page.sort_ranking_by_player_name()
    assert dartblue_page.ranking_names_in_display_order() == sorted(
        initial_names, key=str.casefold, reverse=True
    )


# EXERCISE 5: display the players from the latest match.
def test_exercise_5_last_match_shows_podium(page: Page):
    dartblue_page = _open_home(page)

    dartblue_page.open_last_match()
    assert dartblue_page.last_match_dialog.is_visible()
    assert "Caricamento" not in dartblue_page.last_match_body.inner_text()


# EXERCISE 6: verify signup without creating an account on the live server.
def test_exercise_6_signup_success_is_shown(page: Page):
    page.route(
        "**/api/signup",
        lambda route: _fulfill_json(route, {"message": "Account creato con successo"}),
    )
    dartblue_page = _open_home(page)

    dartblue_page.open_signup_form()
    message = dartblue_page.sign_up(**SIGNUP_USER)
    assert "Account creato con successo" in message


# EXERCISE 7: verify that the monthly ranking loads.
def test_exercise_7_monthly_ranking_displays_players(
    page: Page,
):
    page.route("**/api/refreshMonthlyPoints", lambda route: _fulfill_json(route, {"message": "OK"}))
    real_user_names = {
        user["nome"].strip().casefold()
        for user in _browser_api_get(page, "/api/getAllUsers")["data"]
        if user.get("nome")
    }
    dartblue_page = _open_home(page)

    dartblue_page.open_monthly_ranking()
    monthly_text = dartblue_page.monthly_ranking_text()
    assert any(name in monthly_text.casefold() for name in real_user_names)


# EXERCISE 8: verify that invalid credentials display an error.
def test_exercise_8_invalid_login_shows_error(page: Page):
    dartblue_page = _open_home(page)
    dartblue_page.login(INVALID_USER["username"], INVALID_USER["password"])

    assert "Credenziali non valide" in dartblue_page.invalid_credentials_error()


# EXERCISE 9: register a real match with TEST players and restore the initial data.
def test_exercise_9_match_submission_resets_test_players(page: Page, db_connection):
    dartblue_page = _open_home(page)
    token = _login(dartblue_page)
    _clear_test_players(page, token)
    baseline_match_log_id = _latest_match_log_id(db_connection)
    baseline_last_match = _browser_api_get(page, "/api/getLastMatch")
    test_user_ids = {
        user["nome"].strip().upper(): user["id"]
        for user in _browser_api_get(page, "/api/getAllUsers")["data"]
        if user.get("nome")
    }
    selected_player_ids = [test_user_ids[name] for name in TEST_PLAYER_NAMES]

    try:
        dartblue_page.open_insert_match_form()
        available_players = {
            name.strip().upper(): name
            for name in dartblue_page.available_match_player_names()
        }
        assert set(TEST_PLAYER_NAMES) <= available_players.keys()
        selected_players = [available_players[name] for name in TEST_PLAYER_NAMES]
        dartblue_page.select_match_positions(*selected_players)
        dartblue_page.set_match_participants(selected_players)

        with page.expect_request(
            lambda request: request.url.endswith("/api/addNewGame")
            and request.method == "POST"
        ) as submitted_request:
            with page.expect_response(
                lambda response: response.url.endswith("/api/addNewGame")
                and response.request.method == "POST"
            ) as submitted_response:
                assert dartblue_page.submit_match()

        assert submitted_response.value.ok
        payload = submitted_request.value.post_data_json
        assert [payload["primo"], payload["secondo"], payload["terzo"]] == [
            name.upper() for name in selected_players
        ]
        assert payload["tuttiGiocatori"] == [name.upper() for name in selected_players]

        updated_players = _read_test_players(page)
        assert all(
            updated_players[name]["partiteGiocate"] == 1
            for name in TEST_PLAYER_NAMES
        )
    finally:
        try:
            _delete_new_test_match_log(
                db_connection,
                baseline_match_log_id,
                selected_player_ids,
            )
        finally:
            _clear_test_players(page, token)

    reset_players = _read_test_players(page)
    for name in TEST_PLAYER_NAMES:
        assert reset_players[name]["partiteGiocate"] == 0
        assert reset_players[name]["primo"] == 0
        assert reset_players[name]["secondo"] == 0
        assert reset_players[name]["terzo"] == 0
    assert _browser_api_get(page, "/api/getLastMatch") == baseline_last_match
    assert _latest_match_log_id(db_connection) == baseline_match_log_id


def _fulfill_json(
    route,
    payload: dict | list,
    status: HTTPStatus = HTTPStatus.OK,
) -> None:
    route.fulfill(
        status=status,
        content_type="application/json",
        body=json.dumps(payload),
    )


def _open_home(page: Page) -> LoginPage:
    dartblue_page = LoginPage(page)
    dartblue_page.open()
    return dartblue_page


def _login(dartblue_page: LoginPage) -> str:
    dartblue_page.login(USERNAME, PASSWORD)
    assert dartblue_page.greeting_text()
    token = dartblue_page.session_token()
    assert token
    return token


def _browser_api_get(page: Page, path: str, token: str | None = None) -> dict | list:
    headers = {"Authorization": f"Bearer {token}"} if token else None
    response = page.context.request.get(f"{get_base_url()}{path}", headers=headers)
    assert response.ok, f"GET {path} fallita: {response.status} {response.text()}"
    return response.json()


def _read_test_players(page: Page) -> dict[str, dict]:
    return {
        player["nome"].strip().upper(): player
        for player in _browser_api_get(page, "/api/getRankings")
        if player.get("nome", "").strip().upper().startswith("TEST")
    }


def _clear_test_players(page: Page, token: str) -> None:
    _browser_api_get(page, "/api/clearTestPlayers", token)


def _latest_match_log_id(db_connection) -> int:
    with db_connection.cursor() as cursor:
        cursor.execute('SELECT COALESCE(MAX(id), 0) AS match_id FROM "LogPartite"')
        return cursor.fetchone()["match_id"]


def _delete_new_test_match_log(
    db_connection,
    after_id: int,
    player_ids: list[int],
) -> None:
    with db_connection.cursor() as cursor:
        cursor.execute(
            'SELECT id,id_quarto,id_quinto,id_sesto,id_settimo,id_ottavo,id_nono,id_decimo '
            'FROM "LogPartite" WHERE id>%s AND id_primo=%s AND id_secondo=%s '
            'AND id_terzo=%s ORDER BY id DESC',
            (after_id, *player_ids),
        )
        matches = cursor.fetchall()
        assert len(matches) <= 1, "Trovate più partite TEST dopo l'avvio del test"
        if not matches:
            return

        match = matches[0]
        assert all(
            match[column] is None
            for column in (
                "id_quarto",
                "id_quinto",
                "id_sesto",
                "id_settimo",
                "id_ottavo",
                "id_nono",
                "id_decimo",
            )
        ), "La partita da ripristinare contiene partecipanti non TEST"
        cursor.execute(
            'DELETE FROM "LogPartite" WHERE id=%s AND id_primo=%s '
            'AND id_secondo=%s AND id_terzo=%s',
            (match["id"], *player_ids),
        )
        assert cursor.rowcount == 1


@pytest.fixture
def page(browser):
    test_page = browser.new_page()
    yield test_page
    test_page.close()