from playwright.sync_api import Browser

from config.settings import Env, get_env
from database.classifica import fetch_main_ranking
from data.users import DEFAULT_USER, MATCH_PLAYERS_TO_SELECT
from pages.login_page import LoginPage

USERNAME = get_env(Env.USERNAME, DEFAULT_USER["username"])
PASSWORD = get_env(Env.PASSWORD, DEFAULT_USER["password"])


# Verify that the match form lists every player from the main ranking.
def test_insert_new_match_dropdown_contains_all_main_ranking_players(
    browser: Browser,
    db_connection,
):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(USERNAME, PASSWORD)
    login_page.open_insert_match_form()

    ui_players = login_page.dropdown_option_names(login_page.primo_select)
    db_players = {
        login_page._normalise_name(name) for name in fetch_main_ranking(db_connection)
    }

    assert db_players.issubset(ui_players), (
        "DB players are missing from the UI dropdown: "
        f"db={sorted(db_players - ui_players)}; ui={sorted(ui_players)}"
    )

    page.close()


# Verify that players selected in the first two positions cannot be selected third.
def test_insert_new_match_disables_selected_players_in_third_position(
    browser: Browser,
):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(USERNAME, PASSWORD)
    login_page.open_insert_match_form()

    first_player, second_player = MATCH_PLAYERS_TO_SELECT

    login_page.primo_select.select_option(label=first_player)
    login_page.secondo_select.select_option(label=second_player)

    disabled_names = login_page.disabled_option_names(login_page.terzo_select)

    assert first_player in disabled_names
    assert second_player in disabled_names

    assert (
        login_page.terzo_select.locator(f"option:has-text('{first_player}')")
        .first.get_attribute("disabled")
        is not None
    )
    assert (
        login_page.terzo_select.locator(f"option:has-text('{second_player}')")
        .first.get_attribute("disabled")
        is not None
    )

    page.close()


# Verify that all players in the last match appear in the main ranking.
def test_last_match_players_are_in_main_ranking(browser: Browser, db_connection):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    main_ranking_players = {
        login_page._normalise_name(name) for name in fetch_main_ranking(db_connection)
    }

    login_page.open_last_match()
    last_match_players = login_page.last_match_player_names()

    assert last_match_players, "No players found in the last match modal"
    assert last_match_players.issubset(main_ranking_players), (
        "Last match players are missing from the main ranking: "
        f"{sorted(last_match_players - main_ranking_players)}"
    )
    page.close()
