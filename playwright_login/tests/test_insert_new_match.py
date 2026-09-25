from playwright.sync_api import Browser

from config.settings import Env, get_env
from database.classifica import fetch_main_ranking
from pages.login_page import LoginPage

USERNAME = get_env(Env.USERNAME, "testuser@example.com")
PASSWORD = get_env(Env.PASSWORD, "testpass")


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


def test_insert_new_match_disables_selected_players_in_third_position(
    browser: Browser,
):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(USERNAME, PASSWORD)
    login_page.open_insert_match_form()

    first_player = "DAVIDE"
    second_player = "VALERIO"

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
